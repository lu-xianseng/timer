#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/24 16:47
# @Author   :luye

import sys
import ctypes
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QVBoxLayout, QWidget, QMenu,
    QAction,
)
from PyQt5.QtGui import QPalette, QColor, QIcon
from src.logic.logic import Logic
from src.public.log import def_excepthook
from src.public.settings import RES_PATH
from src.views.menu_bar import MenuBarView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget(self)
        self.menu_bar = MenuBarView()
        self.logic = Logic(self.stacked_widget, self.menu_bar)

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.setMenuBar(self.menu_bar)
        self.init_window()

    def init_window(self):
        self.setWindowTitle("定时设置")
        self.setGeometry(100, 100, 600, 400)
        self.setFixedSize(self.width(), self.height())

        icon = QIcon(rf'{RES_PATH}\\icon.ico')
        self.setWindowIcon(icon)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        self.setPalette(palette)

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
    sys.excepthook = def_excepthook
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("lorientimer")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
