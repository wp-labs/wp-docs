# Elasticsearch Sink

Elasticsearch sink writes parsed records to Elasticsearch indexes in batches, which is useful for search, aggregation, and visualization workloads.

## Connector Definition

Use the built-in template in the repository (`connectors/sink.d/90-elasticsearch.toml`):

```toml
[[connectors]]
id = "elasticsearch_sink"
type = "elasticsearch"
allow_override = [
  "protocol",
  "host",
  "port",
  "username",
  "password",
  "index",
  "timeout_secs",
  "max_retries",
  "batch_size"
]

[connectors.params]
protocol = "http"
host = "localhost"
port = "9200"
username = "elastic"
password = ""
index = "wp_nginx"
timeout_secs = 30
max_retries = 3
batch_size = 100_0000
```

## Available Parameters

| Parameter | Type | Description |
|------|------|------|
| `protocol` | string | Protocol, `http` or `https` (default `http`) |
| `host` | string | Elasticsearch host (required) |
| `port` | string/int | Elasticsearch port (default `9200`) |
| `username` | string | Username (optional) |
| `password` | string | Password (optional) |
| `index` | string | Target index name (required) |
| `timeout_secs` | int | Request timeout in seconds (default `30`) |
| `max_retries` | int | Retry times when write fails (default `3`) |
| `batch_size` | int | Batch write size (default `1000000`) |

## Configuration Example

### Basic Usage (from `extensions/elasticsearch`)

```toml
version = "2.0"

[sink_group]
name = "es"
rule = ["*"]
batch_timeout_ms = 5000
parallel = 4

[[sink_group.sinks]]
name = "es_stream_load"
connect = "elasticsearch_sink"

[sink_group.sinks.params]
protocol = "http"
host = "localhost"
port = "9200"
username = "elastic"
password = "zgVClXP2"
index = "wp_nginx"
timeout_secs = 30
max_retries = 3
batch_size = 100_0000
```

## Notes

- The example environment enables authentication, so valid username/password is required.
- On first write, the index is usually auto-created. In production, define mapping and shard strategy in advance.
- You can use `_count` and `_search` APIs to verify ingestion quickly.
- For an end-to-end example, see `wp-examples/extensions/elasticsearch/README.md`.
