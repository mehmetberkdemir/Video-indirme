# -*- coding: utf-8 -*-
"""
YouTube Clipboard İzleyici
Pano'daki YouTube linklerini otomatik olarak indirir.
"""

import sys
import os
import time
import re
import subprocess
import threading
import queue
import traceback

# Yollar
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
ARACLAR_DIR = os.path.join(BASE_DIR, "araçlar")
VIDEOLAR_DIR = os.path.join(BASE_DIR, "videolar")
YTDLP_EXE   = os.path.join(ARACLAR_DIR, "yt-dlp.exe")
FFMPEG_DIR  = ARACLAR_DIR

# deno ve ffmpeg'in bulunabilmesi için araçlar dizinini PATH'e ekle
os.environ["PATH"] = ARACLAR_DIR + os.pathsep + os.environ.get("PATH", "")

# YouTube link desenleri
YT_PATTERNS = [
    r"https?://(www\.)?youtube\.com/watch\?[^\s]*v=[^\s]+",
    r"https?://youtu\.be/[^\s]+",
    r"https?://(www\.)?youtube\.com/shorts/[^\s]+",
]
YT_REGEX = re.compile("|".join(YT_PATTERNS))

# İndirilen linkleri takip etmek için set
indirilen_linkler = set()
indirme_kuyrugu = queue.Queue()

# -------------------------------------------------------------------
# Bildirim fonksiyonu
# -------------------------------------------------------------------
def bildirim_gonder(baslik, mesaj, icon_type="info"):
    """Windows toast bildirimi gönderir. winotify veya win10toast kullanır."""
    try:
        from winotify import Notification, audio
        toast = Notification(
            app_id="YouTube İzleyici",
            title=baslik,
            msg=mesaj,
            duration="short"
        )
        if icon_type == "error":
            toast.set_audio(audio.Default, loop=False)
        toast.show()
    except Exception:
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(baslik, mesaj, duration=5, threaded=True)
        except Exception:
            # Bildirim paketi yoksa sessizce geç
            pass


# -------------------------------------------------------------------
# İndirme işlevi
# -------------------------------------------------------------------
def indir(url):
    """yt-dlp ile verilen URL'yi indirir."""
    bildirim_gonder("İndirme Başladı", f"İndiriliyor:\n{url[:80]}")

    komut = [
        YTDLP_EXE,
        "-f", "bv*[height<=1080]+ba/b",
        "--merge-output-format", "mp4",
        "--ffmpeg-location", FFMPEG_DIR,
        "-P", VIDEOLAR_DIR,
        "--no-playlist",
        "--output", "%(title)s.%(ext)s",
        url
    ]

    try:
        sonuc = subprocess.run(
            komut,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600
        )

        if sonuc.returncode == 0:
            bildirim_gonder("İndirme Tamamlandı", f"Başarıyla indirildi:\n{url[:80]}")
        else:
            hata = sonuc.stderr[-300:] if sonuc.stderr else "Bilinmeyen hata"
            bildirim_gonder("İndirme Hatası", f"Hata oluştu:\n{hata[:200]}", icon_type="error")

    except subprocess.TimeoutExpired:
        bildirim_gonder("İndirme Zaman Aşımı", f"İndirme 10 dakikada tamamlanamadı:\n{url[:60]}", icon_type="error")
    except Exception as e:
        bildirim_gonder("İndirme Hatası", f"Beklenmeyen hata:\n{str(e)[:200]}", icon_type="error")


# -------------------------------------------------------------------
# İndirme worker thread
# -------------------------------------------------------------------
def indirme_worker():
    """Kuyruktaki linkleri sırayla indirir."""
    while True:
        url = indirme_kuyrugu.get()
        if url is None:
            break
        try:
            indir(url)
        except Exception:
            pass
        finally:
            indirme_kuyrugu.task_done()


