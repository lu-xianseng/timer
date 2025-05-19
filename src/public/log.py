#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/5/18 09:10
# @Author   :luye

import logging
import traceback
from src.public.settings import LOG_PATH


class Logger:
    def __init__(self):
        # 配置控制台日志处理器
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        self.console_handler.setFormatter(console_formatter)

        # 配置普通日志文件处理器
        self.info_handler = logging.FileHandler(rf'{LOG_PATH}\\log.log', encoding='utf-8')
        self.info_handler.setLevel(logging.DEBUG)
        info_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        self.info_handler.setFormatter(info_formatter)

        # 配置错误日志文件处理器
        self.error_handler = logging.FileHandler(rf'{LOG_PATH}\\error.log', encoding='utf-8')
        self.error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        self.error_handler.setFormatter(error_formatter)

        # 创建根日志器
        self.root_logger = logging.getLogger()
        self.root_logger.setLevel(logging.DEBUG)
        self.root_logger.addHandler(self.console_handler)
        self.root_logger.addHandler(self.info_handler)
        self.root_logger.addHandler(self.error_handler)

    def logger(self):
        return self.root_logger


logger = Logger()


def def_excepthook(type_, value, traceback_):
    # 记录异常信息到日志文件
    logger.error(
        "Uncaught exception", exc_info=(type_, value, traceback_))
    # 打印异常信息到控制台（可选）
    print("Uncaught exception:", type_, value)
    traceback.print_tb(traceback_)


logger = logger.logger()
