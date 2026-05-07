# Provider 性能测试与结论


## 结论先看

- provider 层 `sync` 和 `async` 基本持平，`async` 只略优
- 真正进入 SQL/effect 路径后，`wp-oml` 吞吐会降到纯 OML 的约 `8% ~ 9%`
- cache 的收益远大于 sync/async driver 的差异
- 主要成本不在 PG/MySQL driver，而在整条 `OML -> SQL -> provider -> decode -> 回填` 链路

## 测试口径

- `rows=10000`
- `ops=10000`
- `hotset=128`
- 并发测试使用 `1 / 4 / 16 / 64`
- 并发 cache 测试使用 `ops=20000`

## 关键结果

### 1. Provider 层：sync 与 async 对比

| backend | sync QPS | async QPS | 结论 |
| --- | ---: | ---: | --- |
| PostgreSQL | 2690 | 2701 | 基本持平 |
| MySQL | 2616 | 2677 | 基本持平 |

说明：

- 改成 tokio 原生 async driver 后，收益主要是运行模型更合理
- 单条查询延迟没有数量级变化

### 2. OML 端到端：纯 OML 与真实 SQL 路径

| scenario | PostgreSQL | MySQL |
| --- | ---: | ---: |
| pure async OML | 1,233,870 | 1,185,021 |
| async OML + provider | 100,254 | 107,818 |

说明：

- 一旦进入真实知识库查询路径，吞吐会明显下降
- PostgreSQL / MySQL 数字接近，说明瓶颈不在单个 backend

### 3. Cache 的收益

| backend | bypass | global cache | local cache |
| --- | ---: | ---: | ---: |
| PostgreSQL | 2,784 | 131,508 | 151,501 |
| MySQL | 2,674 | 162,610 | 177,758 |

说明：

- 裸查只有 `2.6K ~ 2.8K QPS`
- 命中 cache 后，直接提升到 `13万 ~ 18万 QPS`
- 所以后续优化优先级应先看 cache 命中率，再看 driver 差异

### 4. 并发下的上限

#### Provider 层，`concurrency=64`

| backend | bypass | global cache | local cache |
| --- | ---: | ---: | ---: |
| PostgreSQL | 29,143 | 1,272,680 | 2,092,479 |
| MySQL | 9,432 | 1,033,193 | 1,289,660 |

#### OML + provider + cache，`concurrency=64`

| backend | QPS |
| --- | ---: |
| PostgreSQL | 2,788,461 |
| MySQL | 2,747,599 |

说明：

- `async OML + knowledge + cache` 在并发下已经进入 `170万 ~ 280万 QPS` 区间
- 剩余优化空间主要在 OML 自身调用链，而不是数据库 I/O

## 建议

- 不要把“切成 async driver”当成主要性能手段
- 优先优化 cache 命中率和 OML 到 provider 的固定开销
- 如果查询能稳定命中热点，收益会显著高于继续微调 backend driver

## 复现命令

PostgreSQL provider 层：

```bash
KEEP_DB=1 RUSTC_WRAPPER= bash tests/test-postgres-provider.sh
```

MySQL provider 层：

```bash
KEEP_DB=1 RUSTC_WRAPPER= bash tests/test-mysql-provider.sh
```

PostgreSQL OML 层：

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

MySQL OML 层：

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

PostgreSQL 并发 cache perf：

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

MySQL 并发 cache perf：

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

PostgreSQL OML 并发 cache perf：

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

MySQL OML 并发 cache perf：

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
