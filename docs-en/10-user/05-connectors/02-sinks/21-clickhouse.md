# ClickHouse Sink

ClickHouse sink writes parsed records to ClickHouse database in batches, which is ideal for large-scale log analysis and real-time data query scenarios.

## Connector Definition

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
database = "default"
table = "wp_nginx"
username = "default"
password = "default"
timeout_secs = 30
max_retries = 3
```

## Available Parameters

| Parameter | Type | Description |
|------|------|------|
| `endpoint` | string | ClickHouse endpoint address, format: `http://host:port` or `https://host:port` (required) |
| `database` | string | Target database name (required) |
| `table` | string | Target table name (required) |
| `username` | string | Authentication username (required) |
| `password` | string | Authentication password (optional, default empty) |
| `timeout_secs` | int | Request timeout in seconds (default `30`) |
| `max_retries` | int | Retry times when write fails (default `3`, `-1` for infinite retries) |

## Configuration Example

### Basic Usage

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

### HTTPS Connection

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