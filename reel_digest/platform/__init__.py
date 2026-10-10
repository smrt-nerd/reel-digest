"""
Platform module for multi-platform support.

This module provides abstract base classes and concrete implementations
for different platforms (Instagram, YouTube, etc.).
"""

from .base import BasePlatform, PlatformType, PlatformMetadata
from .instagram import InstagramPlatform
from .youtube import YouTubePlatform

__all__ = [
    'BasePlatform',
    'PlatformType',
    'PlatformMetadata',
    'InstagramPlatform',
    'YouTubePlatform',
]