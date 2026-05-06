# wp-knowledge Provider 与 Cache 方案


配套任务见：

- [Provider / Cache 重构后续任务](../tasks/provider-cache.md)

## 一句话结论

目标架构很简单：

- provider 可替换
- cache 分层明确
- reload 有统一失效语义
- 旧 facade 继续可用，但内部只走统一 runtime

正确性的核心只有两个值：

- `datasource_id`
- `generation`

所有 cache 和线程本地快照都必须绑定这两个值。

## 为什么要改

旧实现主要为 `SQLite + 单进程 + 单次计算内缓存` 设计。现在同时支持 SQLite / PostgreSQL / MySQL 后，问题会直接暴露为正确性和维护成本：

- provider 生命周期过静态
- 调用方自带 cache key，语义不统一
- 元数据缓存没有边界
- `ThreadClonedMDB` 缺少版本感知

## 目标模型

内部只保留四层：

1. `DatasourceRegistry`
   - 持有当前激活 provider
   - 管理 `datasource_id`
   - 管理 `generation`
   - 处理 replace / reload
2. `KnowledgeProvider`
   - 只负责执行查询
   - 不负责缓存策略
3. `QueryRuntime`
   - 负责 cache key、cache 判定和执行路径
   - 持有 result cache 与 metadata cache
4. `Facade Compatibility Layer`
   - 保留 `query/query_row/query_named/cache_query`
   - 只做兼容，不承载核心语义

## 核心契约

### `DatasourceId`

- 表示当前数据源身份
- 可来自配置 hash 或 authority 路径 hash
- 只用于区分来源，不暴露凭据

### `Generation`

- 表示当前数据源版本
- 只要 reload、provider 切换、authority 重建、schema refresh，就必须递增
- 它是主失效机制；TTL 只是兜底

### `QueryRequest`

内部统一查询模型，至少包含：

- `sql`
- `params`
- `mode`
- `cache_policy`

provider 内部各自完成参数绑定，runtime 不再直接依赖 `rusqlite::ToSql`。

### `CachePolicy`

只保留三种语义：

- `Bypass`
  - 不走缓存
- `UseGlobal`
  - 走共享结果缓存
- `UseCallScope`
  - 走单次调用期缓存，主要为兼容旧路径

## Cache 分层

缓存只保留三层，职责不能混。

### 1. Result Cache

- 面向跨调用复用
- key 必须包含：
  - `datasource_id`
  - `generation`
  - `query_hash`
  - `params_hash`
  - `mode`
- 只适合显式允许缓存的热点查询

### 2. Local Cache

- 面向单次计算内去重
- 不承担全局一致性责任
- `FieldQueryCache` 在语义上应视为这一层

### 3. Metadata Cache

- 用于列名、schema 片段等元数据
- key 至少包含：
  - `datasource_id`
  - `generation`
  - `query_hash`
- 必须有容量上限

## Reload 契约

reload 只遵守一条规则：

- 旧 provider 是否还能用，不由时间判断，而由 `generation` 判断

因此：

- generation 变化后，result cache 自然失效
- generation 变化后，metadata cache 自然失效
- generation 变化后，`ThreadClonedMDB` 必须丢弃旧快照并重建
- reload 失败时，应保留旧 provider，不能把 runtime 切到半初始化状态

## 当前落地状态

按 2026-03-25 代码基线，核心结构已基本落地：

- `KnowledgeRuntime` 已存在，provider 可替换安装
- `QueryRequest / QueryParam / CachePolicy` 已统一
- 全局结果缓存已存在，key 已带 `datasource_id + generation`
- `FieldQueryCache` 已具备 generation 失效语义
- `ThreadClonedMDB` 已具备 generation-aware 重建能力
- SQLite metadata cache 已改为 bounded `LruCache`

主要剩余工作还有两类：

- 宿主侧 telemetry / metrics adapter
- 兼容接口的收缩与弃用策略

## 迁移顺序

建议继续按下面顺序推进：

1. 完成 reload 与 observability 对外契约
2. 收敛 provider-neutral API 为默认入口
3. 缩减 `query_named(...)` / `cache_query(...)` 的历史角色
4. 只在必要处保留 local cache 兼容层

## 最终判断

这个方向已经验证成立，后续重点不是“重新设计”，而是把剩余兼容层和宿主接入收尾做干净。
