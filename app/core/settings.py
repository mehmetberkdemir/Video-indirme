# -*- coding: utf-8 -*-
"""config.json okuma/yazma işlemleri."""

import json
import os
from app.core.paths import CONFIG_FILE, VIDEOLAR_DIR

DEFAULTS = {
    "language": "tr",
    "output_dir": VIDEOLAR_DIR,
    "format": "bv[vcodec^=avc1][height<=1080]+ba[acodec^=mp4a]/bv[height<=1080]+ba/b",
    "merge_format": "mp4",
    "max_concurrent": 2,
    "clipboard_monitor": True,
    "notifications": True,
    "start_minimized": False,
}


class Settings:
    def __init__(self):
        self._data: dict = {}
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._data = {**DEFAULTS, **loaded}
            except Exception:
                self._data = dict(DEFAULTS)
        else:
            self._data = dict(DEFAULTS)

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Settings save error: {e}")

    def get(self, key: str, fallback=None):
        return self._data.get(key, fallback)

    def set(self, key: str, value):
        self._data[key] = value
        self.save()

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self.set(key, value)
