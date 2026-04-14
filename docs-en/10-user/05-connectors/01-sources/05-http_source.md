# HTTP Source Configuration

This document describes how to use the generic HTTP source (kind=`http`), its request protocol, and example interactions with the HTTP Sink.

## Feature Overview

`HttpSource` is a receiving Source based on a web service.
### Supported Parameters
1. `port`: the port to listen on.
2. `path`: the path to listen on.
> Different sources can share the same port as long as their paths are different.

### Supported Features
#### Format Selection
Supports both `json` and `ndjson` formats. You can specify the input format through the request parameter `fmt` or the request header `Content-Type`. The `fmt` parameter has higher priority than `Content-Type`. If neither is specified, `json` is used by default.
Content-Type mapping rules:
    - `application/json` => `json`
    - `application/x-ndjson` => `ndjson`
    - `application/ndjson` => `ndjson`
#### Compression Selection
Supports requests compressed with `gzip` or `none` (no compression). You can specify the compression method through the request parameter `compression` or the request header `Content-Encoding`.

## Connector Definition (`source.d`)

```toml
# connectors/source.d/15-http.toml
[[connectors]]
id = "http_src"
type = "http"
allow_override = ["port", "path"]

[connectors.params]
port = 18080
path = "/ingest"
```

## Source Configuration (`wpsrc.toml`)

### Basic Configuration

```toml
[[sources]]
key = "http_ingest"
connect = "http_src"
enable = true
tags = ["source:http", "env:dev"]

[[sources.params]]
port = 18080
path = "/ingest"
```

## Request Protocol

### 1. Input Format Selection

The following two input formats are supported:

- `json`
- `ndjson`

## Parsing Rules

### `json`

- The request body is first parsed as a whole into a JSON value
- If the top level is an array, each element is split into a separate event
- If the top level is not an array, it is automatically wrapped into a single-element array
- Each element is ultimately serialized into a single-line JSON string as the payload of one `SourceEvent`

Example:

```json
[{"a":1},{"b":2}]
```

This produces two event payloads:

```json
{"a":1}
{"b":2}
```

### `ndjson`

- The request body is split line by line
- Empty lines are ignored
- Each line must be valid JSON
- Each line is ultimately normalized into a single-line JSON string as one event

Example:

```text
{"a":1}
{"b":2}
```

If any line is not valid JSON, the request fails.

## Sending Examples

### Example 1: Send a JSON Array

```bash
curl -X POST "http://127.0.0.1:18080/ingest" \
  -H "Content-Type: application/json" \
  --data '[{"message":"hello"},{"message":"world"}]'
```

You can also explicitly override the format through a request parameter:

```bash
curl -X POST "http://127.0.0.1:18080/ingest?fmt=json" \
  -H "Content-Type: application/x-ndjson" \
  --data '[{"message":"hello"},{"message":"world"}]'
```

### Example 2: Send NDJSON

```bash
curl -X POST "http://127.0.0.1:18080/ingest?fmt=ndjson" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary $'{"message":"hello"}\n{"message":"world"}\n'
```

### Example 3: Send gzip-compressed NDJSON

```bash
printf '{"message":"hello"}\n{"message":"world"}\n' \
  | gzip -c \
  | curl -X POST "http://127.0.0.1:18080/ingest?fmt=ndjson" \
      -H "Content-Encoding: gzip" \
      --data-binary @-
```

### Successful Response Example

```text
HTTP/1.1 200 OK

OK
```

### Failed Response Example

When one line in NDJSON is not valid JSON:

```bash
curl -X POST "http://127.0.0.1:18080/ingest?fmt=ndjson" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary $'{"ok":1}\nnot-json\n'
```

You will get:

```text
HTTP/1.1 400 Bad Request

parse body failed: invalid ndjson line 2
```

## Related Documentation

- [Source Configuration Basics](./01-sources_basics.md)
- [HTTP Sink Configuration](../02-sinks/22-http.md)