# -------------------------------------------------------------------
# Clipboard izleme döngüsü
# -------------------------------------------------------------------
def clipboard_izle(durum_callback):
    """Pano'yu izler ve YouTube linkleri bulunca kuyruğa ekler."""
    import pyperclip

    onceki_metin = ""
    while True:
        try:
            metin = pyperclip.paste()
            if metin and metin != onceki_metin:
                onceki_metin = metin
                eslesme = YT_REGEX.search(metin.strip())
                if eslesme:
                    url = eslesme.group(0).strip()
                    # URL'yi temizle (ekstra parametreleri koru ama boşluk vs. kes)
                    url = url.split()[0]
                    if url not in indirilen_linkler:
                        indirilen_linkler.add(url)
                        durum_callback(f"İndiriliyor: {url[:50]}...")
                        indirme_kuyrugu.put(url)
        except Exception:
            pass
        time.sleep(1.5)


# -------------------------------------------------------------------
# System Tray
# -------------------------------------------------------------------
def tray_baslat():
    """System tray ikonunu oluşturur ve başlatır."""
    try:
        from PIL import Image, ImageDraw
        import pystray

        # Basit bir ikon oluştur (kırmızı daire - YouTube rengi)
        def ikon_olustur(renk=(200, 0, 0)):
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            ciz = ImageDraw.Draw(img)
            ciz.ellipse([4, 4, 60, 60], fill=renk)
            # Play üçgeni
            ciz.polygon([(22, 18), (22, 46), (48, 32)], fill=(255, 255, 255))
            return img

        durum_metni = ["Hazır - YouTube linkleri izleniyor"]

        def durum_guncelle(yeni_durum):
            durum_metni[0] = yeni_durum

        def klasoru_ac(icon, item):
            subprocess.Popen(["explorer", VIDEOLAR_DIR])

        def cikis(icon, item):
            indirme_kuyrugu.put(None)  # Worker'ı durdur
            icon.stop()

        def durum_goster(icon, item):
            bildirim_gonder("Durum", durum_metni[0])

        menu = pystray.Menu(
            pystray.MenuItem(lambda text: durum_metni[0], durum_goster, default=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Klasörü Aç", klasoru_ac),
            pystray.MenuItem("Çıkış", cikis),
        )

        ikon = pystray.Icon(
            "yt-izleyici",
            ikon_olustur(),
            "YouTube İzleyici",
            menu
        )

        # Clipboard izlemeyi ayrı thread'de başlat
        izleme_thread = threading.Thread(
            target=clipboard_izle,
            args=(durum_guncelle,),
            daemon=True
        )
        izleme_thread.start()

        # İndirme worker'ını başlat
        worker_thread = threading.Thread(
            target=indirme_worker,
            daemon=True
        )
        worker_thread.start()

        bildirim_gonder("YouTube İzleyici", "Başlatıldı! Pano izleniyor...")

        # Tray ikonunu çalıştır (bu bloklar)
        ikon.run()

    except ImportError as e:
        # pystray veya pillow yoksa basit mod
        eksik_paket = str(e)
        hata_msg = (
            f"Gerekli paket bulunamadı: {eksik_paket}\n"
            "Lütfen şu komutu çalıştırın:\n"
            "pip install pyperclip pystray pillow winotify"
        )
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Eksik Paket", hata_msg)
        sys.exit(1)


# -------------------------------------------------------------------
# Ana giriş noktası
# -------------------------------------------------------------------
if __name__ == "__main__":
    # Videolar dizinini oluştur (yoksa)
    os.makedirs(VIDEOLAR_DIR, exist_ok=True)
    os.makedirs(ARACLAR_DIR, exist_ok=True)

    # yt-dlp varlığını kontrol et
    if not os.path.isfile(YTDLP_EXE):
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "yt-dlp Bulunamadı",
                f"yt-dlp.exe bulunamadı:\n{YTDLP_EXE}\n\n"
                "Lütfen yt-dlp.exe'yi araçlar klasörüne kopyalayın."
            )
        except Exception:
            pass
        sys.exit(1)

    tray_baslat()
