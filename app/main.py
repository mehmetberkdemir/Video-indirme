# -*- coding: utf-8 -*-
"""
Video İndirici – QApplication bootstrap ve AppContext.
Başlatmak için: pythonw.exe app/main.py
"""

import logging
import os
import sys
import traceback

# Proje kökünü sys.path'e ekle (app/ klasörünün bir üstü)
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

# araçlar/ dizinini PATH'e ekle (ffmpeg, yt-dlp)
_TOOLS = os.path.join(_BASE, "araçlar")
os.environ["PATH"] = _TOOLS + os.pathsep + os.environ.get("PATH", "")


def _check_pyside6():
    try:
        import PySide6
    except ImportError:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Eksik Paket",
            "PySide6 bulunamadı!\n\n"
            "Lütfen şu komutu çalıştırın:\n"
            "araçlar\\python\\python.exe -m pip install PySide6",
        )
        sys.exit(1)


def _check_ytdlp():
    from app.core.paths import YTDLP_EXE
    if not os.path.isfile(YTDLP_EXE):
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "yt-dlp Bulunamadı",
                f"yt-dlp.exe bulunamadı:\n{YTDLP_EXE}\n\n"
                "Lütfen kur.bat'i çalıştırın.",
            )
        except Exception:
            print(f"ERROR: yt-dlp not found at {YTDLP_EXE}")
        sys.exit(1)


_check_pyside6()

# Log dosyası: proje kökü/app.log
_LOG_FILE = os.path.join(_BASE, "app.log")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(_LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("main")

def _excepthook(exc_type, exc_value, exc_tb):
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    log.critical("Uncaught exception:\n%s", msg)

sys.excepthook = _excepthook

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from app.core.paths import ensure_dirs, QUEUE_FILE
from app.core.settings import Settings
from app.i18n import set_language
from app.platforms import PlatformRegistry
from app.core.queue_manager import QueueManager
from app.core.clipboard_monitor import ClipboardMonitor
from app.notifications import notify
from app.ui.styles import DARK_STYLE


class AppContext:
    """Tüm bileşenleri tutan bağımlılık konteyneri."""

    def __init__(self):
        self.settings = Settings()
        set_language(self.settings.get("language", "tr"))

        self.platform_registry = PlatformRegistry()
        self.queue_manager = QueueManager(self.settings)
        self.clipboard_monitor = ClipboardMonitor(self.platform_registry)

        # Notifier: basit sarmalayıcı
        class _Notifier:
            def notify(self, title: str, message: str, icon_type: str = "info"):
                notify(title, message, icon_type)
        self.notifier = _Notifier()

    def start(self):
        ensure_dirs()
        if self.settings.get("clipboard_monitor", True):
            self.clipboard_monitor.start()
        # Önceki oturumdan kaydedilen kuyruğu yükle
        import os
        if os.path.exists(QUEUE_FILE):
            self.queue_manager.load_queue(QUEUE_FILE)


def main():
    _check_ytdlp()

    app = QApplication(sys.argv)
    app.setApplicationName("Video İndirici")
    app.setOrganizationName("VideoIndirici")
    app.setQuitOnLastWindowClosed(False)  # Tray'e küçültünce çıkma

    # Stil
    app.setStyleSheet(DARK_STYLE)

    # Yüksek DPI (PySide6 6.x'te varsayılan, uyarı vermemek için kaldırıldı)

    ctx = AppContext()
    ctx.start()

    from app.ui.main_window import MainWindow
    window = MainWindow(ctx)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
