#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/24 16:47
# @Author   :luye
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


def set_label_styles(label, font_size=12, color='#333', bold=False):
    font = QFont("Arial", font_size)
    if bold:
        font.setBold(True)
    label.setFont(font)
    label.setStyleSheet(f"QLabel {{ color: {color}; }}")
    label.setAlignment(Qt.AlignLeft)


def set_checkbox_styles(label, font_size=12, color='#333', bold=False):
    font = label.setFont(QFont("Arial", font_size))
    if bold:
        font.setBold(True)
    label.setStyleSheet(f"QCheckBox {{ color: {color}; }}")


def set_radio_styles(label, font_size=12, color='#333', bold=False):
    font = label.setFont(QFont("Arial", font_size))
    if bold:
        font.setBold(True)
    label.setStyleSheet(f"QCheckBox {{ color: {color}; }}")


def set_line_edit_styles(line_edit, font_size=12):
    font = QFont("Arial", font_size)
    line_edit.setFont(font)
    line_edit.setStyleSheet("QLineEdit { padding: 5px; border: 1px solid #ccc; border-radius: 3px; }")


def set_button_styles(button, background_color, hover_color, color='white', padding='8px 20px'):
    button.setStyleSheet(f"QPushButton {{ background-color: {background_color}; color: {color}; padding: {padding}; "
                         f"margin: 2px;border: none; border-radius: 5px; }}"
                         f"QPushButton:hover {{ background-color: {hover_color}; }}")


def set_table_styles(table):
    table.setStyleSheet("QHeaderView::section {border: 1px solid #ccc;}")
