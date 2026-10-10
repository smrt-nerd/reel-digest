"""
Instagram platform implementation.

This module provides the InstagramPlatform class for handling Instagram Reels
and other Instagram video content.
"""

import re
from typing import Dict, Any
from urllib.parse import urlparse, parse_qs

from .base import BasePlatform, PlatformType, PlatformMetadata


class InstagramPlatform(BasePlatform):
    """Platform implementation for Instagram."""

    @property
    def platform_type(self) -> PlatformType:
        """Return the platform type."""
        return PlatformType.INSTAGRAM

    def validate_url(self, url: str) -> bool:
        """
        Validate if the URL belongs to Instagram.

        Args:
            url: The URL to validate

        Returns:
            True if URL belongs to Instagram, False otherwise
        """
        # Basic URL validation
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False

        # Check domain
        if 'instagram.com' not in parsed.netloc:
            return False

        # Check path patterns for Instagram video content
        path = parsed.path.lower()
        return (
            '/reel/' in path or
            '/p/' in path or
            '/tv/' in path or
            '/reels/' in path
        )

    def extract_metadata(self, url: str) -> PlatformMetadata:
        """
        Extract metadata from an Instagram URL.

        Args:
            url: The Instagram URL

        Returns:
            PlatformMetadata object with extracted information
        """
        # For Instagram, we rely on yt-dlp to get metadata during download
        # This method extracts basic information from the URL structure
        parsed = urlparse(url)

        # Extract post ID from path
        path_parts = parsed.path.strip('/').split('/')
        video_id = None
        for i, part in enumerate(path_parts):
            if part in ['reel', 'p', 'tv', 'reels'] and i + 1 < len(path_parts):
                video_id = path_parts[i + 1]
                break

        # Default title based on post ID
        title = f"Instagram Reel {video_id}" if video_id else "Instagram Content"

        return PlatformMetadata(
            platform=self.platform_type,
            url=url,
            title=title,
            description=None,  # Will be filled during download
            author=None,  # Will be filled during download
            duration=None,  # Will be filled during download
            video_id=video_id,
            thumbnail_url=None,  # Will be filled during download
            view_count=None,
            upload_date=None,
        )

    def get_download_options(self) -> Dict[str, Any]:
        """
        Get Instagram-specific download options for yt-dlp.

        Returns:
            Dictionary of yt-dlp options specific to Instagram
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
            # Instagram-specific options
            'extractor_args': {
                'instagram': {
                    'requested_formats': ['audio']
                }
            }
        }

    def get_default_filename_template(self) -> str:
        """
        Get default filename template for Instagram content.

        Returns:
            Filename template string
        """
        return '%(id)s.%(ext)s'

    def normalize_url(self, url: str) -> str:
        """
        Normalize Instagram URL to standard format.

        Args:
            url: The Instagram URL

        Returns:
            Normalized URL string
        """
        # Strip trailing slash and query parameters for consistency
        url = url.strip()
        if url.endswith('/'):
            url = url[:-1]

        # Remove tracking parameters
        parsed = urlparse(url)
        if parsed.query:
            # Keep only essential query parameters if any
            query_params = parse_qs(parsed.query)
            # Instagram doesn't typically need query params for video IDs
            # So we remove them for cleaner URLs
            query = ''

        # Reconstruct URL without query
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        return normalized