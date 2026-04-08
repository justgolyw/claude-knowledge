# Claude输出导入工具使用指南

## 概述

`claude-to-obsidian.py` 将 Claude 的输出内容自动转换为 Obsidian 笔记，支持自动标题提取、内容分类、标签生成。

## 快速开始

### 1. 安装依赖
```bash
pip install pyperclip
```

### 2. 基本使用
```bash
cd ~/Notes/claude-knowledge

# 从粘贴板读取并保存
python claude-to-obsidian.py

# 保存并自动 Git 提交
python claude-to-obsidian.py --auto-commit
```

### 3. 工作流
1. 复制 Claude 回答内容到粘贴板
2. 运行脚本
3. 在 Obsidian 中刷新查看新笔记

## 笔记格式

每个笔记的结构：

```markdown
# 标题

> 导入自 Claude AI · 2026-04-08 · 工具库

（正文内容）

---
*标签：#claude-output #bash #工具库 #待整理*
```

> **提示**：Obsidian 开启了"内联标题"时，文件名会显示为大标题，建议在「设置 → 外观」中关闭「内联标题」，避免与笔记内的 `# 标题` 重复。

## 自动分类规则

| 分类 | 触发关键词 | 保存路径 |
|------|-----------|---------|
| 代码 | import, def, class, function | claude-outputs/代码片段 |
| 理论概念 | 解释, 什么是, 原理, 概念 | claude-outputs/理论概念 |
| 工具库 | 如何使用, 用法, 命令, 教程, 工具, 框架 | claude-outputs/工具库 |
| 其他 | 不匹配上述 | claude-outputs/其他 |

## 故障排除

| 问题 | 解决方法 |
|------|---------|
| `ImportError: pyperclip` | `pip install pyperclip` |
| 粘贴板为空 | 确保已复制内容 |
| 标题识别不准 | 在 Obsidian 中手动重命名文件 |
| Git 提交失败 | `git config --global user.name '名字'` |

## 创建别名（可选）

在 `~/.zshrc` 或 `~/.bashrc` 中添加：

```bash
alias cto='cd ~/Notes/claude-knowledge && python claude-to-obsidian.py'
alias ctog='cd ~/Notes/claude-knowledge && python claude-to-obsidian.py --auto-commit'
```

---

**最后更新**：2026-04-08
