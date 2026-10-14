# -*- coding: utf-8 -*-
"""Manuel URL ekleme diyalogu."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from app.i18n import t

if TYPE_CHECKING:
    from app.platforms import PlatformRegistry


class AddUrlDialog(QDialog):
    def __init__(self, platform_registry: "PlatformRegistry", parent=None):
        super().__init__(parent)
        self._registry = platform_registry
        self._url: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(t("dialog.add_url.title"))
        self.setMinimumWidth(520)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        lbl = QLabel(t("dialog.add_url.label"))
        layout.addWidget(lbl)

        self._url_edit = QLineEdit()
        self._url_edit.setPlaceholderText(t("dialog.add_url.placeholder"))
        self._url_edit.setMinimumHeight(36)
        layout.addWidget(self._url_edit)

        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color: #f38ba8;")
        self._error_label.hide()
        layout.addWidget(self._error_label)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._url_edit.returnPressed.connect(self._on_accept)
        self._url_edit.setFocus()

    def _on_accept(self):
        url = self._url_edit.text().strip()
        if not url:
            return
        url = url.split()[0]  # ilk token al

        platform = self._registry.match(url)
        if not platform:
            self._error_label.setText(t("dialog.add_url.unsupported"))
            self._error_label.show()
            return

        self._url = url
        self.accept()

    @property
    def url(self) -> Optional[str]:
        return self._url

    def set_url(self, url: str):
        """Diyalogu önceden dolu URL ile aç (clipboard'dan)."""
        self._url_edit.setText(url)
        self._url_edit.selectAll()
