#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/24 16:47
# @Author   :luye
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout,
    QCheckBox, QRadioButton, QPushButton
)
from PyQt5.QtCore import Qt
from src.views.styles import (
    set_radio_styles,
    set_line_edit_styles,
    set_checkbox_styles,
    set_table_styles,
    set_label_styles,
    set_button_styles,
)


class SetTaskPage(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self.countdown_label = QLabel("未设置定时任务")
        set_label_styles(self.countdown_label, font_size=14, color='green')
        self.countdown_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.countdown_label)

        time_set_layout = QVBoxLayout()
        text_label = QLabel("时间设置（24小时制）")
        set_label_styles(text_label, font_size=12, bold=True, location='left')
        time_set_layout.addWidget(text_label, alignment=Qt.AlignBottom)

        time_layout = QHBoxLayout()
        hour_label = QLabel("点")
        set_label_styles(hour_label)
        self.hour_entry = QLineEdit()
        set_line_edit_styles(self.hour_entry)
        time_layout.addWidget(self.hour_entry)
        time_layout.addWidget(hour_label)
        minute_label = QLabel("分")
        set_label_styles(minute_label)
        self.minute_entry = QLineEdit()
        set_line_edit_styles(self.minute_entry)
        time_layout.addWidget(self.minute_entry)
        time_layout.addWidget(minute_label)
        time_set_layout.addLayout(time_layout)

        main_layout.addLayout(time_set_layout)

        date_set_layout = QVBoxLayout()
        date_label = QLabel("日期设置")
        set_label_styles(date_label, font_size=12, bold=True, location='left')
        date_set_layout.addWidget(date_label, alignment=Qt.AlignBottom)

        day_layout = QHBoxLayout()
        day_labels = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        self.day_checkboxes = []
        for label in day_labels:
            checkbox = QCheckBox(label)
            set_checkbox_styles(checkbox)
            day_layout.addWidget(checkbox)
            self.day_checkboxes.append(checkbox)
        main_layout.addLayout(date_set_layout)
        main_layout.addLayout(day_layout)

        action_layout = QHBoxLayout()
        self.shutdown_radio = QRadioButton("关机")
        set_radio_styles(self.shutdown_radio)
        self.shutdown_radio.setChecked(True)
        # self.shutdown_radio.toggled.connect(self.set_action)
        self.restart_radio = QRadioButton("重启")
        set_radio_styles(self.restart_radio)
        # self.restart_radio.toggled.connect(self.set_action)
        action_layout.addWidget(self.shutdown_radio)
        action_layout.addWidget(self.restart_radio)
        main_layout.addLayout(action_layout)
        main_layout.setAlignment(action_layout, Qt.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        set_shutdown_button = QPushButton("启用定时任务")
        set_button_styles(set_shutdown_button, background_color='#4CAF50', hover_color='#45a049')
        # set_shutdown_button.clicked.connect(self.set_task)
        button_layout.addWidget(set_shutdown_button)
        main_layout.addLayout(button_layout)

        # central_widget.setLayout(main_layout)
        # return central_widget
