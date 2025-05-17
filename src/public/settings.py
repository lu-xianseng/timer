#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/25 09:10
# @Author   :luye
import os

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_PATH = os.path.join(ROOT_PATH, 'logs')
DB_PATH = os.path.join(ROOT_PATH, 'db')
RES_PATH = os.path.join(ROOT_PATH, 'resources')
PLUGIN = os.path.join(ROOT_PATH, 'plugin.exe')
for folder in [LOG_PATH, DB_PATH]:
    if not os.path.exists(folder):
        os.makedirs(folder)
PREFIXES = 'LORIENTIMER_'
KEY = 'TJhgy78uYH'
WAIT_TIME = 20

DAY_MAPPING = {
    1: "周一",
    2: "周二",
    3: "周三",
    4: "周四",
    5: "周五",
    6: "周六",
    7: "周日"
}
WEEKDAY_MAPPING = {
    1: "MON",
    2: "TUE",
    3: "WED",
    4: "THU",
    5: "FRI",
    6: "SAT",
    7: "SUN"
}
ACTION_ZH_MAPPING = {
    0: '关机',
    1: '重启',
}
ACTION_EN_MAPPING = {
    0: 'shutdown',
    1: 'reboot',
}

WORLD_DICT = {
    '重启': 'reboot',
    '关机': 'shutdown',
    '每天': 'daily',
    '每月': 'monthly',
    '每周': 'weekly',
    '日': 'day',
}
        