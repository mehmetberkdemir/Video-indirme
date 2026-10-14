# -*- coding: utf-8 -*-
"""System tray ikonunu yönetir."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from app.i18n import t

if TYPE_CHECKING:
    pass


def _make_icon() -> QIcon:
    """Basit bir tray ikonu oluşturur (kırmızı daire + beyaz üçgen)."""
    px = QPixmap(64, 64)
    px.fill(QColor(0, 0, 0, 0))
    painter = QPainter(px)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Kırmızı daire
    painter.setBrush(QBrush(QColor(200, 0, 0)))
    painter.setPen(QPen(QColor(0, 0, 0, 0)))
    painter.drawEllipse(2, 2, 60, 60)

    # Beyaz play üçgeni
    painter.setBrush(QBrush(QColor(255, 255, 255)))
    from PySide6.QtGui import QPolygon
    from PySide6.QtCore import QPoint
    triangle = QPolygon([QPoint(22, 18), QPoint(22, 46), QPoint(48, 32)])
    painter.drawPolygon(triangle)
    painter.end()
    return QIcon(px)


class TrayIcon(QSystemTrayIcon):
    show_window = Signal()
    add_url_requested = Signal()
    open_folder_requested = Signal()
    exit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(_make_icon(), parent)
        self.setToolTip(t("app.tray_tooltip"))
        self._build_menu()
        self.activated.connect(self._on_activated)

    def _build_menu(self):
        menu = QMenu()

        self._act_show = menu.addAction(t("tray.show"))
        self._act_show.triggered.connect(self.show_window)

        menu.addSeparator()

        self._act_add = menu.addAction(t("tray.add_url"))
        self._act_add.triggered.connect(self.add_url_requested)

        self._act_folder = menu.addAction(t("tray.open_folder"))
        self._act_folder.triggered.connect(self.open_folder_requested)

        menu.addSeparator()

        self._act_exit = menu.addAction(t("tray.exit"))
        self._act_exit.triggered.connect(self.exit_requested)

        self.setContextMenu(menu)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window.emit()

    def retranslate(self):
        self.setToolTip(t("app.tray_tooltip"))
        self._act_show.setText(t("tray.show"))
        self._act_add.setText(t("tray.add_url"))
        self._act_folder.setText(t("tray.open_folder"))
        self._act_exit.setText(t("tray.exit"))
