# ClickHouse Sink

ClickHouse sink 用于将解析后的记录批量写入 ClickHouse 数据库，适合大规模日志分析和实时数据查询场景。

## 连接器定义

```toml
[[connectors]]
id = "clickhouse_sink"
type = "clickhouse"
allow_override = [
  "endpoint",
  "database",
  "table",
  "username",
  "password",
  "timeout_secs",
  "max_retries"
]

[connectors.params]
endpoint = "http://clickhouse-server:8123"
database = ""
table = ""
username = ""
password = ""
timeout_secs = 30
max_retries = 3
```

## 可用参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `endpoint` | string | ClickHouse 端点地址，格式：`http://host:port` 或 `https://host:port`（必填） |
| `database` | string | 目标数据库名称（必填） |
| `table` | string | 目标表名称（必填） |
| `username` | string | 认证用户名（必填） |
| `password` | string | 认证密码（可选，默认为空） |
| `timeout_secs` | int | 单次请求超时秒数（默认 `30`） |
| `max_retries` | int | 写入失败重试次数（默认 `3`，`-1` 表示无限重试） |

## 配置示例

### 基础用法

```toml
version = "2.0"

[sink_group]
name = "clickhouse"
rule = ["*"]
batch_timeout_ms = 5000
parallel = 4

[[sink_group.sinks]]
name = "clickhouse_stream_load"
connect = "clickhouse_sink"

[sink_group.sinks.params]
endpoint = "http://localhost:8123"
database = "default"
table = "wp_nginx"
username = "default"
password = "default"
timeout_secs = 30
max_retries = 3
```

### HTTPS 连接

```toml
[sink_group.sinks.params]
endpoint = "https://clickhouse.example.com:8443"
database = "production"
table = "logs"
username = "app_user"
password = "secure_password"
timeout_secs = 60
max_retries = 5
```