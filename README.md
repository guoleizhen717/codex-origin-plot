# codex-origin-plot

> Codex Skill — Drive OriginLab Origin via COM automation for publication-grade scientific figures.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg)](#)
[![Stack: Origin COM + pywin32](https://img.shields.io/badge/Stack-Origin%20COM%20%7C%20pywin32-orange.svg)](#)

A [Codex](https://github.com/openai/codex) Skill that drives OriginLab Origin through COM automation — create, format, and export publication-grade charts directly from the Codex conversation, without a single mouse click.

## 为什么不用 matplotlib？

在很多工程学科（机械、矿业、材料），**导师和审稿人要求 Origin 原生图表**。`matplotlib` 画的图再好看，投出去也可能被要求"用 Origin 重画"。本技能让你在 Codex 中用对话直接操控 Origin。

## 核心能力

- **COM 自动化**：通过 `pywin32` 的 `win32com.client` 驱动 Origin
- **组合刀具切削力分析**：切刀合力 / 先行刀合力 / 切削比能 / 协同切削系数
- **出版级图表**：分组柱状图 + 折线散点图 + 多面板合并图
- **中英文双语标签**：自动配置合适的字体和字号
- **多重导出回退**：应对 Origin COM 的 `expGraph` 静默失败 bug

## 安装

```bash
# 克隆到 Codex skills 目录
git clone https://github.com/guoleizhen717/codex-origin-plot.git \
          ~/.codex/skills/codex-origin-plot

# 安装 Python 依赖
pip install pywin32
```

前提：已安装 OriginLab Origin 2021/2022/2023。

## 使用示例

### 示例 1：一键生成三面板图

```
用Origin画贯入度对组合刀具切削力的影响图
```

Skill 会自动：启动 Origin → 创建 Workbook → 填入数据 → 创建 3 张图表 → 格式化 → 导出 PNG。

### 示例 2：自定义数据

```
这是三组切削力数据：10mm时切刀130N先行刀292N，20mm时切刀145N先行刀316N...
用Origin画组合刀具受力对比图
```

### 示例 3：只导出一张图

```
用Origin画切削比能随贯入度变化的折线图，数据在 results.csv 里
```

## 技能结构

```
codex-origin-plot/
├── SKILL.md                     # 主技能指令（Codex 读取）
├── README.md                    # 本文件
├── LICENSE                      # MIT
├── requirements.txt             # Python 依赖
├── .gitignore
├── scripts/
│   └── origin_plot.py           # 一键生成三面板图的 Python 脚本
└── references/
    ├── origin_com_ref.md        # Origin COM 坑点大全
    └── recipe_forces.md         # 组合刀具切削力图谱
```

## 已知限制

- **不能通过 COM 保存 `.opju`**：`save -i` 会崩溃 COM 连接。告知用户在 Origin GUI 中手动 Ctrl+S。
- **`expGraph` 静默失败**：有时返回 True 但不生成文件。Skill 内置三重回退方案。
- **仅限 Windows**：Origin 没有 macOS/Linux 版本。

## 与其他 Skill 的关系

| Skill | 分工 |
|-------|------|
| `scipilot-figure-skill` | 数据剖析 + 图表类型推荐 + matplotlib 绘制 |
| `codex-origin-plot`（本 skill） | Origin COM 自动化执行 |
| 建议流程 | scipilot-figure-skill 决策 → codex-origin-plot 执行 |

## License

[MIT](LICENSE) © 2026
