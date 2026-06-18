# Flow V2 — 多用户个人成长记录

记录人生状态的流动 — **Everything Flows**

## 安装

```bash
cd flow
D:\anaconda\envs\thesis\python.exe -m pip install -r requirements.txt
D:\anaconda\envs\thesis\python.exe init_db.py
```

## 本地运行（仅本机）

```bash
D:\anaconda\envs\thesis\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 外网 / 局域网访问

```bash
D:\anaconda\envs\thesis\python.exe run_public.py
```

启动后会打印本机与局域网地址，例如 `http://192.168.1.x:8000`。

### 外网部署检查清单

| 项目 | 说明 |
|------|------|
| **监听地址** | `run_public.py` 默认 `0.0.0.0`，允许外网连接 |
| **防火墙** | Windows 防火墙放行 `8000` 端口（或你设的 `FLOW_PORT`） |
| **路由器** | 公网访问需做端口映射：外网端口 → 本机 IP:8000 |
| **隧道（更简单）** | 可用 [ngrok](https://ngrok.com)：`ngrok http 8000` |
| **Session 密钥** | 外网必设：`set FLOW_SECRET_KEY=你的随机长字符串` |
| **HTTPS** | 配好 SSL 后设 `FLOW_HTTPS_ONLY=1` |
| **反向代理** | nginx / frp 后面设 `FLOW_BEHIND_PROXY=1` |

### 环境变量

```powershell
# PowerShell 示例
$env:FLOW_SECRET_KEY = "请换成随机字符串"
$env:FLOW_PORT = "8000"
$env:FLOW_HTTPS_ONLY = "0"
$env:FLOW_BEHIND_PROXY = "0"
D:\anaconda\envs\thesis\python.exe run_public.py
```

### 健康检查

`GET /health` → `{"status":"ok","service":"flow"}`

## 路由

| 路径 | 说明 |
|------|------|
| `/login` `/register` | 登录 / 注册 |
| `/` | 今日记录 |
| `/history` | 历史 |
| `/dashboard` | 图表 |

## 记录字段说明

- **心情 / 睡眠 / 运动 / 关键词 / 日记** — 核心记录项
- **今日数值（可选）** — 可填体重、步数、心率等，由你定义，不填也可以

## 安全

- 密码 bcrypt 哈希
- 多用户数据按 `user_id` 隔离
- 外网部署务必设置 `FLOW_SECRET_KEY`
