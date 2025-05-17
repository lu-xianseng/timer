#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/24 16:47
# @Author   :luye
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


def set_label_styles(label, font_size=12, color='#333', bold=False, location='center'):
    font = QFont("Arial", font_size)
    if bold:
        font.setBold(True)
    label.setFont(font)
    label.setStyleSheet(f"QLabel {{ color: {color}; }}")
    if location == 'left':
        label.setAlignment(Qt.AlignLeft)
    if location == 'center':
        label.setAlignment(Qt.AlignCenter)


def set_checkbox_styles(label, font_size=12, color='#333', bold=False):
    font = label.setFont(QFont("Arial", font_size))
    if bold:
        font.setBold(True)
    label.setStyleSheet(f"QCheckBox {{ color: {color}; }}")


def set_button_styles(button, background_color, hover_color, color='white', padding='8px 20px'):
    button.setStyleSheet(f"QPushButton {{ background-color: {background_color}; color: {color}; padding: {padding}; "
                         f"margin: 2px;border: none; border-radius: 5px; }}"
                         f"QPushButton:hover {{ background-color: {hover_color}; }}")


def set_table_styles(table):
    table.setStyleSheet("QHeaderView::section {border: 1px solid #ccc;}")
