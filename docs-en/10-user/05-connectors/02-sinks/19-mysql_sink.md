# MySQL Sink

The MySQL sink is used to write parsed records into MySQL tables. It generates `INSERT IGNORE` statements based on `columns`, making it suitable for idempotent retry scenarios. It only accepts Record data (raw input is not supported).

## Connector Definition

It's recommended to use the built-in template from the repository (located at `connectors/sink.d/50-mysql.toml`):

```toml
[[connectors]]
id = "mysql_sink"
type = "mysql"
allow_override = ["endpoint", "username", "password", "database", "table", "columns", "batch_size"]

[connectors.params]
endpoint = "localhost:3306"
username = "root"
password = "123456"
database = "wparse"
table = "nginx_logs"
columns = ["sip", "timestamp", "http/request", "status", "size", "referer", "http/agent", "wp_event_id"]
batch_size = 1024
```

## Available Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `endpoint` | string | MySQL address (`host:port`, required) |
| `username` | string | Username (optional, defaults to `root`) |
| `password` | string | Password (optional) |
| `database` | string | Target database (required) |
| `table` | string | Target table name (required) |
| `columns` | array | List of column names, determines field write order (required) |
| `batch_size` | int | Batch write count (optional) |

## Configuration Example

### Basic Usage

```toml
version = "2.0"

[sink_group]
name = "all"
oml = ["/*"]
batch_timeout_ms=5000   # Auto-insert when data doesn't meet batch size within this timeout
parallel = 8

[[sink_group.sinks]]
name = "main"
connect = "mysql_sink"

[sink_group.sinks.params]
endpoint = "localhost:3306"
username = "root"
password = "123456"
database = "wparse"
table = "nginx_logs"
columns = ["sip", "timestamp", "http/request", "status", "size", "referer", "http/agent", "wp_event_id"]
batch_size = 1024   
```

## Notes

- Field names in `columns` must match the OML output fields; missing table fields will be written as `NULL`.
- Connection string can be overridden via the `MYSQL_URL` environment variable (format: `mysql://user:pass@host:port/db`).
- For end-to-end examples, refer to `wp-examples/extensions/tcp_mysql/README.md`.
