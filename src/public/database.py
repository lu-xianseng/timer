#!/usr/bin/env python3
# coding=utf-8
# @Time     :2025/4/24 16:47
# @Author   :luye

import sqlite3
from functools import wraps
from src.public.settings import DB_PATH


class DatabaseManager:

    def __init__(self, db_name=rF'{DB_PATH}\\data.db'):
        self.db_name = db_name
        self.create_table()

    def create_table(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        sql = '''
              CREATE TABLE IF NOT EXISTS tasks
              (
                  id     INTEGER PRIMARY KEY AUTOINCREMENT,
                  action TEXT,
                  hour   INTEGER,
                  minute INTEGER,
                  loop   TEXT,
                  day    INTEGER
              )
              '''
        c.execute(sql)
        conn.commit()
        conn.close()

    def insert_task(self, action, hour, minute, loop, day):
        conn = sqlite3.connect(self.db_name)
        try:
            c = conn.cursor()
            c.execute("INSERT INTO tasks (action, hour, minute, loop, day) VALUES (?,?,?,?,?)",
                      (action, hour, minute, loop, day))
            conn.commit()
            return {"success": True, "row_id": c.lastrowid}  # 返回插入的行ID
        except sqlite3.Error as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                conn.close()

    def delete_task(self, task_id):
        conn = sqlite3.connect(self.db_name)
        try:
            c = conn.cursor()
            c.execute("DELETE FROM tasks WHERE id =?", (task_id,))
            conn.commit()
            return {"success": True, "info": None}  # 返回插入的行ID
        except sqlite3.Error as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                conn.close()

    def delete_tasks_by_action_and_day(self, action, day):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE action =? AND day =?", (action, day))
        conn.commit()
        conn.close()

    def get_all_tasks(self):
        conn = sqlite3.connect(self.db_name)
        try:
            c = conn.cursor()
            c.execute("SELECT id, action, hour, minute, loop, day FROM tasks")
            tasks = c.fetchall()
            conn.close()
            return {"success": True, "tasks": tasks}
        except sqlite3.Error as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                conn.close()

    def delete_all_tasks(self):
        conn = sqlite3.connect(self.db_name)
        try:
            c = conn.cursor()
            c.execute("DELETE FROM tasks")
            conn.commit()
            return {"success": True, 'info': None}  # 返回插入的行ID
        except sqlite3.Error as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                conn.close()

    def get_task_by_id(self, task_id):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = c.fetchone()
        conn.close()
        return task

    def query_tasks(self, action, hour, minute, loop, day):
        conn = sqlite3.connect(self.db_name)
        try:
            c = conn.cursor()
            c.execute("SELECT * FROM tasks WHERE action = ? AND hour = ? AND minute = ? AND loop = ? AND day = ?",
                      (action, hour, minute, loop, day))
            tasks = c.fetchall()
            return {"success": True, "tasks": tasks}
        except sqlite3.Error as e:
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                conn.close()
