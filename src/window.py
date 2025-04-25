#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/24 16:47
# @Author   :luye
import time
from PyQt5.QtWidgets import (
    QApplication, 
    QWidget, 
    QStyle, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel, 
    QLineEdit, 
    QPushButton, 
    QCheckBox, 
    QMessageBox, 
    QMainWindow, 
    QMenuBar, 
    QMenu, 
    QAction, 
    QRadioButton, 
    QTableWidget, 
    QTableWidgetItem, 
    QStackedWidget, 
    QHeaderView
)
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QTimer
from src.database import DatabaseManager
from src.styles import (
    set_label_styles, 
    set_line_edit_styles,
    set_button_styles, 
    set_checkbox_styles,
    set_radio_styles
    )
from src.log import logger
from src.command import run_cmd
from src.settings import RES_PATH



class LorienTimer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.shutdown_time = None
        self.selected_days = []
        self.day_mapping = {
            1: "周一",
            2: "周二",
            3: "周三",
            4: "周四",
            5: "周五",
            6: "周六",
            7: "周日"
        }
        self.weekday_abbr_mapping = {
            1: "MON",
            2: "TUE",
            3: "WED",
            4: "THU",
            5: "FRI",
            6: "SAT",
            7: "SUN"
        }
        self.action = "关机"
        self.db_action = ''
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.db_manager = DatabaseManager()
        self.initUI()
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.main_widget = self.create_main_widget()
        self.stacked_widget.addWidget(self.main_widget)
        self.check_existing_tasks()

    def create_main_widget(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self.countdown_label = QLabel("未设置定时任务")
        set_label_styles(self.countdown_label, font_size=14, color='green')
        self.countdown_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.countdown_label)

        shutdown_layout = QVBoxLayout()
        shutdown_label = QLabel("时间设置（24小时制）")
        set_label_styles(shutdown_label, font_size=12, bold=True)
        shutdown_layout.addWidget(shutdown_label)

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
        shutdown_layout.addLayout(time_layout)

        main_layout.addLayout(shutdown_layout)

        day_layout = QHBoxLayout()
        day_labels = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        self.day_checkboxes = []
        for label in day_labels:
            checkbox = QCheckBox(label)
            set_checkbox_styles(checkbox)
            day_layout.addWidget(checkbox)
            self.day_checkboxes.append(checkbox)
        main_layout.addLayout(day_layout)

        action_layout = QHBoxLayout()
        self.shutdown_radio = QRadioButton("关机")
        set_radio_styles(self.shutdown_radio)
        self.shutdown_radio.setChecked(True)
        self.shutdown_radio.toggled.connect(self.set_action)
        self.restart_radio = QRadioButton("重启")
        set_radio_styles(self.restart_radio)
        self.restart_radio.toggled.connect(self.set_action)
        action_layout.addWidget(self.shutdown_radio)
        action_layout.addWidget(self.restart_radio)
        main_layout.addLayout(action_layout)
        main_layout.setAlignment(action_layout, Qt.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        set_shutdown_button = QPushButton("启用定时任务")
        set_button_styles(set_shutdown_button, background_color='#4CAF50', hover_color='#45a049')
        set_shutdown_button.clicked.connect(self.set_task)
        button_layout.addWidget(set_shutdown_button)
        main_layout.addLayout(button_layout)

        central_widget.setLayout(main_layout)
        return central_widget

    def set_action(self):
        if self.shutdown_radio.isChecked():
            self.action = "关机"
        else:
            self.action = "重启"

    def check_and_delete_task(self, task_name):
        try:
            command = f'schtasks /query /tn "{task_name}"'
            result = run_cmd(command)
            if result[0] == 0:
                command = f'schtasks /delete /tn "{task_name}" /f'
                run_cmd(command)
        except Exception as e:
            pass

    def set_task(self):
        try:
            hour = int(self.hour_entry.text())
            minute = int(self.minute_entry.text())
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                self.selected_days = []
                for i, checkbox in enumerate(self.day_checkboxes):
                    if checkbox.isChecked():
                        self.selected_days.append(i + 1)

                if self.selected_days:
                    for day in self.selected_days:
                        # 删除相同动作和日期的旧任务
                        old_task_name = f"{self.action}Task_{self.day_mapping[day]}"
                        self.check_and_delete_task(old_task_name)
                        self.db_manager.delete_tasks_by_action_and_day(self.action, day)

                        new_task_name = f"{self.action}Task_{self.day_mapping[day]}"
                        if self.action == "关机":
                            command = f'schtasks /create /tn "{new_task_name}" /tr "shutdown /s /t 0" /sc weekly /d {self.weekday_abbr_mapping[day]} /st {hour:02d}:{minute:02d}'
                        else:
                            command = f'schtasks /create /tn "{new_task_name}" /tr "shutdown /r /t 0" /sc weekly /d {self.weekday_abbr_mapping[day]} /st {hour:02d}:{minute:02d}'
                        run_cmd(command)
                        self.db_manager.insert_task(self.action, hour, minute, day)
                        self.db_action = self.action

                    self.shutdown_time = (hour, minute, self.selected_days)
                    QMessageBox.information(self, "成功", f"定时{self.action}设置成功！")
                    logger.info(f"定时器启动，shutdown_time: {self.shutdown_time}")
                    self.timer.start(1000)
                    self.update_countdown()
                else:
                    QMessageBox.critical(self, "错误", "请选择至少一个循环日期！")
            else:
                QMessageBox.critical(self, "错误", "请输入有效的时（0 - 23）和分（0 - 59）！")
        except ValueError:
            QMessageBox.critical(self, "错误", "请输入有效的时（0 - 23）和分（0 - 59）！")

    def cancel_task(self):
        tasks = self.db_manager.get_all_tasks()
        for task in tasks:
            action = task[1]
            day = task[4]
            task_name = f"{action}Task_{self.day_mapping[day]}"
            self.check_and_delete_task(task_name)
        self.db_manager.delete_all_tasks()

        self.shutdown_time = None
        self.timer.stop()
        self.countdown_label.setText("未设置定时任务")
        self.countdown_label.setStyleSheet("QLabel { color: green; }")
        QMessageBox.information(self, "成功", "定时关机或重启已取消！")
        # 返回主页面
        self.stacked_widget.setCurrentWidget(self.main_widget)

    def check_existing_tasks(self):
        tasks = self.db_manager.get_all_tasks()

        if tasks:
            now = time.localtime()
            current_weekday = now.tm_wday + 1
            current_time = time.mktime(now)
            next_time = None
            for task in tasks:
                shutdown_hour = task[2]
                shutdown_minute = task[3]
                shutdown_day = task[4]
                action = task[1]

                target_time = time.mktime(now)
                days_diff = (shutdown_day - current_weekday) % 7
                target_time += days_diff * 24 * 60 * 60
                target_time = time.localtime(target_time)
                target_time = time.mktime((target_time.tm_year, target_time.tm_mon, target_time.tm_mday, shutdown_hour,
                                           shutdown_minute, 0, 0, 0, 0))
                if target_time < current_time:
                    target_time += 7 * 24 * 60 * 60

                if next_time is None or target_time < next_time[0]:
                    next_time = (target_time, shutdown_hour, shutdown_minute, [shutdown_day], action)

            if next_time:
                self.shutdown_time = (next_time[1], next_time[2], next_time[3])
                self.action = next_time[4]
                self.db_action = next_time[4]
                if self.action == "关机":
                    self.shutdown_radio.setChecked(True)
                else:
                    self.restart_radio.setChecked(True)
                logger.info(f"检查到现有任务，shutdown_time: {self.shutdown_time}")
                self.timer.start(1000)
                self.update_countdown()
        else:
            self.countdown_label.setText("未设置定时任务")
            self.shutdown_time = None

    def initUI(self):
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

    def show_about(self):
        about_text = '作者：lorien<br>主页：<a href="https://hi-lorien.cn">hi-lorien.cn</a>'
        QMessageBox.information(self, "关于", about_text)

    def update_countdown(self):
        if self.shutdown_time:
            now = time.localtime()
            hour, minute, days = self.shutdown_time
            logger.info(f"当前时间: {time.strftime('%Y-%m-%d %H:%M:%S', now)}, 设置时间: {hour}:{minute}, 循环日期: {days}")
            next_time = None
            for day in days:
                target_time = time.mktime(now)
                current_weekday = now.tm_wday + 1
                days_diff = (day - current_weekday) % 7
                target_time += days_diff * 24 * 60 * 60
                target_time = time.localtime(target_time)
                target_time = time.mktime(
                    (target_time.tm_year, target_time.tm_mon, target_time.tm_mday, hour, minute, 0, 0, 0, 0))
                if target_time < time.mktime(now):
                    target_time += 7 * 24 * 60 * 60
                if next_time is None or target_time < next_time:
                    next_time = target_time
            logger.info(f"下一次任务时间: {next_time if next_time else '未找到'}")
            if next_time:
                remaining_seconds = int(next_time - time.mktime(now))
                if remaining_seconds > 0:
                    days, remaining_seconds = divmod(remaining_seconds, 86400)
                    hours, remaining_seconds = divmod(remaining_seconds, 3600)
                    minutes, seconds = divmod(remaining_seconds, 60)
                    countdown_str = f"{days}天 {hours:02d}时 {minutes:02d}分 {seconds:02d}秒 后 {self.db_action}"
                    self.countdown_label.setText(countdown_str)
                    self.countdown_label.setStyleSheet("QLabel { color: red; }")
                else:
                    self.timer.stop()
                    self.countdown_label.setText("未设置定时任务")
                    self.countdown_label.setStyleSheet("QLabel { color: green; }")
            else:
                self.timer.stop()
                self.countdown_label.setText("未设置定时任务")
                self.countdown_label.setStyleSheet("QLabel { color: green; }")
        else:
            self.timer.stop()
            self.countdown_label.setText("未设置定时任务")
            self.countdown_label.setStyleSheet("QLabel { color: green; }")

    def view_tasks(self):
        tasks = self.db_manager.get_all_tasks()

        view_widget = QWidget()
        view_layout = QVBoxLayout()

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["动作", "时间", "日期", "操作"])
        table.setRowCount(len(tasks))

        for row, task in enumerate(tasks):
            task_id, action, hour, minute, day = task
            item_action = QTableWidgetItem(action)
            item_action.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 0, item_action)

            item_time = QTableWidgetItem(f"{hour:02d}:{minute:02d}")
            item_time.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 1, item_time)

            item_day = QTableWidgetItem(self.day_mapping[day])
            item_day.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 2, item_day)

            cancel_button = QPushButton("取消计划")
            set_button_styles(cancel_button, background_color='#EB4444', hover_color='#CC0000', padding='1px 10px')
            cancel_button.clicked.connect(lambda _, r=row, t_id=task_id: self.delete_task(t_id))
            table.setCellWidget(row, 3, cancel_button)

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        view_layout.addWidget(table)

        bottom_button_layout = QHBoxLayout()

        cancel_all_button = QPushButton("取消全部")
        set_button_styles(cancel_all_button, background_color='#EB4444', hover_color='#CC0000')
        cancel_all_button.clicked.connect(self.cancel_task)
        bottom_button_layout.addWidget(cancel_all_button)

        back_button = QPushButton("返回")
        set_button_styles(back_button, background_color='#0080FF', hover_color='#CC0000')
        back_button.clicked.connect(self.return_to_main)
        bottom_button_layout.addWidget(back_button)
        view_layout.addLayout(bottom_button_layout)

        view_widget.setLayout(view_layout)
        self.stacked_widget.addWidget(view_widget)
        self.stacked_widget.setCurrentWidget(view_widget)

    def return_to_main(self):
        self.stacked_widget.setCurrentWidget(self.main_widget)
        self.check_existing_tasks()

    def delete_task(self, task_id):
        task = self.db_manager.get_task_by_id(task_id)
        if task:
            action, day = task[1], task[4]
            task_name = f"{action}Task_{self.day_mapping[day]}"
            self.check_and_delete_task(task_name)
            self.db_manager.delete_task(task_id)
        self.view_tasks()
