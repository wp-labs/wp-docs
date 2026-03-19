# Doris Sink

Doris sink 用于通过 Stream Load API 将数据批量写入 Apache Doris，适合日志类、明细类数据的高吞吐落库场景。

## 连接器定义

推荐使用仓库自带模板（位于 `connectors/sink.d/60-doris.toml`）：

```toml
[[connectors]]
id = "doris_sink"
type = "doris"
allow_override = [
  "endpoint",
  "user",
  "password",
  "database",
  "table",
  "timeout_secs",
  "max_retries",
  "headers",
  "batch_size"
]

[connectors.params]
endpoint = "http://localhost:8040"
user = "${SEC_USERNAME}"
password = "${SEC_PASSWORD}"
database = "test_db"
table = "events_parsed"
timeout_secs = 30
max_retries = 3
batch_size = 100_0000

[connectors.params.headers]
strip_outer_array = "false"
max_filter_ratio = "0.1"
strict_mode = "false"
```

## 可用参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `endpoint` | string | Doris Stream Load 地址（必填，推荐使用 BE HTTP 端口，如 `http://host:8040`） |
| `user` | string | Doris 用户名（可选，默认 `root`） |
| `password` | string | Doris 密码（可选） |
| `database` | string | 目标数据库（必填） |
| `table` | string | 目标表名（必填） |
| `timeout_secs` | int | 单次请求超时秒数（默认 `30`） |
| `max_retries` | int | 写入失败重试次数（默认 `3`） |
| `batch_size` | int | 批量写入大小（默认 `1000000`） |
| `headers` | table | Stream Load 自定义 Header（可选），如 `columns`、`strict_mode`、`max_filter_ratio` |

## 配置示例

### 基础用法（参考 `extensions/doris`）

```toml
version = "2.0"

[sink_group]
name = "doris"
rule = ["*"]
batch_timeout_ms = 5000
parallel = 4

[[sink_group.sinks]]
name = "doris_stream_load"
connect = "doris_sink"

[sink_group.sinks.params]
endpoint = "http://localhost:8040"
database = "test_db"
table = "wp_nginx"
user = "${SEC_USERNAME}"
password = "${SEC_PASSWORD}"
timeout_secs = 30
max_retries = 1
batch_size = 10_0000
```

### 指定 Stream Load 列映射

```toml
[sink_group.sinks.params.headers]
strip_outer_array = "false"
max_filter_ratio = "0.1"
columns = "wp_event_id,wp_src_key,sip,timestamp,`http/request`,size,referer,`http/agent`"
```
