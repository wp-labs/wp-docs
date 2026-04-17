# PostgreSQL Source Documentation

`PostgresSource` is used to continuously read data incrementally from a PostgreSQL table with a single cursor.

It works as follows:

```text
Load the local checkpoint
  -> Build a query with an increasing cursor
  -> Fetch a batch of data from PostgreSQL
  -> Convert each full row into JSON
  -> Append the warp_parse_table field automatically
  -> Return the batch to the upstream pipeline
  -> Update the checkpoint with the cursor value of the last record in the current batch
```

The current version supports only a single cursor. Secondary cursors are not supported, and text-based time columns cannot be used as time cursors.

## 1. Suitable Scenarios

- You need to continuously ingest data incrementally from a PostgreSQL table
- The table has a monotonically increasing cursor column
- You want the source to continue from the last position after a process restart

Suitable cursor columns:

- Auto-incrementing `id`
- A monotonically increasing business sequence number
- `numeric` / `decimal` values that increase monotonically and will not be truncated across batches
- Native PostgreSQL time columns: `timestamp with time zone`, `timestamp without time zone`, `date`

Unsuitable cursor columns:

- Fields whose old values may be rewritten
- Fields with many duplicate values that may be truncated across batches
- Text-based time fields
- `time without time zone`

## 2. Basic Configuration

Minimal configuration example:

```toml
[[sources]]
name = "postgres_logs"
connector_id = "postgres_src"

params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  cursor_column = "id"
}
```

If your runtime uses connector definitions, you can also write it like this:

```toml
[[connectors]]
id = "postgres_src"
type = "postgres"
allow_override = [
  "endpoint",
  "username",
  "password",
  "database",
  "table",
  "schema",
  "batch",
  "cursor_column",
  "cursor_type",
  "start_from",
  "start_from_format",
  "poll_interval_ms",
  "error_backoff_ms"
]

[connectors.params]
endpoint = "localhost:5432"
username = "postgres"
password = "123456"
database = "wparse"
table = "http_request_logs"
schema = "public"
batch = 1000
cursor_column = "id"
cursor_type = "int"
```

## 3. Parameter Description

### 3.1 Required Parameters

| Parameter | Description |
| --- | --- |
| `endpoint` | PostgreSQL address in `host:port` format |
| `database` | Database name |
| `table` | Target table name |
| `cursor_column` | Incremental cursor column |

### 3.2 Optional Parameters

| Parameter | Default | Description |
| --- | --- | --- |
| `username` | `root` | Username |
| `password` | `dayu` | Password |
| `schema` | `public` | Schema name |
| `batch` | `5000` | Number of rows read per batch, must be `> 0` |
| `cursor_type` | `int` | `int` or `time` |
| `start_from` | None | Starting point when the source starts for the first time and no checkpoint exists |
| `start_from_format` | None | Only used for `time` cursors, specifies how to parse `start_from` |
| `poll_interval_ms` | `1000` | Poll interval when no new data is available |
| `error_backoff_ms` | `2000` | Backoff interval after a query failure |

## 4. Cursor Types

### 4.1 `cursor_type = "int"`

Suitable for the following column types:

- `smallint`
- `integer`
- `bigint`
- `smallserial`
- `serial`
- `bigserial`
- `numeric`
- `decimal`

Example:

```toml
params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  cursor_column = "id",
  cursor_type = "int"
}
```

If the cursor column is `numeric` / `decimal`:

- The checkpoint stores the original text returned by the database
- The next query passes the value to PostgreSQL as `$1::numeric` for comparison
- The connector does not normalize precision

### 4.2 `cursor_type = "time"`

Suitable for the following column types:

- `timestamp with time zone`
- `timestamp without time zone`
- `timestamp`
- `date`

Not supported:

- `time without time zone`
- Text-based time columns

Example:

```toml
params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  cursor_column = "create_time",
  cursor_type = "time"
}
```

## 5. Using `start_from`

`start_from` only takes effect under this condition:

- No checkpoint currently exists

If a checkpoint already exists, the source always uses the checkpoint first and ignores `start_from`.

In other words:

- `start_from` only determines where the first read begins
- All later incremental reads advance entirely based on the checkpoint

### 5.1 Example for an `int` Cursor

```toml
params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  cursor_column = "id",
  cursor_type = "int",
  start_from = "1000"
}
```

### 5.2 Example for a `time` Cursor

```toml
params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  cursor_column = "create_time",
  cursor_type = "time",
  start_from = "2026-04-16 16:31:25",
  start_from_format = "%Y-%m-%d %H:%M:%S"
}
```

## 6. Using `start_from_format`

`start_from_format` is only used with `cursor_type = "time"`.

Its purpose is to tell the connector how `start_from` should be parsed.

The following values are supported:

- `unix`
- `unix_s`
- `unix_ms`
- A chrono pattern such as `%Y-%m-%d %H:%M:%S`

Notes:

- It is case-sensitive
- Forms such as `UnixMillis` and `UnixSeconds` are not supported at the moment
- `start_from_format` cannot be configured by itself; it must appear together with `start_from`

### 6.1 Unix Seconds Example

```toml
params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  cursor_column = "create_time",
  cursor_type = "time",
  start_from = "1776328285",
  start_from_format = "unix_s"
}
```

`1776328285` is a 10-digit Unix timestamp in seconds. If the PostgreSQL session `TimeZone` is `Asia/Shanghai`, it corresponds to:

