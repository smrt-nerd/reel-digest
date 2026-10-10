"""
YouTube platform implementation.

This module provides the YouTubePlatform class for handling YouTube videos
and YouTube Shorts.
"""

import re
from typing import Dict, Any
from urllib.parse import urlparse, parse_qs

from .base import BasePlatform, PlatformType, PlatformMetadata


class YouTubePlatform(BasePlatform):
    """Platform implementation for YouTube."""

    @property
    def platform_type(self) -> PlatformType:
        """Return the platform type."""
        return PlatformType.YOUTUBE

    def validate_url(self, url: str) -> bool:
        """
        Validate if the URL belongs to YouTube.

        Args:
            url: The URL to validate

        Returns:
            True if URL belongs to YouTube, False otherwise
        """
        # Basic URL validation
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False

        # Check domain
        netloc = parsed.netloc.lower()
        if 'youtube.com' not in netloc and 'youtu.be' not in netloc:
            return False

        # Check path patterns for YouTube video content
        path = parsed.path.lower()

        # Standard YouTube video URLs
        if '/watch' in path:
            # Check for v parameter
            query = parse_qs(parsed.query)
            return 'v' in query and len(query['v'][0]) > 0

        # YouTube Shorts
        if '/shorts/' in path:
            # /shorts/{video_id}
            path_parts = path.strip('/').split('/')
            return len(path_parts) >= 2 and path_parts[0] == 'shorts'

        # youtu.be short URLs
        if netloc == 'youtu.be':
            path_parts = path.strip('/').split('/')
            return len(path_parts) >= 1 and bool(path_parts[0])

        # Embedded URLs
        if '/embed/' in path or '/v/' in path:
            return True

        return False

    def extract_metadata(self, url: str) -> PlatformMetadata:
        """
        Extract metadata from a YouTube URL.

        Args:
            url: The YouTube URL

        Returns:
            PlatformMetadata object with extracted information
        """
        parsed = urlparse(url)
        video_id = self._extract_video_id(url)
        is_shorts = '/shorts/' in url.lower()

        # Determine content type
        content_type = "YouTube Shorts" if is_shorts else "YouTube Video"

        # Default title
        title = f"{content_type} {video_id}" if video_id else content_type

        return PlatformMetadata(
            platform=self.platform_type,
            url=url,
            title=title,
            description=None,  # Will be filled during download
            author=None,  # Will be filled during download
            duration=None,  # Will be filled during download
            video_id=video_id,
            thumbnail_url=self._get_thumbnail_url(video_id) if video_id else None,
            view_count=None,
            upload_date=None,
        )

    def get_download_options(self) -> Dict[str, Any]:
        """
        Get YouTube-specific download options for yt-dlp.

        Returns:
            Dictionary of yt-dlp options specific to YouTube
        """
        return {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            # YouTube-specific options
            'extract_flat': False,
            'ignoreerrors': True,
            # Add metadata extraction
            'writethumbnail': False,
            'writeinfojson': False,
            # Optimize for audio-only
            'format_sort': ['size', 'br', 'res', 'fps'],
            'prefer_ffmpeg': True,
        }

    def get_default_filename_template(self) -> str:
        """
        Get default filename template for YouTube content.

        Returns:
            Filename template string
        """
        return '%(title)s-%(id)s.%(ext)s'

    def normalize_url(self, url: str) -> str:
        """
        Normalize YouTube URL to standard format.

        Args:
            url: The YouTube URL

        Returns:
            Normalized URL string
        """
        url = url.strip()

        # Extract video ID
        video_id = self._extract_video_id(url)
        if not video_id:
            return url

        # Return standard YouTube watch URL
        return f"https://www.youtube.com/watch?v={video_id}"

    def _extract_video_id(self, url: str) -> str:
        """
        Extract video ID from various YouTube URL formats.

        Args:
            url: The YouTube URL

        Returns:
            Video ID string or empty string if not found
        """
        # Do not lower() the url because YouTube IDs are case-sensitive!

        # Standard watch URL: youtube.com/watch?v=VIDEO_ID
        match = re.search(r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)', url, re.IGNORECASE)
        if match:
            return match.group(1)

        # YouTube Shorts: youtube.com/shorts/VIDEO_ID
        match = re.search(r'youtube\.com/shorts/([a-zA-Z0-9_-]+)', url, re.IGNORECASE)
        if match:
            return match.group(1)

        # youtu.be short URL: youtu.be/VIDEO_ID
        match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url, re.IGNORECASE)
        if match:
            return match.group(1)

        # Embedded URL: youtube.com/embed/VIDEO_ID
        match = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]+)', url, re.IGNORECASE)
        if match:
            return match.group(1)

        # /v/ URL: youtube.com/v/VIDEO_ID
        match = re.search(r'youtube\.com/v/([a-zA-Z0-9_-]+)', url, re.IGNORECASE)
        if match:
            return match.group(1)

        return ""

    def _get_thumbnail_url(self, video_id: str) -> str:
        """
        Get YouTube thumbnail URL for a video ID.

        Args:
            video_id: YouTube video ID

        Returns:
            Thumbnail URL string
        """
        # YouTube thumbnail URLs
        # maxresdefault.jpg: Highest resolution
        # sddefault.jpg: Standard definition
        # hqdefault.jpg: High quality
        # mqdefault.jpg: Medium quality
        # default.jpg: Default/low quality
        return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"