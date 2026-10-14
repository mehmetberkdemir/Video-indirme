# -*- coding: utf-8 -*-
"""yt-dlp subprocess yönetimi ve ilerleme parse."""

import logging
import os
import re
import subprocess
import tempfile
import time
from typing import Optional

from PySide6.QtCore import QThread, Signal

from app.core.paths import YTDLP_EXE, FFMPEG_DIR

log = logging.getLogger("downloader")

# yt-dlp ilerleme satırı örneği:
# [download]  45.3% of 123.45MiB at 2.34MiB/s ETA 00:32
_PROGRESS_RE = re.compile(
    r"\[download\]\s+([\d.]+)%\s+of\s+([\d.]+\s*\S+)\s+at\s+([\d.]+\s*\S+/s)(?:\s+ETA\s+(\S+))?"
)

# WinError 32/183 yeniden adlandırma hatası — hem tek hem çift ters eğik çizgi desteklenir
_RENAME_ERR_RE = re.compile(r'ERROR:.*?"(.+?\.temp\.[^"]+)"\s*->\s*"(.+?)"')

# Ara indirme dosyaları: title.f137.mp4, title.f140.m4a, vb.
_INTERMEDIATE_RE = re.compile(r'\.f\d+\.(mp4|m4a|webm|ogg)$', re.IGNORECASE)

# Geçici birleştirme dosyası: title.temp.mp4
_TEMP_FILE_RE = re.compile(r'\.temp\.(mp4|mkv|webm|ogg|m4a)$', re.IGNORECASE)


def _normpath(raw: str) -> str:
    """yt-dlp hata mesajından gelen çift ters eğik çizgili yolu normalize eder."""
    return os.path.normpath(raw)


def _file_accessible(path: str) -> bool:
    """Dosyanın var olup olmadığını kontrol eder; encoding sorunu için dizin taraması yapar."""
    if os.path.exists(path):
        return True
    # Encoding uyumsuzluğu için yedek: üst dizini listele
    try:
        parent = os.path.dirname(path)
        name = os.path.basename(path).lower()
        if os.path.isdir(parent):
            return any(f.lower() == name for f in os.listdir(parent))
    except OSError:
        pass
    return False


def _cleanup_intermediates(output_dir: str):
    """Videolar klasöründeki birleştirilmemiş ara dosyaları siler."""
    try:
        for f in os.listdir(output_dir):
            if _INTERMEDIATE_RE.search(f):
                path = os.path.join(output_dir, f)
                try:
                    os.remove(path)
                    log.debug("Cleaned up intermediate: %s", f)
                except OSError as e:
                    log.warning("Could not delete intermediate %s: %s", f, e)
    except OSError as e:
        log.warning("Could not list output dir for cleanup: %s", e)


