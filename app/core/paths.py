# -*- coding: utf-8 -*-
"""Tüm uygulama yolları tek yerden yönetilir."""

import os

# app/core/paths.py → app/core → app → proje kökü
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ARACLAR_DIR = os.path.join(BASE_DIR, "araçlar")
VIDEOLAR_DIR = os.path.join(BASE_DIR, "videolar")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
QUEUE_FILE  = os.path.join(BASE_DIR, "queue.json")
I18N_DIR = os.path.join(BASE_DIR, "app", "i18n")

YTDLP_EXE = os.path.join(ARACLAR_DIR, "yt-dlp.exe")
FFMPEG_DIR = ARACLAR_DIR


def ensure_dirs():
    """Gerekli dizinlerin var olduğunu garantiler."""
    os.makedirs(VIDEOLAR_DIR, exist_ok=True)
    os.makedirs(ARACLAR_DIR, exist_ok=True)
