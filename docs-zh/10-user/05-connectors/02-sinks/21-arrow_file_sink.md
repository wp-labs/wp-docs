# Arrow File Sink

`arrow-file` sink 用于将记录批编码为 Arrow IPC 负载，并追加写入本地文件。

每个批次写入为一条长度前缀 frame：

- 外层 frame：`[4B BE length][payload]`
- 内层 payload：与 `arrow-ipc` 相同的带 tag Arrow IPC frame

## 连接器定义

```toml
[[connectors]]
id = "arrow_file_sink"
type = "arrow-file"
allow_override = ["base", "file", "tag", "fields", "sync"]

[connectors.params]
base = "./data/out_dat"
file = "default.arrow"
tag = "default"
sync = false
fields = [
  { name = "sip", type = "ip" },
  { name = "dport", type = "digit" }
]
```

## 可用参数

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `base` | string | `./data/out_dat` | 输出目录 |
| `file` | string | `default.arrow` | 输出文件名 |
| `tag` | string | `default` | Arrow frame 标签 |
| `fields` | array | `[]` | Schema 定义数组 |
| `sync` | bool | `false` | 每次写入后调用 `fsync` |

## 注意事项

- 文件内容是 Arrow frame 序列，不是 JSON/文本行
- `sink_str/sink_bytes` 为 no-op；该 sink 主要用于记录型输出
- 磁盘格式与 `arrow-ipc` 对齐，便于本地回放和离线检查
