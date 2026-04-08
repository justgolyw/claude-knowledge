# Git工作流指南

这是一个关于如何使用 Git 来管理和备份你的 Claude 知识库的完整指南。

## 📌 基本概念

你的知识库已初始化为 Git 仓库，这意味着：
- ✅ 所有文件变化都被追踪
- ✅ 完整的修改历史
- ✅ 可以随时恢复到任何历史版本
- ✅ 可以与 GitHub 同步备份

## 🔗 连接到GitHub（可选但推荐）

### 步骤1：创建GitHub私有仓库

1. 访问 https://github.com/new
2. 填写仓库名：`claude-knowledge`
3. 选择 **Private**（私有）
4. 不勾选"Initialize this repository"
5. 点击"Create repository"

### 步骤2：连接本地仓库

```bash
cd ~/Notes/claude-knowledge

# 添加远程仓库（替换YOUR_USERNAME和REPO_URL）
git remote add origin https://github.com/YOUR_USERNAME/claude-knowledge.git

# 改主分支名为main
git branch -M main

# 推送到GitHub
git push -u origin main
```

### 步骤3：验证连接

```bash
# 查看远程配置
git remote -v

# 应该看到
# origin  https://github.com/YOUR_USERNAME/claude-knowledge.git (fetch)
# origin  https://github.com/YOUR_USERNAME/claude-knowledge.git (push)
```

## 💾 基本Git命令

### 查看状态
```bash
cd ~/Notes/claude-knowledge
git status
```

显示：
- 未跟踪的文件
- 已修改但未暂存的文件
- 已暂存但未提交的文件

### 查看修改
```bash
# 查看所有修改
git diff

# 查看已暂存的修改
git diff --staged

# 查看某个文件的修改
git diff 文件名.md
```

### 提交变化

```bash
# 方式1：提交所有修改
git add .
git commit -m "feat: 添加新的知识片段

- 添加Python装饰器笔记
- 更新架构设计笔记"

# 方式2：提交特定文件
git add 文件名.md
git commit -m "update: 更新笔记内容"
```

### 推送到GitHub

```bash
# 首次推送
git push -u origin main

# 后续推送
git push
```

### 查看提交历史

```bash
# 查看日志
git log

# 查看简洁日志
git log --oneline

# 查看最近N条
git log -n 10

# 查看某个文件的历史
git log --oneline 文件名.md
```

## 📝 提交消息规范

遵循 Conventional Commits 格式：

```
<type>: <description>

<optional body>
```

### 类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新增功能或笔记 | `feat: 添加Python装饰器笔记` |
| `update` | 更新已有内容 | `update: 补充异步编程章节` |
| `fix` | 修复错误 | `fix: 修正代码块中的语法错误` |
| `refactor` | 重新组织结构 | `refactor: 重新分类知识库` |
| `docs` | 文档更新 | `docs: 更新README和指南` |
| `style` | 格式调整（无逻辑变化） | `style: 统一markdown格式` |

### 示例

好的提交消息：
```
feat: 添加REST API设计笔记

- 解释RESTful原理
- 代码示例和最佳实践
- 与RPC、GraphQL对比

Related-to: #api-design
```

不好的提交消息：
```
update      ❌ 太笼统
fix bug     ❌ 没有具体说明
补充内容    ❌ 英文仓库用中文
```

## 🔄 常见工作流

### 工作流1：导入新笔记

```bash
# 1. 运行导入脚本（自动创建笔记文件）
python claude-to-obsidian.py

# 2. 检查状态
git status
# 看到新文件在 Untracked files

# 3. 提交
git add .
git commit -m "feat: 添加新笔记 - [笔记名]"

# 4. 推送
git push
```

### 工作流2：编辑笔记

```bash
# 1. 在Obsidian中编辑笔记

# 2. 检查变化
git status
git diff

# 3. 提交
git add .
git commit -m "update: 更新[笔记名]

- 修改了什么
- 为什么修改"

# 4. 推送
git push
```

### 工作流3：重新组织结构

