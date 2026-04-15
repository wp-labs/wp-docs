# Wprescue

`wprescue` 是面向 rescue 数据链路的独立处理入口，用于重新处理失败数据并按现有工程路由输出。

当前使用上需要记住两点：

- 只支持 `batch` 方式
- 通常配合现有工程目录和 sink 路由一起使用

## 建议阅读

- 权威页：[`wprescue` 与 rescue 数据使用指南](../06-usage/cli/rescue.md)
- 如果想了解工程级命令：看 [`wproj` 项目工具使用指南](../06-usage/cli/project.md)

## 常见入口

```bash
wprescue --help
wprescue batch --work-root .
```

## 说明

本页保留为聚合站内的摘要入口。`wprescue` 的详细使用约束和相关统计方式，以 `06-usage` 中同步自 `warp-parse/docs/use` 的内容为准。
