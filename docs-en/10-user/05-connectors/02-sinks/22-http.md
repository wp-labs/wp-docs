# HTTP Sink

HTTP sink sends parsed records to HTTP/HTTPS endpoints in various formats, suitable for webhooks, API integration, and custom data pipeline scenarios.

## Connector Definition
```toml
[[connectors]]
id = "http_sink"
type = "http"
allow_override = [
  "endpoint",
  "method",
  "username",
  "password",
  "headers",
  "fmt",
  "batch_size",
  "timeout_secs",
  "max_retries",
  "compression"
]

[connectors.params]
endpoint = "http://localhost:8080/webhook"
method = "POST"
username = "${SEC_USERNAME}"
password = "${SEC_PASSWORD}"
fmt = "json"
batch_size = 100
timeout_secs = 60
max_retries = 3
compression = "none"
```

## Available Parameters

| Parameter | Type | Description |
|------|------|------|
| `endpoint` | string | HTTP(S) endpoint URL (required) |
| `method` | string | HTTP method: GET, POST, PUT, PATCH, DELETE (default `POST`) |
| `username` | string | HTTP Basic authentication username (optional) |
| `password` | string | HTTP Basic authentication password (optional) |
| `headers` | object | Custom HTTP headers in JSON object format (optional) |
| `fmt` | string | Output format: `json`, `ndjson`, `csv`, `kv`, `raw`, `proto-text` (default `json`) |
| `batch_size` | int | Batch size: 1 for single record, >1 for batch sending (default `1`) |
| `timeout_secs` | int | Request timeout in seconds (default `60`) |
| `max_retries` | int | Retry times on failure: -1 for infinite retries, 0 for no retry (default `3`) |
| `compression` | string | Data compression: `none`, `gzip` (default `none`) |

## Output Formats
Setting the output format automatically sets the corresponding `content-type`.

### JSON Format (`fmt = "json"`)
Sends records as a JSON array:
```json
[
  {"field1": "value1", "field2": "value2"},
  {"field1": "value3", "field2": "value4"}
]
```

### NDJSON Format (`fmt = "ndjson"`)
Sends records as newline-delimited JSON (one record per line):
```
{"field1": "value1", "field2": "value2"}
{"field1": "value3", "field2": "value4"}
```

### CSV Format (`fmt = "csv"`)
Sends records in CSV format (with header):
```
field1,field2
value1,value2
value3,value4
```

### KV Format (`fmt = "kv"`)
Sends records as key-value pairs (one record per line):
```
field1=value1 field2=value2
field1=value3 field2=value4
```

### Raw Format (`fmt = "raw"`)
Sends raw message content without parsing.

### Proto-Text Format (`fmt = "proto-text"`)
Sends records in Protocol Buffer text format (without field names).

## Compression

When `compression = "gzip"` is enabled:
- Request body is compressed with gzip
- Automatically adds `Content-Encoding: gzip` header
- Reduces network bandwidth usage, especially suitable for large batches
- Recommended when batch size > 1000

## Authentication

### HTTP Basic Authentication
```toml
[connectors.params]
endpoint = "https://api.example.com/webhook"
username = "${SEC_USERNAME}"
password = "${SEC_PASSWORD}"
```

### Custom Headers (e.g., Bearer Token)
```toml
[connectors.params]
endpoint = "https://api.example.com/webhook"
[connectors.params.headers]
Authorization="Bearer YOUR_TOKEN_HERE"
```

## Configuration Examples

### Example 1: Simple Webhook (Single Record Sending)

```toml
version = "2.0"

[sink_group]
name = "webhook"
rule = ["*"]
batch_timeout_ms = 1000
parallel = 2

[[sink_group.sinks]]
name = "http_webhook"
connect = "http_sink"

[sink_group.sinks.params]
endpoint = "http://localhost:8080/webhook"
method = "POST"
fmt = "json"
batch_size = 1
timeout_secs = 30
max_retries = 3
compression = "none"
```

Complete examples and test server are available in `https://github.com/wp-labs/wp-examples` at `extensions/http/test_server.py`.

## Retry Strategy

HTTP sink implements exponential backoff retry mechanism:
- Initial retry delay: 1 second
- Delay doubles with each retry (2s, 4s, 8s...)
- Retries on 5xx server errors and network failures
- Does not retry on 4xx client errors (except 429 Too Many Requests)

## Performance Optimization Tips

1. **Batch Size**: Use larger batches (1000-10000) for high throughput scenarios
2. **Compression**: Enable gzip compression when batch > 1000 records
3. **Concurrency**: Increase `parallel` setting to improve concurrent processing
4. **Format**: `ndjson` format performs better than `json` in large batch scenarios
5. **Timeout**: Adjust `timeout_secs` based on endpoint response time
