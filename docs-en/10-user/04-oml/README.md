# OML Object Model Language

OML (Object Modeling Language) is used to transform, aggregate, match, calculate, and enrich structured records produced by WPL.

> This directory is aligned with the current implementation in `wp-motor/crates/wp-oml/src`. Older docs sometimes mentioned features that are not parsed by the current implementation, such as privacy sections, `query ...`, or `sxf_get(...)`. They should not be treated as official syntax.

---

## Reading Order

| Scenario | Recommended Document |
|----------|----------------------|
| Start quickly | [01-quickstart.md](./01-quickstart.md) |
| Understand read/take semantics, types, and batch mode | [02-core-concepts.md](./02-core-concepts.md) |
| Find task-oriented examples | [03-practical-guide.md](./03-practical-guide.md) |
| Check functions supported by the current implementation | [04-functions-reference.md](./04-functions-reference.md) |
| Check grammar boundaries | [06-grammar-reference.md](./06-grammar-reference.md) |
| Browse topic pages | [functions/function_index.md](./functions/function_index.md) |
| Learn integration details | [05-integration.md](./05-integration.md) |

---

## Minimal Example

```oml
name : nginx_access
rule : /nginx/access_log
---
client_ip : ip = read(client_ip) ;
status : digit = read(status) ;
uri = read(request_uri) ;
event_time : time = Now::time() ;
```

This shows the core shape of the current implementation:

- `name` is required and must come first
- `rule` and `enable` are optional, and may appear in either order
- a `---` line is required between the header and the body
- the body must contain at least one aggregate statement, and every statement ends with `;`

---

## What the Current Implementation Supports

- top-level expressions: `read(...)`, `take(...)`, `fmt(...)`, `calc(...)`, `match ... { ... }`
- aggregation expressions: `object { ... }`, `collect ...`
- pipe expressions: `pipe read(...) | ...`, and also `read(...) | ...` without the `pipe` keyword
- lookup: `lookup_nocase(...)`
- built-in functions: `Now::time()`, `Now::date()`, `Now::hour()`
- SQL: `select ... from ... where ... ;`
- `static { ... }`: only for pure constant objects and constant calculations

## What You Should Not Assume

- do not treat privacy sections as official OML syntax
- do not use `query ...` as the SQL entry point; the current parser starts SQL with `select`
- do not rely on functions that are not listed in [04-functions-reference.md](./04-functions-reference.md)
- do not assume `static` can execute `read/take/match/pipe/sql`

---

## Useful Entry Points

| Goal | Document |
|------|----------|
| Learn `read`, `take`, `option`, and `keys` | [02-core-concepts.md](./02-core-concepts.md) |
| Check `calc(...)`, `lookup_nocase(...)`, and `Now::*` | [04-functions-reference.md](./04-functions-reference.md) |
| Check `match` condition functions | [functions/match_functions.md](./functions/match_functions.md) |
| Check `static` limitations | [functions/static_blocks.md](./functions/static_blocks.md) |
| Check EBNF-style grammar summary | [06-grammar-reference.md](./06-grammar-reference.md) |
