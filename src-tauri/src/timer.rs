//! 定时任务模块
//! 提供关机/重启任务的创建、删除、查询功能
//! 使用 Windows Task Scheduler (schtasks命令行) 实现系统级定时任务

use crate::database;

/// 创建子进程时不弹出控制台窗口，避免 GUI 程序调用 schtasks/shutdown 时黑窗闪烁
#[cfg(windows)]
const CREATE_NO_WINDOW: u32 = 0x0800_0000;
#[cfg(windows)]
use std::os::windows::process::CommandExt;
#[cfg(windows)]
use std::os::windows::ffi::OsStringExt;

/// 构造一个不会弹出控制台窗口的 Command（GUI 程序调用控制台程序时使用）
fn silent_command(program: &str) -> std::process::Command {
    let mut cmd = std::process::Command::new(program);
    #[cfg(windows)]
    cmd.creation_flags(CREATE_NO_WINDOW);
    cmd
}

/// 按 Windows 控制台 OEM 代码页解码子进程输出
///
/// schtasks / shutdown 输出的是控制台代码页（中文系统为 936/GBK），
/// 直接按 UTF-8 解码会得到乱码。这里用 CP_OEMCP 让系统自行解析当前代码页，
/// 解码失败时回退到 UTF-8 lossy，保证不会因编码问题中断流程。
#[cfg(windows)]
fn decode_console_output(bytes: &[u8]) -> String {
    const CP_OEMCP: u32 = 1;
    const MB_ERR_INVALID_CHARS: u32 = 0x0000_0008;

    #[link(name = "kernel32")]
    extern "system" {
        fn MultiByteToWideChar(
            code_page: u32,
            flags: u32,
            multi_byte_str: *const u8,
            len_multi_byte: i32,
            wide_char_str: *mut u16,
            cch_wide_char: i32,
        ) -> i32;
    }

    if bytes.is_empty() {
        return String::new();
    }

    let decoded = unsafe {
        // 第一次调用仅取所需缓冲区长度
        let len = MultiByteToWideChar(
            CP_OEMCP,
            MB_ERR_INVALID_CHARS,
            bytes.as_ptr(),
            bytes.len() as i32,
            std::ptr::null_mut(),
            0,
        );
        if len <= 0 {
            return String::from_utf8_lossy(bytes).trim().to_string();
        }
        let mut buf: Vec<u16> = vec![0; len as usize];
        let written = MultiByteToWideChar(
            CP_OEMCP,
            MB_ERR_INVALID_CHARS,
            bytes.as_ptr(),
            bytes.len() as i32,
            buf.as_mut_ptr(),
            len,
        );
        if written <= 0 {
            return String::from_utf8_lossy(bytes).trim().to_string();
        }
        buf.truncate(written as usize);
        std::ffi::OsString::from_wide(&buf)
            .to_string_lossy()
            .trim()
            .to_string()
    };
    decoded
}

#[cfg(not(windows))]
fn decode_console_output(bytes: &[u8]) -> String {
    String::from_utf8_lossy(bytes).trim().to_string()
}

// 动作映射
pub const ACTION_MAPPING: &[(&str, &str)] = &[
    ("reboot", "重启"),
    ("shutdown", "关机"),
];

