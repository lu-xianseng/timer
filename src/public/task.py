#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/5/18 09:10
# @Author   :luye

import win32timezone
import win32com.client
import datetime
from src.public.log import logger


class Task:
    # 定义循环类型常量
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    IDENTIFIER = "LORIEN-TIMER-"

    @classmethod
    def __time_str_to_datetime(cls, time_str):
        """
        将"HH:MM"格式的时间字符串转换为datetime对象

        参数:
        time_str (str): 时间字符串，格式为"HH:MM"

        返回:
        datetime: 对应的datetime对象（日期部分为当前日期）
        """
        try:
            # 解析时间字符串
            time_obj = datetime.datetime.strptime(time_str, '%H:%M').time()

            # 获取当前日期
            today = datetime.datetime.now().date()

            # 组合日期和时间
            return datetime.datetime.combine(today, time_obj)
        except ValueError:
            logger.error("时间格式不正确，请使用'HH:MM'格式！")
            return None

    def create_scheduled_task(
            self,
            task_name,
            executable_path,
            arguments="",
            start_time=None,
            schedule_type=None,
            schedule_days=None,
            description="Created by lorien timer task"
    ):
        """创建 Windows 计划任务"""
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')

        task_def = scheduler.NewTask(0)
        task_def.RegistrationInfo.Description = description
        task_def.Settings.Enabled = True

        # 设置触发器
        start_time = self.__time_str_to_datetime(start_time)

        if schedule_type == self.DAILY:
            trigger = task_def.Triggers.Create(2)  # 每日任务
            trigger.DaysInterval = 1
        elif schedule_type == self.WEEKLY:
            trigger = task_def.Triggers.Create(3)  # 每周任务
            if not schedule_days:
                raise ValueError("每周任务需要指定星期几 (1-7)")
            days_mask = sum(1 << day for day in schedule_days)
            trigger.DaysOfWeek = days_mask
            trigger.WeeksInterval = 1
        elif schedule_type == self.MONTHLY:
            trigger = task_def.Triggers.Create(4)  # 每月任务
            if not schedule_days:
                raise ValueError("每月任务需要指定日期 (1-31)")
            days_mask = sum(1 << (day - 1) for day in schedule_days)
            trigger.DaysOfMonth = days_mask
        else:
            raise ValueError(f"无效的循环类型: {schedule_type}")

        trigger.StartBoundary = start_time.strftime('%Y-%m-%dT%H:%M:%S')

        # 设置操作
        action = task_def.Actions.Create(0)  # 执行操作
        action.Path = executable_path
        action.Arguments = arguments

        # 注册任务
        root_folder.RegisterTaskDefinition(
            f"{self.IDENTIFIER}{task_name}", task_def, 6, "", "", 3, ""
        )
        logger.info(
            f"{task_name}, Create success. "
            f"run time: {self._format_schedule(start_time, schedule_type, schedule_days)}, "
            f"{executable_path}, {arguments}"
        )
        return True

    def delete_scheduled_task(self, task_name):
        """删除指定名称的计划任务"""
        task_name = f"{self.IDENTIFIER}{task_name}"
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            root_folder = scheduler.GetFolder('\\')

            # 尝试直接删除根目录下的任务
            root_folder.DeleteTask(task_name, 0)
            logger.info(f"Delete {task_name}")
            return True
        except Exception as e:
            # 如果根目录下找不到，递归搜索所有子文件夹
            def search_and_delete(folder):
                try:
                    folder.DeleteTask(task_name, 0)
                    logger.info(f"Delete {task_name}")
                    return True
                except:
                    # 遍历子文件夹
                    for sub_folder in folder.GetFolders(0):
                        if search_and_delete(sub_folder):
                            return True
                    return False

            if search_and_delete(root_folder):
                return True
            else:
                logger.warning(f"Not found: {task_name}")
                return False

    def find_next_task(self):
        """查找带有特定标识的下一个即将执行的任务"""
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')

        tasks = []

        def collect_tasks(folder):
            for task in folder.GetTasks(0):
                if self.IDENTIFIER in task.Name:
                    try:
                        action = task.Definition.Actions[0]
                        tasks.append((
                            task.Name,
                            datetime.datetime(
                                task.NextRunTime.year,
                                task.NextRunTime.month,
                                task.NextRunTime.day,
                                task.NextRunTime.hour,
                                task.NextRunTime.minute,
                                task.NextRunTime.second
                            ),
                            action.Path,
                            action.Arguments
                        ))
                    except Exception as e:
                        logger.error(e)

            for sub_folder in folder.GetFolders(0):
                collect_tasks(sub_folder)

        collect_tasks(root_folder)

        if not tasks:
            return None
        # 按执行时间排序
        tasks.sort(key=lambda x: x[1])
        return tasks[0]

    def _format_schedule(self, start_time, schedule_type, schedule_days):
        """格式化输出任务执行时间"""
        if schedule_type == self.DAILY:
            return f"每日 - {start_time.strftime('%H:%M')}"
        elif schedule_type == self.WEEKLY:
            day_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            days_text = ", ".join([day_names[day - 1] for day in schedule_days])
            return f"每周 {days_text} - {start_time.strftime('%H:%M:%S')}"
        elif schedule_type == self.MONTHLY:
            days_text = ", ".join([str(day) for day in schedule_days])
            return f"每月 {days_text}日 - {start_time.strftime('%H:%M:%S')}"
        return "未知"
