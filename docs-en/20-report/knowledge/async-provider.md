# Async Provider Performance


## Summary first

- provider-layer `sync` and `async` are nearly tied; `async` is only slightly better
- once `wp-oml` enters a real SQL/effect path, throughput drops to about `8% ~ 9%` of pure OML
- cache matters far more than the sync/async driver choice
- the main cost is the full `OML -> SQL -> provider -> decode -> write-back` pipeline, not the PG/MySQL driver itself

## Test shape

- `rows=10000`
- `ops=10000`
- `hotset=128`
- concurrency tests use `1 / 4 / 16 / 64`
- concurrent cache tests use `ops=20000`

## Key results

### 1. Provider layer: sync vs async

| backend | sync QPS | async QPS | takeaway |
| --- | ---: | ---: | --- |
| PostgreSQL | 2690 | 2701 | nearly tied |
| MySQL | 2616 | 2677 | nearly tied |

Notes:

- the async driver mainly improves runtime model and scheduling
- it does not produce an order-of-magnitude latency win per query

### 2. End-to-end OML: pure vs real SQL path

| scenario | PostgreSQL | MySQL |
| --- | ---: | ---: |
| pure async OML | 1,233,870 | 1,185,021 |
| async OML + provider | 100,254 | 107,818 |

Notes:

- once real knowledge queries are involved, throughput drops sharply
- PostgreSQL and MySQL stay close, so the bottleneck is not one backend implementation

### 3. Cache gain

| backend | bypass | global cache | local cache |
| --- | ---: | ---: | ---: |
| PostgreSQL | 2,784 | 131,508 | 151,501 |
| MySQL | 2,674 | 162,610 | 177,758 |

Notes:

- uncached provider throughput is only `2.6K ~ 2.8K QPS`
- cache raises that to `130K ~ 180K QPS`
- so cache strategy matters much more than driver selection

### 4. Concurrent ceiling

#### Provider layer at `concurrency=64`

| backend | bypass | global cache | local cache |
| --- | ---: | ---: | ---: |
| PostgreSQL | 29,143 | 1,272,680 | 2,092,479 |
| MySQL | 9,432 | 1,033,193 | 1,289,660 |

#### OML + provider + cache at `concurrency=64`

| backend | QPS |
| --- | ---: |
| PostgreSQL | 2,788,461 |
| MySQL | 2,747,599 |

Notes:

- `async OML + knowledge + cache` reaches roughly `1.7M ~ 2.8M QPS`
- the remaining optimization room is mostly in the OML call chain, not database I/O

## Recommendations

- do not treat “switch to async driver” as the main performance lever
- optimize cache hit rate and OML-to-provider fixed cost first
- if queries are hot and cacheable, the gain is much larger than backend-level driver tuning

## Reproduction commands

PostgreSQL provider layer:

```bash
KEEP_DB=1 RUSTC_WRAPPER= bash tests/test-postgres-provider.sh
```

MySQL provider layer:

```bash
KEEP_DB=1 RUSTC_WRAPPER= bash tests/test-mysql-provider.sh
```

PostgreSQL OML layer:

```bash
WP_KDB_TEST_POSTGRES_URL='postgres://postgres:demo@127.0.0.1:5432/postgres' \
WP_KDB_PERF_ROWS=10000 \
WP_KDB_PERF_OPS=10000 \
WP_KDB_PERF_HOTSET=128 \
RUSTC_WRAPPER= \
cargo test --manifest-path ../wp-motor/Cargo.toml -p wp-oml \
  --test knowledge_async_perf oml_async_postgres_provider_throughput \
  -- --ignored --nocapture
```

MySQL OML layer:

```bash
WP_KDB_TEST_MYSQL_URL='mysql://root:demo@127.0.0.1:3306/demo' \
WP_KDB_PERF_ROWS=10000 \
WP_KDB_PERF_OPS=10000 \
WP_KDB_PERF_HOTSET=128 \
RUSTC_WRAPPER= \
cargo test --manifest-path ../wp-motor/Cargo.toml -p wp-oml \
  --test knowledge_async_perf oml_async_mysql_provider_throughput \
  -- --ignored --nocapture
```

PostgreSQL concurrent cache perf:

```bash
WP_KDB_TEST_POSTGRES_URL='postgres://postgres:demo@127.0.0.1:5432/postgres' \
WP_KDB_PERF_ROWS=10000 \
WP_KDB_PERF_OPS=20000 \
WP_KDB_PERF_HOTSET=128 \
WP_KDB_PERF_CONCURRENCY='1,4,16,64' \
RUSTC_WRAPPER= \
cargo test --manifest-path Cargo.toml \
  --test postgres_provider postgres_provider_async_cache_concurrency_perf \
  -- --ignored --nocapture
```

MySQL concurrent cache perf:

```bash
WP_KDB_TEST_MYSQL_URL='mysql://root:demo@127.0.0.1:3306/demo' \
WP_KDB_PERF_ROWS=10000 \
WP_KDB_PERF_OPS=20000 \
WP_KDB_PERF_HOTSET=128 \
WP_KDB_PERF_CONCURRENCY='1,4,16,64' \
RUSTC_WRAPPER= \
cargo test --manifest-path Cargo.toml \
  --test mysql_provider mysql_provider_async_cache_concurrency_perf \
  -- --ignored --nocapture
```

PostgreSQL OML concurrent cache perf:

```bash
WP_KDB_TEST_POSTGRES_URL='postgres://postgres:demo@127.0.0.1:5432/postgres' \
WP_KDB_PERF_ROWS=10000 \
WP_KDB_PERF_OPS=20000 \
WP_KDB_PERF_HOTSET=128 \
WP_KDB_PERF_CONCURRENCY='1,4,16,64' \
RUSTC_WRAPPER= \
cargo test --manifest-path ../wp-motor/Cargo.toml -p wp-oml \
  --test knowledge_async_perf oml_async_postgres_provider_cache_concurrency \
  -- --ignored --nocapture
```

MySQL OML concurrent cache perf:

```bash
WP_KDB_TEST_MYSQL_URL='mysql://root:demo@127.0.0.1:3306/demo' \
WP_KDB_PERF_ROWS=10000 \
WP_KDB_PERF_OPS=20000 \
WP_KDB_PERF_HOTSET=128 \
WP_KDB_PERF_CONCURRENCY='1,4,16,64' \
RUSTC_WRAPPER= \
cargo test --manifest-path ../wp-motor/Cargo.toml -p wp-oml \
  --test knowledge_async_perf oml_async_mysql_provider_cache_concurrency \
  -- --ignored --nocapture
```
