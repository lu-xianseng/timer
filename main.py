#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/5/18 16:47
# @Author   :luye

import sys
import ctypes
from PyQt5.QtWidgets import QApplication
from src.public.log import def_excepthook
from src.views.views import MainWindow




if __name__ == '__main__':
    # 设置应用程序在高 DPI 屏幕上的缩放行为
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 设置应用程序的唯一标识符，用于在任务栏等地方显示图标
    # 设置全局异常处理函数
    sys.excepthook = def_excepthook
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("lorientimer")
    app = QApplication(sys.argv)
    if len(sys.argv) < 2:
        window = MainWindow()
    else:
        window = MainWindow(sys.argv[1])
    window.show()
    sys.exit(app.exec_())
