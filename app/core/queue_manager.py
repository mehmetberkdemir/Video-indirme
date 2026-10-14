# -*- coding: utf-8 -*-
"""İndirme kuyruğu state machine – ana thread'de çalışır."""

from __future__ import annotations

import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QObject, Signal

from app.core.downloader import DownloadThread

if TYPE_CHECKING:
    from app.core.settings import Settings


class DownloadStatus(Enum):
    PENDING = auto()
    DOWNLOADING = auto()
    PAUSED = auto()
    DONE = auto()
    ERROR = auto()
    CANCELLED = auto()


@dataclass
class DownloadItem:
    url: str
    title: str = ""
    status: DownloadStatus = DownloadStatus.PENDING
    progress: float = 0.0
    speed: str = ""
    error: str = ""
    output_file: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    ytdlp_args: list = field(default_factory=list)
    _thread: Optional[DownloadThread] = field(default=None, repr=False)


class QueueManager(QObject):
    """İndirme kuyruğunu yönetir."""

    item_added   = Signal(object)   # DownloadItem
    item_updated = Signal(object)   # DownloadItem
    item_removed = Signal(str)      # item.id

    def __init__(self, settings: "Settings", parent=None):
        super().__init__(parent)
        self._settings = settings
        self._items: list[DownloadItem] = []
        self._active: list[DownloadItem] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def items(self) -> list[DownloadItem]:
        return list(self._items)

    def add(self, url: str, ytdlp_args: list[str], title: str = "") -> Optional[DownloadItem]:
        """URL'yi kuyruğa ekler. Zaten aktif ise None döner."""
        active_urls = {
            i.url for i in self._items
            if i.status in (DownloadStatus.PENDING, DownloadStatus.DOWNLOADING, DownloadStatus.PAUSED)
        }
        if url in active_urls:
            return None
        # Yeni eklenen öğeler PAUSED olarak başlar — kullanıcı "Başlat" ile başlatır
        item = DownloadItem(url=url, title=title or url, ytdlp_args=ytdlp_args,
                            status=DownloadStatus.PAUSED)
        self._items.append(item)
        self.item_added.emit(item)
        return item

    def cancel(self, item_id: str):
        item = self._find(item_id)
        if not item:
            return
        if item._thread and item._thread.isRunning():
            item._thread.cancel()
        item.status = DownloadStatus.CANCELLED
        self.item_updated.emit(item)
        self._active = [i for i in self._active if i.id != item_id]
        self._schedule()

    def pause(self, item_id: str):
        """İndirmeyi duraklatır (.part dosyaları kalır)."""
        item = self._find(item_id)
        if not item:
            return
        if item.status == DownloadStatus.DOWNLOADING:
            item.status = DownloadStatus.PAUSED   # önce set et, sonra kill
            if item._thread and item._thread.isRunning():
                item._thread.cancel()
            self._active = [i for i in self._active if i.id != item_id]
            self.item_updated.emit(item)
        elif item.status == DownloadStatus.PENDING:
            item.status = DownloadStatus.PAUSED
            self.item_updated.emit(item)

    def resume(self, item_id: str):
        """Duraklatılmış indirmeyi devam ettirir."""
        item = self._find(item_id)
        if not item or item.status != DownloadStatus.PAUSED:
            return
        item.status = DownloadStatus.PENDING
        item.speed = ""
        self.item_updated.emit(item)
        self._schedule()

    def retry(self, item_id: str):
        """Hatalı indirmeyi sıfırlayıp yeniden başlatır."""
        item = self._find(item_id)
        if not item or item.status != DownloadStatus.ERROR:
            return
        item.status = DownloadStatus.PENDING
        item.progress = 0.0
        item.error = ""
        item.speed = ""
        self.item_updated.emit(item)
        self._schedule()

    def pause_all(self):
        """Tüm aktif ve bekleyen indirmeleri duraklatır."""
        for item in list(self._items):
            if item.status in (DownloadStatus.DOWNLOADING, DownloadStatus.PENDING):
                self.pause(item.id)

    def resume_all(self):
        """Tüm duraklatılmış indirmeleri devam ettirir."""
        for item in list(self._items):
            if item.status == DownloadStatus.PAUSED:
                self.resume(item.id)

    def remove(self, item_id: str):
        self.cancel(item_id)
        self._items = [i for i in self._items if i.id != item_id]
        self.item_removed.emit(item_id)

    def clear_done(self):
        done_ids = [
            i.id for i in self._items
            if i.status in (DownloadStatus.DONE, DownloadStatus.ERROR, DownloadStatus.CANCELLED)
        ]
        for item_id in done_ids:
            self._items = [i for i in self._items if i.id != item_id]
            self.item_removed.emit(item_id)

    # ------------------------------------------------------------------
    # Kuyruk kalıcılığı
    # ------------------------------------------------------------------

    def save_queue(self, path: str):
        """PENDING ve PAUSED öğeleri JSON'a yazar."""
        data = []
        for item in self._items:
            if item.status in (DownloadStatus.PENDING, DownloadStatus.PAUSED,
                               DownloadStatus.DOWNLOADING):
                data.append({
                    "id": item.id,
                    "url": item.url,
                    "title": item.title,
                    "status": "PAUSED",   # hepsini PAUSED olarak kaydet
                    "ytdlp_args": item.ytdlp_args,
                    "progress": item.progress,
                })
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Queue save error: {e}")

    def load_queue(self, path: str):
        """queue.json'dan öğeleri yükler."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return
        for entry in data:
            item = DownloadItem(
                url=entry.get("url", ""),
                title=entry.get("title", entry.get("url", "")),
                ytdlp_args=entry.get("ytdlp_args", []),
                id=entry.get("id", str(uuid.uuid4())),
            )
            item.status = DownloadStatus.PAUSED
            item.progress = entry.get("progress", 0.0)
            self._items.append(item)
            self.item_added.emit(item)
        # Kayıtlı PAUSED öğeleri otomatik başlatma — kullanıcı "Tümünü Başlat" desin

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _find(self, item_id: str) -> Optional[DownloadItem]:
        for i in self._items:
            if i.id == item_id:
                return i
        return None

    def _schedule(self):
        max_concurrent = self._settings.get("max_concurrent", 2)
        pending = [i for i in self._items if i.status == DownloadStatus.PENDING]
        while len(self._active) < max_concurrent and pending:
            item = pending.pop(0)
            self._start(item)

    def _start(self, item: DownloadItem):
        item.status = DownloadStatus.DOWNLOADING
        self._active.append(item)
        self.item_updated.emit(item)

        thread = DownloadThread(item.url, item.ytdlp_args)
        item._thread = thread

        thread.progress.connect(lambda pct, spd, i=item: self._on_progress(i, pct, spd))
        thread.finished.connect(lambda ok, msg, fpath, i=item: self._on_finished(i, ok, msg, fpath))
        thread.start()

    def _on_progress(self, item: DownloadItem, pct: float, speed: str):
        item.progress = pct
        item.speed = speed
        self.item_updated.emit(item)

    def _on_finished(self, item: DownloadItem, success: bool, message: str, output_file: str):
        self._active = [i for i in self._active if i.id != item.id]
        if item.status in (DownloadStatus.CANCELLED, DownloadStatus.PAUSED):
            pass  # kill() ile durduruldu, status zaten set edildi
        elif success:
            item.status = DownloadStatus.DONE
            item.progress = 100.0
            item.output_file = output_file
        else:
            item.status = DownloadStatus.ERROR
            item.error = message
        self.item_updated.emit(item)
        self._schedule()

    def delete_file(self, item_id: str):
        """İndirilen dosyayı diskten siler ve öğeyi kuyruktan kaldırır."""
        item = self._find(item_id)
        if not item:
            return
        if item.output_file and os.path.isfile(item.output_file):
            try:
                os.remove(item.output_file)
            except OSError as e:
                logging.getLogger("queue_manager").warning("Delete file failed: %s", e)
        self._items = [i for i in self._items if i.id != item_id]
        self.item_removed.emit(item_id)