```text
2026-04-16 16:31:25 +0800
```

### 6.2 Unix Milliseconds Example

```toml
params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  cursor_column = "create_time",
  cursor_type = "time",
  start_from = "1776328285000",
  start_from_format = "unix_ms"
}
```

### 6.3 Custom Format Example

```toml
params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  cursor_column = "create_time",
  cursor_type = "time",
  start_from = "2026-04-16 16:31:25",
  start_from_format = "%Y-%m-%d %H:%M:%S"
}
```

### 6.4 Behavior Without `start_from_format`

If `cursor_type = "time"` and `start_from_format` is not configured, the connector tries to parse the input using built-in rules:

- RFC3339
- `%Y-%m-%d %H:%M:%S%.f`
- `%Y-%m-%dT%H:%M:%S%.f`
- `%Y-%m-%d`
- 10-digit Unix seconds
- 13-digit Unix milliseconds

For inputs without an explicit time zone, as well as Unix seconds and Unix milliseconds, the source interprets them using the current PostgreSQL connection session `TimeZone` at startup.

If the input already carries an explicit time zone, the connector keeps the user-provided time zone semantics and does not convert it to the session `TimeZone`.

## 7. Query Behavior

### 7.1 With a Lower Bound

The following two cases use a lower-bound query:

- A checkpoint already exists
- No checkpoint exists, but `start_from` is configured

The query logic is equivalent to:

```sql
WHERE cursor_column > lower_bound
ORDER BY cursor_column ASC
LIMIT batch
```

### 7.2 Without a Lower Bound

If neither a checkpoint nor `start_from` exists, the query does not include `WHERE > $1`. Instead, reading starts directly from the smallest cursor value:

```sql
ORDER BY cursor_column ASC
LIMIT batch
```

### 7.3 When No New Data Is Available

When there is no new data:

- The source does not return EOF
- It keeps polling according to `poll_interval_ms`

## 8. Checkpoint

Checkpoint files are always stored at:

```text
./.run/.checkpoints/{source_key}.json
```

For example, if the source name is `postgres_logs`, the checkpoint file may be:

```text
./.run/.checkpoints/postgres_logs.json
```

Example content:

```json
{
  "version": 1,
  "cursor_type": "time",
  "cursor_column": "create_time",
  "last_cursor_raw": "2026-04-16T16:31:25.000000+08:00",
  "updated_at": "2026-04-17T02:30:00Z"
}
```

Please note:

- The checkpoint records how far the source has read
- It does not record how far downstream sinks have successfully written
- If you change `cursor_column` or `cursor_type`, the old checkpoint may no longer be compatible

If you want to restart reading from a new position, delete the old checkpoint before starting the source again.

## 9. Returned Data Format

Each record is converted into JSON text, and the source automatically appends a fixed field:

```json
{
  "warp_parse_table": "http_request_logs"
}
```

If the source table already contains a field with the same name, the value injected by the connector overrides the original field.

## 10. Table Structure Requirements

To ensure stable incremental reading, `cursor_column` must satisfy the following:

- It increases monotonically
- It is globally unique, or business semantics guarantee that the same cursor value will not be truncated within a single batch

Recommended:

- An auto-incrementing `bigint` primary key
- A unique and increasing `timestamptz`
- A unique and increasing `numeric`

Not recommended:

- An update-time field whose old values may be rewritten
- A business time field with duplicate values and unstable ordering

Time cursors require special attention:

- If the same time value can be truncated across multiple batches, records may be missed
- That scenario is a cursor-column design problem, not something the connector compensates for

## 11. Common Configuration Examples

### 11.1 Incremental Collection by Auto-Incrementing `id`

```toml
[[sources]]
name = "postgres_id_source"
connector_id = "postgres_src"

params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  schema = "public",
  batch = 1000,
  cursor_column = "id",
  cursor_type = "int"
}
```

### 11.2 Incremental Collection by `timestamptz`

```toml
[[sources]]
name = "postgres_time_source"
connector_id = "postgres_src"

params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  schema = "public",
  batch = 1000,
  cursor_column = "create_time",
  cursor_type = "time",
  start_from = "2026-04-16T16:31:25+08:00"
}
```

### 11.3 `timestamptz` with a Unix-Seconds Starting Point

```toml
[[sources]]
name = "postgres_time_source"
connector_id = "postgres_src"

params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  schema = "public",
  batch = 1000,
  cursor_column = "create_time",
  cursor_type = "time",
  start_from = "1776328285",
  start_from_format = "unix_s"
}
```

### 11.4 `timestamp` with a Custom-Format Starting Point

```toml
[[sources]]
name = "postgres_time_source"
connector_id = "postgres_src"

params = {
  endpoint = "localhost:5432",
  username = "postgres",
  password = "123456",
  database = "wparse",
  table = "http_request_logs",
  schema = "public",
  batch = 1000,
  cursor_column = "create_time",
  cursor_type = "time",
  start_from = "2026-04-16 16:31:25",
  start_from_format = "%Y-%m-%d %H:%M:%S"
}
```

## 12. Usage Recommendations

- Prefer integer cursors whenever possible
- If you must use a time cursor, prefer a unique and increasing `timestamptz`
- You can configure `start_from` for the first historical backfill
- After catch-up, incremental progress depends on the checkpoint, so avoid changing `start_from` frequently
- If you change the cursor column or cursor type, remember to remove the old checkpoint as well
- For large tables, start with `batch = 1000` and adjust based on actual load
