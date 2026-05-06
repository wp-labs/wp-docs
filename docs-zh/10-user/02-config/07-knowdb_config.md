# KnowDB 配置说明


只记三件事：

1. 当前只支持 `version = 2`
2. 只能二选一：目录式 SQLite authority，或外部 PostgreSQL / MySQL
3. `[cache]` 只控制 `result cache`

## 两种模式

- 静态 CSV 随包分发：用目录式 SQLite authority
- 数据已经在 PostgreSQL / MySQL：用外部 provider

## 最小示例

### 目录式 SQLite authority

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

### 外部 PostgreSQL / MySQL

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

把 `kind = "postgres"` 换成 `kind = "mysql"`，连接串换成 MySQL 格式即可。

## 哪些配置会生效

| 模式 | 会生效 | 不参与主流程 |
| --- | --- | --- |
| 目录式 SQLite authority | `version` `base_dir` `[default]` `[csv]` `[cache]` `[[tables]]` | `authority_uri` 不从 `knowdb.toml` 读取 |
| 外部 PostgreSQL / MySQL | `version` `[provider]` `[cache]` | `base_dir` `[default]` `[csv]` `[[tables]]` |

## 关键字段速查

### 顶层

- `version`
  - 必填，只能是 `2`
- `base_dir`
  - 表目录根路径，相对 `knowdb.toml` 所在目录解析
- `[provider]`
  - 只在外部 provider 模式下使用
- `[[tables]]`
  - 只在目录式 SQLite authority 模式下使用

### `[default]`

- `transaction`
  - 默认 `true`
- `batch_size`
  - 默认 `2000`
- `on_error`
  - `fail` 直接失败
  - `skip` 跳过坏行

### `[csv]`

- `has_header`
  - 默认 `true`
- `delimiter`
  - 建议单字符
- `encoding`
  - 目前只支持 `utf-8`
- `trim`
  - 默认 `true`

### `[cache]`

- `enabled`
  - 默认 `true`
- `capacity`
  - 默认 `1024`，单位是条目数
- `ttl_ms`
  - 默认 `30000`

### `[provider]`

- `kind`
  - 必填，`postgres` 或 `mysql`
- `connection_uri`
  - 必填，支持 `${VAR}`
- `pool_size`
  - 可选，默认 `8`

不要写 `kind = "sqlite_authority"`。目录式模式下直接省略 `[provider]`。

### `[[tables]]`

- `name`
  - 必填
- `dir`
  - 默认等于 `name`
- `data_file`
  - 默认 `data.csv`
- `enabled`
  - 默认 `true`
- 列映射至少配置一组：
  - `columns.by_header`
  - `columns.by_index`
- 优先级：
  - `by_header` 优先
  - `by_header` 为空时才用 `by_index`

## 表目录约定

每个表目录通常长这样：

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

规则：

- `create.sql` 必需
- `insert.sql` 必需
- `data.csv` 是默认数据文件
- `clean.sql` 可选；缺省时默认执行 `DELETE FROM {table}`
- SQL 文件中的 `{table}` 会被当前表名替换

## 路径和环境变量

- `${VAR}` 会在 TOML 反序列化前展开，例如：

```toml
[provider]
kind = "mysql"
connection_uri = "mysql://root:${MYSQL_PASSWORD}@127.0.0.1:3306/demo"
```

- 值来自 `init_thread_cloned_from_knowdb(..., dict)` 传入的 `EnvDict`
- 不是 `wp-knowledge` 直接读进程环境变量

路径解析顺序：

1. `knowdb_conf` 是相对路径时，先相对调用方传入的 `root` 解析
2. `base_dir` 再相对 `knowdb.toml` 所在目录解析
3. `tables[n].dir` 再相对 `base_dir` 解析
4. `tables[n].data_file` 再相对表目录解析

## 常见失败原因

- `version` 不是 `2`
- `create.sql`、`insert.sql` 或数据文件不存在
- `columns.by_header` 和 `columns.by_index` 都没配置
- `columns.by_header` 指向了不存在的表头
- `encoding` 不是 `utf-8`
- CSV 行解析失败且 `on_error = "fail"`
- 实际导入行数小于 `expected_rows.min`
- PostgreSQL / MySQL 初始化连接失败

## 建议写法

- 目录式 SQLite authority 模式下，不要写 `[provider]`
- `enabled` 写在 `[[tables]]` 层，不要写到 `[tables.expected_rows]` 下面
- `delimiter` 用单字符
- 使用 `columns.by_header` 时，保持 `csv.has_header = true`
- 外部 PostgreSQL / MySQL 场景下，把 `[cache]` 理解为 `result cache` 配置