/// 计算任务的下一次执行时间（本地时间 epoch 秒）
/// loop_type: "1"=每天 "2"=每周(day=星期一..星期日) "3"=每月(day=N日，小月自动钳制到月末)
pub fn next_execute_epoch(loop_type: &str, day: &str, hour: i32, minute: i32) -> Option<i64> {
    use chrono::{Datelike, Local, NaiveDate, TimeZone};

    let now = Local::now();
    let at = |d: NaiveDate| -> Option<chrono::DateTime<Local>> {
        Local
            .from_local_datetime(&d.and_hms_opt(hour as u32, minute as u32, 0)?)
            .single()
    };

    let target: NaiveDate = match loop_type {
        "2" => {
            let wd = match day {
                "周一" | "星期一" => chrono::Weekday::Mon,
                "周二" | "星期二" => chrono::Weekday::Tue,
                "周三" | "星期三" => chrono::Weekday::Wed,
                "周四" | "星期四" => chrono::Weekday::Thu,
                "周五" | "星期五" => chrono::Weekday::Fri,
                "周六" | "星期六" => chrono::Weekday::Sat,
                "周日" | "星期日" | "星期天" => chrono::Weekday::Sun,
                _ => return None,
            };
            let mut date = now.date_naive();
            let mut found = None;
            for _ in 0..8 {
                if date.weekday() == wd {
                    if let Some(t) = at(date) {
                        if t > now {
                            found = Some(date);
                            break;
                        }
                    }
                }
                date = date.succ_opt()?;
            }
            found?
        }
        "3" => {
            let dom: u32 = day.trim().trim_end_matches(['日', ' ']).trim().parse().ok()?;
            let (mut y, mut m) = (now.year(), now.month());
            let mut found = None;
            for _ in 0..25 {
                let eff = dom.min(days_in_month(y, m));
                if let Some(d) = NaiveDate::from_ymd_opt(y, m, eff) {
                    if let Some(t) = at(d) {
                        if t > now {
                            found = Some(d);
                            break;
                        }
                    }
                }
                if m == 12 {
                    y += 1;
                    m = 1;
                } else {
                    m += 1;
                }
            }
            found?
        }
        _ => {
            let date = now.date_naive();
            if let Some(t) = at(date) {
                if t > now {
                    date
                } else {
                    date.succ_opt()?
                }
            } else {
                date.succ_opt()?
            }
        }
    };

    at(target).filter(|t| *t > now).map(|t| t.timestamp())
}

fn days_in_month(y: i32, m: u32) -> u32 {
    match m {
        1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
        4 | 6 | 9 | 11 => 30,
        2 => {
            if (y % 4 == 0 && y % 100 != 0) || y % 400 == 0 {
                29
            } else {
                28
            }
        }
        _ => 30,
    }
}

/// 计划任务名后缀：区分不同循环/日期，避免同名任务互相覆盖
fn task_code(loop_type: &str, day: &str) -> String {
    match loop_type {
        "1" => "D0".to_string(),
        "2" => {
            let idx = match day {
                "周一" | "星期一" => 1,
                "周二" | "星期二" => 2,
                "周三" | "星期三" => 3,
                "周四" | "星期四" => 4,
                "周五" | "星期五" => 5,
                "周六" | "星期六" => 6,
                "周日" | "星期日" | "星期天" => 7,
                _ => 0,
            };
            format!("W{}", idx)
        }
        "3" => {
            let dom: u32 = day.trim().trim_end_matches(['日', ' ']).trim().parse().unwrap_or(0);
            format!("M{:02}", dom)
        }
        _ => "X0".to_string(),
    }
}

fn make_task_name(action: &str, hour: i32, minute: i32, loop_type: &str, day: &str) -> String {
    format!(
        "LORIENTIMER-{}-{:02}{:02}-{}",
        action,
        hour,
        minute,
        task_code(loop_type, day)
    )
}

/// 添加定时任务
/// 在Windows任务计划程序中创建任务，并在数据库中记录
#[tauri::command]
pub fn add_task(
    hour: i32,
    minute: i32,
    action: String,
    loop_type: String,
    day: String,
) -> Result<serde_json::Value, String> {
    log::info!("添加任务: {}:{} {} {} {}", hour, minute, action, loop_type, day);

    // 验证输入
    if hour < 0 || hour > 23 {
        return Err("小时必须在0-23之间".to_string());
    }
    if minute < 0 || minute > 59 {
        return Err("分钟必须在0-59之间".to_string());
    }

    // 创建Windows任务计划任务
    let task_name = make_task_name(&action, hour, minute, &loop_type, &day);

    // 尝试创建Windows计划任务（如果失败也不影响应用运行）
    let win_result = create_windows_task(&task_name, hour, minute, &loop_type, &day, &action);
    if let Err(e) = win_result {
        log::warn!("创建Windows任务计划任务失败: {}", e);
        // 不返回错误，继续保存到数据库
    }

    // 保存到数据库
    match database::insert_task(&action, hour, minute, &loop_type, &day) {
        Ok(row_id) => {
            log::info!("任务保存成功, id={}", row_id);
            Ok(serde_json::json!({
                "success": true,
                "row_id": row_id,
                "task_name": task_name
            }))
        }
        Err(e) => {
            log::error!("保存任务失败: {}", e);
            Err(format!("保存任务失败: {}", e))
        }
    }
}

