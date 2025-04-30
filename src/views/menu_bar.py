#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/24 16:47
# @Author   :luye
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QAction


class MenuBarView(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.show_action1 = True
        self.setup_actions()

    def initUI(self):
        self.view_task = QAction('操作 1', self)
        self.action1.triggered.connect(self.switch_action)

        # 创建操作 2
        self.action2 = QAction('操作 2', self)
        self.action2.triggered.connect(self.switch_action)

        # 创建操作 3
        self.action3 = QAction('操作 3', self)

    def setup_actions(self):
        # 清空菜单栏
        self.clear()
        if self.show_action1:
            self.addAction(self.action1)
        else:
            self.addAction(self.action2)
        self.addAction(self.action3)

    def switch_action(self):
        self.show_action1 = not self.show_action1
        self.setup_actions()