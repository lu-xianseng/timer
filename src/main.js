// Lorien Timer - 前端逻辑
// 使用 Tauri v2 API 与 Rust 后端通信

// Tauri 2 全局注入 API（tauri.conf.json 中 withGlobalTauri: true）
const { invoke } = window.__TAURI__.core;
const { getCurrentWindow } = window.__TAURI__.window;

// 窗口容器
const mainWindowEl = document.getElementById('mainWindow');
const confirmWindowEl = document.getElementById('confirmWindow');

// ==================== 无边框窗口控制 ====================
const appWindow = getCurrentWindow();

// 按住深蓝标题栏空白处拖动窗口（按钮与页面内对话框除外）
document.querySelectorAll('.titlebar').forEach((bar) => {
    if (bar.classList.contains('dialog-titlebar')) return;
    bar.addEventListener('mousedown', (e) => {
        if (e.button !== 0 || e.target.closest('button')) return;
        appWindow.startDragging();
    });
});

function bindTitlebarButtons(prefix) {
    const min = document.getElementById(prefix + 'Min');
    const close = document.getElementById(prefix + 'Close');
    if (min) min.addEventListener('click', () => appWindow.minimize());
    if (close) close.addEventListener('click', () => appWindow.close());
}
bindTitlebarButtons('tb');        // 主窗口（tbMin / tbClose）
bindTitlebarButtons('confirm');   // 确认弹窗（confirmMin / confirmClose）

// ==================== 自定义对话框（替代 alert/confirm） ====================
const dialogMask = document.getElementById('dialogMask');
const dialogTitle = document.getElementById('dialogTitle');
const dialogBody = document.getElementById('dialogBody');
const dialogOk = document.getElementById('dialogOk');
const dialogCancel = document.getElementById('dialogCancel');

function showDialog(title, message, withCancel) {
    return new Promise((resolve) => {
        dialogTitle.textContent = title;
        dialogBody.textContent = message;
        dialogCancel.style.display = withCancel ? 'inline-block' : 'none';
        dialogMask.style.display = 'flex';

        const finish = (val) => {
            dialogMask.style.display = 'none';
            dialogOk.removeEventListener('click', onOk);
            dialogCancel.removeEventListener('click', onCancel);
            resolve(val);
        };
        const onOk = () => finish(true);
        const onCancel = () => finish(false);
        dialogOk.addEventListener('click', onOk);
        dialogCancel.addEventListener('click', onCancel);
    });
}

const uiAlert = (msg, title = '提示') => showDialog(title, msg, false).then(() => {});
const uiConfirm = (msg, title = '确认') => showDialog(title, msg, true);

// DOM 元素
const timeEdit = document.getElementById('timeEdit');
const actionCombo = document.getElementById('actionCombo');
const loopCombo = document.getElementById('loopCombo');
const dayRow = document.getElementById('dayRow');
const dayLabel = document.getElementById('dayLabel');
const daySelection = document.getElementById('daySelection');
const addButton = document.getElementById('addButton');
const taskTableBody = document.getElementById('taskTableBody');
const clearAllButton = document.getElementById('clearAllButton');
const countdownLabel = document.getElementById('countdownLabel');

// 标签页切换
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');

tabButtons.forEach((button, index) => {
    button.addEventListener('click', () => {
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabContents.forEach(content => content.style.display = 'none');
        
        button.classList.add('active');
        tabContents[index].style.display = 'block';
        
        // 切换到查看任务标签时刷新列表
        if (index === 1) {
            refreshTaskTable();
        }
    });
});

// 循环类型变化时显示/隐藏日期选择
loopCombo.addEventListener('change', function() {
    hideDaySelection();
    
    const index = parseInt(this.value);
    if (index === 1) { // 每天：无需选择日期（对齐原项目）
        return;
    } else if (index === 2) { // 每周
        showDaySelection(['周一', '周二', '周三', '周四', '周五', '周六', '周日'], 2);
    } else if (index === 3) { // 每月
        showDaySelection(Array.from({length: 31}, (_, i) => (i+1) + ' 日'), 3);
    }
});

function showDaySelection(options, type) {
    dayRow.style.display = 'flex';
    daySelection.innerHTML = '';
    
    dayLabel.textContent = type === 2 ? '星期:' : '日期:';
    options.forEach(optText => {
        const option = document.createElement('option');
        option.value = optText;
        option.textContent = optText;
        daySelection.appendChild(option);
    });
    daySelection.style.display = 'block';
}

function hideDaySelection() {
    dayRow.style.display = 'none';
    daySelection.style.display = 'none';
    daySelection.innerHTML = '';
}

// 添加任务
addButton.addEventListener('click', async function() {
    const timeValue = timeEdit.value;
    if (!timeValue) {
        uiAlert('请选择时间');
        return;
    }
    
    const parts = timeValue.split(':');
    const hour = parseInt(parts[0]);
    const minute = parseInt(parts[1]);
    const action = actionCombo.value;
    const loopType = loopCombo.value;
    const day = daySelection.value || '';
    
    try {
        // 检查是否已存在相同任务
        const exists = await invoke('exists_task', { hour, minute, action, loopType, day });
        if (exists) {
            uiAlert('该任务已存在', '无法添加');
            return;
        }
        
        const result = await invoke('add_task', { hour, minute, action, loopType, day });
        uiAlert('任务添加成功');
        refreshTaskTable();
    } catch (e) {
        uiAlert('添加任务失败: ' + e, '出错了');
    }
});

