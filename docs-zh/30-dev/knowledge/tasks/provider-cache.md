# Provider / Cache 重构后续任务


## 工作规则

每次开工前先做三件事：

1. 重新阅读当前代码，不直接按旧文档开工
2. 先标记已完成 / 部分完成 / 未开始
3. 只做当前基线下仍然有价值的最小任务

每次收尾也固定做三件事：

1. 测试 / 验证
2. review
3. 修复 review 问题后再关闭任务

## 当前状态

### 已完成

- `KnowledgeRuntime`
- 可替换 provider handle
- `datasource_id + generation`
- 统一 `QueryRequest / QueryParam / CachePolicy`
- bounded global result cache
- generation-aware `FieldQueryCache`
- generation-aware `ThreadClonedMDB`
- bounded SQLite metadata cache

### 部分完成

- reload / observability
  - 已有基础日志、snapshot、计数器和失败回退
  - 还缺宿主侧 exporter / adapter
- compatibility layer
  - `query_named(...)` / `cache_query(...)` 仍保留
  - provider-neutral 迁移尚未完全结束

### 主要剩余项

- 宿主侧 metrics / telemetry adapter
- compatibility surface 的弃用策略

## 剩余任务

### 1. Reload 与观测性对外契约

- 目标：
  - 让宿主能稳定接入 metrics / telemetry
  - 统一 reload 成功、失败和回退的诊断出口
  - 让人能回答“当前命中了哪个 provider / 哪层 cache / 哪个 generation”

### 2. 兼容层收缩

- 目标：
  - 新代码默认走 provider-neutral API
  - 明确 `query_named(...)` / `cache_query(...)` 的长期定位
  - 视情况为 SQLite-shaped 接口加 `deprecated`

### 3. Local cache 继续降级为兼容层

- 目标：
  - 保持 `FieldQueryCache` 只承担单次计算内去重
  - 不再让它承担全局一致性语义

## 建议顺序

1. reload / observability 对外契约
2. compatibility layer 收缩
3. local cache 语义继续收紧

## 备注

- 这项重构的核心结构已经落地，当前重点不是“重做一遍”，而是把剩余边界收尾做干净
- 如当前实现与文档有偏移，先更新文档，再继续编码
