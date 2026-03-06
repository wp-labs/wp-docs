# HTTP Sink

HTTP sink 用于将解析后的记录以多种格式发送到 HTTP/HTTPS 端点，适用于 webhook、API 集成和自定义数据管道场景。

## 连接器定义


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
username = ""
password = ""
fmt = "json"
batch_size = 100
timeout_secs = 60
max_retries = 3
compression = "none"
```

## 可用参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `endpoint` | string | HTTP(S) 端点 URL（必填） |
| `method` | string | HTTP 方法：GET、POST、PUT、PATCH、DELETE（默认 `POST`） |
| `username` | string | HTTP Basic 认证用户名（可选） |
| `password` | string | HTTP Basic 认证密码（可选） |
| `headers` | object | 自定义 HTTP 头，JSON 对象格式（可选） |
| `fmt` | string | 输出格式：`json`、`ndjson`、`csv`、`kv`、`raw`、`proto-text`（默认 `json`） |
| `batch_size` | int | 批量大小：1 表示单条发送，>1 表示批量发送（默认 `1`） |
| `timeout_secs` | int | 请求超时时间（秒，默认 `60`） |
| `max_retries` | int | 请求失败重试次数：-1 表示无限重试，0 表示不重试（默认 `3`） |
| `compression` | string | 数据压缩：`none`、`gzip`（默认 `none`） |

## 输出格式
设置输出格式会自动设置对应的`content-type`.

### JSON 格式 (`fmt = "json"`)
以 JSON 数组形式发送记录：
```json
[
  {"field1": "value1", "field2": "value2"},
  {"field1": "value3", "field2": "value4"}
]
```

### NDJSON 格式 (`fmt = "ndjson"`)
以换行分隔的 JSON 形式发送记录（每行一条记录）：
```
{"field1": "value1", "field2": "value2"}
{"field1": "value3", "field2": "value4"}
```

### CSV 格式 (`fmt = "csv"`)
以 CSV 格式发送记录（包含表头）：
```
field1,field2
value1,value2
value3,value4
```

### KV 格式 (`fmt = "kv"`)
以键值对形式发送记录（每行一条记录）：
```
field1=value1 field2=value2
field1=value3 field2=value4
```

### Raw 格式 (`fmt = "raw"`)
发送原始消息内容，不进行解析。

### Proto-Text 格式 (`fmt = "proto-text"`)
以 Protocol Buffer 文本格式发送记录。(不会添加字段名)

## 压缩

当启用 `compression = "gzip"` 时：
- 请求体使用 gzip 压缩
- 自动添加 `Content-Encoding: gzip` 头
- 减少网络带宽占用，特别适合大批量数据
- 建议批量大小 > 1000 时启用

## 认证

### HTTP Basic 认证
```toml
[connectors.params]
endpoint = "https://api.example.com/webhook"
username = "myuser"
password = "mypassword"
```

### 自定义头（如 Bearer Token）
```toml
[connectors.params]
endpoint = "https://api.example.com/webhook"
[connectors.params.headers]
Authorization="Bearer YOUR_TOKEN_HERE"
```

## 配置示例

### 示例 1：简单 Webhook（单条发送）

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

`https://github.com/wp-labs/wp-examples`中提供了完整示例，和测试服务器 `extensions/http/test_server.py`：



## 重试策略

HTTP sink 实现了指数退避重试机制：
- 初始重试延迟：1 秒
- 每次重试延迟翻倍（2秒、4秒、8秒...）
- 对 5xx 服务器错误和网络故障进行重试
- 不对 4xx 客户端错误重试（429 Too Many Requests 除外）

## 性能优化建议

1. **批量大小**：高吞吐场景使用较大批量（1000-10000）
2. **压缩**：批量 > 1000 条记录时启用 gzip 压缩
3. **并发**：增加 `parallel` 设置以提高并发处理能力
4. **格式**：大批量场景下 `ndjson` 格式性能优于 `json`
5. **超时**：根据端点响应时间调整 `timeout_secs`

