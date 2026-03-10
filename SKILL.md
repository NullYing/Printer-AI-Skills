---
name: printer-ai
description: "跨平台本地打印机 - 通过 printer-ai CLI 操作本地打印机（Windows/macOS/Linux）。当用户需要打印文件、查询打印机状态、管理打印任务时使用此 Skill。NOT for: 云打印/远程打印机、非本地直连打印机。"
metadata: {"openclaw":{"emoji":"🖨️","requires":{"bins":["printer-ai"]},"install":[{"id":"uv","kind":"uv","package":"git+https://github.com/NullYing/printer-ai-skills.git","bins":["printer-ai"],"label":"Install printer-ai (uv)"}]}}
---

# 跨平台本地打印机 Skill

通过 `printer-ai` CLI 操作本地打印机，支持 Windows、macOS、Linux。

## When to Use

✅ **USE this skill when:**

- 用户要打印本地文件（PDF、图片、Office文档等）
- 查询本地打印机列表和状态
- 管理打印任务（查询状态、取消任务）
- 获取打印机详细属性/能力

## When NOT to Use

❌ **DON'T use this skill when:**

- 操作云打印机 / 远程打印盒（使用 lianke-print-box skill）
- 非本地直连的打印机

## Setup

```bash
# 安装
uv tool install git+https://github.com/NullYing/printer-ai-skills.git

# 验证
printer-ai printers
```

## 打印流程

### 1. 列出打印机

```bash
# 友好格式
printer-ai printers

# JSON 格式（推荐，便于解析）
printer-ai printers --json
```

从输出中获取打印机 `index`（后续命令需要）。⭐ 标记为默认打印机。

### 2. 检查打印机状态

```bash
printer-ai status INDEX
# 或 JSON 格式
printer-ai status INDEX --json
```

状态说明：
- 🟢 `idle` = 空闲可用
- 🟡 `processing` = 处理中
- 🔴 `stopped` = 已停止

### 3. 获取打印机属性（可选，用于了解打印机能力）

```bash
printer-ai attrs INDEX
```

返回打印机支持的所有选项（纸张、颜色、双面等）。

### 4. 打印文件

```bash
# 使用默认打印机打印
printer-ai print /path/to/file.pdf

# 指定打印机
printer-ai print /path/to/file.pdf --index 2

# 带打印选项（macOS/Linux CUPS 格式）
printer-ai print /path/to/file.pdf --options '{"copies":"2","media":"A4","orientation_requested":"3","print_color_mode":"color"}'

# 带打印选项（Windows 格式）
printer-ai print /path/to/file.pdf --options '{"dmCopies":2,"dmPaperSize":9,"dmOrientation":1,"dmColor":2}'
```

### 5. 查询任务状态

```bash
printer-ai job-status JOB_ID
```

### 6. 列出所有任务

```bash
printer-ai jobs
printer-ai jobs --printer "打印机名称"
printer-ai jobs --json
```

### 取消任务

```bash
printer-ai cancel-job JOB_ID
```

## 打印选项速查

### macOS / Linux (CUPS/IPP 格式)

| 选项 | 值 | 说明 |
|------|------|------|
| `copies` | `"2"` | 打印份数 |
| `media` | `"A4"`, `"Letter"` | 纸张大小 |
| `orientation_requested` | `"3"`=纵向, `"4"`=横向 | 方向 |
| `print_color_mode` | `"monochrome"`, `"color"` | 颜色模式 |
| `sides` | `"one-sided"`, `"two-sided-long-edge"` | 双面打印 |
| `print_quality` | `"3"`=草稿, `"4"`=普通, `"5"`=高质量 | 质量 |
| `page_ranges` | `"1-5,10-15"` | 页面范围 |
| `number_up` | `"2"`, `"4"` | 每页合并页数 |

### Windows (DEVMODE 格式)

| 选项 | 值 | 说明 |
|------|------|------|
| `dmCopies` | `2` | 打印份数 |
| `dmPaperSize` | `9`=A4, `1`=Letter | 纸张大小 |
| `dmOrientation` | `1`=纵向, `2`=横向 | 方向 |
| `dmColor` | `1`=黑白, `2`=彩色 | 颜色模式 |
| `dmDuplex` | `1`=单面, `2`=长边, `3`=短边 | 双面打印 |
| `dmPrintQuality` | `-4`=默认 | 质量 |

## Notes

- 打印前建议先用 `printer-ai status` 确认打印机在线
- 打印选项格式因平台而异，macOS/Linux 用 CUPS/IPP 字符串格式，Windows 用 DEVMODE 整数格式
- 使用 `printer-ai attrs` 查看打印机实际支持的选项
- `--json` 标志可返回纯 JSON 输出，便于程序解析
