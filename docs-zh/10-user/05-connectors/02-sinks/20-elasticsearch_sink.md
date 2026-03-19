# Elasticsearch Sink

Elasticsearch sink 用于将解析后的记录批量写入 Elasticsearch 索引，适合检索、聚合与可视化场景。

## 连接器定义

推荐使用仓库自带模板（位于 `connectors/sink.d/90-elasticsearch.toml`）：

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
username = "${SEC_USERNAME}"
password = "${SEC_PASSWORD}"
index = "wp_nginx"
timeout_secs = 30
max_retries = 3
batch_size = 100_0000
```

## 可用参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `protocol` | string | 协议（`http` 或 `https`，默认 `http`） |
| `host` | string | Elasticsearch 主机地址（必填） |
| `port` | string/int | Elasticsearch 端口（默认 `9200`） |
| `username` | string | 用户名（可选） |
| `password` | string | 密码（可选） |
| `index` | string | 目标索引名称（必填） |
| `timeout_secs` | int | 单次请求超时秒数（默认 `30`） |
| `max_retries` | int | 写入失败重试次数（默认 `3`） |
| `batch_size` | int | 批量写入大小（默认 `1000000`） |

## 配置示例

### 基础用法（参考 `extensions/elasticsearch`）

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
username = "${SEC_USERNAME}"
password = "${SEC_PASSWORD}"
index = "wp_nginx"
timeout_secs = 30
max_retries = 3
batch_size = 100_0000
```

## 注意事项

- 示例环境开启了认证，需提供有效用户名/密码。
- 首次写入通常会自动创建索引，生产环境建议提前规划 mapping 与分片策略。
- 可使用 `_count` 与 `_search` 接口快速验证写入结果。
- 完整示例可参考 `wp-examples/extensions/elasticsearch/README.md`。
