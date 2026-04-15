# Wparse

`wparse` 是真正执行解析引擎的主运行时入口，主要提供两种模式：

- `daemon`：常驻模式，适合在线接入
- `batch`：批处理模式，适合离线回放和联调验证

## 建议阅读

- 权威页：[`wparse` 运行时使用指南](../06-usage/cli/runtime.md)
- 如果涉及管理面和 reload：看 [运行时管理面使用说明](../06-usage/operations/admin.md)
- 如果涉及远端同步和热更新：看 [远程工程拉取与规则热更新 SOP](../06-usage/operations/project-sync.md)

## 常见入口

```bash
wparse --help
wparse daemon --work-root .
wparse batch --work-root .
```

## 说明

本页保留为聚合站内的摘要入口。`wparse` 的详细运行语义、参数说明和运维路径，以 `06-usage` 中同步自 `warp-parse/docs/use` 的内容为准。
