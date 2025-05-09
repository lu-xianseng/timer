#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/24 16:47
# @Author   :luye
from mimetypes import inited

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QAction

class MenuBarView(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_task_action = None
        self.about_action = None
        self.view_task_action = None
        self.initUI()
        self.show_task_view = False
        self.setup_actions()

    def initUI(self):
        self.view_task_action = QAction('√ 查看计划', self)
        self.view_task_action.triggered.connect(self.switch_action)

        self.set_task_action = QAction('☼ 设置计划', self)
        self.set_task_action.triggered.connect(self.switch_action)

        self.about_action = QAction('❉ 关于', self)

    def setup_actions(self):
        # 清空菜单栏
        self.clear()
        if self.show_task_view:
            self.addAction(self.set_task_action)
        else:
            self.addAction(self.view_task_action)
        self.addAction(self.about_action)

    def switch_action(self):
        self.show_task_view = not self.show_task_view
        self.setup_actions()