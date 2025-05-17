#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/24 16:47
# @Author   :luye
import os
import time

from PyQt5.QtWidgets import QMessageBox

from src.public.database import DatabaseManager
from src.public.log import logger
from src.public.public import run_cmd
from src.public.settings import (
    RES_PATH,
    PLUGIN,
    KEY,
    ACTION_EN_MAPPING,
    ACTION_ZH_MAPPING,
    DAY_MAPPING,
    WEEKDAY_MAPPING,
    WAIT_TIME,
    WORLD_DICT
)
from src.public.public import task_name


class Logic:

    def __init__(self):
        self.db = DatabaseManager()

    def __parse_task(self,  _time, action, loop, day):
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
        if day.isVisible():
            task_info += f", date: {day.currentIndex() + 1}"

        logger.info(task_info)
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

    def get_all_tasks(self):
        res = self.db.get_all_tasks()
        return res.get('success'), res.get('tasks')


    def delete_task(self, task_id):
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