```bash
# 1. 在Obsidian中移动或重命名文件

# 2. 提交
git add .
git commit -m "refactor: 重组知识库结构

- 将笔记从A分类移到B分类
- 更新相关链接"

# 3. 推送
git push
```

## 🔍 查看和恢复

### 查看历史版本

```bash
# 查看某个文件的历史
git log --oneline 文件名.md

# 查看某个版本的内容
git show 提交ID:文件路径

# 查看某个版本的diff
git show 提交ID
```

### 恢复文件

```bash
# 恢复某个文件到上一版本
git checkout HEAD -- 文件名.md

# 恢复某个文件到特定版本
git checkout 提交ID -- 文件名.md

# 恢复所有文件到上一版本
git checkout HEAD -- .
```

### 撤销提交

```bash
# 撤销最后一次提交（文件保留）
git reset --soft HEAD~1

# 撤销最后一次提交（文件也撤销）
git reset --hard HEAD~1

# 改写最后一次提交
git commit --amend -m "新的提交消息"
```

## 🔗 与GitHub同步

### 定期备份

```bash
# 每周运行一次
git push

# 或设置自动推送（见下面的设置）
```

### 从GitHub拉取更新

```bash
# 在另一台设备上拉取最新内容
git pull
```

### 处理冲突（多设备编辑）

```bash
# 1. 查看冲突
git status

# 2. 手动解决冲突（编辑文件）

# 3. 标记为已解决
git add 冲突文件.md

# 4. 完成merge
git commit -m "merge: 解决冲突"
```

## ⚙️ 自动提交设置（可选）

### 使用Obsidian Git插件

推荐使用 Obsidian Git 插件实现自动提交：

1. 在Obsidian中安装 "Obsidian Git" 插件
2. 配置设置：
   - **Auto backup interval**: 30分钟
   - **Auto pull interval**: 30分钟
   - **Commit message format**: `feat: 自动提交 - {{date}}`

这样你的笔记会自动定期备份到GitHub。

### 手动设置cron任务（高级）

```bash
# 编辑crontab
crontab -e

# 添加每30分钟自动提交的任务
*/30 * * * * cd ~/Notes/claude-knowledge && git add . && git commit -m "feat: 自动备份 $(date)" && git push 2>/dev/null
```

## 📊 管理和监控

### 仓库统计

```bash
# 查看贡献统计
git shortlog -sn

# 查看代码行数
git diff --stat HEAD~10..HEAD

# 查看仓库大小
du -sh .git/

# 查看笔记总数
find . -name "*.md" | wc -l
```

### 清理无用历史（高级）

```bash
# 垃圾回收
git gc --aggressive

# 重写历史删除大文件（谨慎使用！）
git filter-branch --tree-filter 'rm -f 大文件' -- --all
```

## 🚨 常见问题

### Q: 如何撤销已推送的提交？
A: 
```bash
# 创建反向提交
git revert 提交ID
git push
```

### Q: 如何在本地修改全局用户信息？
A:
```bash
# 编辑仓库级配置
git config user.name "你的名字"
git config user.email "你的邮箱"

# 验证
git config --local -l
```

### Q: 如何删除某个文件的历史记录？
A:
```bash
# 完全删除文件历史（包括所有提交）
git filter-branch --tree-filter 'rm -f 文件名' -- --all
git push --force-with-lease
```

### Q: 如何在不合并的情况下更新?
A:
```bash
git fetch origin
git rebase origin/main
```

## 🔐 安全建议

1. **GitHub Token 认证**（推荐代替密码）
   ```bash
   # 使用Personal Access Token代替密码
   git remote set-url origin https://YOUR_TOKEN@github.com/USERNAME/repo.git
   ```

2. **添加.gitignore**（已包含）
   - 排除 `.obsidian/workspace` 等个人设置
   - 排除 `.env` 和敏感信息

3. **私有仓库**
   - GitHub设置为 Private
   - 定期检查访问权限

## 📚 进阶资源

- [Git官方文档](https://git-scm.com/doc)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Pro Tips](https://docs.github.com/en)

---

**最后更新**：2026-04-07  
**推荐阅读顺序**：基本概念 → 连接GitHub → 常见工作流 → 进阶设置
