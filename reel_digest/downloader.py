import os
import tempfile
from pathlib import Path
from typing import Tuple, Dict, Any
import yt_dlp

from reel_digest.config import settings
from reel_digest.platform import BasePlatform, PlatformMetadata
from reel_digest.detector import detect_and_get_platform


class AudioDownloader:
    def __init__(self, output_dir: str | Path | None = None):
        self.output_dir = Path(output_dir) if output_dir else Path(tempfile.gettempdir()) / "reel_digest_audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download(self, url: str) -> Tuple[str, str, PlatformMetadata]:
        """
        Downloads audio from a URL using yt-dlp with platform-aware options.

        Args:
            url: The URL to download (Instagram Reel, YouTube video, YouTube Shorts, etc.)

        Returns:
            Tuple of (audio_file_path, content_title, platform_metadata)

        Raises:
            RuntimeError: If FFmpeg is not found
            ValueError: If URL is not supported or invalid
            Exception: If download fails
        """
        if not settings.ffmpeg_path:
            raise RuntimeError(
                "FFmpeg could not be found automatically. Please install FFmpeg or set FFMPEG_PATH in your .env file."
            )

        # Detect platform and get metadata
        platform, metadata = detect_and_get_platform(url)

        # Apply YouTube-specific duration limit if applicable
        if metadata.platform == "youtube" and settings.youtube_max_duration > 0:
            # Note: We'll check duration after download since yt-dlp provides it in info
            pass

        # First attempt (with cookies if configured for Instagram)
        use_cookies = bool(settings.browser_cookies) and metadata.platform == "instagram"

        try:
            return self._execute_download(url, platform, metadata, use_cookies=use_cookies)
        except Exception as e:
            err_msg = str(e).lower()
            # If failed due to browser cookie lock or extraction issues, retry without cookies
            if use_cookies and ("cookie" in err_msg or "database" in err_msg):
                return self._execute_download(url, platform, metadata, use_cookies=False)
            raise

    def _execute_download(
        self,
        url: str,
        platform: BasePlatform,
        metadata: PlatformMetadata,
        use_cookies: bool = True
    ) -> Tuple[str, str, PlatformMetadata]:
        """
        Execute download with platform-specific options.

        Args:
            url: The URL to download
            platform: Platform instance
            metadata: Platform metadata
            use_cookies: Whether to use browser cookies

        Returns:
            Tuple of (audio_file_path, content_title, updated_metadata)
        """
        # Get platform-specific download options
        opts = self._build_ydl_opts(platform, use_cookies=use_cookies)

        with yt_dlp.YoutubeDL(opts) as ydl:
            # Download and extract info
            info = ydl.extract_info(url, download=True)

            # Update metadata with info from yt-dlp
            metadata = self._update_metadata_from_info(metadata, info)

            # Get audio file path
            video_id = info.get('id', 'unknown') or metadata.video_id or 'unknown'
            title = info.get('title', metadata.title or platform.platform_type.value.title())

            # Use platform-specific filename template
            filename_template = platform.get_default_filename_template()
            expected_filename = filename_template % {
                'id': video_id,
                'title': self._sanitize_filename(title),
                'ext': 'mp3'
            }

            audio_path = self.output_dir / expected_filename

            # Find the downloaded file (might have different extension)
            if not audio_path.exists():
                # Look for any file with the video ID
                possible_files = list(self.output_dir.glob(f"*{video_id}*"))
                if possible_files:
                    audio_path = possible_files[0]
                else:
                    # Try to find the most recent file in output directory
                    files = list(self.output_dir.glob("*"))
                    if files:
                        audio_path = max(files, key=lambda f: f.stat().st_mtime)
                    else:
                        raise FileNotFoundError(f"Downloaded audio file for ID {video_id} could not be found.")

            return str(audio_path.absolute()), title, metadata

    def _build_ydl_opts(self, platform: BasePlatform, use_cookies: bool = True) -> Dict[str, Any]:
        """
        Build yt-dlp options with platform-specific configuration.

        Args:
            platform: Platform instance
            use_cookies: Whether to use browser cookies

        Returns:
            Dictionary of yt-dlp options
        """
        # Start with platform-specific options
        ydl_opts = platform.get_download_options()

        # Add common options
        ydl_opts.update({
            'outtmpl': str(self.output_dir / platform.get_default_filename_template()),
            'ffmpeg_location': str(Path(settings.ffmpeg_path).parent) if settings.ffmpeg_path else None,
            'quiet': True,
            'no_warnings': True,
        })

        # Add cookies for Instagram if configured
        if use_cookies and settings.browser_cookies and platform.platform_type.value == "instagram":
            ydl_opts['cookiesfrombrowser'] = (settings.browser_cookies,)

        # Apply YouTube-specific settings
        if platform.platform_type.value == "youtube" and settings.youtube_max_duration > 0:
            ydl_opts['match_filter'] = self._create_duration_filter(settings.youtube_max_duration)

        return ydl_opts

    def _update_metadata_from_info(self, metadata: PlatformMetadata, info: Dict) -> PlatformMetadata:
        """
        Update metadata with information from yt-dlp.

        Args:
            metadata: Original metadata
            info: yt-dlp info dictionary

        Returns:
            Updated PlatformMetadata
        """
        # Update fields if they exist in info
        if not metadata.title and 'title' in info:
            metadata.title = info['title']

        if not metadata.description and 'description' in info:
            metadata.description = info['description']

        if not metadata.author and 'uploader' in info:
            metadata.author = info['uploader']

        if not metadata.duration and 'duration' in info:
            metadata.duration = info['duration']

        if not metadata.video_id and 'id' in info:
            metadata.video_id = info['id']

        if not metadata.thumbnail_url and 'thumbnail' in info:
            metadata.thumbnail_url = info['thumbnail']

        if not metadata.view_count and 'view_count' in info:
            metadata.view_count = info['view_count']

        if not metadata.upload_date and 'upload_date' in info:
            metadata.upload_date = info['upload_date']

        return metadata

    def _create_duration_filter(self, max_duration: int):
        """
        Create a match filter for maximum duration.

        Args:
            max_duration: Maximum duration in seconds

        Returns:
            Match filter function for yt-dlp
        """
        def duration_filter(info):
            duration = info.get('duration')
            if duration is not None and duration > max_duration:
                return f"Video too long ({duration}s > {max_duration}s limit)"
            return None

        return duration_filter

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for use in filesystem.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove or replace characters that are problematic in filenames
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Limit length
        if len(filename) > 100:
            filename = filename[:100]

        return filename.strip()
