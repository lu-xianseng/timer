#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/24 16:47
# @Author   :luye

import sys
import ctypes
from src.log import _excepthook
from src.window import LorienTimer
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    # 设置应用程序在高 DPI 屏幕上的缩放行为
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 设置应用程序的唯一标识符，用于在任务栏等地方显示图标
    # 设置全局异常处理函数
    sys.excepthook = _excepthook
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("lorientimer")
    # 创建一个 QApplication 实例，这是 PyQt5 应用程序的基础
    app = QApplication(sys.argv)
    # 创建 LorienTimer 类的实例，这是主窗口类
    timer = LorienTimer()
    # 显示主窗口
    timer.show()
    # 进入应用程序的主循环，等待用户交互和事件处理
    sys.exit(app.exec_())