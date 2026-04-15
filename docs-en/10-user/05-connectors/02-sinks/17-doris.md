# Doris Sink

Doris sink writes records to Apache Doris in batches through the Stream Load API, which is suitable for high-throughput log and detail-data ingestion.

## Connector Definition

Use the built-in template in the repository (`connectors/sink.d/60-doris.toml`):

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

## Available Parameters

| Parameter | Type | Description |
|------|------|------|
| `endpoint` | string | Doris Stream Load endpoint (required). Use BE HTTP port, for example `http://host:8040`. |
| `user` | string | Doris username (optional, default `root`) |
| `password` | string | Doris password (optional) |
| `database` | string | Target database (required) |
| `table` | string | Target table (required) |
| `timeout_secs` | int | Request timeout in seconds (default `30`) |
| `max_retries` | int | Retry times when write fails (default `3`) |
| `batch_size` | int | Batch write size (default `1000000`) |
| `headers` | table | Optional Stream Load headers, such as `columns`, `strict_mode`, `max_filter_ratio` |

## Configuration Examples

### Basic Usage (from `extensions/doris`)

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

### Stream Load Column Mapping

```toml
[sink_group.sinks.params.headers]
strip_outer_array = "false"
max_filter_ratio = "0.1"
columns = "wp_event_id,wp_src_key,sip,timestamp,`http/request`,size,referer,`http/agent`"
```

## Notes

- Use BE HTTP port for `endpoint` (example: `8040`), not FE query port.
- Create database/table before writing. See `wp-examples/extensions/doris/test.sql`.
- If field names include `/` (for example `http/request`), wrap them in backticks in `headers.columns`.
- For an end-to-end example, see `wp-examples/extensions/doris/README.md`.
