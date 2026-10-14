# -*- coding: utf-8 -*-
"""Basit JSON tabanlı i18n sistemi."""

import json
import os
from typing import Optional

from app.core.paths import I18N_DIR

_current_lang = "tr"
_strings: dict[str, str] = {}


def _load(lang: str):
    global _strings
    path = os.path.join(I18N_DIR, f"{lang}.json")
    if not os.path.exists(path):
        # Fallback to Turkish
        path = os.path.join(I18N_DIR, "tr.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            _strings = json.load(f)
    except Exception:
        _strings = {}


def set_language(lang: str):
    global _current_lang
    _current_lang = lang
    _load(lang)


def t(key: str, **kwargs) -> str:
    """Çeviri anahtarını çevirir. Bilinmeyen anahtar → anahtar kendisi döner."""
    text = _strings.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text


def current_language() -> str:
    return _current_lang


# İlk yükle
_load(_current_lang)
