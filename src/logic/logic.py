#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/5/18 16:47
# @Author   :luye

import datetime
import os

from src.public.database import DatabaseManager
from src.public.log import logger
from src.public.task import Task
from src.public.settings import (
    ROOT_PATH,
    WORLD_DICT,
    LOOP_MAPPING,
    ACTION_MAPPING,
    WEEKDAY_MAPPING
)
logger.info(f'rp: {ROOT_PATH}')


class Logic:

    def __init__(self):
        self.db = DatabaseManager()
        self.task = Task()

    def __parse_task(self, _time, action, loop, day):
        # 获取设置的时间
        selected_time = _time.time()
        hour = selected_time.hour()
        minute = selected_time.minute()
        action_type = action.currentText()
        loop_type = loop.currentText()
        day_text = ''
        day_index = 0
        if day.isVisible():
            day_text = day.currentText()
            day_index = day.currentIndex() + 1
        return hour, minute, day_text, day_index, action_type, loop_type

    def add_task(self, _time, action, loop, day):
        """添加任务按钮的槽函数"""
        # 获取设置的时间
        hour, minute, day_text, day_index, action_type, loop_type = self.__parse_task(_time, action, loop, day)
        task_info = f"Task setting: {hour}:{minute}, operation: {WORLD_DICT[action_type]}, loop: {WORLD_DICT[loop_type]}"
        task_name = f"{WORLD_DICT[action_type]}-{hour}-{minute}-{WORLD_DICT[loop_type]}"
        if day.isVisible():
            task_info += f", date: {day_index}"
            task_name += f"-{day_index}"

        logger.info(task_info)
        if self.task.create_scheduled_task(
                task_name=task_name,
                executable_path=fr'{ROOT_PATH}\timer.exe',
                arguments=f'H86R74H2BFY201' if action_type == '重启' else 'H86S74H2BFY201',
                start_time=f"{hour}:{minute}",
                schedule_type=LOOP_MAPPING[loop_type],
                schedule_days=[day_index]
        ):
            res = self.db.insert_task(
                action=action_type,
                hour=hour,
                minute=minute,
                loop=loop_type,
                day=day_text,
            )

            info = {
                "action": action_type,
                "hour": hour,
                "minute": minute,
                "loop": loop_type,
                "day": day_text,
            }

            return res.get('success'), info
        return None, {}

    def get_all_tasks(self):
        res = self.db.get_all_tasks()
        return res.get('success'), res.get('tasks')

    def delete_task(self, task_id):
        _, action, hour, minute, loop, day = self.db.get_task_by_id(task_id)
        task_name = f"{WORLD_DICT[action]}-{hour}-{minute}-{WORLD_DICT[loop]}"
        if day:
            if loop == '每周':
                task_name += f"-{WEEKDAY_MAPPING[day]}"
            else:
                task_name += f"-{day.split()[0]}"
        self.task.delete_scheduled_task(
            task_name=task_name)
        res = self.db.delete_task(task_id)
        logger.info('Deleted task {}'.format(task_id))
        return res.get('success')

    def exists_task(self, _time, action, loop, day):
        hour, minute, day_text, day_index, action_type, loop_type = self.__parse_task(_time, action, loop, day)
        res = self.db.query_tasks(
            action=action_type,
            hour=hour,
            minute=minute,
            loop=loop_type,
            day=day_text,
        )
        return True if res.get('tasks') else False

    def next_task(self):
        # 获取当前时间
        now = datetime.datetime.now()
        next_task = self.task.find_next_task()
        if next_task is None:
            return False, "\n\n未设置定时任务"
        # 计算时间差
        delta = next_task[1] - now
        action = next_task[0].split('-')[2]

        # 提取天、时、分、秒
        days = delta.days
        seconds = delta.seconds
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # 构建格式化字符串
        time_parts = []
        if days > 0:
            time_parts.append(f"{days}天")
        if hours > 0:
            time_parts.append(f"{hours}小时")
        if minutes > 0:
            time_parts.append(f"{minutes}分钟")
        if seconds > 0 or not time_parts:  # 确保至少显示 0 秒
            time_parts.append(f"{seconds}秒")
        text = f"\n\n{"".join(time_parts)} 后{ACTION_MAPPING[action]}"
        return True, text

    @staticmethod
    def execute_action(action):
        if action == "shutdown":
            logger.info('Shutdown now')
            os.system("shutdown /f /s /t 0")
        elif action == "reboot":
            logger.info('Reboot now')
            os.system("shutdown /f /r /t 0")
