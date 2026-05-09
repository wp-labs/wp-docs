# PostgreSQL Provider Tasks


## Current baseline

Already available:

- `[provider] kind = "postgres"` support
- `query_fields(...)` / `cache_query_fields(...)` as the recommended path
- baseline queries, named-parameter rewriting, and manual verification scripts

This is enough to validate the main flow, but not yet enough for long-term production-grade PostgreSQL support.

## Remaining work

### 1. Connection pool

- Current: `src/postgres.rs` still behaves like a serialized single-client path
- Goal:
  - integrate a connection pool
  - define connect/disconnect/retry behavior
  - remove dependence on one serialized client

### 2. Startup validation

- Current: startup mostly checks only basic connectivity
- Goal:
  - validate database, schema, permissions, and key objects at startup
  - fail early on wrong DB, wrong schema, or wrong permissions

### 3. SQL / UDF boundary

- Current: baseline SQL works, but SQLite UDF assumptions are still incomplete
- Goal:
  - list SQL that can move directly
  - list SQL that must be rewritten
  - list functions users must provide in PostgreSQL themselves

### 4. Type coverage

- Current: result-type support and bind behavior are still incomplete
- Goal:
  - cover common numeric, temporal, JSON, and network types
  - return clearer errors for unsupported types

### 5. Automated verification

- Current: verification is still too manual
- Goal:
  - add a stable CI path
  - choose one main path between Compose and `testcontainers`
  - emit enough diagnostics on failure

### 6. End-to-end example in a consuming repo

- Current: `wp-knowledge` can validate itself, but the consuming-repo chain is incomplete
- Goal:
  - add a PostgreSQL example in a consumer repo
  - validate `wp-oml` with a real schema
  - provide reusable run instructions

### 7. Compatibility cleanup

- Current: `query_named(...)` / `cache_query(...)` still preserve older SQLite-shaped behavior
- Goal:
  - make provider-neutral APIs the default for new code
  - define the retention and deprecation strategy for compatibility APIs

## Suggested order

1. connection pool
2. startup validation
3. SQL / UDF boundary
4. type coverage
5. automated verification
6. end-to-end example
7. compatibility cleanup
