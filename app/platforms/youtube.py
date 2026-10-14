# -*- coding: utf-8 -*-
"""YouTube platform desteği."""

import re
from typing import TYPE_CHECKING

from app.platforms.base import PlatformBase

if TYPE_CHECKING:
    from app.core.settings import Settings

_PATTERNS = [
    r"https?://(www\.)?youtube\.com/watch\?[^\s]*v=[^\s]+",
    r"https?://youtu\.be/[^\s]+",
    r"https?://(www\.)?youtube\.com/shorts/[^\s]+",
    r"https?://(www\.)?youtube\.com/live/[^\s]+",
    r"https?://music\.youtube\.com/watch\?[^\s]*v=[^\s]+",
]
_REGEX = re.compile("|".join(_PATTERNS))

FORMAT_MAP = {
    "bv*[height<=1080]+ba/b": "-f bv*[height<=1080]+ba/b",
    "bv*[height<=720]+ba/b": "-f bv*[height<=720]+ba/b",
    "bv*[height<=480]+ba/b": "-f bv*[height<=480]+ba/b",
    "bestvideo+bestaudio/best": "-f bestvideo+bestaudio/best",
    "audio_only": "-f bestaudio",
}


class YouTubePlatform(PlatformBase):
    @property
    def name(self) -> str:
        return "youtube"

    @property
    def display_name(self) -> str:
        return "YouTube"

    def match(self, url: str) -> bool:
        return bool(_REGEX.search(url))

    def get_ytdlp_args(self, url: str, settings: "Settings") -> list[str]:
        fmt = settings.get("format", "bv[vcodec^=avc1][height<=1080]+ba[acodec^=mp4a]/bv[height<=1080]+ba/b")
        merge = settings.get("merge_format", "mp4")
        output_dir = settings.get("output_dir", ".")

        if fmt == "audio_only":
            args = [
                "-f", "bestaudio",
                "-x", "--audio-format", "mp3",
                "-P", output_dir,
                "--no-playlist",
                "--output", "%(title)s.%(ext)s",
            ]
        else:
            args = [
                "-f", fmt,
                "--merge-output-format", merge,
                "-P", output_dir,
                "--no-playlist",
                "--output", "%(title)s.%(ext)s",
            ]
        return args
