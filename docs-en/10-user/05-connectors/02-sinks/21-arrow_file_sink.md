# Arrow File Sink

The `arrow-file` sink encodes record batches as Arrow IPC payloads and appends them to a local file.

Each batch is written as a length-prefixed frame:

- outer frame: `[4B BE length][payload]`
- payload: the same tagged Arrow IPC frame used by `arrow-ipc`

## Connector Definition

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

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `base` | string | `./data/out_dat` | Output directory |
| `file` | string | `default.arrow` | Output file name |
| `tag` | string | `default` | Arrow frame tag |
| `fields` | array | `[]` | Schema definition array |
| `sync` | bool | `false` | Call `fsync` after each write |

## Notes

- The file stores a sequence of Arrow frames, not JSON/text lines
- `sink_str/sink_bytes` are no-op; this sink is intended for record output
- The on-disk payload format is aligned with `arrow-ipc`, which is convenient for local replay or offline inspection
