# PostgreSQL Source 使用文档

`PostgresSource` 用于从 PostgreSQL 表中按单游标持续增量读取数据。

它的工作方式是：

```text
读取本地 checkpoint
  -> 生成按游标递增的查询
  -> 从 PostgreSQL 拉取一批数据
  -> 将整行记录转成 JSON
  -> 自动追加 warp_parse_table 字段
  -> 返回给上游
  -> 用当前批次最后一条记录的游标值更新 checkpoint
```

当前版本只支持单游标，不支持二级游标，也不支持文本时间列作为时间游标。

## 1. 适用场景

- 需要从 PostgreSQL 表中持续增量采集数据
- 表中存在单调递增的游标列
- 希望进程重启后可以从上次位置继续读取

适合的游标列：

- 自增 `id`
- 单调递增的业务流水号
- 单调递增且不会跨批截断的 `numeric` / `decimal`
- PostgreSQL 原生时间列：`timestamp with time zone`、`timestamp without time zone`、`date`

不适合的游标列：

- 会回写旧值的字段
- 存在大量重复值且可能跨批截断的字段
- 文本时间字段
- `time without time zone`

## 2. 基本配置

最小配置示例：

```toml
[[sources]]
name = "postgres_logs"
connector_id = "postgres_src"

params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  cursor_column = "id"
}
```

如果你的运行时使用的是 connector 定义方式，也可以这样写：

```toml
[[connectors]]
id = "postgres_src"
type = "postgres"
allow_override = [
  "endpoint",
  "username",
  "password",
  "database",
  "table",
  "schema",
  "batch",
  "cursor_column",
  "cursor_type",
  "start_from",
  "start_from_format",
  "poll_interval_ms",
  "error_backoff_ms"
]

[connectors.params]
endpoint = "localhost:5432"
username = "postgres"
password = "123456"
database = "wparse"
table = "http_request_logs"
schema = "public"
batch = 1000
cursor_column = "id"
cursor_type = "int"
```

## 3. 配置项说明

### 3.1 必填项

| 参数 | 说明 |
| --- | --- |
| `endpoint` | PostgreSQL 地址，格式为 `host:port` |
| `database` | 数据库名 |
| `table` | 目标表名 |
| `cursor_column` | 增量游标列 |

### 3.2 可选项

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `username` | `root` | 用户名 |
| `password` | `dayu` | 密码 |
| `schema` | `public` | schema 名 |
| `batch` | `5000` | 每批读取条数，范围 ` > 0` |
| `cursor_type` | `int` | `int` 或 `time` |
| `start_from` | 无 | 首次启动且无 checkpoint 时的起点 |
| `start_from_format` | 无 | 仅 `time` 游标使用，用于指定 `start_from` 的输入格式 |
| `poll_interval_ms` | `1000` | 没有新数据时的轮询间隔 |
| `error_backoff_ms` | `2000` | 查询失败时的退避间隔 |

## 4. 游标类型

### 4.1 `cursor_type = "int"`

适用于以下列类型：

- `smallint`
- `integer`
- `bigint`
- `smallserial`
- `serial`
- `bigserial`
- `numeric`
- `decimal`

示例：

```toml
params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  cursor_column = "id",
  cursor_type = "int"
}
```

如果游标列是 `numeric` / `decimal`：

- checkpoint 中保存数据库返回的原始文本
- 下次查询时通过 `$1::numeric` 交给 PostgreSQL 比较
- connector 不做精度标准化

### 4.2 `cursor_type = "time"`

适用于以下列类型：

- `timestamp with time zone`
- `timestamp without time zone`
- `timestamp`
- `date`

不支持：

- `time without time zone`
- 文本时间列

示例：

```toml
params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  cursor_column = "create_time",
  cursor_type = "time"
}
```

## 5. start_from 的使用

`start_from` 只在下面这个条件下生效：

- 当前没有 checkpoint

如果已经存在 checkpoint，那么会优先使用 checkpoint，忽略 `start_from`。

也就是说：

- `start_from` 只决定第一次从哪里开始
- 后续增量读取完全由 checkpoint 推进

### 5.1 int 游标示例

```toml
params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  cursor_column = "id",
  cursor_type = "int",
  start_from = "1000"
}
```

### 5.2 time 游标示例

```toml
params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  cursor_column = "create_time",
  cursor_type = "time",
  start_from = "2026-04-16 16:31:25",
  start_from_format = "%Y-%m-%d %H:%M:%S"
}
```

## 6. start_from_format 的使用

`start_from_format` 只给 `cursor_type = "time"` 使用。

它的作用是告诉 connector：`start_from` 应该按什么格式解析。

支持以下值：

- `unix`
- `unix_s`
- `unix_ms`
- chrono pattern，例如 `%Y-%m-%d %H:%M:%S`

注意：

- 大小写敏感
- `UnixMillis`、`UnixSeconds` 这类写法当前不支持
- `start_from_format` 不能单独配置，必须和 `start_from` 一起出现

### 6.1 Unix 秒示例

```toml
params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  cursor_column = "create_time",
  cursor_type = "time",
  start_from = "1776328285",
  start_from_format = "unix_s"
}
```

`1776328285` 是 10 位 Unix 秒。如果 PostgreSQL session `TimeZone` 为 `Asia/Shanghai`，则对应：

