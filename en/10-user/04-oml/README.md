# OML Object Modeling Language

OML (Object Modeling Language) is used in Warp Parse to assemble and aggregate parsed records. It provides capabilities including read/take value extraction, object and array aggregation (object/collect), conditional matching (match), string formatting (fmt), pipe transformations (pipe), and SQL query construction.

Note: Starting from the current version, the engine does not enable "privacy/masking" runtime processing by default. The privacy section syntax mentioned in this chapter is only for DSL capability description. If you need data masking, please implement it in your business logic or custom plugins/pipelines.

## Table of Contents

- [OML Basics](./01-oml_basics.md)
- [OML Examples](./02-oml_examples.md)
- [OML Functions Reference](./03-oml_functions.md)
- [OML Grammar (EBNF)](./04-oml_grammar.md)

## Feature Overview

- Value extraction with defaults: `read(...)` (non-destructive) / `take(...)` (destructive) + default body `{ _ : <value/function> }`
- Object/Array aggregation: `object { ... }`, `collect read(keys:[...])`
- Conditional matching: `match read(x) { ... }` and binary matching `match (read(a), read(b)) { ... }`
- Pipe and formatting: `read(x) | to_json | base64_encode`, `fmt("{}-{}", @a, read(b))`
- SQL: `select <cols from table> where <cond>;` (body whitelist validation, strict mode can be disabled via `OML_SQL_STRICT=0`)
- Batch targets: When target name contains `*`, batch mode evaluation is used (only supports take/read)
- Privacy section: Field privacy processor mapping declared through a second `---` at the end

## Quick Example

```oml
name : example
---
user_id        = read(user_id) ;
occur_time:time= Now::time() ;
values : obj   = object {
  cpu_free, memory_free : digit = take() ;
};
ports : array  = collect read(keys:[sport,dport]) ;
ports_json     = pipe read(ports) | to_json ;
full           = fmt("{}-{}", @user, read(city)) ;
name,pinying   = select name,pinying from example where pinying = read(py) ;
---
src_ip : privacy_ip
pos_sn : privacy_keymsg
```

## Built-in Functions

| Function | Description | Return Type |
|----------|-------------|-------------|
| `Now::time()` | Get current time | `time` |
| `Now::date()` | Get current date (YYYYMMDD) | `digit` |
| `Now::hour()` | Get current time to the hour (YYYYMMDDHH) | `digit` |

## Pipe Functions

| Function | Description |
|----------|-------------|
| `base64_encode` | Base64 encoding |
| `base64_decode` | Base64 decoding (supports multiple character encodings) |
| `html_escape` / `html_unescape` | HTML escape/unescape |
| `json_escape` / `json_unescape` | JSON escape/unescape |
| `str_escape` | String escape |
| `Time::to_ts` / `Time::to_ts_ms` / `Time::to_ts_us` | Time to timestamp (seconds/milliseconds/microseconds, UTC+8) |
| `Time::to_ts_zone(timezone,unit)` | Time to specified timezone timestamp |
| `nth(index)` | Get array element |
| `get(field_name)` | Get object field |
| `path(name\|path)` | Extract file path part |
| `url(domain\|host\|uri\|path\|params)` | Extract URL part |
| `sxf_get(field_name)` | Extract special format field |
| `to_str` / `to_json` | Convert to string/JSON |
| `ip4_to_int` | IPv4 to integer |
| `skip_empty` | Skip empty values |

For detailed descriptions, see [OML Functions Reference](./03-oml_functions.md).

## Data Types

| Type | Description |
|------|-------------|
| `auto` | Auto-infer (default) |
| `chars` | String |
| `digit` | Integer |
| `float` | Floating point |
| `ip` | IP address |
| `time` | Time |
| `bool` | Boolean |
| `obj` | Object |
| `array` | Array |

## Related Documentation

- [WPL Rule Language](../06-wpl/README.md)
- [Configuration Guide Overview](../02-config/README.md)
- [Schema Reference](../../80-reference/schemas/README.md)

Tip: For the difference between read/take, see "OML Basics"; for complete grammar, see "OML Grammar (EBNF)"; for end-to-end examples, see "OML Examples".
