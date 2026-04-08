# jq命令如何使用

> 导入自 Claude AI · 2026-04-08 · 工具库

- jq 是轻量级命令行 JSON 处理工具。

## 基本语法

```bash
jq [选项] '过滤器' [文件]
echo '{"key":"value"}' | jq '过滤器'
```

## 常用过滤器

```bash
# 格式化输出
echo '{"a":1}' | jq '.'

# 获取字段
echo '{"name":"Alice"}' | jq '.name'          # 输出: "Alice"
echo '{"user":{"name":"Alice"}}' | jq '.user.name'

# 数组操作
echo '[1,2,3]' | jq '.[0]'                    # 第一个元素
echo '[1,2,3]' | jq '.[-1]'                   # 最后一个
echo '[1,2,3]' | jq '.[1:3]'                  # 切片

# 遍历数组
echo '[{"name":"A"},{"name":"B"}]' | jq '.[] | .name'

# 过滤
echo '[1,2,3,4,5]' | jq '[.[] | select(. > 3)]'

# 映射
echo '[1,2,3]' | jq '[.[] | . * 2]'

# 构造新对象
echo '{"name":"Alice","age":30}' | jq '{用户名: .name}'

# keys / values
echo '{"a":1,"b":2}' | jq 'keys'
echo '{"a":1,"b":2}' | jq 'values'

# 长度
echo '[1,2,3]' | jq 'length'
```

## 条件与字符串

```bash
jq 'if .age > 18 then "adult" else "minor" end'
jq '"Hello, \(.name)!"'          # 字符串插值
jq 'has("name")'                 # 键是否存在
```

## 常用选项

| 选项 | 说明 |
| --- | --- |
| -r | 原始输出（去掉字符串引号） |
| -c | 紧凑输出 |
| -s | 合并输入为数组 |
| -n | 不读取输入 |
| --arg k v | 传入变量 |

## 实战示例

```bash
curl -s https://api.example.com/users | jq '.[0].name'

# 提取特定字段
cat data.json | jq '[.[] | {id, name}]'

# 用变量过滤
jq --arg name "Alice" '.[] | select(.name == $name)' data.json

# 读取文件
jq '.' data.json
```

---
*标签：#claude-output #bash #待整理 #工具库*
