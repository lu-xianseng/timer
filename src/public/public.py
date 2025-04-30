#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/25 09:10
# @Author   :luye
import subprocess
import locale
from src.public.log import logger
default_encoding = locale.getdefaultlocale()[1]
from src.public.settings import PREFIXES

def task_name(action, _date):
    return f"{PREFIXES}{action}_Task_{_date}"



def run_cmd(command, text=True):
    try:
        result = subprocess.run(command, shell=True, check=True, text=text, capture_output=True, encoding=default_encoding)
        return result.returncode, result.stdout
    except subprocess.CalledProcessError as e:
        logger.warning(e)
        logger.warning(e.stderr)
    