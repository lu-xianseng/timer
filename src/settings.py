#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/25 09:10
# @Author   :luye
import os

LOG_PATH = 'logs'
DB_PATH = 'db'
RES_PATH = 'resources'

for folder in [LOG_PATH, DB_PATH]:
    if not os.path.exists(folder):
        os.makedirs(folder)