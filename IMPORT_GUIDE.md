# Claude输出导入工具使用指南

## 📋 概述

`claude-to-obsidian.py` 是一个快速导入工具，可以自动将 Claude 的输出内容转换成 Obsidian 笔记，并自动分类、标记和保存。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install pyperclip
```

### 2. 基本使用
```bash
# 从粘贴板读取，自动转换和保存
python claude-to-obsidian.py

# 自动提交到Git（可选）
python claude-to-obsidian.py --auto-commit
```

### 3. 工作流
1. 在 Claude 界面复制你要保存的内容
2. 运行脚本：`python claude-to-obsidian.py`
3. 脚本自动：
   - 提取标题
   - 分类内容
   - 生成元数据
   - 保存到合适的文件夹
4. 在 Obsidian 中刷新查看新笔记

## 🔧 功能详解

### 自动标题提取
- 优先使用内容中的 `#` 标题
- 否则使用第一行内容
- 自动截断长度（100字符）

### 自动分类
系统会根据内容自动分类：

| 分类 | 关键词 | 保存路径 |
|------|--------|--------|
| 代码 | ``` code, import, def, class | 10-claude-outputs/代码片段 |
| 理论概念 | 解释, 原理, 基础 | 10-claude-outputs/理论概念 |
| 工具库 | 库, 工具, 框架 | 10-claude-outputs/工具库 |
| 其他 | 不匹配上述 | 10-claude-outputs/其他 |

### 自动标签生成
脚本会根据内容自动添加标签：

- **始终添加**：`#claude-output`, `#待整理`
- **分类标签**：根据内容分类自动添加
- **语言标签**：自动检测代码块中的编程语言
- **特殊标签**：根据内容类型（如`#问题解答`）

示例：
```yaml
tags: [claude-output, 待整理, Python, Flask, 框架]
```

### 自动元数据
每个笔记自动包含：
```yaml
date: 2026-04-07 14:30           # 导入时间
tags: [...]                      # 自动生成的标签
source: Claude AI                # 来源
category: 代码                   # 分类
```

## 📂 输出示例

### 代码片段
```
notes/claude-knowledge/
└── 10-claude-outputs/
    └── 代码片段/
        └── Python装饰器完全指南.md
            ├── date: 2026-04-07 14:30
            ├── tags: [claude-output, 待整理, 代码, Python]
            └── 内容...
```

### 概念笔记
```
notes/claude-knowledge/
└── 10-claude-outputs/
    └── 理论概念/
        └── 什么是异步编程.md
            ├── date: 2026-04-07 14:30
            ├── tags: [claude-output, 待整理, 理论概念]
            └── 内容...
```

## ⚙️ 高级用法

### 使用Git自动提交
```bash
python claude-to-obsidian.py --auto-commit
```

或简写：
```bash
python claude-to-obsidian.py -a
```

这会：
1. 保存笔记
2. 自动运行 `git add`
3. 自动运行 `git commit`
4. 提交消息格式：`feat: 添加笔记 - [标题]`

### 创建别名（可选）

在 `.bashrc` 或 `.zshrc` 中添加：

```bash
# 快速导入
alias claude-import='python ~/Notes/claude-knowledge/claude-to-obsidian.py'

# 快速导入并提交
alias claude-import-git='python ~/Notes/claude-knowledge/claude-to-obsidian.py --auto-commit'
```

然后直接运行：
```bash
claude-import
claude-import-git
```

## 🐛 故障排除

### 问题：ImportError - No module named 'pyperclip'
**解决**：
```bash
pip install pyperclip
```

### 问题：知识库目录不存在
**解决**：确保已创建 `~/Notes/claude-knowledge` 目录

### 问题：粘贴板为空
**解决**：确保已复制内容到粘贴板

### 问题：文件保存失败
**解决**：检查目录权限，确保可写

### 问题：Git提交失败
**解决**：
- 检查 Git 是否已安装
- 检查仓库是否初始化：`git status`
- 检查用户配置：`git config user.name`

## 📝 文件夹自定义

如果想修改知识库路径，编辑脚本中的：

```python
# 第35行
VAULT_ROOT = Path.home() / "Notes" / "claude-knowledge"
```

改为你想要的路径：
```python
VAULT_ROOT = Path("/your/custom/path")
```

## 🔄 与Obsidian集成

### 自动刷新
Obsidian 会自动检测文件变化，刷新显示。如果没有自动刷新：
- 使用快捷键：`Ctrl+R`（Windows/Linux）或 `Cmd+R`（Mac）
- 或在 Obsidian 中手动刷新

### 查看新笔记
1. 在左侧文件浏览器中找到新笔记
2. 或使用搜索功能快速查找
3. 或在关系图中查看知识联系

## 💡 最佳实践

1. **定期导入**：养成习惯，常用的输出立即导入
2. **及时整理**：导入后在 Obsidian 中补充链接和标签
3. **定期回顾**：查看孤立笔记（Graph view），建立关联
4. **使用Git**：定期同步到 GitHub 备份

## 📊 批量导入

如果有多个内容要导入：

```bash
# 方式1：逐个导入（推荐）
python claude-to-obsidian.py  # 第1个
python claude-to-obsidian.py  # 第2个
# ...

# 方式2：编辑脚本支持文件输入（高级用户）
# 可以扩展脚本支持从文件或URL读取
```

## 🚀 未来改进

- [ ] 支持从URL直接导入
- [ ] 支持批量导入
- [ ] Web界面
- [ ] 与Claude网页版集成

---

**版本**：1.0  
**最后更新**：2026-04-07  
**作者**：Claude AI
