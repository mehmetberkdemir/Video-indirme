# -*- coding: utf-8 -*-
"""Ana uygulama penceresi."""

from __future__ import annotations

import os
import subprocess
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QSizePolicy,
    QStatusBar,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.i18n import t
from app.core.paths import QUEUE_FILE
from app.ui.queue_widget import QueueWidget
from app.ui.add_url_dialog import AddUrlDialog
from app.ui.settings_dialog import SettingsDialog
from app.ui.tray_icon import TrayIcon

if TYPE_CHECKING:
    from app.main import AppContext


class MainWindow(QMainWindow):
    def __init__(self, ctx: "AppContext"):
        super().__init__()
        self._ctx = ctx
        self._paused_all = False
        self._setup_ui()
        self._setup_tray()
        self._connect_signals()

        if ctx.settings.get("start_minimized", False):
            self.hide()
        else:
            self.show()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setup_ui(self):
        self.setWindowTitle(t("app.title"))
        self.setMinimumSize(860, 500)
        self.resize(1060, 620)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self._queue_widget = QueueWidget(self._ctx.queue_manager, self)
        layout.addWidget(self._queue_widget)

        self._build_menubar()
        self._build_toolbar()

        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_label = QLabel(t("app.tray_tooltip"))
        self._status_label.setObjectName("statusLabel")
        self._status_bar.addWidget(self._status_label)

    def _build_menubar(self):
        mb = self.menuBar()

        self._menu_file = mb.addMenu(t("menu.file"))

        self._act_add_url = QAction(t("menu.add_url"), self)
        self._act_add_url.setShortcut(QKeySequence("Ctrl+N"))
        self._act_add_url.triggered.connect(self._open_add_url)
        self._menu_file.addAction(self._act_add_url)

        self._act_open_folder = QAction(t("menu.open_folder"), self)
        self._act_open_folder.triggered.connect(self._open_folder)
        self._menu_file.addAction(self._act_open_folder)

        self._menu_file.addSeparator()

        self._act_settings = QAction(t("menu.settings"), self)
        self._act_settings.setShortcut(QKeySequence("Ctrl+,"))
        self._act_settings.triggered.connect(self._open_settings)
        self._menu_file.addAction(self._act_settings)

        self._menu_file.addSeparator()

        self._act_exit = QAction(t("menu.exit"), self)
        self._act_exit.setShortcut(QKeySequence("Ctrl+Q"))
        self._act_exit.triggered.connect(self._exit_app)
        self._menu_file.addAction(self._act_exit)

        self._menu_view = mb.addMenu(t("menu.view"))

        self._act_clear_done = QAction(t("menu.clear_done"), self)
        self._act_clear_done.triggered.connect(self._ctx.queue_manager.clear_done)
        self._menu_view.addAction(self._act_clear_done)

    def _build_toolbar(self):
        tb = QToolBar()
        tb.setMovable(False)
        self.addToolBar(tb)
        self._toolbar = tb

        # URL Ekle
        self._tb_add_url = tb.addAction(t("btn.add_url"))
        self._tb_add_url.triggered.connect(self._open_add_url)

        tb.addSeparator()

        # Tümünü Duraklat / Başlat toggle
        self._tb_pause_all = QToolButton()
        self._tb_pause_all.setText("⏸  " + t("btn.pause_all"))
        self._tb_pause_all.setCheckable(True)
        self._tb_pause_all.setToolTip(t("btn.pause_all"))
        self._tb_pause_all.toggled.connect(self._on_pause_all_toggled)
        tb.addWidget(self._tb_pause_all)

        # Spacer — klasörü sağa it
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(spacer)

        # İndirme klasörü label
        self._folder_label = QLabel()
        self._folder_label.setToolTip(t("btn.change_folder"))
        self._folder_label.setStyleSheet("color: #a6adc8; padding: 0 6px;")
        tb.addWidget(self._folder_label)
        self._update_folder_label()

        # Klasörü Değiştir butonu
        self._folder_btn = QToolButton()
        self._folder_btn.setText("📁")
        self._folder_btn.setToolTip(t("btn.change_folder"))
        self._folder_btn.clicked.connect(self._change_output_dir)
        tb.addWidget(self._folder_btn)

        # Klasörü Aç butonu
        self._open_folder_btn = QToolButton()
        self._open_folder_btn.setText("↗")
        self._open_folder_btn.setToolTip(t("btn.open_folder"))
        self._open_folder_btn.clicked.connect(self._open_folder)
        tb.addWidget(self._open_folder_btn)

    def _setup_tray(self):
        self._tray = TrayIcon(self)
        self._tray.show_window.connect(self._show_window)
        self._tray.add_url_requested.connect(self._open_add_url)
        self._tray.open_folder_requested.connect(self._open_folder)
        self._tray.exit_requested.connect(self._exit_app)
        self._tray.show()

    def _connect_signals(self):
        self._ctx.clipboard_monitor.url_detected.connect(self._on_clipboard_url)
        self._ctx.queue_manager.item_updated.connect(self._update_status)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _open_add_url(self, url: str = ""):
        dlg = AddUrlDialog(self._ctx.platform_registry, self)
        if url:
            dlg.set_url(url)
        if dlg.exec():
            final_url = dlg.url
            if final_url:
                self._add_url(final_url)

    def _add_url(self, url: str):
        args = self._ctx.platform_registry.get_ytdlp_args(url, self._ctx.settings)
        self._ctx.queue_manager.add(url, args, title=url)
        if self._ctx.settings.get("notifications", True):
            self._ctx.notifier.notify(t("notify.url_detected"), t("notify.url_added"))

    def _on_clipboard_url(self, url: str):
        if not self._ctx.settings.get("clipboard_monitor", True):
            return
        self._add_url(url)
        self._tray.showMessage(t("notify.url_detected"), url[:80], QIcon(), 3000)

    def _on_pause_all_toggled(self, checked: bool):
        if checked:
            self._tb_pause_all.setText("▶  " + t("btn.resume_all"))
            self._ctx.queue_manager.pause_all()
        else:
            self._tb_pause_all.setText("⏸  " + t("btn.pause_all"))
            self._ctx.queue_manager.resume_all()

    def _change_output_dir(self):
        current = self._ctx.settings.get("output_dir", os.path.expanduser("~"))
        path = QFileDialog.getExistingDirectory(self, t("btn.change_folder"), current)
        if path:
            self._ctx.settings.set("output_dir", path)
            self._update_folder_label()

    def _update_folder_label(self):
        path = self._ctx.settings.get("output_dir", "")
        short = path if len(path) <= 40 else "..." + path[-37:]
        self._folder_label.setText(short)
        self._folder_label.setToolTip(path)

    def _open_folder(self):
        path = self._ctx.settings.get("output_dir", ".")
        subprocess.Popen(["explorer", path], creationflags=subprocess.CREATE_NO_WINDOW)

    def _open_settings(self):
        dlg = SettingsDialog(self._ctx.settings, self)
        dlg.language_changed.connect(self._retranslate)
        dlg.exec()
        self._update_folder_label()

        enabled = self._ctx.settings.get("clipboard_monitor", True)
        if enabled and not self._ctx.clipboard_monitor.isRunning():
            self._ctx.clipboard_monitor.start()
        elif not enabled and self._ctx.clipboard_monitor.isRunning():
            self._ctx.clipboard_monitor.stop()

    def _show_window(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _update_status(self, item):
        active = sum(1 for i in self._ctx.queue_manager.items
                     if i.status.name == "DOWNLOADING")
        paused = sum(1 for i in self._ctx.queue_manager.items
                     if i.status.name == "PAUSED")
        if active:
            self._status_label.setText(f"{active} indirme aktif" +
                                       (f", {paused} duraklatılmış" if paused else ""))
        elif paused:
            self._status_label.setText(f"{paused} indirme duraklatılmış")
        else:
            self._status_label.setText(t("app.tray_tooltip"))

    def _save_queue(self):
        self._ctx.queue_manager.save_queue(QUEUE_FILE)

    def _exit_app(self):
        self._save_queue()
        self._ctx.clipboard_monitor.stop()
        self._tray.hide()
        from PySide6.QtWidgets import QApplication
        QApplication.quit()

    def _retranslate(self, lang: str):
        self.setWindowTitle(t("app.title"))
        self._menu_file.setTitle(t("menu.file"))
        self._menu_view.setTitle(t("menu.view"))
        self._act_add_url.setText(t("menu.add_url"))
        self._act_open_folder.setText(t("menu.open_folder"))
        self._act_settings.setText(t("menu.settings"))
        self._act_exit.setText(t("menu.exit"))
        self._act_clear_done.setText(t("menu.clear_done"))
        self._tb_add_url.setText(t("btn.add_url"))
        if self._tb_pause_all.isChecked():
            self._tb_pause_all.setText("▶  " + t("btn.resume_all"))
        else:
            self._tb_pause_all.setText("⏸  " + t("btn.pause_all"))
        self._folder_btn.setToolTip(t("btn.change_folder"))
        self._status_label.setText(t("app.tray_tooltip"))
        self._queue_widget.retranslate()
        self._tray.retranslate()

    # ------------------------------------------------------------------
    # Close event — sistray'e küçült, kuyruğu kaydet
    # ------------------------------------------------------------------

    def closeEvent(self, event):
        self._save_queue()
        event.ignore()
        self.hide()
        self._tray.showMessage(t("app.title"), t("app.tray_tooltip"), QIcon(), 2000)
