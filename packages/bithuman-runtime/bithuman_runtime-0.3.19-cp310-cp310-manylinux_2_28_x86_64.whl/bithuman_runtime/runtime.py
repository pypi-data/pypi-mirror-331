"""Bithuman Runtime."""

import asyncio
import copy
import logging
from functools import cached_property
from pathlib import Path
from queue import Empty, Queue
from threading import Event
from typing import Callable, Generic, Iterable, Optional, Self, TypeVar

import numpy as np
from loguru import logger

from . import audio as audio_utils
from .api import AudioChunk, VideoControl, VideoFrame
from .config import load_settings
from .lib.generator import BithumanGenerator
from .video_graph import Frame as FrameMeta
from .video_graph import VideoGraphNavigator

logging.getLogger("numba").setLevel(logging.WARNING)

T = TypeVar("T")

BufferEmptyCallback = Callable[[], bool]


class BithumanRuntime:
    """Bithuman Runtime."""

    def __init__(
        self, *, input_buffer_size: int = 0, token: Optional[str] = None
    ) -> None:
        """Initialize the Bithuman Runtime.

        Args:
            input_buffer_size: The size of the input buffer.
            token: The token for the Bithuman Runtime.
        """
        self.settings = copy.deepcopy(load_settings())
        self.generator = BithumanGenerator(str(self.settings.AUDIO_ENCODER_PATH))
        self.video_graph: Optional[VideoGraphNavigator] = None
        if token:
            if not self.generator.validate_token(token):
                raise ValueError("Invalid token")
        self._warmup()

        # Ignore audios when muted
        self.muted = Event()
        self.interrupt_event = Event()
        self._input_buffer = ThreadSafeAsyncQueue[VideoControl](
            maxsize=input_buffer_size
        )

        # Video
        self.audio_batcher = audio_utils.AudioStreamBatcher(
            output_sample_rate=self.settings.INPUT_SAMPLE_RATE
        )
        self._video_loaded = False
        self._sample_per_video_frame = (
            self.settings.INPUT_SAMPLE_RATE / self.settings.FPS
        )

    def validate_token(self, token: str) -> bool:
        """Validate the token."""
        return self.generator.validate_token(token)

    def is_token_validated(self) -> bool:
        """Check if the token is validated."""
        return self.generator.is_token_validated()

    def get_expiration_time(self) -> int:
        """Get the expiration time of the token."""
        return self.generator.get_expiration_time()

    def set_avatar_model(self, avatar_model_path: str) -> Self:
        """Set the video file or workspace directory.

        Args:
            avatar_model_path: The workspace directory.
        """
        if Path(avatar_model_path).is_file():
            self.generator.set_model_hash_from_file(avatar_model_path)
        else:
            logger.info(
                "Skip model hash verification for non-file avatar model, "
                "make sure the token is valid for kind of usage."
            )

        self.video_graph = VideoGraphNavigator.from_workspace(
            avatar_model_path, extract_to_local=self.settings.EXTRACT_WORKSPACE_TO_LOCAL
        ).load_workspace()

        self.video_graph.update_runtime_configs(self.settings)
        self.generator.set_output_size(self.settings.OUTPUT_WIDTH)
        self._video_loaded = False

        self.load_data()
        return self

    def load_data(self) -> None:
        """Load the workspace and set up related components."""
        if self._video_loaded:
            return
        if self.video_graph is None:
            raise ValueError("Video graph is not set. Call set_avatar_model() first.")

        models_path = Path(self.video_graph.avatar_model_path)

        def find_avatar_data_file(video_path: str) -> Optional[str]:
            video_name = Path(video_path).stem
            for type in ["feature-first", "time-first"]:
                files = list(models_path.glob(f"*/{video_name}.{type}.*"))
                if files:
                    return str(files[0])
            return None

        try:
            audio_feature_file = list(models_path.glob("*/feature_centers.npy"))[0]
        except IndexError:
            raise FileNotFoundError(f"Audio features file not found in {models_path}")
        audio_features = np.load(audio_feature_file)
        self.generator.set_audio_feature(audio_features)

        videos = list(self.video_graph.videos.items())
        filler_videos = list(self.video_graph.filler_videos.items())
        logger.info(
            f"Loading avatar data: {len(videos)} models and {len(filler_videos)} fillers"
        )
        logger.debug(f"Compression method: {self.settings.COMPRESS_METHOD}")
        for name, video in videos + filler_videos:
            video_data_path = video.video_data_path
            avatar_data_path = find_avatar_data_file(video.video_path)
            if video.lip_sync_required:
                assert video_data_path and avatar_data_path, (
                    f"Avatar data not found for video {name}"
                )
            else:
                video_data_path, avatar_data_path = "", ""

            # Process the video data file if needed
            video_data_path = self._process_video_data_file(video_data_path)
            self.generator.add_video(
                name,
                video_path=video.video_path,
                video_data_path=video_data_path,
                avatar_data_path=avatar_data_path,
                compression_type=self.settings.COMPRESS_METHOD,
                loading_mode=self.settings.LOADING_MODE,
            )
        logger.info("Avatar data loaded")

    def get_first_frame(self) -> Optional[np.ndarray]:
        """Get the first frame of the video."""
        if not self.video_graph:
            logger.error("Avatar model is not set. Call set_avatar_model() first.")
            return None
        try:
            return self.video_graph.get_first_frame(self.settings.OUTPUT_WIDTH)
        except Exception as e:
            logger.error(f"Failed to get the first frame: {e}")
            return None

    def get_frame_size(self) -> tuple[int, int]:
        """Get the frame size in width and height."""
        image = self.get_first_frame()
        if image is None:
            raise ValueError("Failed to get the first frame")
        return image.shape[1], image.shape[0]

    def interrupt(self) -> None:
        """Interrupt the daemon."""
        # clear the input buffer
        while not self._input_buffer.empty():
            try:
                self._input_buffer.get_nowait()
            except Empty:
                break
        self.audio_batcher.reset()
        self.interrupt_event.set()

    def set_muted(self, mute: bool) -> None:
        """Set the muted state."""
        if mute:
            self.muted.set()
        else:
            self.muted.clear()

    def push_audio(
        self, data: bytes, sample_rate: int, last_chunk: bool = True
    ) -> None:
        """Push the audio to the input buffer."""
        self._input_buffer.put(VideoControl.from_audio(data, sample_rate, last_chunk))

    def flush(self) -> None:
        """Flush the input buffer."""
        self._input_buffer.put(VideoControl(end_of_speech=True))

    def push(self, control: VideoControl) -> None:
        """Push the control (with audio, text, action, etc.) to the input buffer."""
        self._input_buffer.put(control)

    def run(
        self, out_buffer_empty: Optional[BufferEmptyCallback] = None
    ) -> Iterable[VideoFrame]:
        # Current frame index, reset for every new audio
        curr_frame_index = 0
        action_played = False  # Whether the action is played in this speech
        while True:
            try:
                if self.interrupt_event.is_set():
                    # Clear the interrupt event for the next loop
                    self.interrupt_event.clear()
                control = self._input_buffer.get(timeout=0.001)
                if self.muted.is_set():
                    # Consume and skip the audio when muted
                    control = VideoControl(message_id="MUTED")
                    action_played = False  # Reset the action played flag
            except Empty:
                if out_buffer_empty and not out_buffer_empty():
                    continue
                control = VideoControl(message_id="IDLE")  # idle

            # Edit the video based on script if the input is None
            if not control.target_video and not control.action:
                control.target_video, control.action = (
                    self.video_graph.videos_script.get_video_and_actions(
                        curr_frame_index,
                        control.emotion_preds,
                        text=control.text,
                        is_idle=control.is_idle,
                    )
                )
            if not control.is_idle:
                # Avoid playing the action multiple times in a conversation
                if action_played:
                    control.action = None
                elif control.action:
                    action_played = True

            for frame in self.process(control):
                yield frame
                curr_frame_index += 1

            if control.end_of_speech:
                self.audio_batcher.reset()
                # Passthrough the end flag of the speech
                yield VideoFrame(
                    source_message_id=control.message_id,
                    end_of_speech=control.end_of_speech,
                )

                # Reset the action played flag
                action_played = False
                curr_frame_index = 0
                self.video_graph.videos_script.last_nonidle_frame = 0

                # Reset the video graph if needed
                self.video_graph.next_n_frames(num_frames=0, on_user_speech=True)

    def process(self, control: VideoControl) -> Iterable[VideoFrame]:
        """Process the audio or control data."""

        def _get_next_frame() -> FrameMeta:
            return self.video_graph.next_n_frames(
                num_frames=1,
                target_video_name=control.target_video,
                actions_name=control.action,
                on_agent_speech=control.is_speaking,
            )[0]

        frame_index = 0
        for padded_chunk in self.audio_batcher.push(control.audio):
            audio_array = padded_chunk.array

            # get the mel chunks on padded audio
            mel_chunks = audio_utils.get_mel_chunks(
                audio_utils.int16_to_float32(audio_array), fps=self.settings.FPS
            )
            # unpad the audio and mel chunks
            audio_array = self.audio_batcher.unpad(audio_array)
            start = self.audio_batcher.pre_pad_video_frames
            valid_frames = int(len(audio_array) / self._sample_per_video_frame)
            mel_chunks = mel_chunks[start : start + valid_frames]

            num_frames = len(mel_chunks)
            samples_per_frame = len(audio_array) // max(num_frames, 1)
            for i, mel_chunk in enumerate(mel_chunks):
                if self.muted.is_set():
                    return
                if self.interrupt_event.is_set():
                    self.interrupt_event.clear()
                    return

                frame_meta = _get_next_frame()
                frame = self._process_talking_frame(frame_meta, mel_chunk)

                audio_start = i * samples_per_frame
                audio_end = (
                    audio_start + samples_per_frame
                    if i < num_frames - 1
                    else len(audio_array)
                )
                yield VideoFrame(
                    bgr_image=frame,
                    audio_chunk=AudioChunk(
                        data=audio_array[audio_start:audio_end],
                        sample_rate=padded_chunk.sample_rate,
                        last_chunk=i == num_frames - 1,
                    ),
                    frame_index=frame_index,
                    source_message_id=control.message_id,
                )
                frame_index += 1

        if frame_index == 0 and not control.audio:
            # generate idle frame if no frame is generated
            frame_meta = _get_next_frame()
            frame = self._process_idle_frame(frame_meta)
            yield VideoFrame(
                bgr_image=frame,
                frame_index=frame_index,
                source_message_id=control.message_id,
            )

    def _process_talking_frame(
        self, frame: FrameMeta, mel_chunk: np.ndarray
    ) -> np.ndarray:
        frame_np = self.generator.process_audio(
            mel_chunk, frame.video_name, frame.frame_index
        )
        return frame_np

    def _process_idle_frame(self, frame: FrameMeta) -> np.ndarray:
        """Get the idle frame with cache."""
        # Skip processing idle video
        if not self.settings.PROCESS_IDLE_VIDEO:
            frame_np = self.generator.get_original_frame(
                frame.video_name, frame.frame_index
            )
        else:
            frame_np = self.generator.process_audio(
                self.silent_mel_chunk, frame.video_name, frame.frame_index
            )
        return frame_np

    @cached_property
    def silent_mel_chunk(self) -> np.ndarray:
        """The mel chunk for silent audio."""
        audio_np = np.zeros(self.settings.INPUT_SAMPLE_RATE * 1, dtype=np.float32)
        return audio_utils.get_mel_chunks(audio_np, fps=self.settings.FPS)[0]

    def _process_video_data_file(self, video_data_path: str) -> str:
        """Process the video data file."""
        if not video_data_path:
            return video_data_path

        if video_data_path.endswith(".pth"):
            logger.debug(f"Converting pth to h5, torch is required: {video_data_path}")
            from .lib.pth2h5 import convert_pth_to_h5

            return convert_pth_to_h5(video_data_path)
        return video_data_path

    def _warmup(self) -> None:
        """Warm up the audio processing."""
        audio_utils.get_mel_chunks(
            np.zeros(16000, dtype=np.float32), fps=self.settings.FPS
        )

    def cleanup(self) -> None:
        """Clean up the video graph."""
        if self.video_graph:
            self.video_graph.cleanup()
            self.video_graph = None

    def __del__(self) -> None:
        """Clean up the video graph."""
        self.cleanup()


