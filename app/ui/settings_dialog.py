# -*- coding: utf-8 -*-
"""Ayarlar diyalogu."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from app.i18n import t, set_language

if TYPE_CHECKING:
    from app.core.settings import Settings

LANGUAGES = [("tr", "Türkçe"), ("en", "English")]

FORMATS = [
    ("bv[vcodec^=avc1][height<=1080]+ba[acodec^=mp4a]/bv[height<=1080]+ba/b", t("format.1080p")),
    ("bv[vcodec^=avc1][height<=720]+ba[acodec^=mp4a]/bv[height<=720]+ba/b",  t("format.720p")),
    ("bv[vcodec^=avc1][height<=480]+ba[acodec^=mp4a]/bv[height<=480]+ba/b",  t("format.480p")),
    ("bestvideo+bestaudio/best", t("format.best")),
    ("audio_only", t("format.audio_only")),
]


class SettingsDialog(QDialog):
    language_changed = Signal(str)

    def __init__(self, settings: "Settings", parent=None):
        super().__init__(parent)
        self._settings = settings
        self._setup_ui()
        self._load()

    def _setup_ui(self):
        self.setWindowTitle(t("dialog.settings.title"))
        self.setMinimumWidth(480)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # --- Genel Grup ---
        general_group = QGroupBox(t("dialog.settings.title"))
        form = QFormLayout(general_group)
        form.setSpacing(10)

        # Dil
        self._lang_combo = QComboBox()
        for code, name in LANGUAGES:
            self._lang_combo.addItem(name, code)
        form.addRow(t("dialog.settings.language") + ":", self._lang_combo)

        # İndirme klasörü
        dir_row = QHBoxLayout()
        self._dir_edit = QLineEdit()
        self._dir_btn = QPushButton(t("dialog.settings.browse"))
        self._dir_btn.setMaximumWidth(90)
        self._dir_btn.clicked.connect(self._browse_dir)
        dir_row.addWidget(self._dir_edit)
        dir_row.addWidget(self._dir_btn)
        form.addRow(t("dialog.settings.output_dir") + ":", dir_row)

        # Video kalitesi
        self._format_combo = QComboBox()
        for key, label in FORMATS:
            self._format_combo.addItem(label, key)
        form.addRow(t("dialog.settings.format") + ":", self._format_combo)

        # Eş zamanlı indirme
        self._concurrent_spin = QSpinBox()
        self._concurrent_spin.setRange(1, 5)
        form.addRow(t("dialog.settings.max_concurrent") + ":", self._concurrent_spin)

        main_layout.addWidget(general_group)

        # --- Seçenekler Grup ---
        options_group = QGroupBox("")
        options_layout = QVBoxLayout(options_group)
        self._cb_clipboard = QCheckBox(t("dialog.settings.clipboard"))
        self._cb_notifications = QCheckBox(t("dialog.settings.notifications"))
        self._cb_minimized = QCheckBox(t("dialog.settings.start_minimized"))
        options_layout.addWidget(self._cb_clipboard)
        options_layout.addWidget(self._cb_notifications)
        options_layout.addWidget(self._cb_minimized)
        main_layout.addWidget(options_group)

        # Butonlar
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

    def _load(self):
        # Dil
        lang = self._settings.get("language", "tr")
        for i, (code, _) in enumerate(LANGUAGES):
            if code == lang:
                self._lang_combo.setCurrentIndex(i)
                break

        self._dir_edit.setText(self._settings.get("output_dir", ""))

        # Format
        fmt = self._settings.get("format", "bv*[height<=1080]+ba/b")
        for i, (key, _) in enumerate(FORMATS):
            if key == fmt:
                self._format_combo.setCurrentIndex(i)
                break

        self._concurrent_spin.setValue(self._settings.get("max_concurrent", 2))
        self._cb_clipboard.setChecked(self._settings.get("clipboard_monitor", True))
        self._cb_notifications.setChecked(self._settings.get("notifications", True))
        self._cb_minimized.setChecked(self._settings.get("start_minimized", False))

    def _on_save(self):
        old_lang = self._settings.get("language", "tr")
        new_lang = self._lang_combo.currentData()

        self._settings.set("language", new_lang)
        self._settings.set("output_dir", self._dir_edit.text().strip())
        self._settings.set("format", self._format_combo.currentData())
        self._settings.set("max_concurrent", self._concurrent_spin.value())
        self._settings.set("clipboard_monitor", self._cb_clipboard.isChecked())
        self._settings.set("notifications", self._cb_notifications.isChecked())
        self._settings.set("start_minimized", self._cb_minimized.isChecked())

        if new_lang != old_lang:
            set_language(new_lang)
            self.language_changed.emit(new_lang)

        self.accept()

    def _browse_dir(self):
        current = self._dir_edit.text() or os.path.expanduser("~")
        path = QFileDialog.getExistingDirectory(self, t("dialog.settings.output_dir"), current)
        if path:
            self._dir_edit.setText(path)
