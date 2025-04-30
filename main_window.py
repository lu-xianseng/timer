#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/24 16:47
# @Author   :luye

import sys
import ctypes
from PyQt5.QtWidgets import (
    QApplication, QWidget, QStackedWidget, QVBoxLayout, QMenuBar, QMenu,
    QAction,
)
from PyQt5.QtGui import QPalette, QColor, QIcon
from src.logic.logic import Logic
from src.public.log import _excepthook
from src.public.settings import RES_PATH

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget(self)
        self.logic = Logic(self.stacked_widget)

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
        
    def init_window(self):
        self.setWindowTitle("定时设置")
        self.setGeometry(100, 100, 600, 400)
        self.setFixedSize(self.width(), self.height())

        icon = QIcon(rf'{RES_PATH}\\icon.ico')
        self.setWindowIcon(icon)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        self.setPalette(palette)

        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        main_menu = QMenu("菜单", self)
        menu_bar.addMenu(main_menu)
        icon = self.style().standardIcon(QStyle.SP_DesktopIcon)
        view_tasks_action = QAction(icon, "查看计划", self)
        view_tasks_action.triggered.connect(self.view_tasks)
        main_menu.addAction(view_tasks_action)
        icon = self.style().standardIcon(QStyle.SP_MessageBoxInformation)
        about_action = QAction(icon, "关于", self)
        about_action.triggered.connect(self.show_about)
        main_menu.addAction(about_action)

        screen_geometry = QApplication.desktop().screenGeometry()
        window_width = self.width()
        window_height = self.height()
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        self.move(x, y)
        

if __name__ == '__main__':
    # 设置应用程序在高 DPI 屏幕上的缩放行为
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 设置应用程序的唯一标识符，用于在任务栏等地方显示图标
    # 设置全局异常处理函数
    sys.excepthook = _excepthook
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("lorientimer")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())