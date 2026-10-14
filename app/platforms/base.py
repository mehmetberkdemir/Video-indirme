# -*- coding: utf-8 -*-
"""Platform abstract base class."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.settings import Settings


class PlatformBase(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Platform teknik adı (örn. 'youtube')."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Kullanıcıya gösterilen ad (örn. 'YouTube')."""
        ...

    @abstractmethod
    def match(self, url: str) -> bool:
        """URL bu platforma ait mi?"""
        ...

    @abstractmethod
    def get_ytdlp_args(self, url: str, settings: "Settings") -> list[str]:
        """Bu URL için yt-dlp komut satırı argümanlarını döner."""
        ...
