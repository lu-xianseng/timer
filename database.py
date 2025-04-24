#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/24 16:47
# @Author   :luye

import sqlite3


class DatabaseManager:
    def __init__(self, db_name='data.db'):
        self.db_name = db_name
        self.create_table()

    def create_table(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tasks
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      action TEXT,
                      hour INTEGER,
                      minute INTEGER,
                      day INTEGER)''')
        conn.commit()
        conn.close()

    def insert_task(self, action, hour, minute, day):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("INSERT INTO tasks (action, hour, minute, day) VALUES (?,?,?,?)",
                  (action, hour, minute, day))
        conn.commit()
        conn.close()

    def delete_task(self, task_id):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id =?", (task_id,))
        conn.commit()
        conn.close()

    def delete_tasks_by_action_and_day(self, action, day):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE action =? AND day =?", (action, day))
        conn.commit()
        conn.close()

    def get_all_tasks(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT id, action, hour, minute, day FROM tasks")
        tasks = c.fetchall()
        conn.close()
        return tasks

    def delete_all_tasks(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM tasks")
        conn.commit()
        conn.close()
