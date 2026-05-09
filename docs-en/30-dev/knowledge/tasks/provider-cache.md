# Provider / Cache Refactor Tasks


## Work rules

Before each task:

1. reread the current code
2. mark done / partial / not started
3. keep only the smallest still-useful scope

After each task:

1. test / verify
2. review
3. fix review findings before closing

## Current status

### Completed

- `KnowledgeRuntime`
- replaceable provider handle
- `datasource_id + generation`
- unified `QueryRequest / QueryParam / CachePolicy`
- bounded global result cache
- generation-aware `FieldQueryCache`
- generation-aware `ThreadClonedMDB`
- bounded SQLite metadata cache

### Partially completed

- reload / observability
  - baseline logs, snapshots, counters, and rollback already exist
  - host-side exporters / adapters are still missing
- compatibility layer
  - `query_named(...)` / `cache_query(...)` still exist
  - provider-neutral migration is still incomplete

### Main remaining items

- host-side metrics / telemetry adapters
- deprecation strategy for the compatibility surface

## Remaining work

### 1. External reload / observability contract

- Goal:
  - let hosts wire metrics / telemetry cleanly
  - unify diagnostics for reload success, failure, and rollback
  - make it easy to answer which provider, which cache layer, and which generation served a query

### 2. Compatibility cleanup

- Goal:
  - make provider-neutral APIs the default for new code
  - define the long-term role of `query_named(...)` and `cache_query(...)`
  - add `deprecated` where SQLite-shaped APIs should start shrinking

### 3. Keep local cache as compatibility only

- Goal:
  - keep `FieldQueryCache` only for per-call deduplication
  - stop treating it as a global-consistency mechanism

## Suggested order

1. external reload / observability contract
2. compatibility cleanup
3. further narrowing of local-cache semantics

## Notes

- the core refactor is already in place; the current job is cleanup, not another full redesign
- if implementation and docs drift, update docs first, then code
