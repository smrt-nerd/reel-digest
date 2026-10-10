import os
from typing import Callable, Any
from pathlib import Path
from reel_digest.downloader import AudioDownloader
from reel_digest.transcriber import FasterWhisperTranscriber
from reel_digest.summarizer import OmnirouteSummarizer
from reel_digest.storage import NoteExporter

class ReelDigestPipeline:
    def __init__(
        self,
        progress_callback: Callable[[str], None] | None = None
    ):
        self.progress = progress_callback or (lambda msg: print(f"-> {msg}"))

        self.progress("Initializing pipeline components...")
        self.downloader = AudioDownloader()
        self.transcriber = FasterWhisperTranscriber()
        self.summarizer = OmnirouteSummarizer()
        self.storage = NoteExporter()

    def process(self, url: str) -> str:
        audio_path = None
        try:
            self.progress(f"Downloading audio from {url}")
            audio_path, title, platform_metadata = self.downloader.download(url)
            self.progress(f"Audio downloaded: {title} (saved to temp)")

            self.progress(f"Transcribing audio with faster-whisper (CPU int8)...")
            transcript_result = self.transcriber.transcribe(audio_path)
            self.progress(f"Transcription complete ({transcript_result.duration:.1f}s audio). Idea synthesis starting...")

            summary_result = self.summarizer.summarize(transcript_result.text, title)
            self.progress(f"Summarized successfully. Generating Markdown note...")

            note_path = self.storage.export(
                url=url,
                title=title,
                transcript_result=transcript_result,
                summary_result=summary_result,
                platform_metadata=platform_metadata
            )
            self.progress(f"Success! Note saved to {note_path}")
            return note_path

        finally:
            # Cleanup temporary audio file
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                    self.progress("Cleaned up temporary audio tracks.")
                except Exception as e:
                    self.progress(f"Note: Could not clean up audio {audio_path}: {e}")
