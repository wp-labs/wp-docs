# HTTP 源配置

本文档介绍通用 HTTP 源（kind=`http`）的使用方式、请求协议，以及与 HTTP Sink 的联动示例。

## 功能概览

`HttpSource` 是一个基于 web服务 的接收型 Source。
### 支持的参数
1. port监听的端口。
2. path监听的路径。
> 不同的source之间可以共用一个端口，只要保证path不同即可。

### 支持的功能
#### 格式选择
支持json格式和ndjson格式，通过请求参数 `fmt` 或者请求头`Content-Type`指定输入格式，`fmt` 参数优先级高于 Content-Type，且两者都不指定时默认使用 `json`。
Content-Type 映射规则：
    - `application/json` => `json`
    - `application/x-ndjson` => `ndjson`
    - `application/ndjson` => `ndjson`
#### 压缩选择
支持请求以gzip格式压缩或none(不压缩)，通过请求参数 `compression` 或者请求头`Content-Encoding`指定压缩方式。

## 连接器定义（source.d）

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

## 源配置（wpsrc.toml）

### 基础配置

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

## 请求协议

### 1. 输入格式选择

支持以下两种输入格式：

- `json`
- `ndjson`

## 解析规则

### `json`

- 请求体先整体解析为一个 JSON 值
- 如果顶层是数组，则逐元素拆成多条事件
- 如果顶层不是数组，则自动包装为单元素数组
- 每个元素最终会被序列化成一行 JSON 字符串，作为一条 `SourceEvent` 的 payload

示例：

```json
[{"a":1},{"b":2}]
```

会生成两条事件 payload：

```json
{"a":1}
{"b":2}
```

### `ndjson`

- 按行切分请求体
- 忽略空行
- 每一行都必须是合法 JSON
- 每一行最终会被规范化成一行 JSON 字符串，作为一条事件

示例：

```text
{"a":1}
{"b":2}
```

如果其中一行不是合法 JSON，请求会失败。

## 发送示例

### 示例 1：发送 JSON 数组

```bash
curl -X POST "http://127.0.0.1:18080/ingest" \
  -H "Content-Type: application/json" \
  --data '[{"message":"hello"},{"message":"world"}]'
```

也可以显式通过请求参数覆盖格式：

```bash
curl -X POST "http://127.0.0.1:18080/ingest?fmt=json" \
  -H "Content-Type: application/x-ndjson" \
  --data '[{"message":"hello"},{"message":"world"}]'
```

### 示例 2：发送 NDJSON

```bash
curl -X POST "http://127.0.0.1:18080/ingest?fmt=ndjson" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary $'{"message":"hello"}\n{"message":"world"}\n'
```

### 示例 3：发送 gzip 压缩的 NDJSON

```bash
printf '{"message":"hello"}\n{"message":"world"}\n' \
  | gzip -c \
  | curl -X POST "http://127.0.0.1:18080/ingest?fmt=ndjson" \
      -H "Content-Encoding: gzip" \
      --data-binary @-
```

### 成功响应示例

```text
HTTP/1.1 200 OK

OK
```

### 失败响应示例

当 NDJSON 中某一行不是合法 JSON 时：

```bash
curl -X POST "http://127.0.0.1:18080/ingest?fmt=ndjson" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary $'{"ok":1}\nnot-json\n'
```

将得到：

```text
HTTP/1.1 400 Bad Request

parse body failed: invalid ndjson line 2
```

## 相关文档

- [源配置基础](./01-sources_basics.md)
- [HTTP Sink 配置](../02-sinks/06-http_sink.md)