// 刷新任务表格
async function refreshTaskTable() {
    try {
        const result = await invoke('get_all_tasks');
        const tasks = result.tasks || [];
        
        taskTableBody.innerHTML = '';
        
        tasks.forEach(task => {
            const row = document.createElement('tr');
            
            // 动作
            const actionText = task.action === 'shutdown' ? '关机' : '重启';
            row.innerHTML += '<td>' + actionText + '</td>';
            
            // 时间
            const h = String(task.hour).padStart(2, '0');
            const m = String(task.minute).padStart(2, '0');
            row.innerHTML += '<td>' + h + ':' + m + '</td>';
            
            // 循环类型
            let loopText = '每天';
            if (task.loop_type === '2') loopText = '每周';
            else if (task.loop_type === '3') loopText = '每月';
            row.innerHTML += '<td>' + loopText + '</td>';
            
            // 日期
            row.innerHTML += '<td>' + (task.day || '-') + '</td>';
            
            // 删除按钮
            row.innerHTML += '<td><button class="btn btn-danger btn-small delete-btn" data-id="' + task.id + '">删除</button></td>';
            
            taskTableBody.appendChild(row);
        });
        
        // 绑定删除按钮事件
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', async function() {
                const taskId = parseInt(this.dataset.id);
                try {
                    await invoke('delete_task', { taskId });
                    refreshTaskTable();
                } catch (e) {
                    uiAlert('删除失败: ' + e, '出错了');
                }
            });
        });
    } catch (e) {
        console.error('获取任务列表失败:', e);
    }
}

// 清空全部任务
clearAllButton.addEventListener('click', async function() {
    const ok = await uiConfirm('确定要清空所有任务吗？', '清空确认');
    if (!ok) return;
    
    try {
        const result = await invoke('get_all_tasks');
        const tasks = result.tasks || [];
        
        if (tasks.length === 0) return;
        
        for (const task of tasks) {
            await invoke('delete_task', { taskId: task.id });
        }
        
        refreshTaskTable();
    } catch (e) {
        uiAlert('清空失败: ' + e, '出错了');
    }
});

// 更新倒计时
async function updateCountdown() {
    try {
        const result = await invoke('next_task');
        if (result.success) {
            countdownLabel.textContent = result.text || '00:00:00';
            countdownLabel.style.color = '#f70707';
        } else {
            countdownLabel.textContent = result.text || '暂无任务';
            countdownLabel.style.color = '#999';
        }
    } catch (e) {
        console.error('更新倒计时失败:', e);
    }
}

// ==================== 启动模式判断 ====================
// 计划任务到点会以 "--action shutdown|reboot" 拉起本程序，
// 此时窗口显示 10 秒倒计时确认框，可取消或立即执行（对齐原项目行为）

async function startConfirmMode(action) {
    const text = action === 'shutdown' ? '关机' : '重启';
    mainWindowEl.style.display = 'none';
    confirmWindowEl.style.display = 'flex';

    const popupCountdown = document.getElementById('popupCountdown');
    const popupActionText = document.getElementById('popupActionText');
    const btnExecute = document.getElementById('popupExecute');
    const btnCancel = document.getElementById('popupCancel');
    btnExecute.textContent = '立即' + text;
    btnCancel.textContent = '取消' + text;
    popupActionText.textContent = text;

    let remaining = 60;
    const render = () => {
        popupCountdown.textContent = remaining;
    };
    render();

    const tick = setInterval(async () => {
        remaining -= 1;
        if (remaining < 1) {
            clearInterval(tick);
            try { await invoke('execute_action', { action }); } catch (e) { /* 关机/重启已开始，无需处理 */ }
            return;
        }
        render();
    }, 1000);

    btnCancel.addEventListener('click', async () => {
        clearInterval(tick);
        await invoke('window_close');
    });
    btnExecute.addEventListener('click', async () => {
        clearInterval(tick);
        await invoke('execute_action', { action });
    });
}

async function start() {
    try {
        const action = await invoke('get_confirm_action');
        if (action) {
            await startConfirmMode(action);
            return;
        }
    } catch (e) {
        console.error('查询启动模式失败:', e);
    }

    // 主窗口模式
    initMainWindow();
}

// 初始化（主窗口模式）
function initMainWindow() {
    mainWindowEl.style.display = 'flex';
    // 默认时间 = 当前时间 +1 小时（对齐原项目）
    const d = new Date(Date.now() + 3600 * 1000);
    timeEdit.value = String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
    refreshTaskTable();
    setInterval(updateCountdown, 1000);
    updateCountdown();
    console.log('Lorien Timer 前端初始化完成');
}

start();
