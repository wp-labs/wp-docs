# OML Function and Topic Index

This directory contains focused topic pages for OML expressions and specific features. For the authoritative list of functions supported by the current implementation, use [04-functions-reference.md](../04-functions-reference.md).

## Expressions and Topics

| Name | Description | Document |
|------|-------------|----------|
| `calc(...)` | Explicit numeric expressions with `+ - * / %` and `abs/round/floor/ceil` | [calc.md](./calc.md) |
| `lookup_nocase(...)` | Case-insensitive lookup against a `static object` | [lookup_nocase.md](./lookup_nocase.md) |
| `match` condition functions | `starts_with`, `iequals_any`, and other `match` condition helpers | [match_functions.md](./match_functions.md) |
| `map_to(...)` | Constant mapping in pipes | [map_to.md](./map_to.md) |
| `starts_with(...)` | Prefix filtering in pipes | [starts_with.md](./starts_with.md) |
| `extract_main_word` | Main-word extraction from text | [extract_main_word.md](./extract_main_word.md) |
| `extract_subject_object` | Subject-object extraction from text | [extract_subject_object.md](./extract_subject_object.md) |
| `static { ... }` | Static constants, allowed expressions, and restrictions | [static_blocks.md](./static_blocks.md) |

## Current Implementation Boundaries

- built-in functions currently only include `Now::time()`, `Now::date()`, and `Now::hour()`
- top-level built-in expressions include `calc(...)`, `match ... { ... }`, `lookup_nocase(...)`, `fmt(...)`, `object { ... }`, `collect ...`, and `select ... where ... ;`
- the supported pipe function set is the one listed in [04-functions-reference.md](../04-functions-reference.md)
- older doc examples such as `sxf_get(...)`, privacy sections, and `query ...` are not part of the current `wp-oml` parser implementation