/// 删除定时任务
#[tauri::command]
pub fn delete_task(task_id: i64) -> Result<bool, String> {
    log::info!("删除任务, id={}", task_id);

    // 获取任务信息以删除Windows计划任务
    let task_opt = database::get_task_by_id(task_id);

    match task_opt {
        Ok(Some((_, action, hour, minute, loop_type, day))) => {
            let task_name = make_task_name(&action, hour, minute, &loop_type, &day);
            // 兼容旧版本命名（不含循环后缀）的残留任务
            let legacy_name = format!("LORIENTIMER-{}-{}-{}", action, hour, minute);
            // 主任务删除失败是真实故障（计划任务仍会触发），保留日志；
            // 旧命名清理通常本就不存在，失败属预期，静默处理避免刷屏
            let _ = delete_windows_task(&task_name, false);
            if legacy_name != task_name {
                let _ = delete_windows_task(&legacy_name, true);
            }

            // 从数据库删除
            match database::delete_task(task_id) {
                Ok(()) => Ok(true),
                Err(e) => Err(format!("数据库删除失败: {}", e)),
            }
        }
        Ok(None) => Err("任务不存在".to_string()),
        Err(e) => Err(format!("查询任务失败: {}", e)),
    }
}

/// 获取所有任务
#[tauri::command]
pub fn get_all_tasks() -> Result<serde_json::Value, String> {
    match database::get_all_tasks() {
        Ok(tasks) => {
            let tasks_json: Vec<serde_json::Value> = tasks.iter().map(|t| {
                serde_json::json!({
                    "id": t.0,
                    "action": t.1,
                    "hour": t.2,
                    "minute": t.3,
                    "loop_type": t.4,
                    "day": t.5,
                })
            }).collect();

            Ok(serde_json::json!({
                "success": true,
                "tasks": tasks_json
            }))
        }
        Err(e) => Err(format!("查询失败: {}", e)),
    }
}

/// 检查任务是否存在
#[tauri::command]
pub fn exists_task(
    hour: i32,
    minute: i32,
    action: String,
    loop_type: String,
    day: String,
) -> Result<bool, String> {
    match database::query_tasks(&action, hour, minute, &loop_type, &day) {
        Ok(tasks) => Ok(!tasks.is_empty()),
        Err(e) => Err(format!("查询失败: {}", e)),
    }
}

/// 获取下一个任务及倒计时（遍历所有任务，取最早执行的一个）
#[tauri::command]
pub fn next_task() -> Result<serde_json::Value, String> {
    use std::time::{SystemTime, UNIX_EPOCH};

    let tasks_result = database::get_all_tasks();

    match tasks_result {
        Ok(tasks) => {
            if tasks.is_empty() {
                return Ok(serde_json::json!({
                    "success": false,
                    "text": "未设置定时任务"
                }));
            }

            let now_secs = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .map(|d| d.as_secs() as i64)
                .unwrap_or(0);

            // 找到执行时间最近的一个任务
            let mut best: Option<(i64, &String)> = None;
            for t in &tasks {
                if let Some(next) = next_execute_epoch(&t.4, &t.5, t.2, t.3) {
                    if next > now_secs {
                        let is_better = match &best {
                            Some((b, _)) => next < *b,
                            None => true,
                        };
                        if is_better {
                            best = Some((next, &t.1));
                        }
                    }
                }
            }

            let (next_epoch, action) = match best {
                Some(v) => v,
                None => {
                    return Ok(serde_json::json!({
                        "success": false,
                        "text": "未设置定时任务"
                    }));
                }
            };

            let delta = next_epoch - now_secs;
            let days = (delta / 86400) as i32;
            let remaining = delta % 86400;
            let hours = remaining / 3600;
            let minutes = (remaining % 3600) / 60;
            let secs = remaining % 60;

            // 构建时间文本
            let mut time_parts = Vec::new();
            if days > 0 {
                time_parts.push(format!("{}天", days));
            }
            if hours > 0 {
                time_parts.push(format!("{}小时", hours));
            }
            if minutes > 0 {
                time_parts.push(format!("{}分钟", minutes));
            }
            if secs > 0 || time_parts.is_empty() {
                time_parts.push(format!("{}秒", secs));
            }

            let action_text = ACTION_MAPPING.iter()
                .find(|(k, _)| *k == action.as_str())
                .map(|(_, v)| *v)
                .unwrap_or(action.as_str());

            let text = format!("{} 后{}", time_parts.join(""), action_text);

            Ok(serde_json::json!({
                "success": true,
                "text": text
            }))
        }
        Err(e) => Err(format!("查询失败: {}", e)),
    }
}

