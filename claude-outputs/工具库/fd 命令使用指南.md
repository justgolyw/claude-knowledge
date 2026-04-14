# fd 命令使用指南

> 导入自 Claude AI · 2026-04-14 · 工具库

                                                                                                               
- 我来帮你介绍 fd 命令的使用。                                                                                 
                                                                                                               
- Skill(find-skills)                                                                                           
## ⎿  Successfully loaded skill
                                                                                                               
- fd 是 find 命令的现代替代品，速度快、语法简洁。以下是使用指南：                                              
                                                                                                               
## 安装

```bash
# Ubuntu/Debian                                                                                              
sudo apt install fd-find                                                                                     
# 注意：Ubuntu 上命令名为 fdfind，建议设置别名                                                               
```
## alias fd=fdfind

```
# macOS                                                                                                      
```
## brew install fd

```
# Arch Linux                                                                                                 
sudo pacman -S fd                                                                                            
```

## 基本语法

## fd [选项] [模式] [搜索路径]

## 常用示例

## 按文件名搜索

## fd filename          # 搜索包含 filename 的文件
```
fd "^main"           # 以 main 开头的文件（正则）                                                            
fd ".py$"            # 以 .py 结尾的文件                                                                     
```

## 按类型过滤

```
fd -t f pattern      # 只搜索文件 (file)                                                                     
fd -t d pattern      # 只搜索目录 (directory)                                                                
fd -t l pattern      # 只搜索符号链接 (symlink)                                                              
```

## 按扩展名搜索

```
fd -e py             # 所有 .py 文件                                                                         
fd -e js -e ts       # .js 或 .ts 文件                                                                       
```

## 指定搜索路径

## fd pattern /home     # 在 /home 下搜索
## fd pattern . src/    # 在当前目录和 src/ 下搜索

## 排除目录

```bash
fd pattern -E node_modules    # 排除 node_modules                                                            
fd pattern -E "*.git"         # 排除 .git 目录                                                               
```

## 包含隐藏文件

```
fd -H pattern        # 包含隐藏文件（默认忽略）                                                              
```

## 忽略大小写

```
fd -i pattern        # 大小写不敏感                                                                          
```

## 执行命令

```
fd -e py -x chmod +x {}        # 对每个结果执行命令                                                          
fd -e log -X rm                 # 批量删除（危险，谨慎使用）                                                 
```

## 按时间/大小过滤

```
fd -S +1M            # 大于 1MB 的文件                                                                       
fd --changed-within 1d   # 最近 1 天修改的文件                                                               
fd --changed-before 1w   # 超过 1 周未修改的文件                                                             
```

## 与 find 对比

| 功能 | fd | find |
| --- | --- | --- |
| 搜索名称 | fd foo | find . -name "*foo*" |
| 按类型 | fd -t f foo | find . -type f -name "*foo*" |
| 按扩展名 | fd -e py | find . -name "*.py" |
| 执行命令 | fd foo -x cmd {} | find . -name "*foo*" -exec cmd {} \; |

## fd 默认忽略 .gitignore 中的文件、隐藏文件和目录，更适合日常开发使用。

---
*标签：#工具库 #Python #bash #待整理 #claude-output*
