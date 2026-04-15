# KnowDB Configuration


Remember only three things:

1. only `version = 2` is supported
2. choose one mode only: directory-based SQLite authority, or external PostgreSQL / MySQL
3. `[cache]` controls `result cache` only

## Two modes

- Static CSV assets: use directory-based SQLite authority
- Data already in PostgreSQL / MySQL: use external provider

## Minimal examples

### Directory-based SQLite authority

```toml
version = 2
base_dir = "."

[default]
transaction = true
batch_size = 2000
on_error = "fail"

[csv]
has_header = true
delimiter = ","
encoding = "utf-8"
trim = true

[cache]
enabled = true
capacity = 1024
ttl_ms = 30000

[[tables]]
name = "example"
dir = "example"
enabled = true
columns.by_header = ["name", "pinying"]

[tables.expected_rows]
min = 5
max = 100
```

### External PostgreSQL / MySQL

```toml
version = 2

[cache]
enabled = true
capacity = 1024
ttl_ms = 30000

[provider]
kind = "postgres"
connection_uri = "postgres://user:${DB_PASSWORD}@127.0.0.1:5432/demo"
pool_size = 8
```

Replace `kind = "postgres"` with `kind = "mysql"` and switch the connection URI to MySQL format if needed.

## Which settings take effect

| Mode | Active settings | Not part of the main flow |
| --- | --- | --- |
| Directory-based SQLite authority | `version` `base_dir` `[default]` `[csv]` `[cache]` `[[tables]]` | `authority_uri` is not read from `knowdb.toml` |
| External PostgreSQL / MySQL | `version` `[provider]` `[cache]` | `base_dir` `[default]` `[csv]` `[[tables]]` |

## Key fields

### Top level

- `version`
  - required, must be `2`
- `base_dir`
  - root for table directories
- `[provider]`
  - only for external provider mode
- `[[tables]]`
  - only for directory-based SQLite authority mode

### `[default]`

- `transaction`
  - default `true`
- `batch_size`
  - default `2000`
- `on_error`
  - `fail` stops
  - `skip` ignores bad rows

### `[csv]`

- `has_header`
  - default `true`
- `delimiter`
  - keep it to one character
- `encoding`
  - only `utf-8` is supported
- `trim`
  - default `true`

### `[cache]`

- `enabled`
  - default `true`
- `capacity`
  - default `1024`, in entries
- `ttl_ms`
  - default `30000`

### `[provider]`

- `kind`
  - required, `postgres` or `mysql`
- `connection_uri`
  - required, `${VAR}` expansion supported
- `pool_size`
  - optional, default `8`

Do not write `kind = "sqlite_authority"`. In directory-based mode, omit `[provider]` completely.

### `[[tables]]`

- `name`
  - required
- `dir`
  - defaults to `name`
- `data_file`
  - defaults to `data.csv`
- `enabled`
  - defaults to `true`
- configure at least one column mapping:
  - `columns.by_header`
  - `columns.by_index`
- priority:
  - `by_header` first
  - `by_index` only when `by_header` is empty

## Table directory convention

A typical table directory looks like this:

```text
knowdb/
  knowdb.toml
  example/
    create.sql
    insert.sql
    data.csv
  zone/
    create.sql
    insert.sql
    clean.sql
    data.scv
```

Rules:

- `create.sql` is required.
- `insert.sql` is required.
- `data.csv` is the default data file.
- `clean.sql` is optional; if omitted, the default cleanup statement is `DELETE FROM {table}`.
- `{table}` inside SQL files is replaced with the current table name.

## Paths and environment variables

- `${VAR}` is expanded before TOML deserialization. Example:

```toml
[provider]
kind = "mysql"
connection_uri = "mysql://root:${MYSQL_PASSWORD}@127.0.0.1:3306/demo"
```

- Values come from the `EnvDict` passed into `init_thread_cloned_from_knowdb(..., dict)`.
- `wp-knowledge` does not read process environment variables directly.

Path resolution order:

1. If `knowdb_conf` is relative, resolve it against the caller-provided `root`.
2. Resolve `base_dir` relative to the directory that contains `knowdb.toml`.
3. Resolve `tables[n].dir` relative to `base_dir`.
4. Resolve `tables[n].data_file` relative to the table directory.

## Common failures

- `version` is not `2`
- `create.sql`, `insert.sql`, or the data file is missing
- neither `columns.by_header` nor `columns.by_index` is configured
- `columns.by_header` refers to a missing CSV header
- `encoding` is not `utf-8`
- CSV row parsing fails and `on_error = "fail"`
- imported rows are below `expected_rows.min`
- PostgreSQL / MySQL initialization fails to connect

## Recommended patterns

- In the directory-based SQLite authority mode, do not add a `[provider]` block.
- Put `enabled` under `[[tables]]`, not under `[tables.expected_rows]`.
- Keep `delimiter` to a single character.
- If you use `columns.by_header`, keep `csv.has_header = true`.
- In external PostgreSQL / MySQL mode, treat `[cache]` strictly as `result cache` configuration.
