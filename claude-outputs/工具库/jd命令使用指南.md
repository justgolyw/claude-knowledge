# jd 命令使用指南

> 导入自 Claude AI · 2026-04-08 · 工具库
## 基本对比

```
# 对比两个 JSON 文件
jd a.json b.json

# 带颜色输出
jd -color a.json b.json

# 字符级高亮
jd -color-words a.json b.json
```

## 输出格式说明

```
@ ["key"]   # 差异路径
- "old"     # 被删除的值
+ "new"     # 新增的值
```

## 数组对比模式

```
jd -set a.json b.json    # 忽略顺序，视为集合
jd -mset a.json b.json   # 忽略顺序，允许重复（multiset）
```

## 生成并应用 Patch

```
# 生成 patch 文件
jd a.json b.json > patch.jd

# 应用 patch
jd -p patch.jd a.json
```

## 输出格式切换

```
jd -f patch a.json b.json   # RFC 6902 JSON Patch 格式
jd -f merge a.json b.json   # JSON Merge Patch 格式
jd -f jd    a.json b.json   # 默认 jd 格式
```

## YAML 支持

```
jd -yaml a.yaml b.yaml
```

## 数字精度

```
# 差值在 0.01 内视为相等
jd -precision 0.01 a.json b.json
```

## Web UI

```
jd -port 8080 a.json b.json   # 浏览器中可视化查看 diff
```

## 实用示例

```bash
# 对比 API 响应
curl api1/endpoint | jd - <(curl api2/endpoint)

# 对比配置文件变更
jd -color config.old.json config.new.json

# 识别对象数组的 set key（按 id 字段匹配）
jd -setkeys id a.json b.json
```

---
*标签：#待整理 #bash #claude-output #JavaScript #工具库*
