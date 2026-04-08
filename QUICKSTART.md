# 🚀 快速入门指南

欢迎使用 Claude 知识库系统！这个指南将帮助你在5分钟内快速上手。

## ✅ 系统已就绪！

你的知识库已初始化完成，包括：
- ✅ 本地文件夹结构（`~/Notes/claude-knowledge`）
- ✅ Git仓库初始化
- ✅ 导入工具脚本（`claude-to-obsidian.py`）
- ✅ 完整文档和指南

## 📋 现在需要做什么？

### 第1步：安装Obsidian（如果还没有）

1. 访问 https://obsidian.md
2. 下载并安装
3. 打开Obsidian
4. 选择 "Open folder as vault"
5. 选择 `~/Notes/claude-knowledge`
6. 完成！

**验证**：Obsidian会显示所有文件夹和笔记

### 第2步：测试导入脚本

```bash
# 复制以下任意内容到粘贴板
# （例如从Claude对话中复制）

# 然后运行脚本
cd ~/Notes/claude-knowledge
python claude-to-obsidian.py
```

**预期结果**：
```
📋 Claude输出导入工具 v1.0
--------------------------------------------------
📥 从粘贴板读取内容...
✓ 读取成功 (234 字符)

📝 提取标题...
✓ 标题：笔记标题

🏷️  分类内容...
✓ 分类：代码

...

✅ 导入完成！
📍 笔记已保存到：claude-outputs/代码片段/笔记标题.md
```

### 第3步（可选）：连接GitHub备份

```bash
# 创建GitHub私有仓库后，运行以下命令

cd ~/Notes/claude-knowledge

# 替换YOUR_USERNAME和REPO_URL
git remote add origin https://github.com/YOUR_USERNAME/claude-knowledge.git
git branch -M main
git push -u origin main
```

**验证**：https://github.com/YOUR_USERNAME/claude-knowledge 出现你的笔记

## 📝 完整工作流示例

### 场景：从Claude学到一个Python技巧

```bash
# 1️⃣ 在Claude对话中复制你想保存的内容
(复制内容)

# 2️⃣ 运行导入脚本
python ~/Notes/claude-knowledge/claude-to-obsidian.py

# ✨ 脚本自动：
#  - 从粘贴板读取内容
#  - 识别为"代码"分类
#  - 添加标签：#claude-output, #待整理, #Python, #代码
#  - 保存到：claude-outputs/代码片段/

# 3️⃣ 在Obsidian中查看新笔记
# （自动刷新，或按 Ctrl+R）

# 4️⃣ 补充和整理
# - 添加额外的说明
# - 创建链接到相关笔记
# - 调整标签

# 5️⃣ Git自动备份
# （Obsidian Git插件每30分钟自动提交）
```

## 🎯 下一步任务

### 今天完成
- [ ] 安装Obsidian
- [ ] 打开知识库（Open folder as vault）
- [ ] 测试导入脚本（python claude-to-obsidian.py）
- [ ] 导入第一个笔记

### 本周完成
- [ ] 导入5-10个常用知识片段
- [ ] 熟悉Obsidian界面和快捷键
- [ ] 创建2-3个主题中心页面（如Python.md）
- [ ] 在笔记间建立双向链接

### 本月完成
- [ ] 连接GitHub私有仓库
- [ ] 安装Obsidian Git插件（自动备份）
- [ ] 建立完整的知识体系
- [ ] 定期回顾和优化

## 📚 重要文档位置

| 文档 | 用途 | 路径 |
|------|------|------|
| README.md | 项目总览 | 根目录 |
| IMPORT_GUIDE.md | 导入脚本详细指南 | 根目录 |
| GIT_WORKFLOW.md | Git使用完整指南 | 根目录 |
| 笔记模板 | 新笔记参考 | _templates/ |

## 🔧 常用命令速查

```bash
# 导入新笔记
python ~/Notes/claude-knowledge/claude-to-obsidian.py

# 查看Git状态
cd ~/Notes/claude-knowledge && git status

# 手动提交
git add . && git commit -m "feat: 添加笔记"

# 推送到GitHub
git push

# 查看笔记文件夹
open ~/Notes/claude-knowledge  # Mac
# 或 explorer ~/Notes/claude-knowledge  # Windows
```

## ⌨️ Obsidian快捷键

| 功能 | Mac | Windows/Linux |
|------|-----|---------------|
| 打开搜索 | Cmd+P | Ctrl+P |
| 新建笔记 | Cmd+N | Ctrl+N |
| 刷新 | Cmd+R | Ctrl+R |
| 搜索内容 | Cmd+F | Ctrl+F |
| 打开图谱 | Cmd+Shift+G | Ctrl+Shift+G |
| 命令面板 | Cmd+: | Ctrl+: |

## 💡 Pro Tips

1. **快速导入**：养成习惯，有好内容立即运行脚本导入
2. **建立中心页面**：为每个主题创建概览页面（如Python.md）
3. **定期链接**：在Graph view中识别孤立笔记，建立关联
4. **及时提交**：利用自动提交，不用担心数据丢失
5. **备份检查**：定期访问GitHub检查备份状态

## 🆘 遇到问题？

### 导入脚本错误
- **检查**：pyperclip是否安装（`pip install pyperclip`）
- **检查**：粘贴板是否有内容（复制后再试）
- **检查**：知识库路径是否正确

### Obsidian不显示新笔记
- **解决**：按 Ctrl+R 手动刷新
- **解决**：关闭后重新打开Obsidian

### Git推送失败
- **检查**：是否连接了GitHub（`git remote -v`）
- **检查**：GitHub账户认证信息

### 需要帮助？
- 查看详细文档：IMPORT_GUIDE.md, GIT_WORKFLOW.md
- 检查Obsidian官方文档：https://help.obsidian.md/

## 🎉 成功标志

当你看到以下情况，说明系统正常运行：

✅ Obsidian打开了你的知识库  
✅ 导入脚本成功创建了笔记  
✅ Obsidian自动刷新显示新笔记  
✅ Git提交历史中有你的提交  
✅ GitHub仓库显示你的笔记内容  

## 📞 获取帮助

文档位置：
- 导入工具：IMPORT_GUIDE.md
- Git操作：GIT_WORKFLOW.md
- 项目概览：README.md

---

**准备好了吗？** 👉 现在就试试导入你的第一个笔记吧！

```bash
python ~/Notes/claude-knowledge/claude-to-obsidian.py
```

祝你使用愉快！✨