```text
2026-04-16 16:31:25 +0800
```

### 6.2 Unix 毫秒示例

```toml
params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  cursor_column = "create_time",
  cursor_type = "time",
  start_from = "1776328285000",
  start_from_format = "unix_ms"
}
```

### 6.3 自定义格式示例

```toml
params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  cursor_column = "create_time",
  cursor_type = "time",
  start_from = "2026-04-16 16:31:25",
  start_from_format = "%Y-%m-%d %H:%M:%S"
}
```

### 6.4 不配置 start_from_format 的行为

如果 `cursor_type = "time"` 且没有配置 `start_from_format`，connector 会按内置规则尝试解析：

- RFC3339
- `%Y-%m-%d %H:%M:%S%.f`
- `%Y-%m-%dT%H:%M:%S%.f`
- `%Y-%m-%d`
- 10 位 Unix 秒
- 13 位 Unix 毫秒

对于没有显式时区的信息，以及 Unix 秒/毫秒，统一按 Source 启动时 PostgreSQL 当前连接的 session `TimeZone` 解释。

如果输入中已经显式携带时区，则保留用户输入的时区语义，不再转换到 session `TimeZone`。

## 7. 查询行为

### 7.1 有下界时

以下两种情况会带下界查询：

- 已有 checkpoint
- 没有 checkpoint，但配置了 `start_from`

查询逻辑等价于：

```sql
WHERE cursor_column > lower_bound
ORDER BY cursor_column ASC
LIMIT batch
```

### 7.2 没有下界时

如果既没有 checkpoint，也没有 `start_from`，则不会带 `WHERE > $1`，而是直接从最小游标开始读取：

```sql
ORDER BY cursor_column ASC
LIMIT batch
```

### 7.3 无新数据时

当没有新数据时：

- source 不会返回 EOF
- 会按 `poll_interval_ms` 持续轮询

## 8. Checkpoint

checkpoint 文件固定保存在：

```text
./.run/.checkpoints/{source_key}.json
```

例如 source 名字是 `postgres_logs`，则 checkpoint 文件可能是：

```text
./.run/.checkpoints/postgres_logs.json
```

示例内容：

```json
{
  "version": 1,
  "cursor_type": "time",
  "cursor_column": "create_time",
  "last_cursor_raw": "2026-04-16T16:31:25.000000+08:00",
  "updated_at": "2026-04-17T02:30:00Z"
}
```

需要注意：

- checkpoint 记录的是“source 已读取到哪里”
- 它不是“下游已经成功写入到哪里”
- 如果你修改了 `cursor_column` 或 `cursor_type`，旧 checkpoint 可能不再兼容

如果你想重新从新的起点开始读取，需要删除旧 checkpoint 后再启动。

## 9. 返回数据格式

每条记录会被转成 JSON 文本，并自动追加一个固定字段：

```json
{
  "warp_parse_table": "http_request_logs"
}
```

如果源表里原本就有同名字段，connector 注入的值会覆盖原字段。

## 10. 对表结构的要求

要想稳定增量读取，`cursor_column` 必须满足：

- 单调递增
- 全局唯一，或者业务上能保证同一游标值不会被单批截断

推荐：

- `bigint` 自增主键
- 唯一且递增的 `timestamptz`
- 唯一且递增的 `numeric`

不推荐：

- 可能回写旧值的更新时间字段
- 会重复且顺序不稳定的业务时间字段

时间游标尤其要注意：

- 如果同一个时间值会在多批之间被截断，可能出现漏读
- 这种情况属于游标字段选型问题，不是 connector 兜底范围

## 11. 常见配置示例

### 11.1 自增 id 增量采集

```toml
[[sources]]
name = "postgres_id_source"
connector_id = "postgres_src"

params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  schema = "public",
  batch = 1000,
  cursor_column = "id",
  cursor_type = "int"
}
```

### 11.2 timestamptz 增量采集

```toml
[[sources]]
name = "postgres_time_source"
connector_id = "postgres_src"

params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  schema = "public",
  batch = 1000,
  cursor_column = "create_time",
  cursor_type = "time",
  start_from = "2026-04-16T16:31:25+08:00"
}
```

### 11.3 timestamptz + Unix 秒起点

```toml
[[sources]]
name = "postgres_time_source"
connector_id = "postgres_src"

params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  schema = "public",
  batch = 1000,
  cursor_column = "create_time",
  cursor_type = "time",
  start_from = "1776328285",
  start_from_format = "unix_s"
}
```

### 11.4 timestamp + 自定义格式起点

```toml
[[sources]]
name = "postgres_time_source"
connector_id = "postgres_src"

params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  schema = "public",
  batch = 1000,
  cursor_column = "create_time",
  cursor_type = "time",
  start_from = "2026-04-16 16:31:25",
  start_from_format = "%Y-%m-%d %H:%M:%S"
}
```

## 12. 使用建议

- 优先使用整数游标
- 如果必须用时间游标，优先使用唯一且递增的 `timestamptz`
- 首次历史回补时可以配 `start_from`
- 追平后增量依赖 checkpoint，不要频繁改 `start_from`
- 如果改了游标列或游标类型，记得同步清理旧 checkpoint
- 大表场景先从 `batch = 1000` 开始，按实际压力再调
