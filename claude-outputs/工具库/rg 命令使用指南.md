# rg 命令使用指南

> 导入自 Claude AI · 2026-04-09 · 工具库                      
## 基本搜索

```
rg "pattern"              # 当前目录递归搜索                                                                                
rg "pattern" /path        # 指定目录搜索                                                                                    
rg "pattern" file.txt     # 搜索单个文件                                                                                    
```

## 常用选项

```
rg -i "pattern"           # 忽略大小写                                                                                      
rg -v "pattern"           # 反向匹配（不含该模式的行）                                                                      
rg -w "word"              # 全词匹配                                                                                        
rg -F "literal.string"   # 固定字符串（不解析正则）                                                                         
rg -x "whole line"        # 整行匹配                                                                                        
```

## 输出控制

```
rg -l "pattern"           # 只显示文件名                                                                                    
rg -c "pattern"           # 显示每个文件的匹配数                                                                            
rg -n "pattern"           # 显示行号（默认已开启）                                                                          
rg -N "pattern"           # 不显示行号                                                                                      
rg --no-filename "pat"    # 不显示文件名                                                                                    
rg -o "pattern"           # 只输出匹配的部分                                                                                
```

## 上下文行

```
rg -A 3 "pattern"         # 匹配后 3 行                                                                                     
rg -B 3 "pattern"         # 匹配前 3 行                                                                                     
rg -C 3 "pattern"         # 前后各 3 行                                                                                     
```

## 文件过滤

```
rg -t py "pattern"        # 只搜索 Python 文件                                                                              
rg -T py "pattern"        # 排除 Python 文件                                                                                
rg -g "*.json" "pattern"  # glob 模式过滤                                                                                   
rg -g "!*.min.js" "pat"   # 排除 minified JS                                                                                
```

## 替换输出

```
rg "foo" -r "bar"         # 输出替换后内容（不修改文件）                                                                    
```

## 多模式搜索

```
rg -e "foo" -e "bar"      # 同时搜索多个模式                                                                                
rg -f patterns.txt        # 从文件读取模式列表                                                                              
```

## 隐藏文件与忽略规则

```
rg -. "pattern"           # 包含隐藏文件                                                                                    
rg --no-ignore "pattern"  # 忽略 .gitignore                                                                                 
rg -u "pattern"           # 同上（--unrestricted）                                                                          
rg -uu "pattern"          # 同时包含隐藏文件和忽略规则                                                                      
```

## 实用示例

```bash
# 搜索 TODO 注释                                                                                                            
rg "TODO|FIXME" --type-add 'src:*.{py,js,ts}' -t src                                                                        

# 搜索函数定义                                                                                                              
rg "^def \w+" -t py                                                                                                         

# 统计各文件匹配数，排序                                                                                                    
rg -c "error" | sort -t: -k2 -rn                                                                                            

# 搜索多行模式                                                                                                              
rg -U "func.*\{[\s\S]*?\}" -t go                                                                                            

# 只看文件列表并传给其他命令                                                                                                
rg -l "deprecated" | xargs sed -i 's/deprecated/obsolete/g'
```

---
*标签：#问题解答 #claude-output #Python #工具库 #bash #待整理*
