# -*- coding: utf-8 -*-
"""Platform registry – tüm desteklenen platformları tek yerden yönetir."""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from app.platforms.base import PlatformBase
from app.platforms.youtube import YouTubePlatform
from app.platforms.facebook import FacebookPlatform

if TYPE_CHECKING:
    from app.core.settings import Settings


class PlatformRegistry:
    def __init__(self):
        self._platforms: list[PlatformBase] = [
            YouTubePlatform(),
            FacebookPlatform(),
        ]

    def match(self, url: str) -> Optional[PlatformBase]:
        """URL'ye uyan ilk platformu döner, yoksa None."""
        for p in self._platforms:
            if p.match(url):
                return p
        return None

    def get_ytdlp_args(self, url: str, settings: "Settings") -> list[str]:
        """URL için yt-dlp argümanlarını döner. Platform bulunamazsa temel argümanlar döner."""
        platform = self.match(url)
        if platform:
            return platform.get_ytdlp_args(url, settings)
        # Generic fallback
        output_dir = settings.get("output_dir", ".")
        return [
            "-f", "bv*+ba/b",
            "-P", output_dir,
            "--output", "%(title)s.%(ext)s",
        ]

    @property
    def platforms(self) -> list[PlatformBase]:
        return list(self._platforms)

    def register(self, platform: PlatformBase):
        self._platforms.append(platform)
