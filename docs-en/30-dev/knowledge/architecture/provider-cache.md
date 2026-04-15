# wp-knowledge Provider and Cache Plan


Companion tasks:

- [Provider / Cache Follow-up Tasks](../tasks/provider-cache.md)

## One-line summary

The target architecture is simple:

- providers are replaceable
- cache layers are explicit
- reload has one invalidation contract
- legacy facade APIs still exist, but only as wrappers over one runtime

Correctness depends on two values:

- `datasource_id`
- `generation`

Every cache entry and every thread-local snapshot must be tied to them.

## Why this exists

The old implementation was built for `SQLite + single process + per-call cache`. Once SQLite, PostgreSQL, and MySQL all coexist, the old assumptions become correctness and maintenance problems:

- provider lifecycle is too static
- caller-owned cache keys are too weak
- metadata cache has no clear bound
- `ThreadClonedMDB` is not version-aware

## Target model

Keep only four layers:

1. `DatasourceRegistry`
   - owns the active provider
   - manages `datasource_id`
   - manages `generation`
   - handles replace / reload
2. `KnowledgeProvider`
   - executes queries only
   - does not own cache policy
3. `QueryRuntime`
   - decides cache usage
   - builds cache keys
   - owns result cache and metadata cache
4. `Facade Compatibility Layer`
   - keeps `query/query_row/query_named/cache_query`
   - serves only as compatibility glue

## Core contracts

### `DatasourceId`

- identifies the current data source
- can come from config hash or authority-path hash
- must not expose secrets

### `Generation`

- identifies the current runtime version
- must advance on reload, provider switch, authority rebuild, or schema refresh
- is the main invalidation mechanism; TTL is only fallback

### `QueryRequest`

Use one internal request model that carries at least:

- `sql`
- `params`
- `mode`
- `cache_policy`

Providers perform their own binding internally. Runtime code should not depend on `rusqlite::ToSql`.

### `CachePolicy`

Only three meanings are needed:

- `Bypass`
  - no cache
- `UseGlobal`
  - shared result cache
- `UseCallScope`
  - per-call cache, mainly for compatibility

## Cache layers

Keep only three layers, with separate responsibilities.

### 1. Result Cache

- for reuse across calls
- key must include:
  - `datasource_id`
  - `generation`
  - `query_hash`
  - `params_hash`
  - `mode`
- only for explicitly cacheable hotspot queries

### 2. Local Cache

- for deduplication inside one evaluation
- does not provide global consistency
- `FieldQueryCache` should be treated as this layer

### 3. Metadata Cache

- for column names and schema fragments
- key must include at least:
  - `datasource_id`
  - `generation`
  - `query_hash`
- must be bounded

## Reload contract

Reload follows one simple rule:

- whether old state is still valid is decided by `generation`, not by time

That means:

- result cache invalidates naturally when generation changes
- metadata cache invalidates naturally when generation changes
- `ThreadClonedMDB` must rebuild snapshots when generation changes
- reload failure must keep the old provider alive; runtime must not enter a half-initialized state

## Current landing status

On the 2026-03-25 baseline, most core pieces already exist:

- `KnowledgeRuntime`
- unified `QueryRequest / QueryParam / CachePolicy`
- bounded global result cache keyed by `datasource_id + generation`
- generation-aware `FieldQueryCache`
- generation-aware `ThreadClonedMDB`
- bounded SQLite metadata cache

The main unfinished areas are now:

- host-side telemetry / metrics adapters
- shrinking and deprecating the old compatibility surface

## Migration order

The remaining work should stay in this order:

1. finish the external reload / observability contract
2. make provider-neutral APIs the default path
3. shrink the role of `query_named(...)` and `cache_query(...)`
4. keep local cache only where compatibility still needs it

## Final judgment

This direction is already validated. The remaining job is cleanup, not another redesign.