/// 执行动作（关机/重启）
#[tauri::command]
pub fn execute_action(action: String) -> Result<(), String> {
    log::info!("执行动作: {}", action);

    let flag = match action.as_str() {
        "shutdown" => "/s",
        "reboot" => "/r",
        _ => return Err(format!("未知动作: {}", action)),
    };

    // 使用系统 shutdown 命令（自带关机/重启权限处理）
    let output = silent_command("shutdown")
        .args(&[flag, "/f", "/t", "0"])
        .output()
        .map_err(|e| format!("执行关机命令失败: {}", e))?;

    if output.status.success() {
        Ok(())
    } else {
        let err = decode_console_output(&output.stderr);
        Err(format!("关机命令返回错误: {}", err))
    }
}

/// 关闭窗口（确认弹窗的"取消"按钮使用）
#[tauri::command]
pub fn window_close(window: tauri::WebviewWindow) -> Result<(), String> {
    log::info!("关闭确认窗口: {}", window.label());
    window.close().map_err(|e| e.to_string())
}

/// 解析命令行，判断是否由计划任务以确认弹窗模式拉起
/// 形如：timer-tauri.exe --action shutdown|reboot
pub fn parse_action_arg() -> Option<&'static str> {
    let args: Vec<String> = std::env::args().collect();
    for i in 0..args.len().saturating_sub(1) {
        if args[i] == "--action" {
            return match args[i + 1].as_str() {
                "shutdown" => Some("shutdown"),
                "reboot" => Some("reboot"),
                _ => None,
            };
        }
    }
    None
}

/// 前端查询当前确认动作（无则为主窗口模式）
#[tauri::command]
pub fn get_confirm_action() -> Option<&'static str> {
    parse_action_arg()
}

/// 获取应用目录
#[tauri::command]
pub fn get_app_dir() -> Result<String, String> {
    let app_dir = dirs::config_dir()
        .map(|p| p.join("LorienTimer").to_string_lossy().to_string())
        .unwrap_or_default();
    Ok(app_dir)
}

// ==================== Windows Task Scheduler 操作 ====================

/// 创建Windows计划任务
fn create_windows_task(
    task_name: &str,
    hour: i32,
    minute: i32,
    loop_type: &str,
    day: &str,
    action: &str,
) -> Result<(), String> {
    // 计划任务触发时拉起本应用并进入确认模式（弹窗倒计时，可取消），
    // 与原项目行为一致：不直接执行 shutdown，给用户 10 秒反悔机会
    let exe_path = std::env::current_exe()
        .map_err(|e| format!("获取程序路径失败: {}", e))?
        .to_string_lossy()
        .to_string();
    if action != "shutdown" && action != "reboot" {
        return Err(format!("未知动作: {}", action));
    }
    let cmd = format!("\"{}\" --action {}", exe_path, action);

    let sc_type = match loop_type {
        "1" => "DAILY",
        "2" => "WEEKLY",
        "3" => "MONTHLY",
        _ => "DAILY",
    };

    let time_str = format!("{:02}:{:02}:00", hour, minute);

    // 每周/每月必须带上日期参数，否则 schtasks 会创建失败
    let mut args: Vec<String> = vec![
        "/create".to_string(),
        "/tn".to_string(), task_name.to_string(),
        "/tr".to_string(), cmd,
        "/sc".to_string(), sc_type.to_string(),
        "/st".to_string(), time_str,
    ];
    match loop_type {
        "2" => {
            let d = match day {
                "周一" | "星期一" => "MON",
                "周二" | "星期二" => "TUE",
                "周三" | "星期三" => "WED",
                "周四" | "星期四" => "THU",
                "周五" | "星期五" => "FRI",
                "周六" | "星期六" => "SAT",
                "周日" | "星期日" | "星期天" => "SUN",
                _ => return Err(format!("未知的星期: {}", day)),
            };
            args.push("/d".to_string());
            args.push(d.to_string());
        }
        "3" => {
            let dom: u32 = day
                .trim()
                .trim_end_matches(['日', ' '])
                .trim()
                .parse()
                .map_err(|_| format!("未知的日期: {}", day))?;
            args.push("/d".to_string());
            args.push(dom.to_string());
        }
        _ => {}
    }
    args.push("/f".to_string());

    let arg_refs: Vec<&str> = args.iter().map(|s| s.as_str()).collect();
    let output = silent_command("schtasks").args(&arg_refs).output();

    match output {
        Ok(out) => {
            if out.status.success() {
                log::info!("Windows计划任务创建成功: {}", task_name);
                Ok(())
            } else {
                let err = decode_console_output(&out.stderr);
                log::warn!("schtasks创建失败: {}", err);
                Err(format!("schtasks创建失败: {}", err))
            }
        }
        Err(e) => {
            log::warn!("执行schtasks失败: {}", e);
            Err(format!("执行schtasks失败: {}", e))
        }
    }
}

