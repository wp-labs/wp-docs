# OML Grammar

This document summarizes the actual usable grammar of OML based on the parsing implementation in the source code crates/wp-oml (winnow parser combinator), presented in EBNF form. Lexical details (such as data types, JSON paths, SQL operators, etc.) reuse the existing parsing capabilities of `wp_parser` and `wpl`, with abstract conventions provided where necessary.

> Related implementation entry points: `crates/wp-oml/src/parser/oml_conf.rs`, `oml_aggregate.rs`, `match_prm.rs`, `map_prm.rs`, `pipe_prm.rs`, `sql_prm.rs`, `fmt_prm.rs`, `fun_prm.rs`, etc.

## Top-Level Structure

```ebnf
oml              = header, sep_line, aggregate_items, [ sep_line, privacy_items ] ;

header           = "name", ":", name, eol,
                   [ "rule", ":", rule_path, { rule_path }, eol ] ;
sep_line         = "---" ;
name             = path ;                       (* e.g.: test *)
rule_path        = wild_path ;                  (* e.g.: wpx/abc, wpx/efg *)

aggregate_items  = aggregate_item, { aggregate_item } ;
aggregate_item   = target_list, "=", eval, ";" ;

target_list      = target, { ",", target } ;
target           = target_name, [ ":", data_type ] ;
target_name      = wild_key | "_" ;            (* Allows wildcard '*'; '_' indicates anonymous/discard *)
data_type        = type_ident ;                 (* Reuses wpl::take_datatype: auto|ip|chars|digit|float|time|bool|obj|array|... *)
```

## Evaluation (Right-Hand Side Expressions)

```ebnf
eval             = take_expr
                 | read_expr
                 | fmt_expr
                 | pipe_expr
                 | map_expr
                 | collect_expr
                 | match_expr
                 | sql_expr
                 | value_expr
                 | fun_call ;

(* Variable retrieval: take/read support unified parameter form; can have default body *)
take_expr        = "take", "(", [ arg_list ], ")", [ default_body ] ;
read_expr        = "read", "(", [ arg_list ], ")", [ default_body ] ;
; Note: '@' is only syntactic sugar for variable retrieval at var_get positions in fmt/pipe/collect, does not support default body, not an independent evaluation expression

arg_list         = arg, { ",", arg } ;
arg              = "option", ":", "[", key, { ",", key }, "]"
                 | ("in"|"keys"), ":", "[", key, { ",", key }, "]"
                 | "get",    ":", simple
                 | json_path ;                 (* See wp_parser::atom::take_json_path *)

default_body     = "{", "_", ":", gen_acq, [ ";" ], "}" ;
gen_acq          = take_expr | read_expr | value_expr | fun_call ;

(* Constant value: type name + literal wrapped in parentheses *)
value_expr       = data_type, "(", literal, ")" ;

(* Built-in functions (zero-param placeholders): Now::* family *)
fun_call         = ("Now::time"
                   |"Now::date"
                   |"Now::hour"), "(", ")" ;

(* String formatting, at least 1 parameter *)
fmt_expr         = "fmt", "(", string, ",", var_get, { ",", var_get }, ")" ;
var_get          = ("read" | "take"), "(", [ arg_list ], ")"
                 | "@", ident ;                  (* '@ref' equivalent to read(ref), does not support default body *)

(* Pipeline: pipe keyword can be omitted *)
pipe_expr        = ["pipe"], var_get, "|", pipe_fun, { "|", pipe_fun } ;
pipe_fun         = "nth",           "(", unsigned, ")"
                 | "get",           "(", ident,   ")"
                 | "base64_decode", "(", [ encode_type ], ")"
                 | "sxf_get",       "(", alnum*,  ")"
                 | "path",          "(", ("name"|"path"), ")"
                 | "url",           "(", ("domain"|"host"|"uri"|"path"|"params"), ")"
                 | "Time::to_ts_zone", "(", [ "-" ], unsigned, ",", ("ms"|"us"|"ss"|"s"), ")"
                 | "base64_encode" | "html_escape" | "html_unescape"
                 | "str_escape" | "json_escape" | "json_unescape"
                 | "Time::to_ts" | "Time::to_ts_ms" | "Time::to_ts_us"
                 | "to_json" | "to_str" | "skip_empty" | "ip4_to_int" ;

encode_type      = ident ;                     (* e.g.: Utf8/Gbk/Imap/... See functions reference doc *)

(* Aggregate to object: object internal is a sequence of sub-assignments; semicolons optional but recommended *)
map_expr         = "object", "{", map_item, { map_item }, "}" ;
map_item         = map_targets, "=", sub_acq, [ ";" ] ;
map_targets      = ident, { ",", ident }, [ ":", data_type ] ;
sub_acq          = take_expr | read_expr | value_expr | fun_call ;

(* Aggregate to array: collect from VarGet (supports keys/option wildcards) *)
collect_expr     = "collect", var_get ;

(* Pattern matching: single source/dual source two forms, supports in/!= and default branch *)
match_expr       = "match", match_source, "{", case1, { case1 }, [ default_case ], "}"
                 | "match", "(", var_get, ",", var_get, ")", "{", case2, { case2 }, [ default_case ], "}" ;
match_source     = var_get ;
case1            = cond1, "=>", calc, [ "," ], [ ";" ] ;
case2            = "(", cond1, ",", cond1, ")", "=>", calc, [ "," ], [ ";" ] ;
default_case     = "_", "=>", calc, [ "," ], [ ";" ] ;
calc             = read_expr | take_expr | value_expr | collect_expr ;

cond1            = "in", "(", value_expr, ",", value_expr, ")"
                 | "!", value_expr
                 | value_expr ;                 (* Omitting operator means equals *)
```

