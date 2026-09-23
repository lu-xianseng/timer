//! 数据库模块
//! 使用 SQLite 存储定时任务配置

use rusqlite::{Connection, Result};
use rusqlite::OptionalExtension;
use std::fs;
use std::path::PathBuf;

/// 获取数据库路径
pub fn get_db_path() -> PathBuf {
    let mut path = dirs::config_dir().unwrap_or_else(|| PathBuf::from("."));
    path.push("LorienTimer");
    path.push("db");
    fs::create_dir_all(&path).unwrap_or_else(|_| {});
    path.join("data.db")
}

/// 初始化数据库表
pub fn init_db() -> Result<()> {
    let db_path = get_db_path();
    let conn = Connection::open(&db_path)?;
    
    conn.execute(
        r#"CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            hour INTEGER NOT NULL,
            minute INTEGER NOT NULL,
            loop_type TEXT NOT NULL,
            day TEXT
        )"#,
        [],
    )?;
    

    log::info!("数据库初始化完成: {:?}", db_path);
    Ok(())
}

/// 插入任务
pub fn insert_task(action: &str, hour: i32, minute: i32, loop_type: &str, day: &str) -> Result<i64> {
    let db_path = get_db_path();
    let conn = Connection::open(&db_path)?;
    
    let mut stmt = conn.prepare(
        "INSERT INTO tasks (action, hour, minute, loop_type, day) VALUES (?1, ?2, ?3, ?4, ?5)"
    )?;
    
    let row_id = stmt.insert(rusqlite::params![action, hour, minute, loop_type, day])?;

    
    log::info!("插入任务成功, id={}", row_id);
    Ok(row_id)
}

/// 删除任务
pub fn delete_task(id: i64) -> Result<()> {
    let db_path = get_db_path();
    let conn = Connection::open(&db_path)?;
    
    conn.execute("DELETE FROM tasks WHERE id = ?1", [id])?;

    
    log::info!("删除任务成功, id={}", id);
    Ok(())
}

/// 获取所有任务
pub fn get_all_tasks() -> Result<Vec<(i64, String, i32, i32, String, String)>> {
    let db_path = get_db_path();
    let conn = Connection::open(&db_path)?;
    
    let mut stmt = conn.prepare(
        "SELECT id, action, hour, minute, loop_type, day FROM tasks"
    )?;
    
    let tasks = stmt.query_map([], |row| {
        Ok((
            row.get(0)?,
            row.get(1)?,
            row.get(2)?,
            row.get(3)?,
            row.get(4)?,
            row.get(5)?,
        ))
    })?;
    
    let tasks: Result<Vec<_>> = tasks.collect();

    
    tasks
}

/// 查询任务是否存在
pub fn query_tasks(action: &str, hour: i32, minute: i32, loop_type: &str, day: &str) -> Result<Vec<(i64, String, i32, i32, String, String)>> {
    let db_path = get_db_path();
    let conn = Connection::open(&db_path)?;
    
    let mut stmt = conn.prepare(
        "SELECT id, action, hour, minute, loop_type, day FROM tasks WHERE action = ?1 AND hour = ?2 AND minute = ?3 AND loop_type = ?4 AND day = ?5"
    )?;
    
    let tasks = stmt.query_map(rusqlite::params![action, hour, minute, loop_type, day], |row| {
        Ok((
            row.get(0)?,
            row.get(1)?,
            row.get(2)?,
            row.get(3)?,
            row.get(4)?,
            row.get(5)?,
        ))
    })?;
    
    let tasks: Result<Vec<_>> = tasks.collect();

    
    tasks
}

/// 获取任务详情
pub fn get_task_by_id(id: i64) -> Result<Option<(i64, String, i32, i32, String, String)>> {
    let db_path = get_db_path();
    let conn = Connection::open(&db_path)?;
    
    let mut stmt = conn.prepare(
        "SELECT id, action, hour, minute, loop_type, day FROM tasks WHERE id = ?1"
    )?;
    
    let task = stmt.query_row(rusqlite::params![id], |row| {
        Ok((
            row.get(0)?,
            row.get(1)?,
            row.get(2)?,
            row.get(3)?,
            row.get(4)?,
            row.get(5)?,
        ))
    }).optional()?;
    

    Ok(task)
}
