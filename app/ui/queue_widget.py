# -*- coding: utf-8 -*-
"""İndirme kuyruğu widget'ı."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from app.core.queue_manager import DownloadItem, DownloadStatus
from app.i18n import t

if TYPE_CHECKING:
    from app.core.queue_manager import QueueManager

COL_TITLE    = 0
COL_STATUS   = 1
COL_PROGRESS = 2
COL_SPEED    = 3
COL_ACTIONS  = 4

# progress bar renkleri
_COLOR_DEFAULT  = ""   # QSS'den
_COLOR_DONE     = "QProgressBar::chunk { background-color: #a6e3a1; }"
_COLOR_ERROR    = "QProgressBar::chunk { background-color: #f38ba8; }"
_COLOR_PAUSED   = "QProgressBar::chunk { background-color: #f9e2af; }"


class ActionWidget(QWidget):
    start_clicked       = Signal()
    pause_clicked       = Signal()
    resume_clicked      = Signal()
    retry_clicked       = Signal()
    cancel_clicked      = Signal()
    remove_clicked      = Signal()
    delete_file_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(3)

        def _btn(text, name="", width=76):
            b = QPushButton(text)
            if name:
                b.setObjectName(name)
            b.setMaximumWidth(width)
            return b

        self.btn_start       = _btn(t("btn.start"))
        self.btn_pause       = _btn(t("btn.pause"))
        self.btn_resume      = _btn(t("btn.resume"))
        self.btn_retry       = _btn(t("btn.retry"))
        self.btn_cancel      = _btn(t("btn.cancel"), "dangerButton")
        self.btn_remove      = _btn(t("btn.remove"))
        self.btn_delete_file = _btn(t("btn.delete_file"), "dangerButton", width=90)

        self.btn_start.clicked.connect(self.start_clicked)
        self.btn_pause.clicked.connect(self.pause_clicked)
        self.btn_resume.clicked.connect(self.resume_clicked)
        self.btn_retry.clicked.connect(self.retry_clicked)
        self.btn_cancel.clicked.connect(self.cancel_clicked)
        self.btn_remove.clicked.connect(self.remove_clicked)
        self.btn_delete_file.clicked.connect(self.delete_file_clicked)

        for b in (self.btn_start, self.btn_pause, self.btn_resume, self.btn_retry,
                  self.btn_cancel, self.btn_remove, self.btn_delete_file):
            layout.addWidget(b)
        layout.addStretch()

        self.set_state(DownloadStatus.PAUSED)

    def set_state(self, status: DownloadStatus):
        s = status
        self.btn_start.setVisible(s == DownloadStatus.PAUSED)
        self.btn_pause.setVisible(s == DownloadStatus.DOWNLOADING)
        self.btn_resume.setVisible(False)           # artık btn_start kullanılıyor
        self.btn_retry.setVisible(s == DownloadStatus.ERROR)
        self.btn_cancel.setVisible(s in (DownloadStatus.DOWNLOADING, DownloadStatus.PENDING))
        self.btn_remove.setVisible(s in (DownloadStatus.DONE, DownloadStatus.ERROR,
                                         DownloadStatus.CANCELLED))
        self.btn_delete_file.setVisible(s == DownloadStatus.DONE)

    def retranslate(self):
        self.btn_start.setText(t("btn.start"))
        self.btn_pause.setText(t("btn.pause"))
        self.btn_resume.setText(t("btn.resume"))
        self.btn_retry.setText(t("btn.retry"))
        self.btn_cancel.setText(t("btn.cancel"))
        self.btn_remove.setText(t("btn.remove"))
        self.btn_delete_file.setText(t("btn.delete_file"))


class QueueWidget(QTreeWidget):
    def __init__(self, queue_manager: "QueueManager", parent=None):
        super().__init__(parent)
        self._manager = queue_manager
        self._items: dict[str, QTreeWidgetItem] = {}

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.setColumnCount(5)
        self.setHeaderLabels([
            t("queue.columns.title"),
            t("queue.columns.status"),
            t("queue.columns.progress"),
            t("queue.columns.speed"),
            t("queue.columns.actions"),
        ])
        self.setRootIsDecorated(False)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)

        header = self.header()
        header.setStretchLastSection(False)
        self.setColumnWidth(COL_TITLE, 320)
        self.setColumnWidth(COL_STATUS, 100)
        self.setColumnWidth(COL_PROGRESS, 130)
        self.setColumnWidth(COL_SPEED, 90)
        self.setColumnWidth(COL_ACTIONS, 260)

    def _connect_signals(self):
        self._manager.item_added.connect(self._on_item_added)
        self._manager.item_updated.connect(self._on_item_updated)
        self._manager.item_removed.connect(self._on_item_removed)

    # ------------------------------------------------------------------

    def _on_item_added(self, item: DownloadItem):
        row = QTreeWidgetItem()
        row.setText(COL_TITLE, item.title or item.url)
        row.setText(COL_STATUS, t(f"status.{item.status.name.lower()}"))
        row.setToolTip(COL_TITLE, item.url)
        self.addTopLevelItem(row)
        self._items[item.id] = row

        pb = QProgressBar()
        pb.setRange(0, 100)
        pb.setValue(int(item.progress))
        pb.setFormat("%p%")
        self.setItemWidget(row, COL_PROGRESS, pb)

        aw = ActionWidget()
        aw.set_state(item.status)
        aw.start_clicked.connect(lambda i=item: self._manager.resume(i.id))
        aw.pause_clicked.connect(lambda i=item: self._manager.pause(i.id))
        aw.resume_clicked.connect(lambda i=item: self._manager.resume(i.id))
        aw.retry_clicked.connect(lambda i=item: self._manager.retry(i.id))
        aw.cancel_clicked.connect(lambda i=item: self._manager.cancel(i.id))
        aw.remove_clicked.connect(lambda i=item: self._manager.remove(i.id))
        aw.delete_file_clicked.connect(lambda i=item: self._manager.delete_file(i.id))
        self.setItemWidget(row, COL_ACTIONS, aw)

    def _on_item_updated(self, item: DownloadItem):
        row = self._items.get(item.id)
        if not row:
            return

        display = item.title if item.title and item.title != item.url else item.url
        row.setText(COL_TITLE, display)
        row.setText(COL_STATUS, t(f"status.{item.status.name.lower()}"))
        row.setText(COL_SPEED, item.speed if item.status == DownloadStatus.DOWNLOADING else "")

        pb = self.itemWidget(row, COL_PROGRESS)
        if isinstance(pb, QProgressBar):
            pb.setValue(int(item.progress))
            if item.status == DownloadStatus.ERROR:
                pb.setFormat(t("status.error"))
                pb.setStyleSheet(_COLOR_ERROR)
            elif item.status == DownloadStatus.DONE:
                pb.setFormat("100%")
                pb.setStyleSheet(_COLOR_DONE)
            elif item.status == DownloadStatus.PAUSED:
                pb.setStyleSheet(_COLOR_PAUSED)
            else:
                pb.setFormat("%p%")
                pb.setStyleSheet(_COLOR_DEFAULT)

        aw = self.itemWidget(row, COL_ACTIONS)
        if isinstance(aw, ActionWidget):
            aw.set_state(item.status)

    def _on_item_removed(self, item_id: str):
        row = self._items.pop(item_id, None)
        if row:
            index = self.indexOfTopLevelItem(row)
            if index >= 0:
                self.takeTopLevelItem(index)

    def retranslate(self):
        self.setHeaderLabels([
            t("queue.columns.title"),
            t("queue.columns.status"),
            t("queue.columns.progress"),
            t("queue.columns.speed"),
            t("queue.columns.actions"),
        ])
        for item_id, row in self._items.items():
            for item in self._manager.items:
                if item.id == item_id:
                    row.setText(COL_STATUS, t(f"status.{item.status.name.lower()}"))
                    break
            aw = self.itemWidget(row, COL_ACTIONS)
            if isinstance(aw, ActionWidget):
                aw.retranslate()
