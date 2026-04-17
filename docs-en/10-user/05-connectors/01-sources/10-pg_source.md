# PostgreSQL Source Usage Guide

`PostgresSource` continuously reads data incrementally from a PostgreSQL table by using a single cursor.

It works as follows:

```text
Read the local checkpoint
  -> Generate a query ordered by an increasing cursor
  -> Fetch one batch of data from PostgreSQL
  -> Convert each full row into JSON
  -> Automatically append the warp_parse_table field
  -> Return the records to the upstream pipeline
  -> Update the checkpoint with the cursor value of the last record in the current batch
```

The current version supports only a single cursor. It does not support a secondary cursor, and it does not support text time columns as time cursors.

## 1. Use Cases

- Continuously collect incremental data from a PostgreSQL table
- The table has a monotonically increasing cursor column
- The process should resume reading from the previous position after restart

Suitable cursor columns:

- Auto-increment `id`
- Monotonically increasing business sequence number
- Monotonically increasing `numeric` / `decimal` values that will not be split across batches
- Native PostgreSQL time columns: `timestamp with time zone`, `timestamp without time zone`, `date`

Unsuitable cursor columns:

- Fields whose old values may be updated later
- Fields with many duplicate values that may be split across batches
- Text time fields
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

If your runtime uses connector definitions, you can also configure it as follows:

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

## 3. Parameters

### 3.1 Required Parameters

| Parameter | Description |
| --- | --- |
| `endpoint` | PostgreSQL endpoint in `host:port` format |
| `database` | Database name |
| `table` | Target table name |
| `cursor_column` | Incremental cursor column |

### 3.2 Optional Parameters

| Parameter | Default | Description |
| --- | --- | --- |
| `username` | `root` | Username |
| `password` | `dayu` | Password |
| `schema` | `public` | Schema name |
| `batch` | `5000` | Number of rows to read per batch. The value must be ` > 0` |
| `cursor_type` | `int` | `int` or `time` |
| `start_from` | None | Start point used on the first run when no checkpoint exists |
| `start_from_format` | None | Used only by `time` cursors to specify the input format of `start_from` |
| `poll_interval_ms` | `1000` | Polling interval when there is no new data |
| `error_backoff_ms` | `2000` | Backoff interval after a query failure |

## 4. Cursor Types

### 4.1 `cursor_type = "int"`

Applicable to the following column types:

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
- The next query passes it to PostgreSQL for comparison through `$1::numeric`
- The connector does not normalize precision

### 4.2 `cursor_type = "time"`

Applicable to the following column types:

- `timestamp with time zone`
- `timestamp without time zone`
- `timestamp`
- `date`

Not supported:

- `time without time zone`
- Text time columns

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

`start_from` takes effect only when:

- No checkpoint currently exists

If a checkpoint already exists, the checkpoint is used first and `start_from` is ignored.

In other words:

- `start_from` only decides where the first read starts
- Subsequent incremental reads are fully advanced by the checkpoint

### 5.1 Integer Cursor Example

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

### 5.2 Time Cursor Example

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

`start_from_format` is used only when `cursor_type = "time"`.

It tells the connector how to parse `start_from`.

Supported values:

- `unix`
- `unix_s`
- `unix_ms`
- Chrono patterns, for example `%Y-%m-%d %H:%M:%S`

Notes:

- Values are case-sensitive
- Formats such as `UnixMillis` and `UnixSeconds` are not supported in the current version
- `start_from_format` cannot be configured alone. It must be used together with `start_from`

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

If `cursor_type = "time"` and `start_from_format` is not configured, the connector tries to parse the value using its built-in rules:

- RFC3339
- `%Y-%m-%d %H:%M:%S%.f`
- `%Y-%m-%dT%H:%M:%S%.f`
- `%Y-%m-%d`
- 10-digit Unix timestamp in seconds
- 13-digit Unix timestamp in milliseconds

For values without an explicit time zone, and for Unix seconds or milliseconds, the value is interpreted by using the PostgreSQL session `TimeZone` of the Source connection at startup.

If the input already contains an explicit time zone, the connector preserves the time zone semantics from the user input and does not convert it to the session `TimeZone`.

## 7. Query Behavior

### 7.1 With a Lower Bound

The following two cases use a query with a lower bound:

- A checkpoint already exists
- No checkpoint exists, but `start_from` is configured

The query logic is equivalent to:

```sql
WHERE cursor_column > lower_bound
ORDER BY cursor_column ASC
LIMIT batch
```

### 7.2 Without a Lower Bound

If neither a checkpoint nor `start_from` exists, no `WHERE > $1` condition is added. The Source reads from the smallest cursor value:

```sql
ORDER BY cursor_column ASC
LIMIT batch
```

### 7.3 When There Is No New Data

When there is no new data:

- The Source does not return EOF
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

Important notes:

- The checkpoint records where the Source has read up to
- It does not mean the downstream system has successfully written data up to that position
- If you change `cursor_column` or `cursor_type`, the old checkpoint may no longer be compatible

If you want to read again from a new start point, delete the old checkpoint before starting the Source.

## 9. Returned Data Format

Each record is converted into JSON text, and a fixed field is automatically appended:

```json
{
  "warp_parse_table": "http_request_logs"
}
```

If the source table already contains a field with the same name, the value injected by the connector overwrites the original field.

## 10. Table Structure Requirements

For stable incremental reads, `cursor_column` must be:

- Monotonically increasing
- Globally unique, or guaranteed by business logic not to have the same cursor value split across batches

Recommended:

- Auto-increment `bigint` primary key
- Unique and increasing `timestamptz`
- Unique and increasing `numeric`

Not recommended:

- Update time fields whose old values may be changed later
- Business time fields that may be duplicated and have unstable ordering

Pay special attention to time cursors:

- If the same timestamp value can be split across multiple batches, records may be missed
- This is a cursor column selection issue and is not something the connector can compensate for

## 11. Common Configuration Examples

### 11.1 Incremental Collection by Auto-Increment ID

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

### 11.3 `timestamptz` with a Unix Seconds Start Point

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

### 11.4 `timestamp` with a Custom Format Start Point

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

## 12. Recommendations

- Prefer integer cursors
- If you must use a time cursor, prefer a unique and increasing `timestamptz`
- Configure `start_from` for the first historical backfill
- After catching up, rely on the checkpoint for incremental reads and avoid changing `start_from` frequently
- If you change the cursor column or cursor type, remember to clean up the old checkpoint as well
- For large tables, start with `batch = 1000` and tune it based on actual load
