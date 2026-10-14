# -*- coding: utf-8 -*-
"""Pano izleyici – QThread içinde çalışır."""

import time

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication


class ClipboardMonitor(QThread):
    """Panonun içeriğini izler ve yeni bir URL tespit edince sinyal gönderir."""

    url_detected = Signal(str)

    def __init__(self, platform_registry, parent=None):
        super().__init__(parent)
        self._registry = platform_registry
        self._running = False
        self._seen: set[str] = set()

    def run(self):
        self._running = True
        previous = ""
        while self._running:
            try:
                cb = QApplication.clipboard()
                text = cb.text().strip()
                if text and text != previous:
                    previous = text
                    url = text.split()[0] if text else ""
                    if url and url not in self._seen:
                        platform = self._registry.match(url)
                        if platform:
                            self._seen.add(url)
                            self.url_detected.emit(url)
            except Exception:
                pass
            time.sleep(1.5)

    def stop(self):
        self._running = False
        self.quit()
        self.wait(3000)
