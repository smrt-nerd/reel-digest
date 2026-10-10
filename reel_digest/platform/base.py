from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class PlatformType(Enum):
    """Supported platform types."""
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    UNKNOWN = "unknown"


@dataclass
class PlatformMetadata:
    """Platform-specific metadata extracted from URLs."""
    platform: PlatformType
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    duration: Optional[float] = None  # in seconds
    video_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    view_count: Optional[int] = None
    upload_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for easy serialization."""
        return {
            'platform': self.platform.value,
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'author': self.author,
            'duration': self.duration,
            'video_id': self.video_id,
            'thumbnail_url': self.thumbnail_url,
            'view_count': self.view_count,
            'upload_date': self.upload_date,
        }


class BasePlatform(ABC):
    """Abstract base class for platform implementations."""

    @property
    @abstractmethod
    def platform_type(self) -> PlatformType:
        """Return the platform type."""
        pass

    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """
        Validate if the URL belongs to this platform.

        Args:
            url: The URL to validate

        Returns:
            True if URL belongs to this platform, False otherwise
        """
        pass

    @abstractmethod
    def extract_metadata(self, url: str) -> PlatformMetadata:
        """
        Extract metadata from a URL.

        Args:
            url: The URL to extract metadata from

        Returns:
            PlatformMetadata object with extracted information
        """
        pass

    @abstractmethod
    def get_download_options(self) -> Dict[str, Any]:
        """
        Get platform-specific download options for yt-dlp.

        Returns:
            Dictionary of yt-dlp options specific to this platform
        """
        pass

    @abstractmethod
    def get_default_filename_template(self) -> str:
        """
        Get default filename template for downloaded content.

        Returns:
            Filename template string (e.g., "%(title)s-%(id)s.%(ext)s")
        """
        pass

    def normalize_url(self, url: str) -> str:
        """
        Normalize URL to standard format.

        Args:
            url: The URL to normalize

        Returns:
            Normalized URL string
        """
        # Default implementation returns URL as-is
        return url.strip()