/// 删除Windows计划任务
///
/// `quiet` 为 true 时不写任何日志，用于清理旧版本命名的残留任务：
/// 这类任务通常本就不存在，schtasks 必然返回"找不到文件"，属于预期情况而非故障。
fn delete_windows_task(task_name: &str, quiet: bool) -> Result<(), String> {
    let output = silent_command("schtasks")
        .args(&[
            "/delete",
            "/tn", task_name,
            "/f",
        ])
        .output();

    match output {
        Ok(out) => {
            if out.status.success() {
                if !quiet {
                    log::info!("Windows计划任务删除成功: {}", task_name);
                }
                Ok(())
            } else {
                let err = decode_console_output(&out.stderr);
                if !quiet {
                    log::warn!("schtasks删除失败: {}", err);
                }
                Err(format!("schtasks删除失败: {}", err))
            }
        }
        Err(e) => {
            if !quiet {
                log::warn!("执行schtasks删除失败: {}", e);
            }
            Err(format!("执行schtasks删除失败: {}", e))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::decode_console_output;

    /// 用户日志中实际出现的 schtasks 错误输出（GBK/OEM 936 字节）
    /// 原文为「错误: 系统找不到指定的文件。」，按 UTF-8 解码会得到乱码
    #[cfg(windows)]
    const SCHTASKS_GBK_BYTES: &[u8] = &[
        0xB4, 0xED, 0xCE, 0xF3, 0x3A, 0x20, 0xCF, 0xB5, 0xCD, 0xB3, 0xD5, 0xD2,
        0xB2, 0xBB, 0xB5, 0xBD, 0xD6, 0xB8, 0xB6, 0xA8, 0xB5, 0xC4, 0xCE, 0xC4,
        0xBC, 0xFE, 0xA1, 0xA3,
    ];

    /// 确认系统 OEM 代码页为 936（GBK），否则该测试用例的期望值不成立
    #[cfg(windows)]
    #[test]
    fn oem_codepage_is_gbk() {
        #[link(name = "kernel32")]
        extern "system" {
            fn GetOEMCP() -> u32;
        }
        let cp = unsafe { GetOEMCP() };
        assert_eq!(cp, 936, "当前系统 OEM 代码页为 {}，非 GBK 环境", cp);
    }

    #[cfg(windows)]
    #[test]
    fn decodes_gbk_schtasks_error() {
        let decoded = decode_console_output(SCHTASKS_GBK_BYTES);
        assert_eq!(decoded, "错误: 系统找不到指定的文件。");
        // 不应再出现 UTF-8 lossy 的替换字符
        assert!(!decoded.contains('\u{FFFD}'));
    }

    #[test]
    fn decodes_empty_and_ascii() {
        assert_eq!(decode_console_output(b""), "");
        assert_eq!(decode_console_output(b"OK 123"), "OK 123");
    }
}
