# -*- coding: utf-8 -*-
"""Facebook platform desteği (stub)."""

import re
from typing import TYPE_CHECKING

from app.platforms.base import PlatformBase

if TYPE_CHECKING:
    from app.core.settings import Settings

_PATTERNS = [
    r"https?://(www\.)?facebook\.com/.*videos?/[^\s]+",
    r"https?://(www\.)?fb\.watch/[^\s]+",
]
_REGEX = re.compile("|".join(_PATTERNS))


class FacebookPlatform(PlatformBase):
    @property
    def name(self) -> str:
        return "facebook"

    @property
    def display_name(self) -> str:
        return "Facebook"

    def match(self, url: str) -> bool:
        return bool(_REGEX.search(url))

    def get_ytdlp_args(self, url: str, settings: "Settings") -> list[str]:
        output_dir = settings.get("output_dir", ".")
        return [
            "-f", "best",
            "-P", output_dir,
            "--output", "%(title)s.%(ext)s",
        ]
