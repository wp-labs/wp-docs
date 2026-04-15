# Wproj

`wproj` 是 Warp Parse 的项目级工具入口，主要负责工程初始化、配置检查、模型查看、运行时管理以及部分数据统计操作。

如果你在做下面这些事情，通常都应该优先看 `wproj`：

- 初始化或更新一个工作目录
- 检查工程配置是否完整可用
- 查看模型、统计数据、执行运行时管理动作

## 建议阅读

- 权威页：[`wproj` 项目工具使用指南](../06-usage/cli/project.md)
- 如果你刚开始接触 Warp Parse：先看 [快速开始](../01-getting-started.md)
- 如果你想了解整体 CLI 分工：看 [功能与 CLI 使用指南](../06-usage/cli/index.md)

## 常见入口

```bash
wproj --help
wproj init --work-root .
wproj check --work-root .
```

## 说明

本页保留为聚合站内的摘要入口。`wproj` 的详细命令说明与运维路径，以 `06-usage` 中同步自 `warp-parse/docs/use` 的内容为准。
