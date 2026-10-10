import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from typing import Literal

# Load .env if present
load_dotenv()


class Settings:
    def __init__(self):
        # AI Configuration
        self.omniroute_base_url: str = os.getenv("OMNIROUTE_BASE_URL", "https://api.openai.com/v1")
        self.omniroute_api_key: str = os.getenv("OMNIROUTE_API_KEY", "")
        self.omniroute_model: str = os.getenv("OMNIROUTE_MODEL", "gpt-4o-mini")

        # Whisper Transcription Configuration
        self.whisper_model_size: str = os.getenv("WHISPER_MODEL_SIZE", "small.en")
        self.whisper_device: str = os.getenv("WHISPER_DEVICE", "cpu")
        self.whisper_compute_type: str = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
        self.whisper_threads: int = int(os.getenv("WHISPER_THREADS", "4"))

        # Platform Configuration
        self.platform_output_org: Literal["same_folder", "subfolders", "prefix"] = os.getenv(
            "PLATFORM_OUTPUT_ORG", "same_folder"
        )
        self.default_platform: str = os.getenv("DEFAULT_PLATFORM", "auto")

        # YouTube-specific Configuration
        self.youtube_max_duration: int = int(os.getenv("YOUTUBE_MAX_DURATION", "3600"))  # 1 hour default
        self.youtube_download_format: str = os.getenv("YOUTUBE_DOWNLOAD_FORMAT", "bestaudio")

        # Download Configuration
        self.ffmpeg_path: str = os.getenv("FFMPEG_PATH", "")
        self.browser_cookies: str = os.getenv("BROWSER_COOKIES", "")
        self.output_dir: Path = Path(os.getenv("OUTPUT_DIR", "output"))

        # Validate platform output organization
        if self.platform_output_org not in ["same_folder", "subfolders", "prefix"]:
            self.platform_output_org = "same_folder"

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Auto-discover ffmpeg if not explicitly provided
        if not self.ffmpeg_path:
            self.ffmpeg_path = self._discover_ffmpeg()

    def _discover_ffmpeg(self) -> str:
        # Check system PATH first
        ffmpeg_cmd = shutil.which("ffmpeg")
        if ffmpeg_cmd:
            return ffmpeg_cmd

        # Common Windows WinGet locations
        winget_base = Path(os.path.expanduser("~")) / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
        if winget_base.exists():
            for pkg_dir in winget_base.iterdir():
                if "ffmpeg" in pkg_dir.name.lower():
                    for f in pkg_dir.rglob("ffmpeg.exe"):
                        return str(f.absolute())

        # Common AppData locations (CapCut, File Converter, etc.)
        local_app = Path(os.path.expanduser("~")) / "AppData" / "Local"
        for candidate in local_app.rglob("ffmpeg.exe"):
            return str(candidate.absolute())

        return ""

    def get_output_path(self, filename: str, platform: str = "") -> Path:
        """
        Get output path based on platform output organization settings.

        Args:
            filename: The filename to save
            platform: The platform name (e.g., 'youtube', 'instagram')

        Returns:
            Path object for the output file
        """
        if not platform or self.platform_output_org == "same_folder":
            return self.output_dir / filename

        elif self.platform_output_org == "subfolders":
            platform_dir = self.output_dir / platform
            platform_dir.mkdir(exist_ok=True)
            return platform_dir / filename

        elif self.platform_output_org == "prefix":
            prefixed_filename = f"{platform}_{filename}"
            return self.output_dir / prefixed_filename

        else:
            # Fallback to same folder
            return self.output_dir / filename


settings = Settings()
