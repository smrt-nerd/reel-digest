"""
Platform detection and URL validation.

This module provides functions for detecting the platform type from URLs
and validating URLs for different platforms.
"""

import re
from typing import Optional, Tuple
from urllib.parse import urlparse

from .platform import PlatformType, InstagramPlatform, YouTubePlatform
from .platform.base import BasePlatform, PlatformMetadata


# Regex patterns for platform detection
INSTAGRAM_PATTERNS = [
    r'instagram\.com/reel/',
    r'instagram\.com/p/',
    r'instagram\.com/tv/',
    r'instagram\.com/reels/',
]

YOUTUBE_PATTERNS = [
    r'youtube\.com/watch\?v=',
    r'youtube\.com/shorts/',
    r'youtu\.be/',
    r'youtube\.com/embed/',
    r'youtube\.com/v/',
]


def detect_platform(url: str) -> PlatformType:
    """
    Detect the platform type from a URL.

    Args:
        url: The URL to analyze

    Returns:
        PlatformType enum value
    """
    try:
        # Basic URL validation
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return PlatformType.UNKNOWN
    except Exception:
        return PlatformType.UNKNOWN

    # Normalize for pattern matching
    normalized_url = url.lower()

    # Check YouTube patterns
    for pattern in YOUTUBE_PATTERNS:
        if re.search(pattern, normalized_url):
            return PlatformType.YOUTUBE

    # Check Instagram patterns
    for pattern in INSTAGRAM_PATTERNS:
        if re.search(pattern, normalized_url):
            return PlatformType.INSTAGRAM

    return PlatformType.UNKNOWN


def get_platform_instance(platform_type: PlatformType) -> BasePlatform:
    """
    Get platform instance for the given platform type.

    Args:
        platform_type: The platform type

    Returns:
        Platform instance

    Raises:
        ValueError: If platform type is unknown or not supported
    """
    if platform_type == PlatformType.INSTAGRAM:
        return InstagramPlatform()
    elif platform_type == PlatformType.YOUTUBE:
        return YouTubePlatform()
    else:
        raise ValueError(f"Unsupported platform type: {platform_type}")


def detect_and_get_platform(url: str) -> Tuple[BasePlatform, PlatformMetadata]:
    """
    Detect platform from URL and get platform instance with metadata.

    Args:
        url: The URL to process

    Returns:
        Tuple of (platform_instance, platform_metadata)

    Raises:
        ValueError: If platform cannot be detected or URL is invalid
    """
    # Detect platform
    platform_type = detect_platform(url)
    if platform_type == PlatformType.UNKNOWN:
        raise ValueError(f"Unsupported or invalid URL: {url}")

    # Get platform instance
    platform = get_platform_instance(platform_type)

    # Normalize URL
    normalized_url = platform.normalize_url(url)

    # Extract metadata
    metadata = platform.extract_metadata(normalized_url)

    return platform, metadata


def validate_url(url: str, platform_type: Optional[PlatformType] = None) -> bool:
    """
    Validate if URL is valid for the specified platform.

    Args:
        url: The URL to validate
        platform_type: Optional platform type to validate against.
                       If None, tries to auto-detect.

    Returns:
        True if URL is valid, False otherwise
    """
    try:
        if platform_type:
            # Validate against specific platform
            platform = get_platform_instance(platform_type)
            return platform.validate_url(url)
        else:
            # Auto-detect and validate
            platform_type = detect_platform(url)
            if platform_type == PlatformType.UNKNOWN:
                return False
            platform = get_platform_instance(platform_type)
            return platform.validate_url(url)
    except (ValueError, Exception):
        return False


def extract_platform_metadata(url: str) -> PlatformMetadata:
    """
    Extract metadata from URL for any supported platform.

    Args:
        url: The URL to extract metadata from

    Returns:
        PlatformMetadata object

    Raises:
        ValueError: If platform cannot be detected or URL is invalid
    """
    platform_type = detect_platform(url)
    if platform_type == PlatformType.UNKNOWN:
        raise ValueError(f"Unsupported or invalid URL: {url}")

    platform = get_platform_instance(platform_type)
    normalized_url = platform.normalize_url(url)
    return platform.extract_metadata(normalized_url)