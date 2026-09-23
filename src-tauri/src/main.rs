//! Lorien Timer - Tauri版
//! 适用于Windows系统的定时任务程序（关机和重启）

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod timer;
mod database;
mod logger;

use logger::init_logger;

fn main() {
    // 初始化日志
    init_logger();

    let confirm_action = timer::parse_action_arg();

    tauri::Builder::default()
        .setup(move |app| {
            // 初始化数据库
            database::init_db()?;

            if let Some(action) = confirm_action {
                // 确认弹窗模式：由计划任务在到点时拉起，进程只存在这一个窗口，
                // 用户点"取消"关闭窗口即整个进程退出（与原项目一致）
                let title = if action == "shutdown" { "定时关机" } else { "定时重启" };
                tauri::WebviewWindowBuilder::new(
                    app,
                    format!("confirm-{}", action),
                    tauri::WebviewUrl::App("index.html".into()),
                )
                .title(title)
                .inner_size(360.0, 240.0)
                .resizable(false)
                .decorations(false)
                .always_on_top(true)
                .skip_taskbar(true)
                .center()
                .build()
                .map_err(|e| format!("创建确认窗口失败: {}", e))?;
                log::info!("确认弹窗已创建, action={}", action);
            } else {
                // 正常模式：主窗口
                tauri::WebviewWindowBuilder::new(
                    app,
                    "main",
                    tauri::WebviewUrl::App("index.html".into()),
                )
                .title("Lorien Timer")
                .inner_size(600.0, 480.0)
                .resizable(false)
                .decorations(false)
                .center()
                .build()
                .map_err(|e| format!("创建主窗口失败: {}", e))?;
                log::info!("Lorien Timer 启动成功");
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            timer::add_task,
            timer::delete_task,
            timer::get_all_tasks,
            timer::exists_task,
            timer::next_task,
            timer::execute_action,
            timer::get_app_dir,
            timer::window_close,
            timer::get_confirm_action,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
