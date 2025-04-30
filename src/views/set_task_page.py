#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/24 16:47
# @Author   :luye
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QLabel
)

class SetTaskPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.input_field = QLineEdit(self)
        self.label = QLabel('页面 2 标签', self)
        layout = QVBoxLayout()
        layout.addWidget(self.input_field)
        layout.addWidget(self.label)
        self.setLayout(layout)