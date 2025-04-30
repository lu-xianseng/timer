#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/24 16:47
# @Author   :luye
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QLabel
)

class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("关于页面", self)
        layout.addWidget(label)
        self.setLayout(layout)