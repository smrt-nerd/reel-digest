"""
Tests for platform detection and URL validation.
"""

import pytest
from reel_digest.detector import (
    detect_platform,
    validate_url,
    get_platform_instance,
    extract_platform_metadata,
    detect_and_get_platform,
)
from reel_digest.platform import PlatformType, InstagramPlatform, YouTubePlatform


class TestPlatformDetection:
    """Test platform detection from URLs."""

    def test_detect_platform_instagram_reel(self):
        """Test detection of Instagram Reel URLs."""
        urls = [
            "https://www.instagram.com/reel/Cxample123/",
            "https://instagram.com/reel/Cxample123/",
            "https://www.instagram.com/reel/Cxample123/?igshid=xyz",
            "https://www.instagram.com/reel/Cxample123/?utm_source=ig_web_copy_link",
        ]

        for url in urls:
            result = detect_platform(url)
            assert result == PlatformType.INSTAGRAM

    def test_detect_platform_instagram_post(self):
        """Test detection of Instagram post URLs."""
        urls = [
            "https://www.instagram.com/p/Cxample123/",
            "https://instagram.com/p/Cxample123/",
            "https://www.instagram.com/p/Cxample123/?igshid=xyz",
        ]

        for url in urls:
            result = detect_platform(url)
            assert result == PlatformType.INSTAGRAM

    def test_detect_platform_youtube_video(self):
        """Test detection of YouTube video URLs."""
        urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=share",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ?si=xyz",
        ]

        for url in urls:
            result = detect_platform(url)
            assert result == PlatformType.YOUTUBE

    def test_detect_platform_youtube_shorts(self):
        """Test detection of YouTube Shorts URLs."""
        urls = [
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "https://youtube.com/shorts/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ?feature=share",
        ]

        for url in urls:
            result = detect_platform(url)
            assert result == PlatformType.YOUTUBE

    def test_detect_platform_embedded_youtube(self):
        """Test detection of embedded YouTube URLs."""
        urls = [
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/v/dQw4w9WgXcQ",
        ]

        for url in urls:
            result = detect_platform(url)
            assert result == PlatformType.YOUTUBE

    def test_detect_platform_unknown(self):
        """Test detection of unknown URLs."""
        urls = [
            "https://www.example.com/video",
            "https://vimeo.com/123456",
            "https://tiktok.com/@user/video/123456",
            "not-a-url",
            "",
        ]

        for url in urls:
            result = detect_platform(url)
            assert result == PlatformType.UNKNOWN

    def test_detect_platform_invalid_url(self):
        """Test detection with invalid URL."""
        assert detect_platform("not-a-valid-url") == PlatformType.UNKNOWN


class TestPlatformValidation:
    """Test URL validation for platforms."""

    def test_validate_url_instagram(self):
        """Test validation of Instagram URLs."""
        valid_urls = [
            "https://www.instagram.com/reel/Cxample123/",
            "https://instagram.com/p/Cxample123/",
        ]

        invalid_urls = [
            "https://www.instagram.com/username/",
            "https://www.instagram.com/",
            "https://www.example.com/reel/123",
        ]

        for url in valid_urls:
            assert validate_url(url) == True
            assert validate_url(url, PlatformType.INSTAGRAM) == True

        for url in invalid_urls:
            assert validate_url(url) == False

    def test_validate_url_youtube(self):
        """Test validation of YouTube URLs."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        ]

        invalid_urls = [
            "https://www.youtube.com/",
            "https://www.youtube.com/@channel",
            "https://www.youtube.com/playlist?list=xyz",
        ]

        for url in valid_urls:
            assert validate_url(url) == True
            assert validate_url(url, PlatformType.YOUTUBE) == True

        for url in invalid_urls:
            assert validate_url(url) == False


class TestPlatformInstances:
    """Test platform instance creation."""

    def test_get_platform_instance_instagram(self):
        """Test getting Instagram platform instance."""
        platform = get_platform_instance(PlatformType.INSTAGRAM)
        assert isinstance(platform, InstagramPlatform)
        assert platform.platform_type == PlatformType.INSTAGRAM

    def test_get_platform_instance_youtube(self):
        """Test getting YouTube platform instance."""
        platform = get_platform_instance(PlatformType.YOUTUBE)
        assert isinstance(platform, YouTubePlatform)
        assert platform.platform_type == PlatformType.YOUTUBE

    def test_get_platform_instance_unknown(self):
        """Test getting unknown platform instance."""
        with pytest.raises(ValueError):
            get_platform_instance(PlatformType.UNKNOWN)


class TestPlatformMetadata:
    """Test platform metadata extraction."""

    def test_extract_metadata_instagram(self):
        """Test metadata extraction from Instagram URLs."""
        url = "https://www.instagram.com/reel/Cxample123/"
        metadata = extract_platform_metadata(url)

        assert metadata.platform == PlatformType.INSTAGRAM
        assert metadata.url == "https://www.instagram.com/reel/Cxample123"
        assert metadata.video_id == "Cxample123"
        assert metadata.title is not None

    def test_extract_metadata_youtube(self):
        """Test metadata extraction from YouTube URLs."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        metadata = extract_platform_metadata(url)

        assert metadata.platform == PlatformType.YOUTUBE
        assert metadata.url.startswith("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert metadata.video_id == "dQw4w9WgXcQ"
        assert metadata.title is not None

    def test_extract_metadata_youtube_shorts(self):
        """Test metadata extraction from YouTube Shorts URLs."""
        url = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        metadata = extract_platform_metadata(url)

        assert metadata.platform == PlatformType.YOUTUBE
        assert metadata.video_id == "dQw4w9WgXcQ"
        assert metadata.title is not None

    def test_extract_metadata_invalid_url(self):
        """Test metadata extraction from invalid URL."""
        with pytest.raises(ValueError):
            extract_platform_metadata("https://www.example.com/video")


class TestDetectAndGetPlatform:
    """Test combined detection and platform instance creation."""

    def test_detect_and_get_platform_instagram(self):
        """Test detection and platform creation for Instagram."""
        url = "https://www.instagram.com/reel/Cxample123/"
        platform, metadata = detect_and_get_platform(url)

        assert isinstance(platform, InstagramPlatform)
        assert metadata.platform == PlatformType.INSTAGRAM
        assert metadata.url == "https://www.instagram.com/reel/Cxample123"

    def test_detect_and_get_platform_youtube(self):
        """Test detection and platform creation for YouTube."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        platform, metadata = detect_and_get_platform(url)

        assert isinstance(platform, YouTubePlatform)
        assert metadata.platform == PlatformType.YOUTUBE

    def test_detect_and_get_platform_invalid(self):
        """Test detection and platform creation for invalid URL."""
        with pytest.raises(ValueError):
            detect_and_get_platform("https://www.example.com/video")