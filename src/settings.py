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
        
print(LOG_PATH)