from abc import ABC, abstractmethod
from typing import NamedTuple
from faster_whisper import WhisperModel
from reel_digest.config import settings

class TranscriptSegment(NamedTuple):
    start: float
    end: float
    text: str

class TranscriptResult(NamedTuple):
    text: str
    language: str
    duration: float
    segments: list[TranscriptSegment]

class BaseTranscriber(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> TranscriptResult:
        """Transcribe an audio file into text."""
        pass

class FasterWhisperTranscriber(BaseTranscriber):
    def __init__(
        self,
        model_size: str | None = None,
        device: str | None = None,
        compute_type: str | None = None,
        cpu_threads: int | None = None
    ):
        self.model_size = model_size or settings.whisper_model_size
        self.device = device or settings.whisper_device
        self.compute_type = compute_type or settings.whisper_compute_type
        self.cpu_threads = cpu_threads or settings.whisper_threads

        # Lazy load model on demand to save memory during startup
        self._model: WhisperModel | None = None

    def _get_model(self) -> WhisperModel:
        if self._model is None:
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                cpu_threads=self.cpu_threads,
            )
        return self._model

    def transcribe(self, audio_path: str) -> TranscriptResult:
        model = self._get_model()

        # Transcribe with faster-whisper
        segments_gen, info = model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True, # Filter out background noise/silence
            vad_parameters=dict(min_silence_duration_ms=500),
        )

        segments = []
        full_text_parts = []

        for s in segments_gen:
            segments.append(TranscriptSegment(start=s.start, end=s.end, text=s.text.strip()))
            full_text_parts.append(s.text.strip())

        full_text = " ".join(full_text_parts)

        return TranscriptResult(
            text=full_text,
            language=info.language,
            duration=info.duration,
            segments=segments
        )
