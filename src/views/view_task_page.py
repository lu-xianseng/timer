#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/24 16:47
# @Author   :luye
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QHBoxLayout, QHeaderView
)
from src.views.styles import *
from src.public.settings import *
from src.public.database import DatabaseManager


class ViewTaskPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        view_layout = QVBoxLayout()
        
        # tasks = self.db_manager.get_all_tasks()
        tasks = []
        view_layout = QVBoxLayout()

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["动作", "时间", "日期", "操作"])
        table.setRowCount(len(tasks))
        set_table_styles(table)

        for row, task in enumerate(tasks):
            task_id, action, hour, minute, day = task
            action = '关机' if action == '0' else '重启'
            item_action = QTableWidgetItem(action)
            item_action.setFlags(item_action.flags() & ~Qt.ItemIsEditable)
            item_action.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 0, item_action)

            item_time = QTableWidgetItem(f"{hour:02d}:{minute:02d}")
            item_time.setFlags(item_time.flags() & ~Qt.ItemIsEditable)
            item_time.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 1, item_time)

            item_day = QTableWidgetItem(DAY_MAPPING[day])
            item_day.setFlags(item_day.flags() & ~Qt.ItemIsEditable)
            item_day.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 2, item_day)

            cancel_button = QPushButton("取消计划")
            set_button_styles(cancel_button, background_color='#EB4444', hover_color='#CC0000', padding='1px 3px')
            # cancel_button.clicked.connect(lambda _, r=row, t_id=task_id: self.delete_task(t_id))
            table.setCellWidget(row, 3, cancel_button)

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        view_layout.addWidget(table)

        bottom_button_layout = QHBoxLayout()

        cancel_all_button = QPushButton("取消全部")
        set_button_styles(cancel_all_button, background_color='#EB4444', hover_color='#CC0000')
        # cancel_all_button.clicked.connect(self.cancel_task)
        bottom_button_layout.addWidget(cancel_all_button)

        view_layout.addLayout(bottom_button_layout)

        self.setLayout(view_layout)