# Arrow IPC Sink

`arrow-ipc` sink 用于将记录批量编码为 Arrow IPC 负载，并通过 TCP 发送给下游消费端。

当前实现仅支持 TCP 目标地址，发送协议为长度前缀帧（4 字节大端长度 + IPC 负载）。

## 连接器定义

```toml
[[connectors]]
id = "arrow_ipc_sink"
type = "arrow-ipc"
allow_override = ["target", "tag", "fields"]

[connectors.params]
target = "tcp://127.0.0.1:9800"
tag = "default"
fields = [
  { name = "sip", type = "ip" },
  { name = "dport", type = "digit" },
  { name = "action", type = "chars", nullable = false }
]
```

## 可用参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `target` | string | `tcp://127.0.0.1:9800` | 目标地址，必须是 `tcp://host:port` |
| `tag` | string | `default` | Arrow IPC 帧标签 |
| `fields` | array | `[]` | Schema 定义数组，元素格式为 `{name,type,nullable?}` |

`fields[].type` 支持：`chars`、`digit`、`float`、`bool`、`time`、`ip`、`hex`、`array<...>`（大小写不敏感）。

## 配置示例

```toml
version = "2.0"

[sink_group]
name = "/sink/arrow"
oml = ["logs"]

[[sink_group.sinks]]
name = "arrow_out"
connect = "arrow_ipc_sink"

[sink_group.sinks.params]
target = "tcp://127.0.0.1:9800"
tag = "flow-log"
fields = [
  { name = "sip", type = "ip" },
  { name = "dip", type = "ip" },
  { name = "dport", type = "digit" },
  { name = "action", type = "chars" },
  { name = "event_time", type = "time" }
]
```

## 传输与容错行为

- 每次发送一个 frame：`[4B BE length][Arrow IPC payload]`
- 初始连接失败会导致 sink 构建失败
- 运行期发送失败后进入断线状态，按退避策略重连：`1s -> 2s -> 4s ... -> 30s`（上限 30 秒）
- 断线期间数据会被丢弃（当前无 WAL/补发机制）
- `sink_str/sink_bytes` 等原始接口为 no-op，`arrow-ipc` 主要用于记录型输出

## 注意事项

- `target` 目前不支持 `unix://`、`http://` 等非 TCP 地址
- `fields` 需要与输出记录结构保持一致，类型不匹配会导致批次转换失败
