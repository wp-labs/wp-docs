# Wpgen

`wpgen` 是 Warp Parse 的测试数据生成工具，主要用于：

- 初始化和检查生成器配置
- 基于规则生成测试数据
- 基于样本回放生成联调数据

## 建议阅读

- 权威页：[`wpgen` 生成器使用指南](../06-usage/cli/generator.md)
- 如果你还没有工程目录：先看 [快速开始](../01-getting-started.md)
- 如果你想了解 CLI 整体分工：看 [功能与 CLI 使用指南](../06-usage/cli/index.md)

## 常见入口

```bash
wpgen --help
wpgen conf init --work-root .
wpgen conf check --work-root .
```

## 说明

本页保留为聚合站内的摘要入口。`wpgen` 的详细配置、子命令和运行语义，以 `06-usage` 中同步自 `warp-parse/docs/use` 的内容为准。