class DownloadThread(QThread):
    """Tek bir URL'yi arka planda indirir."""

    progress = Signal(float, str)      # percent, speed
    finished = Signal(bool, str, str)  # success, message, output_file
    title_found = Signal(str)          # video title

    def __init__(self, url: str, ytdlp_args: list[str], parent=None):
        super().__init__(parent)
        self.url = url
        self.ytdlp_args = ytdlp_args
        self._process: Optional[subprocess.Popen] = None
        self._pending_renames: list[tuple[str, str]] = []  # (src_raw, dst_raw)
        self._output_dir: str = ""
        self._output_file: str = ""  # yt-dlp'nin bildirdiği son dosya yolu

    def run(self):
        # output_dir'i argümanlardan bul (-P parametresi)
        try:
            p_idx = self.ytdlp_args.index("-P")
            self._output_dir = self.ytdlp_args[p_idx + 1]
        except (ValueError, IndexError):
            self._output_dir = ""

        # Merge temp dosyasını Google Drive yerine yerel diske yaz
        local_temp = tempfile.gettempdir()
        cmd = [YTDLP_EXE] + self.ytdlp_args + [
            "--ffmpeg-location", FFMPEG_DIR,
            "--paths", f"temp:{local_temp}",
            "--continue",          # varsa .part dosyasından devam et
            "--no-overwrites",     # zaten var olan dosyayı tekrar indirme
            "--newline",
            self.url,
        ]
        log.debug("CMD: %s", " ".join(cmd))
        # Hem yt-dlp hem de yt-dlp'nin açtığı ffmpeg pencerelerini gizle
        _si = subprocess.STARTUPINFO()
        _si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        _si.wShowWindow = 0  # SW_HIDE
        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW,
                startupinfo=_si,
            )
            for line in self._process.stdout:
                line = line.rstrip()
                log.debug("YTDLP: %s", line)
                self._parse_line(line)
            self._process.wait(timeout=600)
            rc = self._process.returncode
            log.debug("Return code: %s", rc)

            if rc == 0:
                _cleanup_intermediates(self._output_dir)
                self.finished.emit(True, "", self._output_file)
            else:
                # Encoding sorunu nedeniyle regex yakalayamadıysa dizini tara
                if self._output_dir:
                    self._scan_temp_files()
                if self._pending_renames:
                    success = self._retry_renames()
                    if success:
                        _cleanup_intermediates(self._output_dir)
                        self.finished.emit(True, "", self._output_file)
                    else:
                        self.finished.emit(False, "Dosya kilidi: Windows Defender videolar klasörünü taradı. Tekrar deneyin.", "")
                else:
                    self.finished.emit(False, f"Return code: {rc}", "")

        except subprocess.TimeoutExpired:
            if self._process:
                self._process.kill()
            log.error("Download timeout: %s", self.url)
            self.finished.emit(False, "Timeout (10 dakika)", "")
        except Exception as e:
            log.exception("Download error: %s", self.url)
            self.finished.emit(False, str(e), "")

    def _scan_temp_files(self):
        """Çıktı dizinindeki .temp. dosyalarını tarar ve _pending_renames'e ekler."""
        if not os.path.isdir(self._output_dir):
            return
        existing_srcs = {_normpath(s) for s, _ in self._pending_renames}
        try:
            for fname in os.listdir(self._output_dir):
                if not _TEMP_FILE_RE.search(fname):
                    continue
                src = os.path.join(self._output_dir, fname)
                if src in existing_srcs:
                    continue
                # temp dosyadan hedef adı çıkar: title.temp.mp4 → title.mp4
                ext = _TEMP_FILE_RE.search(fname).group(0)      # ".temp.mp4"
                final_ext = "." + ext.rsplit(".", 1)[-1]         # ".mp4"
                dst_name = fname[: fname.lower().rfind(".temp.")] + final_ext
                dst = os.path.join(self._output_dir, dst_name)
                log.info("Found orphan temp file: %s -> %s", src, dst)
                self._pending_renames.append((src, dst))
        except OSError as e:
            log.warning("Temp file scan failed: %s", e)

    def _retry_renames(self, attempts: int = 8, delay: float = 1.5) -> bool:
        """WinError 32/183 sonrası temp→final yeniden adlandırmayı birkaç kez dener."""
        for attempt in range(1, attempts + 1):
            time.sleep(delay)
            remaining = []
            for src_raw, dst_raw in self._pending_renames:
                src = _normpath(src_raw)
                dst = _normpath(dst_raw)

                if not os.path.exists(src):
                    log.warning("Temp file missing (attempt %d): %s", attempt, src)
                    # Hedef dosya erişilebilir mi? (online-only Drive dosyaları dahil)
                    if _file_accessible(dst):
                        log.info("Destination accessible, treating as success: %s", dst)
                        continue
                    remaining.append((src_raw, dst_raw))
                    continue

                try:
                    os.replace(src, dst)
                    log.info("Rename succeeded (attempt %d): %s -> %s", attempt, src, dst)
                except OSError as e:
                    log.warning("Rename attempt %d failed: %s", attempt, e)
                    remaining.append((src_raw, dst_raw))

            self._pending_renames = remaining
            if not remaining:
                return True

        log.error("All rename attempts failed: %s", self._pending_renames)
        return False

    def _parse_line(self, line: str):
        # İlerleme
        m = _PROGRESS_RE.search(line)
        if m:
            try:
                pct = float(m.group(1))
                speed = m.group(3) or ""
                self.progress.emit(pct, speed)
            except ValueError:
                pass

        # WinError 32/183 yeniden adlandırma hatası
        m2 = _RENAME_ERR_RE.search(line)
        if m2:
            src_raw, dst_raw = m2.group(1), m2.group(2)
            log.warning("Rename error detected: %s -> %s", src_raw, dst_raw)
            self._pending_renames.append((src_raw, dst_raw))

        # İndirilen dosya yolu
        if line.startswith("[download] Destination:"):
            self._output_file = line[len("[download] Destination:"):].strip()
        elif "[Merger] Merging formats into" in line:
            mm = re.search(r'"(.+?)"', line)
            if mm:
                self._output_file = mm.group(1)
        elif line.startswith("[ffmpeg] Destination:"):
            self._output_file = line[len("[ffmpeg] Destination:"):].strip()

        # Video başlığı
        if line.startswith("[info]") and "title" in line.lower():
            self.title_found.emit(line)

    def cancel(self):
        if self._process and self._process.poll() is None:
            self._process.kill()
        self.quit()
