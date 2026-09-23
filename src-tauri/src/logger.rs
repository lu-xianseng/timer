//! 日志模块
//! 提供应用日志功能

use log::{info, LevelFilter};
use env_logger::Builder;
use std::fs::{self, OpenOptions};
use std::path::PathBuf;

/// 获取日志目录路径
pub fn get_log_dir() -> PathBuf {
    let mut path = dirs::config_dir().unwrap_or_else(|| PathBuf::from("."));
    path.push("LorienTimer");
    path
}

/// 日志文件超过该大小时滚动归档，避免无限增长
const MAX_LOG_SIZE: u64 = 512 * 1024;

/// 归档旧日志：app.log -> app.log.1（已存在的归档会被覆盖）
fn rotate_log(log_file: &PathBuf) {
    let archived = log_file.with_extension("log.1");
    let _ = fs::remove_file(&archived);
    let _ = fs::rename(log_file, archived);
}

/// 初始化日志系统
pub fn init_logger() {
    let log_dir = get_log_dir();
    fs::create_dir_all(&log_dir).unwrap_or_else(|_| {});
    
    let log_file = log_dir.join("app.log");

    // 超过上限先归档，再追加写入（保留历史，便于回溯定时任务触发记录）
    if let Ok(meta) = fs::metadata(&log_file) {
        if meta.len() > MAX_LOG_SIZE {
            rotate_log(&log_file);
        }
    }
    
    let mut builder = Builder::default();
    builder
        .format(|buf, record| {
            use std::io::Write;
            writeln!(buf, "{} - {} - {}", 
                chrono::Local::now().format("%Y-%m-%d %H:%M:%S"),
                record.level(),
                record.args()
            )
        })
        .filter_module("timer", LevelFilter::Debug)
        .filter_module("rusqlite", LevelFilter::Warn);
    
    if let Ok(f) = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&log_file)
    {
        builder.target(env_logger::Target::Pipe(Box::new(f)));
    }
    
    builder.init();
    
    info!("日志系统初始化完成");
}

#[cfg(test)]
mod tests {
    use super::get_log_dir;
    use std::path::PathBuf;

    /// 归档名必须为 app.log.1，而非 app.log.1 之外的意外结果
    #[test]
    fn archive_name_is_app_log_1() {
        let log_file = PathBuf::from("app.log");
        assert_eq!(
            log_file.with_extension("log.1").to_string_lossy(),
            "app.log.1"
        );

        // 带完整路径时同样只替换最后一段扩展名
        let full = get_log_dir().join("app.log");
        let archived = full.with_extension("log.1");
        assert!(archived.to_string_lossy().ends_with("LorienTimer\\app.log.1")
            || archived.to_string_lossy().ends_with("LorienTimer/app.log.1"));
        // 归档文件必须与原日志同目录
        assert_eq!(archived.parent(), full.parent());
    }
}
