# CyberAgent - AI 驱动的自动化渗透测试 Agent

基于 **Ollama + Qwen2.5** 本地大模型的 ReAct 模式自动化渗透测试 Agent，能够自主进行多轮安全推理并调用安全测试工具，完成从资产发现到漏洞验证的完整渗透测试流程。

> 目标靶场：DVWA (Damn Vulnerable Web Application)

## 架构概览

```
┌──────────────────────────────────────────────────┐
│                 agent_core.py                     │
│  ┌─────────────────────────────────────────────┐ │
│  │  SYSTEM_PROMPT (渗透测试角色定义 + 工具说明) │ │
│  └─────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────┐ │
│  │  ReAct 主循环 (max 6 步)                    │ │
│  │   1. ask_local_llm() → Ollama qwen2.5:14b   │ │
│  │   2. 解析 Action / Action Input              │ │
│  │   3. 执行安全测试工具                         │ │
│  │   4. 将 Observation 反馈给 LLM               │ │
│  │   5. 检测 Final Answer 终止信号              │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────┐
│                 tools.py                          │
│  ├── scan_target_ports()     端口扫描             │
│  ├── check_target_web()      Web 指纹探测        │
│  ├── login_target_web()      CSRF Token 突破登录 │
│  └── check_sql_injection()   SQL 注入漏洞嗅探    │
└──────────────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────┐
│  Ollama (localhost:11434) + qwen2.5:14b          │
│  DVWA 靶场 (localhost:8080)                      │
└──────────────────────────────────────────────────┘
```

## 攻击链路

```
端口扫描 → Web 资产发现 → CSRF Token 突破登录 → 安全等级降级 → SQL 注入验证
```

## 技术栈

| 层级 | 技术 |
|------|------|
| LLM 引擎 | Ollama + qwen2.5:14b |
| Agent 框架 | ReAct (Reasoning + Acting) |
| HTTP 客户端 | urllib + http.cookiejar (标准库) |
| 端口扫描 | socket (标准库) |
| HTML 解析 | re 正则表达式 |
| GUI | tkinter (标准库) |
| 语言 | Python 3 |
| 零外部 pip 依赖 | ✅ |

## 核心特性

### ReAct 推理循环
```
Thought (思考) → Action (行动) → Action Input (参数) → Observation (观察) → 下一轮思考...
```
最多 6 轮推理，输出 `Final Answer:` 时自动终止并生成渗透测试报告。

### CSRF Token 自动突破
先 GET 抓取 `user_token`，再 POST 携带。使用双模式正则匹配，兼容 Token 在 value 前后的两种情况。

### 安全等级强制降级
登录成功后注入 `security=low` Cookie，确保后续 SQL 注入测试在最低防护等级下执行。

### Cookie 域名错位修复
放弃 urllib CookieJar 的自动域名匹配，改为手动提取 `PHPSESSID` 拼接到 HTTP Header，解决 `localhost` 与 `localhost.local` 之间的 Cookie 锁定 Bug。

### 工业级容错
每个工具函数均包含多层 try/except、边界检查和兜底逻辑。

## 环境要求

- Python 3.8+
- [Ollama](https://ollama.com) 已安装并运行
- qwen2.5:14b 模型已拉取

```bash
ollama pull qwen2.5:14b
```

- DVWA 靶场已部署在 `localhost:8080`

## 快速开始

### 1. 启动 Ollama

```bash
ollama serve
```

### 2. 启动 DVWA 靶场

确保 DVWA 运行在 `http://localhost:8080`

### 3. 运行 Agent (命令行)

```bash
python agent_core.py
```

### 4. 运行 GUI 版本

```bash
python run_gui.py
```

### 5. 独立测试登录模块

```bash
python test_login.py
```

## 项目结构

```
CyberAgent/
├── agent_core.py       # ReAct Agent 核心引擎
├── tools.py            # 四个安全测试工具
├── run_gui.py          # Tkinter 桌面 GUI
├── test_login.py       # DVWA 登录专项单元测试
├── git日志.txt          # Git 提交历史记录
└── README.md
```

## Agent 工具集

| 工具 | 功能 | 探测目标 |
|------|------|----------|
| `scan_target_ports` | TCP Connect 端口扫描 | 80, 443, 3306, 8080, 11434 |
| `check_target_web` | HTTP GET 指纹探测 + 标题提取 | Web 服务识别 |
| `login_target_web` | CSRF Token 突破 + 自动登录 | DVWA 认证绕过 |
| `check_sql_injection` | SQL 注入漏洞嗅探 | 单引号 payload 注入 |

## 安全声明

本项目仅用于**安全教育和授权测试**。请勿在未授权的系统上使用。使用者需对自身行为负责。

## License

MIT
