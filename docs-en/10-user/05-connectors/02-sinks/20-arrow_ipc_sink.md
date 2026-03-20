# Arrow IPC Sink

The `arrow-ipc` sink encodes record batches as Arrow IPC payloads and sends them to a downstream consumer over TCP.

Current implementation supports TCP targets only. The wire format is length-prefixed frames (`4-byte big-endian length + IPC payload`).

## Connector Definition

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

## Available Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target` | string | `tcp://127.0.0.1:9800` | Target endpoint, must be `tcp://host:port` |
| `tag` | string | `default` | Arrow IPC frame tag |
| `fields` | array | `[]` | Schema definitions, each item is `{name,type,nullable?}` |

Supported `fields[].type` values: `chars`, `digit`, `float`, `bool`, `time`, `ip`, `hex`, `array<...>` (case-insensitive).

## Configuration Example

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

## Transport and Fault-Tolerance Behavior

- Each send writes one frame: `[4B BE length][Arrow IPC payload]`
- Initial connection failure makes sink build fail
- Runtime send failures switch to disconnected mode, then reconnect with backoff: `1s -> 2s -> 4s ... -> 30s` (capped at 30 seconds)
- Data is dropped while disconnected (no WAL/replay in current implementation)
- Raw interfaces (`sink_str/sink_bytes`) are no-op; `arrow-ipc` is intended for record output

## Notes

- `target` currently rejects non-TCP schemes such as `unix://` or `http://`
- Keep `fields` aligned with actual output records; type mismatch will fail batch conversion
