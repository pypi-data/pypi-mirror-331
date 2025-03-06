"""Asynchronous wrapper for Bithuman Runtime."""

import asyncio
import threading
from typing import AsyncIterator, Optional, Union

from loguru import logger

from .api import VideoControl, VideoFrame
from .runtime import BithumanRuntime, BufferEmptyCallback


class AsyncBithumanRuntime(BithumanRuntime):
    """Asynchronous wrapper for Bithuman Runtime.

    This class wraps the synchronous BithumanRuntime to provide an asynchronous interface.
    It runs the runtime in a separate thread to avoid blocking the asyncio event loop.
    """

    def __init__(
        self,
        *,
        input_buffer_size: int = 0,
        output_buffer_size: int = 5,
        token: Optional[str] = None,
    ) -> None:
        """Initialize the async runtime with a BithumanRuntime instance.

        Args:
            input_buffer_size: Size of the input buffer.
            output_buffer_size: Size of the output buffer.
            token: The token for the Bithuman Runtime.
        """
        super().__init__(input_buffer_size=input_buffer_size, token=token)

        # Thread management
        self._stop_event = threading.Event()
        self._thread = None

        # Use a standard asyncio.Queue for frames since they're only accessed from async context
        self._frame_queue = asyncio.Queue[Union[VideoFrame, Exception]](
            maxsize=output_buffer_size
        )

        # State
        self._running = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    async def set_avatar_model(self, avatar_model_path: str) -> None:
        """Set the avatar model for the runtime.

        Args:
            avatar_model_path: The path to the avatar model.
        """
        # run the set_avatar_model in the executor and wait for it to finish
        loop = self._loop or asyncio.get_running_loop()
        await loop.run_in_executor(None, super().set_avatar_model, avatar_model_path)

    async def push_audio(
        self, data: bytes, sample_rate: int, last_chunk: bool = True
    ) -> None:
        """Push audio data to the runtime asynchronously.

        Args:
            data: Audio data in bytes.
            sample_rate: Sample rate of the audio.
            last_chunk: Whether this is the last chunk of the speech.
        """
        control = VideoControl.from_audio(data, sample_rate, last_chunk)
        await self._input_buffer.aput(control)

    async def push(self, control: VideoControl) -> None:
        """Push a VideoControl to the runtime asynchronously.

        Args:
            control: The VideoControl to push.
        """
        await self._input_buffer.aput(control)

    async def flush(self) -> None:
        """Flush the audio buffer, indicating end of speech."""
        await self._input_buffer.aput(VideoControl(end_of_speech=True))

    async def run(
        self,
        out_buffer_empty: Optional[BufferEmptyCallback] = None,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> AsyncIterator[VideoFrame]:
        """Stream video frames asynchronously.

        Yields:
            VideoFrame objects from the runtime.
        """
        # Start the runtime if not already running
        await self.start(out_buffer_empty, loop=loop)

        try:
            while True:
                # Get the next frame from the queue
                item = await self._frame_queue.get()

                # If we got an exception, raise it
                if isinstance(item, Exception):
                    raise item

                # Yield the frame
                yield item

                # Mark the task as done
                self._frame_queue.task_done()

        except asyncio.CancelledError:
            # Stream was cancelled, stop the runtime
            await self.stop()
            raise

    async def start(
        self,
        out_buffer_empty: Optional[BufferEmptyCallback] = None,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        """Start the runtime thread."""
        if self._running:
            return

        # Store the current event loop
        self._loop = loop or asyncio.get_running_loop()
        self._input_buffer.set_loop(self._loop)

        # Clear the stop event
        self._stop_event.clear()

        # Start the runtime thread
        self._running = True
        self._thread = threading.Thread(
            target=self._frame_producer, args=(out_buffer_empty,)
        )
        self._thread.daemon = True
        self._thread.start()

    async def stop(self) -> None:
        """Stop the runtime thread."""
        if not self._running:
            return

        # Set the stop event
        self._stop_event.set()

        # Wait for the thread to finish
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

        # Reset state
        self._running = False

    def _frame_producer(
        self, out_buffer_empty: Optional[BufferEmptyCallback] = None
    ) -> None:
        """Run the runtime in a separate thread and produce frames."""
        try:
            # Run the runtime and process frames
            out_buffer_empty = out_buffer_empty or self._frame_queue.empty
            for frame in super().run(out_buffer_empty):
                if self._stop_event.is_set():
                    break

                # Put the frame in the frame queue
                if self._loop and self._loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._frame_queue.put(frame), self._loop
                    )
                    # Wait for the frame to be added to the queue
                    future.result()
                else:
                    break

        except Exception as e:
            # If an exception occurs, put it in the frame queue
            if self._loop and self._loop.is_running():
                try:
                    asyncio.run_coroutine_threadsafe(
                        self._frame_queue.put(e), self._loop
                    ).result()
                except Exception as e:
                    logger.error(f"Error putting exception in frame queue: {e}")
