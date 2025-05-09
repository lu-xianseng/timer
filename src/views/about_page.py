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
        about_text = (
            '<font size=4>'
            '作者：lorien<br>'
            '主页：<a href="https://hi-lorien.cn"><b>hi-lorien.cn</a><br>'
            'Email:<a href="mailto:1173381395@qq.com"><b>1173381395@qq.com</a><br><br>'
            '<p><b>☞ 设置定时任务：</b><br>您可以设置定时任务（关机或重启）并激活它。到达预定时间点后，系统会弹出提示。<br>'
            '如果您不处理提示，系统将在倒计时结束后执行关机或重启操作。</p>'
            '<p><b>☞ 关闭或取消任务：</b><br>若点击“关闭”或“取消”按钮，定时任务将不会继续执行。定时任务支持设置多个日期，<br>'
            '但对于相同的操作（关机或重启），同一天内仅允许设置一个任务，后设置的任务将覆盖<br>之前的设置。</p>'
            '<p><b>☞ 任务管理：</b><br>在查看任务界面，您可以对定时任务进行单个取消或批量取消操作。</p><br>'
            '</font>'
        )
        label = QLabel(about_text, self)
        layout.addWidget(label)
        self.setLayout(layout)