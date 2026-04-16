# 新增 C++ Metric 流程

> 导入自 Claude AI · 2026-04-16 · 工具库

## 需要修改/新增以下 6 类文件：

```
---
```
## 1. 新增 Proto 定义文件（metric 的输入/输出结构）

## 新增文件：
```
simulation/simulation/simulation_proto/hmi_output_check_metric.proto
```

## 定义两个 message：
```
- HmiOutputCheckMetric — metric 的输入参数（配置项）
- HmiOutputCheckMetricResult — metric 的每帧输出结果
```

```
---
```
## 2. 修改 Proto 汇总文件

## 修改文件 1：
```
simulation/simulation/simulation_proto/scenario_metric.proto
```

```
- import 新 proto 文件
- 在 ScenarioMetric 的 oneof metric 中添加新字段（field number 唯一）：
HmiOutputCheckMetric hmi_output_check_metric = 304;
```

## 修改文件 2：
```
simulation/simulation/simulation_proto/frame_passing_result.proto
```

```
- 同样 import 并在 FrameResult 的 oneof 中添加结果字段：
HmiOutputCheckMetricResult hmi_output_check_metric_result = 277;
```

```
---
```
## 3. 新增 C++ Handler 类（核心逻辑）

## 新增文件：
```
- post_process/scenario_evaluator/metrics/hmi_output_check_metric_handler.h
- post_process/scenario_evaluator/metrics/hmi_output_check_metric_handler.cpp
```

## 关键点：
```
- 继承 MetricHandlerBase，实现 Evaluate() 方法
- 构造函数中 assert metric_case 类型匹配
- 末尾调用宏 REGISTER_METRIC_HANDLER(HmiOutputCheckMetricHandler) 完成自动注册（无需手动注册）
```

```
---
```
## 4. 修改 Topic Map（声明订阅哪些 topic）

## 修改文件：
## post_process/scenario_evaluator/metric_topic_map.h

## 在 MetricToTopics() 的静态 map 中添加一行：
```
{proto::ScenarioMetric::kHmiOutputCheckMetric, {
    topic::kBpHMIOutputTopicName,
    topic::kMfLocalPoseTopicName,
    topic::kSimMfLocalPoseTopicName
}},
```

```
---
```
## 5. 修改 BUILD.bazel（声明编译目标）

## 修改文件 1：
```
post_process/scenario_evaluator/metrics/BUILD.bazel
```

## 新增一个 cc_library 目标：
```
cc_library(
    name = "hmi_output_check_metric_handler",
    srcs = ["hmi_output_check_metric_handler.cpp"],
    hdrs = ["hmi_output_check_metric_handler.h"],
    deps = [":metric_handler_base", ...],
    alwayslink = 1,  # 必须，保证静态注册宏生效
```
## )

## 修改文件 2：
```
post_process/scenario_evaluator/BUILD.bazel
```

## 在主 binary 的 deps 中引用新 target：
```
"//scenario_evaluator/metrics:hmi_output_check_metric_handler",
```

```
---
```
## 汇总表

| 文件 | 操作 | 说明 |
| --- | --- | --- |
| simulation_proto/hmi_output_check_metric.proto | 新增 | 定义 metric 输入/输出 message |
| simulation_proto/scenario_metric.proto | 修改 | import + oneof 新增 field |
| simulation_proto/frame_passing_result.proto | 修改 | import + oneof 新增 result field |
| metrics/hmi_output_check_metric_handler.h | 新增 | Handler 类声明 |
| metrics/hmi_output_check_metric_handler.cpp | 新增 | Handler 实现 + REGISTER_METRIC_HANDLER 宏 |
| scenario_evaluator/metric_topic_map.h | 修改 | 声明 metric 订阅的 topic 列表 |
| metrics/BUILD.bazel | 修改 | 新增 cc_library，alwayslink = 1 |
| scenario_evaluator/BUILD.bazel | 修改 | 主 target deps 引用新 handler |

```
关键机制：REGISTER_METRIC_HANDLER 宏通过静态全局变量在 main() 前自动注册工厂类，alwayslink = 1 保证链接器不丢弃该目标。无需修改
scenario_evaluator.cpp 中的主逻辑。
```

---
*标签：#待整理 #claude-output #C++ #Python #Rust #工具库*
