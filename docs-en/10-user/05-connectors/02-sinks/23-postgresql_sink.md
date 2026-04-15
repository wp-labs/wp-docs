# PostgreSQL Sink

The PostgreSQL sink writes parsed records into PostgreSQL tables. It builds `INSERT IGNORE` statements from `columns`, which is suitable for idempotent retry scenarios. It only accepts Record data (raw input is not supported).

## Connector Definition

Use the built-in template (located at `connectors/sink.d/50-mysql.toml`; PostgreSQL uses the same configuration set as MySQL):

```toml
[[connectors]]
id = "postgresql_sink"
type = "postgresql"
allow_override = ["endpoint", "username", "password", "database", "table", "columns", "batch_size"]

[connectors.params]
endpoint = "localhost:5432"
username = "${SEC_USERNAME}"
password = "${SEC_PASSWORD}"
database = "wparse"
table = "nginx_logs"
columns = ["sip", "timestamp", "http/request", "status", "size", "referer", "http/agent", "wp_event_id"]
batch_size = 1024
```

## Parameters

| Parameter | Type | Description |
|------|------|------|
| `endpoint` | string | PostgreSQL endpoint (`host:port`, required) |
| `username` | string | Username (optional, default `postgres`) |
| `password` | string | Password (optional) |
| `database` | string | Target database (required) |
| `table` | string | Target table name (required) |
| `columns` | array | Column list that defines write order (required) |
| `batch_size` | int | Batch insert size (optional) |

## Configuration Example

### Basic Usage

```toml
version = "2.0"

[sink_group]
name = "all"
oml = ["/*"]
batch_timeout_ms=5000   # Auto flush when batch size is not reached within this time window
parallel = 8

[[sink_group.sinks]]
name = "main"
connect = "postgresql_sink"

[sink_group.sinks.params]
endpoint = "localhost:5432"
username = "${SEC_USERNAME}"
password = "${SEC_PASSWORD}"
database = "wparse"
table = "nginx_logs"
columns = ["sip", "timestamp", "http/request", "status", "size", "referer", "http/agent", "wp_event_id"]
batch_size = 1024
```

## Notes

- Field names in `columns` must match OML output fields. Missing table columns are written as `NULL`.
- You can override the connection string with `POSTGRESQL_URL` (format: `postgresql://user:pass@host:port/db`).
- PostgreSQL uses the same configuration keys as MySQL. Only connector `type`, port, and connection details differ.