class ThreadSafeAsyncQueue(Generic[T]):
    """A thread-safe queue that can be used from both async and sync contexts.

    This queue uses a standard threading.Queue internally for thread safety,
    but provides async methods for use in async contexts.
    """

    def __init__(
        self, maxsize: int = 0, event_loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        """Initialize the queue.

        Args:
            maxsize: Maximum size of the queue. 0 means unlimited.
            event_loop: The event loop to use.
        """
        self._queue = Queue[T](maxsize=maxsize)
        self._loop = event_loop

    def put_nowait(self, item: T) -> None:
        """Put an item into the queue without blocking."""
        self._queue.put_nowait(item)

    async def aput(self, item: T, *args, **kwargs) -> None:
        """Put an item into the queue asynchronously."""
        # Use run_in_executor to avoid blocking the event loop
        if not self._loop:
            self._loop = asyncio.get_event_loop()
        await self._loop.run_in_executor(None, self._queue.put, item, *args, **kwargs)

    def put(self, item: T, *args, **kwargs) -> None:
        """Put an item into the queue."""
        self._queue.put(item, *args, **kwargs)

    def get_nowait(self) -> T:
        """Get an item from the queue without blocking."""
        return self._queue.get_nowait()

    async def aget(self, *args, **kwargs) -> T:
        """Get an item from the queue asynchronously."""
        # Use run_in_executor to avoid blocking the event loop
        if not self._loop:
            self._loop = asyncio.get_event_loop()
        return await self._loop.run_in_executor(None, self._queue.get, *args, **kwargs)

    def get(self, *args, **kwargs) -> T:
        """Get an item from the queue."""
        return self._queue.get(*args, **kwargs)

    def task_done(self) -> None:
        """Mark a task as done."""
        self._queue.task_done()

    def empty(self) -> bool:
        """Check if the queue is empty."""
        return self._queue.empty()

    def qsize(self) -> int:
        """Get the size of the queue."""
        return self._queue.qsize()

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set the event loop."""
        self._loop = loop