## SQL Expressions

```ebnf
sql_expr        = "select", sql_body, "where", sql_cond, ";" ;
sql_body        = sql_safe_body ;              (* Source code whitelisting: only [A-Za-z0-9_.] and '*' *)
sql_cond        = cond_expr ;
cond_expr       = cmp, { ("and" | "or"), cmp }
                 | "not", cond_expr
                 | "(", cond_expr, ")" ;
cmp             = ident, sql_op, cond_rhs ;
sql_op          = sql_cmp_op ;                 (* See wp_parser::sql_symbol::symbol_sql_cmp *)
cond_rhs        = read_expr | take_expr | fun_call | sql_literal ;
sql_literal     = number | string ;
```

Strict Mode Notes:
- Strict mode (enabled by default): When the body `<cols from table>` doesn't satisfy whitelist rules, parsing fails with an error (no longer falls back to original text).
- Compatibility mode: Set environment variable `OML_SQL_STRICT=0`, if body is invalid it falls back to original text (not recommended).
- Whitelist rules:
  - Column list: `*` or column names consisting of `[A-Za-z0-9_.]+` (dots allowed for qualification); functions, aggregates, aliases not supported.
  - Table name: `[A-Za-z0-9_.]+` (single table, join/subqueries not supported).
  - `from` is case-insensitive; extra whitespace allowed.

Error examples (strict mode):
- `select a, b from table-1 where ...` → Invalid table identifier (contains `-`).
- `select sum(a) from t where ...` → Column list contains function.
- `select a from t1 join t2 ...` → Join not supported.

## Privacy Section (Description)
Note: The engine does not enable runtime privacy/masking processing by default; the following is a DSL grammar capability description for scenarios that need it.

```ebnf
privacy_items   = privacy_item, { privacy_item } ;
privacy_item    = ident, ":", privacy_type ;
privacy_type    = "privacy_ip" | "privacy_specify_ip" | "privacy_id_card" | "privacy_mobile"
                 | "privacy_mail" | "privacy_domain" | "privacy_specify_name"
                 | "privacy_specify_domain" | "privacy_specify_address"
                 | "privacy_specify_company" | "privacy_keymsg" ;
```

## Lexical Conventions (Abstracted from wp_parser/wpl)

```ebnf
path            = ident, { ("/" | "."), ident } ;
wild_path       = path | path, "*" ;          (* Allows wildcard *)
wild_key        = ident, { ident | "*" } ;    (* Allows '*' in key name *)
type_ident      = ident ;                      (* e.g. auto/ip/chars/digit/float/time/bool/obj/array/... *)
ident           = letter, { letter | digit | "_" } ;
key             = ident ;
string          = "\"", { any-but-quote }, "\""
                | "'", { any-but-quote }, "'" ;
literal         = string | number | ip | bool | datetime | ... ;
json_path       = "/" , ... ;                 (* e.g. /a/b/[0]/1 *)
simple          = ident | number | string ;
unsigned        = digit, { digit } ;
eol             = { " " | "\t" | "\r" | "\n" } ;

letter          = "A" | ... | "Z" | "a" | ... | "z" ;
digit           = "0" | ... | "9" ;
alnum           = letter | digit ;
```

