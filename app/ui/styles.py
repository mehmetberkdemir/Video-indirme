# -*- coding: utf-8 -*-
"""QSS stilleri."""

DARK_STYLE = """
QMainWindow, QDialog {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
}

QMenuBar {
    background-color: #181825;
    color: #cdd6f4;
    border-bottom: 1px solid #313244;
}

QMenuBar::item:selected {
    background-color: #313244;
}

QMenu {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
}

QMenu::item:selected {
    background-color: #45475a;
}

QToolBar {
    background-color: #181825;
    border-bottom: 1px solid #313244;
    spacing: 4px;
    padding: 4px;
}

QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 14px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #45475a;
}

QPushButton:pressed {
    background-color: #585b70;
}

QPushButton#primaryButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    font-weight: bold;
}

QPushButton#primaryButton:hover {
    background-color: #b4d0fb;
}

QPushButton#dangerButton {
    background-color: #f38ba8;
    color: #1e1e2e;
    border: none;
}

QPushButton#dangerButton:hover {
    background-color: #f5a9bc;
}

QTreeWidget {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    alternate-background-color: #1e1e2e;
    gridline-color: #313244;
}

QTreeWidget::item {
    padding: 4px 2px;
    border-bottom: 1px solid #313244;
}

QTreeWidget::item:selected {
    background-color: #313244;
    color: #89b4fa;
}

QTreeWidget::item:hover {
    background-color: #2a2a3d;
}

QHeaderView::section {
    background-color: #181825;
    color: #a6adc8;
    border: none;
    border-right: 1px solid #313244;
    border-bottom: 1px solid #313244;
    padding: 6px 8px;
    font-weight: bold;
}

QProgressBar {
    background-color: #313244;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: #cdd6f4;
    font-size: 11px;
    max-height: 16px;
}

QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 4px;
}

QLineEdit, QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
}

QLineEdit:focus, QComboBox:focus {
    border-color: #89b4fa;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #181825;
    color: #cdd6f4;
    selection-background-color: #313244;
    border: 1px solid #45475a;
}

QLabel {
    color: #cdd6f4;
    background: transparent;
}

QLabel#statusLabel {
    color: #a6adc8;
    font-size: 12px;
    padding: 2px 8px;
}

QCheckBox {
    color: #cdd6f4;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 1px solid #45475a;
    background-color: #313244;
}

QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

QSpinBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 4px 8px;
}

QStatusBar {
    background-color: #181825;
    color: #a6adc8;
    border-top: 1px solid #313244;
}

QScrollBar:vertical {
    background-color: #181825;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QGroupBox {
    color: #a6adc8;
    border: 1px solid #313244;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 8px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    left: 10px;
}
"""
