# AGENTS.md

## 项目简介

远程输入粘贴板 — 用手机浏览器作为 Windows 电脑的远程文本输入面板。支持文字发送、按键控制、鼠标触控板、快捷指令、多端同步。

- **服务端口**: 3210
- **Python 包**: `py_remote_input`
- **入口**: `python -m py_remote_input`

---

## 开机自启动

本项目通过 Windows 计划任务（Task Scheduler）实现开机自启动，任务名为 **`Remote Input Board`**。

### 工作原理

1. 用户登录时，计划任务触发
2. 执行 `wscript.exe start-hidden.vbs`
3. VBS 以后台隐藏窗口方式启动 `dist\RemoteInputBoard\RemoteInputBoard.exe`
4. 工作目录为 `dist\`（日志和统计文件存于 `dist\logs\`）

### 计划任务配置

将以下路径替换为你的实际项目路径后执行：

```powershell
$projectDir = "D:\your-path\remote-input-board"   # ← 改成你的路径
$userName   = "$env:USERDOMAIN\$env:USERNAME"

$action = New-ScheduledTaskAction -Execute "wscript.exe" `
  -Argument "`"$projectDir\start-hidden.vbs`"" `
  -WorkingDirectory $projectDir

$trigger = New-ScheduledTaskTrigger -AtLogOn -User $userName

Register-ScheduledTask -TaskName "Remote Input Board" `
  -Action $action -Trigger $trigger `
  -Description "Start Remote Input Board in the interactive user session at logon, hidden"
```

---

## 修改代码后部署

### 一键部署

在项目根目录下执行：

```powershell
# 1. 停止旧服务
Get-Process -Name "RemoteInputBoard" -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. 清理旧构建
Remove-Item -Recurse -Force "dist\RemoteInputBoard" -ErrorAction SilentlyContinue

# 3. 构建 EXE
.\.venv\Scripts\activate.ps1
pyinstaller --clean -y RemoteInputBoard.spec

# 4. 启动服务
wscript.exe "start-hidden.vbs"

# 5. 验证
Start-Sleep 2
Get-Process -Name "RemoteInputBoard" -ErrorAction SilentlyContinue | Format-Table Id, ProcessName, StartTime
curl -s http://127.0.0.1:3210/
```

### 关键文件说明

| 文件 | 作用 |
|------|------|
| `py_remote_input/templates/index.html` | 前端页面（单文件） |
| `py_remote_input/server.py` | HTTP + WebSocket 服务入口 |
| `py_remote_input/web.py` | HTTP 路由 + WebSocket 消息处理 |
| `py_remote_input/typer.py` | 文字输入模拟 / 剪贴板粘贴（Ctrl+V） |
| `py_remote_input/settings_store.py` | 设置持久化（inputMethod 等） |
| `py_remote_input/snippets_store.py` | 快捷指令服务端存储 |
| `py_remote_input/stats.py` | 字数统计存储 |
| `RemoteInputBoard.spec` | PyInstaller 构建配置 |
| `start-hidden.vbs` | 后台启动脚本（VBS） |
| `dist/logs/` | 运行时日志和持久化数据 |
| `dist/logs/stats.json` | 累计字数备份（手机上报，内存缓存约 5 分钟落盘） |
| `dist/logs/snippets.json` | 快捷指令（兼容，当前存手机本地） |
| `dist/logs/settings.json` | 设置（兼容，当前存手机本地） |
| `dist/logs/history/YYYY-MM-DD/HH.log` | 输入历史，按天+小时分文件，一行一条 JSON |
| `dist/logs/server.log` | 服务日志 |

### 注意事项

- PyInstaller 使用 **onedir** 模式，构建产物在 `dist\RemoteInputBoard\`（含 `RemoteInputBoard.exe` 和 `_internal\`）
- `start-hidden.vbs` 的工作目录必须在 `dist\`，否则统计数据会写入错误位置
- 服务端口 3210 需确保 Windows 防火墙允许局域网访问
- 页面被前端强缓存时可能需要强制刷新（Ctrl+Shift+R）
