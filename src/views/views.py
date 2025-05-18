#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/24 16:47
# @Author   :luye

import sys

from PyQt5.QtCore import Qt, QDateTime, QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QVBoxLayout, QWidget,
    QTabWidget, QLabel, QHBoxLayout, QPushButton, QComboBox, QTimeEdit,
    QGridLayout, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QTextBrowser, QMessageBox,
)
from PyQt5.QtGui import QPalette, QColor, QIcon
from src.logic.logic import Logic
from src.public.log import logger
from src.public.settings import RES_PATH, WAIT_TIME
from src.views.styles import (
    set_checkbox_styles,
    set_label_styles,
    set_button_styles, set_table_styles,
)


class MainWindow(QMainWindow):
    def __init__(self, action='0'):
        super().__init__()
        self.action = action
        self.remaining_time = WAIT_TIME
        self.countdown_txt = ""
        self.countdown_txt_with_sub = ""
        self.current_task_info = None
        self.tasks_table = None
        self.text = ''
        self.day_selection = None
        self.loop_combo = None
        self.loop_label = None
        self.time_edit = None
        self.action_combo = None
        self.date_label = None
        self.countdown_label_with_sub = QLabel(self.countdown_txt_with_sub)
        self.countdown_label = QLabel(self.countdown_txt)
        self.about_tab = None
        self.view_tasks_tab = None
        self.setup_task_tab = None
        self.tab_widget = None
        self.logic = Logic()
        self.stacked_widget = QStackedWidget(self)

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.timer = QTimer(self)
        if int(action[-1]) == 0:
            self.init_main_window()
            self.timer.timeout.connect(self.update_countdown)
        else:
            self.init_sub_window()
            self.timer.timeout.connect(self.update_countdown_with_sub)
        self.timer.start(1000)

    def init_sub_window(self):
        self.setWindowTitle("计划执行")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setGeometry(100, 100, 300, 100)
        self.setFixedSize(self.width(), self.height())
        icon = QIcon(rf'{RES_PATH}\\icon.ico')
        self.setWindowIcon(icon)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        self.setPalette(palette)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局

        layout = QVBoxLayout(central_widget)
        if self.action[3].lower() == 's':
            self.text = '关机'
        elif self.action[3].lower() == 'r':
            self.text = '重启'
        else:
            sys.exit(1)


        set_label_styles(self.countdown_label_with_sub, font_size=12, color='red', bold=True)
        layout.addWidget(self.countdown_label_with_sub)

        self.cancel_button = QPushButton('取消', self)
        set_button_styles(self.cancel_button, background_color='#EB4444', hover_color='#CC0000')
        self.cancel_button.clicked.connect(self.cancel_action)
        layout.addWidget(self.cancel_button)

        self.move_window()

    def update_countdown_with_sub(self):
        self.remaining_time -= 1
        self.countdown_txt_with_sub = f"系统将在 {self.remaining_time} 秒后 {self.text}..."
        self.countdown_label_with_sub.setText(self.countdown_txt_with_sub)

        if self.remaining_time < 1:
            if self.action[3].lower() == 's':
                self.logic.execute_action('shutdown')
            elif self.action[3].lower() == 'r':
                self.logic.execute_action('reboot')
            self.timer.stop()


    def cancel_action(self):
        self.close()

    def init_main_window(self):
        self.setWindowTitle("定时设置")
        self.setGeometry(100, 100, 600, 400)
        self.setFixedSize(self.width(), self.height())

        icon = QIcon(rf'{RES_PATH}\\icon.ico')
        self.setWindowIcon(icon)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        self.setPalette(palette)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(central_widget)

        # 创建标签页控件
        self.tab_widget = QTabWidget()

        # 添加"设置任务"标签页
        self.setup_task_tab = QWidget()
        self.set_task_ui()
        self.tab_widget.addTab(self.setup_task_tab, '设置任务')

        # 添加"查看任务"标签页
        self.view_tasks_tab = QWidget()
        # self.view_tasks_ui()
        self.setup_view_tasks_ui()
        self.tab_widget.addTab(self.view_tasks_tab, '查看任务')
        # 连接标签页切换信号
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # 添加"关于"标签页
        self.about_tab = QWidget()
        self.about_ui()
        self.tab_widget.addTab(self.about_tab, '关于')

        # 添加标签页到主布局
        main_layout.addWidget(self.tab_widget)
        self.move_window()

    def move_window(self):
        screen_geometry = QApplication.desktop().screenGeometry()
        window_width = self.width()
        window_height = self.height()
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        self.move(x, y)

    def set_task_ui(self):
        # 主布局（垂直布局，顶部弹性区域 + 底部固定按钮）
        main_layout = QVBoxLayout(self.setup_task_tab)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 顶部弹性布局（放置任务设置组件）
        set_layout = QVBoxLayout()
        set_layout.setAlignment(Qt.AlignBottom)  # 顶部对齐
        set_layout.setContentsMargins(0, 0, 0, 0)
        set_layout.setSpacing(8)

        set_label_styles(self.countdown_label, font_size=14, color='green', bold=True)
        self.countdown_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.countdown_label)

        # 创建任务设置组
        task_group = QGroupBox("")
        task_layout = QGridLayout(task_group)

        # 时间选择
        time_label = QLabel('时间设置:')
        set_label_styles(time_label, location='left')
        self.time_edit = QTimeEdit()
        set_label_styles(self.time_edit, location='left')
        self.time_edit.setTime(QDateTime.currentDateTime().time().addSecs(3600))

        # 操作类型选择
        action_label = QLabel('操作设置:')
        set_label_styles(action_label, location='left')
        self.action_combo = QComboBox()
        set_checkbox_styles(self.action_combo)
        self.action_combo.addItems(['关机', '重启'])

        # 循环设置
        self.loop_label = QLabel('循环操作:')
        set_label_styles(self.loop_label, location='left')
        self.loop_combo = QComboBox()
        self.loop_combo.addItems(['每天', '每周', '每月'])
        set_checkbox_styles(self.loop_combo)
        self.loop_combo.currentIndexChanged.connect(self.show_hide_day_selection)

        # 日期选择框（初始隐藏）
        self.date_label = QLabel('日期设置:')
        set_label_styles(self.date_label, location='left')
        self.date_label.hide()
        self.day_selection = QComboBox()
        set_checkbox_styles(self.day_selection)
        self.day_selection.hide()

        # 组内布局（任务设置组件）
        task_layout.addWidget(time_label, 0, 0)
        task_layout.addWidget(self.time_edit, 0, 1)
        task_layout.addWidget(action_label, 1, 0)
        task_layout.addWidget(self.action_combo, 1, 1)
        task_layout.addWidget(self.loop_label, 2, 0)
        task_layout.addWidget(self.loop_combo, 2, 1)
        task_layout.addWidget(self.date_label, 3, 0)
        task_layout.addWidget(self.day_selection, 3, 1)

        # 将任务组添加到顶部布局
        set_layout.addWidget(task_group)

        # 底部固定布局（按钮靠下）
        bottom_layout = QHBoxLayout()

        # 添加任务按钮（右对齐）
        add_button = QPushButton('添加任务')
        add_button.setFixedWidth(200)
        set_button_styles(add_button, background_color='#4CAF50', hover_color='#45a049')
        add_button.clicked.connect(self.add_task)
        bottom_layout.addWidget(add_button)

        # 将顶部布局和底部布局添加到主布局
        main_layout.addLayout(set_layout)
        main_layout.addLayout(bottom_layout)
        main_layout.setStretchFactor(set_layout, 1)  # 顶部布局占据弹性空间

    def update_countdown(self):
        state, text = self.logic.next_task()
        color = 'red' if state else 'green'
        self.countdown_label.setText(text)
        set_label_styles(self.countdown_label, font_size=14, color=color, bold=True)

    def add_task(self):
        if self.logic.exists_task(
                self.time_edit,
                self.action_combo,
                self.loop_combo,
                self.day_selection,
        ):
            QMessageBox.critical(self, '错误', "已存在此任务")
            return
        res, info = self.logic.add_task(
            self.time_edit,
            self.action_combo,
            self.loop_combo,
            self.day_selection
        )
        if res:
            QMessageBox.information(self, '消息', "添加任务成功")
        self.current_task_info = info
        # self.update_countdown()

    def show_hide_day_selection(self, index):  # 必须接收 index 参数
        self.day_selection.clear()
        weekday_mapping = {
            1: "周一",
            2: "周二",
            3: "周三",
            4: "周四",
            5: "周五",
            6: "周六",
            7: "周日",
        }
        if index == 1:  # 每周（索引从0开始，原代码中 '每周' 是第2项，索引为1）
            self.day_selection.addItems([f"{weekday_mapping[i]}" for i in range(1, 8)])
            self.date_label.show()
            self.day_selection.show()
        elif index == 2:  # 每月（索引为2）
            self.day_selection.addItems([f"{i} 日" for i in range(1, 32)])
            self.date_label.show()
            self.day_selection.show()
        else:  # 每天（索引为0）或其他
            self.date_label.hide()
            self.day_selection.hide()

    def setup_view_tasks_ui(self):
        view_layout = QVBoxLayout(self.view_tasks_tab)

        # 创建表格但不填充数据
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(5)
        self.tasks_table.setHorizontalHeaderLabels(["动作", "时间", "循环", "日期", "操作"])
        set_table_styles(self.tasks_table)

        self.tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        view_layout.addWidget(self.tasks_table)

        # 底部按钮
        bottom_button_layout = QHBoxLayout()

        cancel_all_button = QPushButton("取消全部")
        set_button_styles(cancel_all_button, background_color='#EB4444', hover_color='#CC0000')
        cancel_all_button.clicked.connect(self.cancel_all_tasks)
        bottom_button_layout.addWidget(cancel_all_button)

        view_layout.addLayout(bottom_button_layout)

    def refresh_tasks_table(self):
        # 清空表格
        self.tasks_table.setRowCount(0)

        # 从数据库获取最新任务
        state, tasks = self.logic.get_all_tasks()

        # 填充表格
        self.tasks_table.setRowCount(len(tasks))

        for row, task in enumerate(tasks):
            task_id, action, hour, minute, loop, day = task

            # 设置动作列
            item_action = QTableWidgetItem(action)
            item_action.setFlags(item_action.flags() & ~Qt.ItemIsEditable)
            item_action.setTextAlignment(Qt.AlignCenter)
            self.tasks_table.setItem(row, 0, item_action)

            # 设置时间列
            item_time = QTableWidgetItem(f"{hour:02d}:{minute:02d}")
            item_time.setFlags(item_time.flags() & ~Qt.ItemIsEditable)
            item_time.setTextAlignment(Qt.AlignCenter)
            self.tasks_table.setItem(row, 1, item_time)

            # 设置循环列
            item_loop = QTableWidgetItem(loop)
            item_loop.setFlags(item_loop.flags() & ~Qt.ItemIsEditable)
            item_loop.setTextAlignment(Qt.AlignCenter)
            self.tasks_table.setItem(row, 2, item_loop)

            # 设置日期列
            item_day = QTableWidgetItem(day)
            item_day.setFlags(item_day.flags() & ~Qt.ItemIsEditable)
            item_day.setTextAlignment(Qt.AlignCenter)
            self.tasks_table.setItem(row, 3, item_day)

            # 设置取消按钮
            cancel_button = QPushButton("取消计划")
            set_button_styles(cancel_button, background_color='#EB4444', hover_color='#CC0000', padding='1px 3px')
            cancel_button.clicked.connect(lambda _, t_id=task_id: self.delete_task(t_id))
            self.tasks_table.setCellWidget(row, 4, cancel_button)

    def on_tab_changed(self, index):
        # 当切换到"查看任务"标签页时刷新数据
        if self.tab_widget.tabText(index) == '查看任务':
            self.refresh_tasks_table()

    def cancel_all_tasks(self):
        # 取消所有任务的逻辑
        state, tasks = self.logic.get_all_tasks()
        if not tasks:
            return
        for task in tasks:
            self.logic.delete_task(task[0])
        else:
            QMessageBox.information(self, "消息", "计划任务全部取消")
            self.refresh_tasks_table()

    def delete_task(self, task_id):
        # 删除单个任务的逻辑
        if self.logic.delete_task(task_id):
            self.refresh_tasks_table()

    def about_ui(self):
        about_layout = QVBoxLayout(self.about_tab)
        about_text = (
            '<h2 style="color: #2c3e50; border-bottom: 1px solid #ddd; padding-bottom: 8px;">帮助说明</h2>'
            '<p style="font-size: 15px; line-height: 1.6;">'
            '<b>▶ 设置定时任务：</b><br>'
            '您可以设置定时任务并激活它。到达预定时间点后，系统会弹出提示。如果您不处理提示，系统将在倒计时结束后执行操作。支持设置每天、每周、每月循环任务设定。'
            '</p>'
            '<p style="font-size: 15px; line-height: 1.6;">'
            '<b>▶ 关闭或取消任务：</b><br>'
            '到达任务出发时间，系统将弹出倒计时提示，若点击"关闭"或"取消"按钮，定时任务将不会继续执行。定时任务可设置多个时间点任务'
            '</p>'
            '<p style="font-size: 15px; line-height: 1.6;">'
            '<b>▶ 任务管理：</b><br>在查看任务界面，您可以对定时任务进行单个取消或批量取消操作。'
            '</p><br>'
            '<h2 style="color: #2c3e50; border-bottom: 1px solid #ddd; padding-bottom: 8px;">关于作者</h2>'
            '<p style="font-size: 16px; line-height: 1.6;">'
            '作者：lorien<br>'
            'Github：<a href="https://github.com/lu-xianseng/timer" style="color: #3498db; text-decoration: none;">github.com/lu-xianseng/timer</a><br>'
            'Email: <a href="mailto:1173381395@qq.com" style="color: #3498db; text-decoration: none;">1173381395@qq.com</a>'
            '</p>'
        )
        text_browser = QTextBrowser()
        text_browser.setHtml(about_text)
        text_browser.setReadOnly(True)
        text_browser.setOpenExternalLinks(True)
        about_layout.addWidget(text_browser)
