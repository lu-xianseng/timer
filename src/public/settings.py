#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/5/18 09:10
# @Author   :luye
import os

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print(ROOT_PATH)
LOG_PATH = os.path.join(ROOT_PATH, 'logs')
DB_PATH = os.path.join(ROOT_PATH, 'db')
RES_PATH = os.path.join(ROOT_PATH, 'resources')
for folder in [LOG_PATH, DB_PATH]:
    if not os.path.exists(folder):
        os.makedirs(folder)
PREFIXES = 'LORIENTIMER_'
WAIT_TIME = 20

WEEKDAY_MAPPING = {
    "周一": 1,
    "周二": 2,
    "周三": 3,
    "周四": 4,
    "周五": 5,
    "周六": 6,
    "周日": 7
}

WORLD_DICT = {
    '重启': 'reboot',
    '关机': 'shutdown',
    '每天': 'daily',
    '每月': 'monthly',
    '每周': 'weekly',
    '日': 'day',
}

LOOP_MAPPING = {
    '每天': 1,
    '每月': 3,
    '每周': 2,
}

ACTION_MAPPING = {
    'reboot': '重启',
    'shutdown': '关机',
}
