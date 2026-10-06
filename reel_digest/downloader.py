import os
import tempfile
from pathlib import Path
import yt_dlp
from reel_digest.config import settings

class AudioDownloader:
    def __init__(self, output_dir: str | Path | None = None):
        self.output_dir = Path(output_dir) if output_dir else Path(tempfile.gettempdir()) / "reel_digest_audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _build_ydl_opts(self, use_cookies: bool = True) -> dict:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': str(self.output_dir / '%(id)s.%(ext)s'),
            'ffmpeg_location': str(Path(settings.ffmpeg_path).parent) if settings.ffmpeg_path else None,
            'quiet': True,
            'no_warnings': True,
        }

        if use_cookies and settings.browser_cookies:
            ydl_opts['cookiesfrombrowser'] = (settings.browser_cookies,)

        return ydl_opts

    def download(self, url: str) -> tuple[str, str]:
        """
        Downloads audio from an Instagram Reel URL using yt-dlp.
        Returns a tuple of (audio_file_path, reel_title).
        """
        if not settings.ffmpeg_path:
            raise RuntimeError(
                "FFmpeg could not be found automatically. Please install FFmpeg or set FFMPEG_PATH in your .env file."
            )

        # First attempt (with cookies if configured)
        try:
            return self._execute_download(url, use_cookies=bool(settings.browser_cookies))
        except Exception as e:
            err_msg = str(e).lower()
            # If failed due to browser cookie lock or extraction issues, retry without cookies
            if settings.browser_cookies and ("cookie" in err_msg or "database" in err_msg):
                return self._execute_download(url, use_cookies=False)
            raise

    def _execute_download(self, url: str, use_cookies: bool) -> tuple[str, str]:
        opts = self._build_ydl_opts(use_cookies=use_cookies)
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get('id', 'unknown')
            title = info.get('title', 'Instagram Reel')

            audio_path = self.output_dir / f"{video_id}.mp3"

            if not audio_path.exists():
                possible_files = list(self.output_dir.glob(f"{video_id}.*"))
                if possible_files:
                    audio_path = possible_files[0]
                else:
                    raise FileNotFoundError(f"Downloaded audio file for ID {video_id} could not be found.")

            return str(audio_path.absolute()), title
