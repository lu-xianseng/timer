#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/24 16:47
# @Author   :luye
import os
import time
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
    )
from src.public.public import task_name
from src.views.set_task_page import SetTaskPage
from src.views.view_task_page import ViewTaskPage
from src.views.about_page import AboutPage

class Logic:
    def __init__(self, stacked_widget):
        self.stacked_widget = stacked_widget
        self.set_task_page = SetTaskPage()
        self.about_page = AboutPage()
        self.view_task_page = ViewTaskPage()
        self.stacked_widget.addWidget(self.set_task_page)
        self.stacked_widget.addWidget(self.about_page)
        self.stacked_widget.addWidget(self.view_task_page)
        self.connect_signals()

    def connect_signals(self):
        ...