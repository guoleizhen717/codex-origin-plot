---
name: codex-origin-plot
description: >-
  Drive OriginLab Origin via COM automation to create publication-grade
  scientific figures. Handles combined-tool cutting force analysis
  (force, specific energy, synergistic coefficient) with grouped column
  and line+symbol charts. Supports Chinese + English labels. Designed
  for mechanical engineering / mining engineering research papers.
  When the user needs Origin figures (not matplotlib) for journal
  submission, or when the user says "画一张Origin图", "用Origin画",
  "Origin绘图", "COM自动化Origin", trigger this skill.
---

# codex-origin-plot — Codex驱动Origin科研绘图

> 直接通过 COM 自动化控制 OriginLab Origin，从数据到出版级图表一步完成。

## 概述

本技能解决的核心问题：**在 Codex 中调用 Origin COM 接口，自动创建、格式化、导出科研图表**。

与 matplotlib/seaborn 不同，Origin 是许多工程学科（机械、矿业、材料）的**标准投稿工具**。审稿人和导师往往要求 `.opju` 源文件 + Origin 原生图表。本技能让你在 Codex 对话中直接操控 Origin，无需手动点击。

**定位**：本技能专注于 **Origin COM 自动化执行**，不做数据剖析和图表类型推荐（这些由 scipilot-figure-skill 负责）。如果你不确定该画什么图，先走 scipilot-figure-skill 的流程。

## 何时使用

- 用户说"用Origin画图"、"Origin绘图"、"COM自动化Origin"
- 用户需要 `.opju` 源文件 + Origin 原生导出 PNG/PDF
- 用户在做组合刀具切削力分析（切刀/先行刀合力、比能、协同系数）
- 用户需要中文/英文双语标签的出版级图表
- 用户指定目标期刊需要 Origin 格式（而非 matplotlib）
- 用户已有数据，需要快速生成 Origin 图表预览

## 核心工作流（6 步）

```
0. 环境检查    —— 确认 Origin 安装路径、Python 环境、pywin32
   ↓
1. 准备数据    —— 从 CSV 或计算结果中整理数据
   ↓
2. 启动 Origin  —— kill 残留进程 → COM Dispatch → Visible
   ↓
3. 创建图表    —— Workbook → 填数 → plotxy（逐个创建，逐个格式化）
   ↓
4. 格式化      —— 坐标轴标签/范围/标题，字体大小
   ↓
5. 导出        —— expGraph PNG（逐个导出；合并图用 merge_graph）
   ↓
6. 展示给用户  —— 用 view_image 展示 PNG，等待反馈
```

## 关键经验（避免踩坑）

### 稳定可用的
- `newproject`, `win -t wks`, 填数据 ✅
- `plotxy` 创建图表 ✅
- 设置坐标轴标签/范围/标题 ✅
- 逐个图表创建 + 逐个导出 ✅

### 会崩溃/静默失败的
- `save -i` 保存项目 → **COM 崩溃** `(-2147417851)` ❌
- `expGraph` → 返回 True 但**不生成文件** ❌（需多重回退方案）
- `merge_graph` → 可能返回 False ❌（用独立导出代替）
- `echo %H` → 始终返回 False ❌（COM 无法捕获 LabTalk 输出）

### 导出回退策略
1. 优先：`expGraph type:=png filename:="D:/path/fig.png" width:=2400 height:=3600 tr1.unit:=2`
2. 回退：`page.export(type:=png, filename:=D:/path/fig.png)`
3. 回退：不带引号的 expGraph
4. 兜底：截图 Origin 窗口

## 依赖

```
pywin32>=305       # COM automation (pip install pywin32)
OriginLab Origin   # 2021/2022/2023 tested
Python 3.9+
```

Origin 安装路径检测（按优先级）：
1. `D:\Program Files\OriginLab\Origin2022\Origin64.exe`
2. `C:\Program Files\OriginLab\Origin2022\Origin64.exe`
3. 全盘搜索 `Origin64.exe`

## 参考文件

| 文件 | 用途 |
|------|------|
| `references/origin_com_ref.md` | COM 自动化坑点大全 — 新建会话前必读 |
| `references/recipe_forces.md` | 组合刀具切削力图谱 — 柱状图/折线图/多面板配方 |
| `scripts/origin_plot.py` | 可独立运行的 Python 脚本 — 一键生成三面板图 |

每份文件开头都有目录，先查目录定位，再读对应小节。

## 常见任务示例

### 任务 A：用户给了一组贯入度数据，要画三面板图

**流程**：
1. 读 `references/recipe_forces.md` 确认图表配方
2. 读 `references/origin_com_ref.md` 确认 COM 要点
3. 运行 `scripts/origin_plot.py` 或手动执行 COM 命令
4. 导出 3 张 PNG → `view_image` 展示给用户
5. 根据用户反馈迭代（调坐标轴、字体、颜色）

### 任务 B：用户已有 CSV 原始数据（未计算合力/比能/协同系数）

**流程**：
1. 先读取 CSV，按第三章方法计算：
   - 合力 = sqrt(Fx² + Fy² + Fz²)，取稳态阶段均值
   - 切削比能 = 总合力 / 贯入度（或按用户公式）
   - 协同切削系数 K = 切刀合力 / 先行刀合力
2. 将计算结果整理成 Python dict
3. 然后走任务 A 的流程

### 任务 C：用户要求多面板合并图

**流程**：
1. 先逐个创建 3 张独立图表（按 Recipe 1-3）
2. 尝试 `merge_graph option:=2 row:=3 col:=1 keepsize:=0`
3. 如果 merge_graph 返回 False → 导出 3 张独立 PNG，告知用户手动合并
4. 如果 merge_graph 成功 → 导出合并后的 MGraph1 为单张长图

## 图表类型映射

| 分析指标 | Origin plot type | template | iy 参数 |
|----------|-----------------|----------|---------|
| 合力对比 | Grouped Column (202) | Column | (1,2) |
| 切削比能 | Line + Symbol (201) | LineSymb | (1,3) |
| 协同系数 | Line + Symbol (201) | LineSymb | (1,4) |

## Python 环境说明

Codex 的 Python 运行时路径：
```
C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

如果 pywin32 未安装：
```powershell
& "C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m pip install pywin32
```

## COM 会话模板

```python
import win32com.client, time, pythoncom
pythoncom.CoInitialize()
origin = win32com.client.Dispatch("Origin.Application")
origin.Visible = True
time.sleep(3)
# ... send LabTalk commands via origin.Execute(cmd) ...
pythoncom.CoUninitialize()
```

每个 COM 会话必须配对 `CoInitialize/CoUninitialize`，否则资源泄漏。

## 注意事项

- 在开始前必须 `taskkill /f /im Origin64.exe`，避免残留进程干扰
- 不要尝试通过 COM 保存 `.opju` 项目文件（会崩溃），告知用户手动保存
- 每个图表创建后立即格式化和导出，不要在多个图表间跳转
- COM 返回值 `True/False` 不代表操作是否完成，需要检查实际文件是否生成
- 如果 `expGraph` 三次回退都失败，截图 Origin 窗口作为兜底方案