## Data Types

OML supports the following data types:

| Type | Description | Example |
|------|-------------|---------|
| `auto` | Auto-infer (default) | `field = read() ;` |
| `chars` | String | `name : chars = read() ;` |
| `digit` | Integer | `count : digit = read() ;` |
| `float` | Floating point | `ratio : float = read() ;` |
| `ip` | IP address | `addr : ip = read() ;` |
| `time` | Time | `occur_time : time = Now::time() ;` |
| `bool` | Boolean | `flag : bool = read() ;` |
| `obj` | Object | `info : obj = object { ... } ;` |
| `array` | Array | `items : array = collect read(keys:[...]) ;` |

## Typical Example (Consistent with Implementation)

```oml
name : csv_example
---
# Basic retrieval and default
version : chars = Now::time() ;
pos_sn           = read() { _ : chars(FALLBACK) };

# object aggregation
values : obj = object {
  cpu_free, memory_free : digit = read();
};

# collect array aggregation + pipeline
ports : array = collect read(keys:[sport,dport]);
ports_json      = pipe read(ports) | to_json ;
first_port      = pipe read(ports) | nth(0) ;

# Omitting pipe keyword
url_host        = read(http_url) | url(host) ;

# match
quarter : chars = match read(month) {
  in (digit(1), digit(3))   => chars(Q1),
  in (digit(4), digit(6))   => chars(Q2),
  in (digit(7), digit(9))   => chars(Q3),
  in (digit(10), digit(12)) => chars(Q4),
  _ => chars(QX) ;
};

# Dual source match
X : chars = match (read(city1), read(city2)) {
    (ip(127.0.0.1), ip(127.0.0.100)) => chars(bj) ;
    _ => chars(sz) ;
};

# SQL (where clause can mix read/take/Now::time/constants)
name,pinying = select name,pinying from example where pinying = read(py) ;
_,_ = select name,pinying from example where pinying = 'xiaolongnu' ;
---
# Privacy configuration (bind processor enums by key)
src_ip : privacy_ip
pos_sn : privacy_keymsg
```

## Pipe Function Quick Reference

| Function | Syntax | Description |
|----------|--------|-------------|
| `base64_encode` | `base64_encode` | Base64 encoding |
| `base64_decode` | `base64_decode` / `base64_decode(encoding)` | Base64 decoding |
| `html_escape` | `html_escape` | HTML escape |
| `html_unescape` | `html_unescape` | HTML unescape |
| `json_escape` | `json_escape` | JSON escape |
| `json_unescape` | `json_unescape` | JSON unescape |
| `str_escape` | `str_escape` | String escape |
| `Time::to_ts` | `Time::to_ts` | Time to timestamp (seconds, UTC+8) |
| `Time::to_ts_ms` | `Time::to_ts_ms` | Time to timestamp (milliseconds, UTC+8) |
| `Time::to_ts_us` | `Time::to_ts_us` | Time to timestamp (microseconds, UTC+8) |
| `Time::to_ts_zone` | `Time::to_ts_zone(timezone,unit)` | Time to specified timezone timestamp |
| `nth` | `nth(index)` | Get array element |
| `get` | `get(field_name)` | Get object field |
| `path` | `path(name\|path)` | Extract file path part |
| `url` | `url(domain\|host\|uri\|path\|params)` | Extract URL part |
| `sxf_get` | `sxf_get(field_name)` | Extract special format field |
| `to_str` | `to_str` | Convert to string |
| `to_json` | `to_json` | Convert to JSON |
| `ip4_to_int` | `ip4_to_int` | IPv4 to integer |
| `skip_empty` | `skip_empty` | Skip empty values |

## Notes
- Comments: Source code supports `//` single-line comments via CommentParser preprocessing.
- Target wildcards: When target name contains `*`, enters batch mode (BatchEval), see implementation in `oml_aggregate.rs`.
- Pipeline omission: From current version onwards, pipe expressions can omit the `pipe` prefix, writing directly as `read(...) | func` form.
- Grammar error prompts: Key positions include context and expected strings to help locate issues (see `keyword.rs` and `.context(...)` in each parser).
- This document only depicts the actually effective grammar; examples align completely with tests, see `crates/wp-oml/tests/test_case.rs`.
- Read semantics: `read` is non-destructive (can be read repeatedly, not removed from src); `take` is destructive (taken away and removed from src, cannot be taken again afterwards).
