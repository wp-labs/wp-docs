# OML Grammar Reference

This document provides the complete grammar definition of OML in EBNF format for precise understanding of syntax rules.

> Based on the parser implementation in `crates/wp-oml`, with lexical details reusing `wp_parser` and `wpl` parsing capabilities.

---

## Table of Contents

| Section | Content |
|---------|---------|
| [EBNF Notation](#ebnf-notation) | Grammar symbol conventions |
| [Top-Level Structure](#top-level-structure) | OML file structure |
| [Evaluation Expressions](#evaluation-expressions) | Expression types, value expressions, function calls, etc. |
| [Advanced Expressions](#advanced-expressions) | Format strings, pipes, match, aggregation |
| [SQL Expressions](#sql-expressions) | SQL query syntax |
| [Static Bindings](#static-bindings) | Static constant definitions and references |
| [Temporary Fields](#temporary-fields) | `__` prefixed intermediate fields |
| [Privacy Section](#privacy-section) | Data masking syntax |
| [Lexical Conventions](#lexical-conventions) | Identifiers, literals, comments |
| [Data Types](#data-types) | Data types |
| [Complete Example](#complete-example) | Comprehensive example |
| [Pipe Function Reference](#pipe-function-reference) | Common pipe functions |
| [Syntax Summary](#syntax-summary) | Required elements, optional elements, notes |

---

## EBNF Notation

- `=` : Definition
- `,` : Concatenation (sequence)
- `|` : Alternation (choice)
- `[ ]` : Optional (0 or 1 time)
- `{ }` : Repetition (0 or more times)
- `( )` : Grouping
- `"text"` : Literal
- `(* ... *)` : Comment

---

## Top-Level Structure

```ebnf
oml              = header, sep_line, [ static_blocks ], aggregate_items,
                   [ sep_line, privacy_items ] ;

header           = "name", ":", name, eol,
                   [ "rule", ":", rule_path, { rule_path }, eol ],
                   [ "enable", ":", ("true" | "false"), eol ] ;

sep_line         = "---" ;

static_blocks    = { "static", "{", static_item, { static_item }, "}" } ;
static_item      = target, "=", eval, ";" ;

name             = path ;                       (* e.g.: test *)
rule_path        = wild_path ;                  (* e.g.: wpx/abc, wpx/efg *)

aggregate_items  = aggregate_item, { aggregate_item } ;
aggregate_item   = target_list, "=", eval, ";" ;

target_list      = target, { ",", target } ;
target           = target_name, [ ":", data_type ] ;
target_name      = wild_key | "_" ;            (* wildcards with '*' allowed; '_' means anonymous/discard *)
data_type        = type_ident ;                (* auto|ip|chars|digit|float|time|bool|obj|array etc. *)
```

**Notes**:
- `name : <config_name>` - Required configuration name declaration
- `rule : <rule_path>` - Optional rule association, supports space or newline separated multiple rules
- `enable : true|false` - Optional enable switch (default `true`); order of `rule` and `enable` is flexible
- `static { ... }` - Optional static binding block, placed after `---` separator and before main bindings
- `---` - Separator, distinguishes declaration section from configuration section
- Every configuration entry must end with `;`

---

## Evaluation Expressions

### Expression Types

```ebnf
eval             = take_expr
                 | read_expr
                 | fmt_expr
                 | pipe_expr
                 | map_expr
                 | collect_expr
                 | calc_expr
                 | match_expr
                 | sql_expr
                 | value_expr
                 | fun_call
                 | static_ref ;
```

### Read Expressions

```ebnf
(* Variable access: take/read support uniform parameter format; can be followed by default body *)
take_expr        = "take", "(", [ arg_list ], ")", [ default_body ] ;
read_expr        = "read", "(", [ arg_list ], ")", [ default_body ] ;

arg_list         = arg, { ",", arg } ;
arg              = "option", ":", "[", key, { ",", key }, "]"
                 | ("in"|"keys"), ":", "[", key, { ",", key }, "]"
                 | "get",    ":", simple
                 | json_path ;                 (* see wp_parser::atom::take_json_path *)

default_body     = "{", "_", ":", gen_acq, [ ";" ], "}" ;
gen_acq          = take_expr | read_expr | value_expr | fun_call | static_ref ;
```

**Notes**:
- `@` is only used as syntactic sugar for var_get positions in fmt/pipe/collect
- `@ref` is equivalent to `read(ref)`, but does not support default body
- Not available as a standalone evaluation expression

**Examples**:
```oml
# Basic read
value = read(field) ;

# With default value
value = read(field) { _ : chars(default) } ;

# option parameter
value = read(option:[id, uid, user_id]) ;

# keys parameter
values = collect read(keys:[field1, field2]) ;

# JSON path
name = read(/user/info/name) ;
item = read(/data/[0]/name) ;
```

### Value Expressions

```ebnf
(* Constant value: type name + parenthesized literal *)
value_expr       = data_type, "(", literal, ")" ;
```

**Examples**:
```oml
text = chars(hello) ;
text2 = chars('hello world') ;
count = digit(42) ;
ratio = float(3.14) ;
address = ip(192.168.1.1) ;
flag = bool(true) ;
ts = time(2020-10-01 12:30:30) ;
```

### Function Calls

```ebnf
(* Built-in functions (zero-argument placeholders): Now::* family *)
fun_call         = ("Now::time"
                   |"Now::date"
                   |"Now::hour"), "(", ")" ;
```

**Examples**:
```oml
now = Now::time() ;
today = Now::date() ;
hour = Now::hour() ;
```

### Static Symbol References

```ebnf
(* Reference constants defined in static blocks, using identifier directly *)
static_ref       = ident ;                     (* must be defined in static { } *)
```

**Examples**:
```oml
static {
    tpl = object { id = chars(E1) ; } ;
}
target = tpl ;                                 # reference tpl from static block
```

---

## Advanced Expressions

### Format Strings

```ebnf
(* String formatting, requires at least 1 parameter *)
fmt_expr         = "fmt", "(", string, ",", var_get, { ",", var_get }, ")" ;
var_get          = ("read" | "take"), "(", [ arg_list ], ")"
                 | "@", ident ;                  (* '@ref' equivalent to read(ref), no default body *)
```

**Examples**:
```oml
message = fmt("{}-{}", @user, read(city)) ;
id = fmt("{}:{}", read(host), read(port)) ;
```

### Pipe Expressions

```ebnf
(* Pipe: pipe keyword can be omitted *)
pipe_expr        = ["pipe"], var_get, "|", pipe_fun, { "|", pipe_fun } ;

pipe_fun         = "nth",           "(", unsigned, ")"
                 | "get",           "(", ident,   ")"
                 | "base64_decode", "(", [ encode_type ], ")"
                 | "path",          "(", ("name"|"path"), ")"
                 | "url",           "(", ("domain"|"host"|"uri"|"path"|"params"), ")"
                 | "Time::to_ts_zone", "(", [ "-" ], unsigned, ",", ("ms"|"us"|"ss"|"s"), ")"
                 | "starts_with",   "(", string, ")"
                 | "map_to",        "(", (string | number | bool), ")"
                 | "base64_encode" | "html_escape" | "html_unescape"
                 | "str_escape" | "json_escape" | "json_unescape"
                 | "Time::to_ts" | "Time::to_ts_ms" | "Time::to_ts_us"
                 | "to_json" | "to_str" | "skip_empty" | "ip4_to_int"
                 | "extract_main_word" | "extract_subject_object" ;

encode_type      = ident ;                     (* e.g.: Utf8/Gbk/Imap/... *)
```

**Examples**:
```oml
# With pipe keyword
result = pipe read(data) | to_json | base64_encode ;

# Without pipe keyword
result = read(data) | to_json | base64_encode ;

# Time conversion
ts = read(time) | Time::to_ts_zone(0, ms) ;

# URL parsing
host = read(url) | url(host) ;

# String prefix check
is_http = read(url) | starts_with('http://') ;

# Map to constant value
status = read(code) | map_to(200) ;

# Extract main word
keyword = read(message) | extract_main_word ;

# Extract subject-object structure
log_struct = read(message) | extract_subject_object ;
```

### Object Aggregation

```ebnf
(* Aggregate to object: object body is a sequence of sub-assignments; semicolons optional but recommended *)
map_expr         = "object", "{", map_item, { map_item }, "}" ;
map_item         = map_targets, "=", sub_acq, [ ";" ] ;
map_targets      = ident, { ",", ident }, [ ":", data_type ] ;
sub_acq          = take_expr | read_expr | value_expr | fun_call | static_ref ;
```

**Examples**:
```oml
info : obj = object {
    name : chars = read(name) ;
    age : digit = read(age) ;
    city : chars = read(city) ;
} ;
```

### Array Aggregation

```ebnf
(* Aggregate to array: collect from VarGet (supports keys/option wildcards) *)
collect_expr     = "collect", var_get ;
```

**Examples**:
```oml
# Collect multiple fields
ports = collect read(keys:[sport, dport]) ;

# Using wildcards
metrics = collect read(keys:[cpu_*]) ;
```

### Arithmetic Expressions

```ebnf
calc_expr         = "calc", "(", calc_add_expr, ")" ;
calc_add_expr     = calc_mul_expr, { ("+" | "-"), calc_mul_expr } ;
calc_mul_expr     = calc_unary_expr, { ("*" | "/" | "%"), calc_unary_expr } ;
calc_unary_expr   = [ "-" ], calc_primary_expr ;
calc_primary_expr = number
                  | var_get
                  | calc_fun_expr
                  | "(", calc_add_expr, ")" ;
calc_fun_expr     = calc_fun, "(", calc_add_expr, ")" ;
calc_fun          = "abs" | "round" | "floor" | "ceil" ;
```

**Notes**:
- `var_get` supports `read(...)`, `take(...)`, and the `@field` shorthand
- Operands only accept numeric literals or numeric fields; `/` always returns `float`
- `%` only supports integer modulo; divide-by-zero, missing fields, non-numeric inputs, and invalid `%` return `ignore`
- `match` branch values still use the existing sub-expression set and do not accept `calc(...)` directly; bind a temp field first if needed

**Examples**:
```oml
risk_score : float = calc(read(cpu) * 0.7 + read(mem) * 0.3) ;
delta      : digit = calc(read(cur) - read(prev)) ;
ratio      : float = calc(read(ok_cnt) / read(total_cnt)) ;
bucket     : digit = calc(read(uid) % 16) ;
error_pct  : digit = calc(round((read(err_cnt) * 100) / read(total_cnt))) ;
```

### Pattern Matching

```ebnf
(* Pattern matching: single-source/multi-source variants, supports in/!=/OR/function matching and default branch *)
match_expr       = "match", match_source, "{", case1, { case1 }, [ default_case ], "}"
                 | "match", "(", var_get, ",", var_get, { ",", var_get }, ")", "{", case_multi, { case_multi }, [ default_case ], "}" ;

match_source     = var_get ;
case1            = cond1, "=>", match_value, [ "," ], [ ";" ] ;
case_multi       = "(", cond1, ",", cond1, { ",", cond1 }, ")", "=>", match_value, [ "," ], [ ";" ] ;
default_case     = "_", "=>", match_value, [ "," ], [ ";" ] ;
match_value      = read_expr | take_expr | value_expr | collect_expr | static_ref ;

cond1            = cond1_atom, { "|", cond1_atom }   (* OR: multiple conditions separated by | *)
cond1_atom       = "in", "(", value_expr, ",", value_expr, ")"
                 | "!", value_expr
                 | match_fun                           (* function matching *)
                 | value_expr ;                        (* omitted operator means equality *)

match_fun        = "starts_with",  "(", string, ")"   (* prefix matching *)
                 | "ends_with",    "(", string, ")"   (* suffix matching *)
                 | "contains",     "(", string, ")"   (* substring matching *)
                 | "regex_match",  "(", string, ")"   (* regex matching *)
                 | "iequals",      "(", string, ")"   (* case-insensitive equality *)
                 | "is_empty",     "(", ")"            (* empty value check *)
                 | "gt",           "(", number, ")"    (* greater than *)
                 | "lt",           "(", number, ")"    (* less than *)
                 | "eq",           "(", number, ")"    (* equal (float tolerance) *)
                 | "in_range",     "(", number, ",", number, ")" ; (* range check *)
```

**Notes**:
- **Multi-source matching**: `match (src1, src2, ...)` supports any number of source fields (>=2), not limited to two
- **OR syntax**: Use `|` to separate multiple alternative conditions at a condition position; any match succeeds
- **Function matching**: 11 built-in match functions for flexible string and numeric comparisons

**Examples**:
```oml
# Single-source matching
level = match read(status) {
    in (digit(200), digit(299)) => chars(success) ;
    in (digit(400), digit(499)) => chars(error) ;
    _ => chars(other) ;
} ;

# Single-source OR matching
tier = match read(city) {
    chars(bj) | chars(sh) | chars(gz) => chars(tier1) ;
    chars(cd) | chars(wh) => chars(tier2) ;
    _ => chars(other) ;
} ;

# Multi-source matching (two sources)
result = match (read(a), read(b)) {
    (digit(1), digit(2)) => chars(case1) ;
    _ => chars(default) ;
} ;

# Multi-source matching (three sources)
zone = match (read(city), read(region), read(country)) {
    (chars(bj), chars(north), chars(cn)) => chars(result1) ;
    _ => chars(default) ;
} ;

# Multi-source + OR matching
priority = match (read(city), read(level)) {
    (chars(bj) | chars(sh), chars(high)) => chars(priority) ;
    (chars(gz), chars(low) | chars(mid)) => chars(normal) ;
    _ => chars(default) ;
} ;

# Function matching
event = match read(Content) {
    starts_with('[ERROR]') => chars(error) ;
    starts_with('[WARN]') => chars(warning) ;
    contains('timeout') => chars(timeout) ;
    ends_with('.failed') => chars(failure) ;
    regex_match('^\d{4}-\d{2}-\d{2}') => chars(dated) ;
    is_empty() => chars(empty) ;
    _ => chars(other) ;
} ;

# Numeric function matching
grade = match read(score) {
    gt(90) => chars(excellent) ;
    in_range(60, 90) => chars(pass) ;
    lt(60) => chars(fail) ;
    _ => chars(unknown) ;
} ;

# Case-insensitive matching
status = match read(result) {
    iequals('success') => chars(ok) ;
    iequals('error') => chars(fail) ;
    _ => chars(other) ;
} ;

# Case-insensitive multi-value matching
status_class = match read(status) {
    iequals_any('success', 'ok', 'done') => chars(good) ;
    iequals_any('error', 'failed', 'timeout') => chars(bad) ;
    _ => chars(other) ;
} ;
```

### `lookup_nocase`

`lookup_nocase(dict_symbol, key_expr, default_expr)` performs a case-insensitive lookup against a static object dictionary.

```oml
static {
    status_score = object {
        error = float(90.0);
        warning = float(70.0);
        success = float(20.0);
    };
}

risk_score : float = lookup_nocase(status_score, read(status), 40.0) ;
```

- `dict_symbol` must reference an object defined in `static`
- `key_expr` is normalized with `trim + lowercase` before lookup
- If the key misses or is not a string, `default_expr` is returned

### `calc(...)`

`calc(expr)` evaluates an explicit numeric arithmetic expression.

```oml
risk_score : float = calc(read(cpu) * 0.7 + read(mem) * 0.3) ;
bucket     : digit = calc(read(uid) % 16) ;
distance   : float = calc(abs(read(actual) - read(expect))) ;
error_pct  : digit = calc(round((read(err_cnt) * 100) / read(total_cnt))) ;
```

- Supported operators: `+ - * / %`
- Supported functions: `abs(...)`, `round(...)`, `floor(...)`, `ceil(...)`
- Supported field access: `read(...)`, `take(...)`, `@field`
- Divide-by-zero, missing fields, non-numeric inputs, and float `%` all return `ignore`

---

## SQL Expressions

```ebnf
sql_expr        = "select", sql_body, "where", sql_cond, ";" ;
sql_body        = sql_safe_body ;              (* source whitelisting: only [A-Za-z0-9_.] and '*' *)
sql_cond        = cond_expr ;

cond_expr       = cmp, { ("and" | "or"), cmp }
                 | "not", cond_expr
                 | "(", cond_expr, ")" ;

cmp             = ident, sql_op, cond_rhs ;
sql_op          = sql_cmp_op ;                 (* see wp_parser::sql_symbol::symbol_sql_cmp *)
cond_rhs        = read_expr | take_expr | fun_call | sql_literal ;
sql_literal     = number | string ;
```

### Strict Mode

- **Strict mode (enabled by default)**: Parse error when `<cols from table>` violates whitelist rules
- **Compatibility mode**: Set environment variable `OML_SQL_STRICT=0`, falls back to raw text on invalid body (not recommended)
- **Whitelist rules**:
  - Column list: `*` or column names matching `[A-Za-z0-9_.]+` (dot allowed as qualifier)
  - Table name: `[A-Za-z0-9_.]+` (single table, no join/subquery)
  - `from` is case-insensitive; extra whitespace allowed

**Examples**:
```oml
# Valid examples
name, email = select name, email from users where id = read(user_id) ;

# Using string constants
data = select * from table where type = 'admin' ;

# IP range query
zone = select zone from ip_geo
    where ip_start_int <= ip4_int(read(src_ip))
      and ip_end_int >= ip4_int(read(src_ip)) ;
```

**Invalid examples (strict mode)**:
```oml
# Table name contains illegal characters
data = select a, b from table-1 where ... ;

# Column list contains functions
data = select sum(a) from t where ... ;

# Joins not supported
data = select a from t1 join t2 ... ;
```

---

## Static Bindings

`static` blocks define compile-time constants that can be referenced in main bindings and match expressions.

```ebnf
static_blocks    = { "static", "{", static_item, { static_item }, "}" } ;
static_item      = target, "=", eval, ";" ;
```

**Notes**:
- `static` blocks are placed after the `---` separator and before the main bindings
- Each binding within the block is evaluated at compile time into a `DataField`
- Reference in main bindings by using the identifier directly: `result = symbol_name ;`
- Can be referenced in `match` conditions and results, `object` sub-bindings, and `read/take` default bodies
- Duplicate symbol names are not allowed

**Examples**:
```oml
name : model_with_static
---
static {
    tpl = object {
        id = chars(E1) ;
        type = chars(default) ;
    } ;
    fallback = chars(N/A) ;
}

# Direct reference to static symbol
template = tpl ;

# Reference in match result
target = match read(Content) {
    starts_with('foo') => tpl ;
    _ => tpl ;
} ;

# Reference in default body
value = take(Value) { _ : fallback } ;

# Reference in object sub-binding
result = object {
    clone = tpl ;
} ;
```

---

## Temporary Fields

Field names starting with `__` (double underscore) are marked as temporary fields and automatically converted to `Ignore` type in the output (they do not appear in the final data).

**Purpose**: Intermediate computation results that should not appear in the output record.

**Examples**:
```oml
name : temp_example
---
# Temporary field: participates in intermediate computation, not output
__temp_type = chars(error) ;

# Reference temporary field in matching
result = match read(__temp_type) {
    chars(error) => chars(failed) ;
    _ => chars(ok) ;
} ;
```

In the output record, `result` is output normally while `__temp_type` is automatically ignored.

---

## Privacy Section

> Note: The engine does not enable runtime privacy/masking by default; the following describes the DSL syntax capability for reference in scenarios that require it.

```ebnf
privacy_items   = privacy_item, { privacy_item } ;
privacy_item    = ident, ":", privacy_type ;

privacy_type    = "privacy_ip"
                 | "privacy_specify_ip"
                 | "privacy_id_card"
                 | "privacy_mobile"
                 | "privacy_mail"
                 | "privacy_domain"
                 | "privacy_specify_name"
                 | "privacy_specify_domain"
                 | "privacy_specify_address"
                 | "privacy_specify_company"
                 | "privacy_keymsg" ;
```

**Examples**:
```oml
name : privacy_example
---
field = read() ;
---
src_ip : privacy_ip
pos_sn : privacy_keymsg
```

---

## Lexical Conventions

```ebnf
path            = ident, { ("/" | "."), ident } ;
wild_path       = path | path, "*" ;          (* wildcards allowed *)
wild_key        = ident, { ident | "*" } ;    (* '*' allowed within key names *)
type_ident      = ident ;                      (* e.g. auto/ip/chars/digit/float/time/bool/obj/array *)
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

---

## Data Types

OML type annotations support the following values (parsed by `DataType::from()`):

### Common Types

| Type | Description | Example |
|------|-------------|---------|
| `auto` | Auto-detect (default) | `field = read() ;` |
| `chars` | String | `name : chars = read() ;` |
| `digit` | Integer | `count : digit = read() ;` |
| `float` | Floating-point | `ratio : float = read() ;` |
| `ip` | IP address | `addr : ip = read() ;` |
| `time` | Time | `timestamp : time = Now::time() ;` |
| `bool` | Boolean | `flag : bool = read() ;` |
| `obj` | Object | `info : obj = object { ... } ;` |
| `array` | Array | `items : array = collect read(...) ;` |

### Extended Types

| Type | Description |
|------|-------------|
| `time_iso` | ISO format time |
| `time_3339` | RFC 3339 time |
| `time_2822` | RFC 2822 time |
| `time_timestamp` | Unix timestamp |
| `time_clf` | CLF log time (Apache/Nginx) |
| `time/apache` | CLF alias |
| `time/timestamp` | Timestamp alias |
| `time/rfc3339` | RFC 3339 alias |
| `url` | URL |
| `domain` | Domain name |
| `ip_net` | Network segment |
| `kv` | Key-Value text |
| `json` | JSON text |
| `base64` | Base64 encoded text |
| `array/<sub>` | Typed array (e.g. `array/digit`) |

---

## Complete Example

```oml
name : csv_example
rule : /csv/data
enable : true
---
static {
    ERROR_TPL = object {
        type = chars(error) ;
        level = digit(0) ;
    } ;
}

# Basic value retrieval with default
version : chars = Now::time() ;
pos_sn = read() { _ : chars(FALLBACK) } ;

# Temporary field (not included in output)
__raw_type = read(type) ;

# Object aggregation
values : obj = object {
    cpu_free, memory_free : digit = read() ;
} ;

# Collect array aggregation + pipe
ports : array = collect read(keys:[sport, dport]) ;
ports_json = pipe read(ports) | to_json ;
first_port = pipe read(ports) | nth(0) ;

# Pipe without pipe keyword
url_host = read(http_url) | url(host) ;

# match
quarter : chars = match read(month) {
    in (digit(1), digit(3))   => chars(Q1) ;
    in (digit(4), digit(6))   => chars(Q2) ;
    in (digit(7), digit(9))   => chars(Q3) ;
    in (digit(10), digit(12)) => chars(Q4) ;
    _ => chars(QX) ;
} ;

# Two-source match
X : chars = match (read(city1), read(city2)) {
    (ip(127.0.0.1), ip(127.0.0.100)) => chars(bj) ;
    _ => chars(sz) ;
} ;

# Three-source match
zone : chars = match (read(city), read(region), read(country)) {
    (chars(bj), chars(north), chars(cn)) => chars(zone1) ;
    (chars(sh), chars(east), chars(cn)) => chars(zone2) ;
    _ => chars(unknown) ;
} ;

# OR matching (single source)
tier : chars = match read(city) {
    chars(bj) | chars(sh) | chars(gz) => chars(tier1) ;
    chars(cd) | chars(wh) => chars(tier2) ;
    _ => chars(other) ;
} ;

# OR matching (multi-source)
priority : chars = match (read(city), read(level)) {
    (chars(bj) | chars(sh), chars(high)) => chars(priority) ;
    (chars(gz), chars(low) | chars(mid)) => chars(normal) ;
    _ => chars(default) ;
} ;

# Function matching
event = match read(log_line) {
    starts_with('[ERROR]') => chars(error) ;
    ends_with('.failed') => chars(failure) ;
    contains('timeout') => chars(timeout) ;
    regex_match('^\d{4}-\d{2}-\d{2}') => chars(dated) ;
    is_empty() => chars(empty) ;
    _ => chars(other) ;
} ;

# Numeric function matching
grade = match read(score) {
    gt(90) => chars(excellent) ;
    in_range(60, 90) => chars(pass) ;
    lt(60) => chars(fail) ;
    _ => chars(unknown) ;
} ;

# Case-insensitive matching
result = match read(status) {
    iequals('success') => chars(ok) ;
    _ => chars(fail) ;
} ;

# Static reference
error_info = match read(__raw_type) {
    chars(error) => ERROR_TPL ;
    _ => chars(normal) ;
} ;

# SQL (where clause can mix read/take/Now::time/constants)
name, pinying = select name, pinying from example where pinying = read(py) ;
_, _ = select name, pinying from example where pinying = 'xiaolongnu' ;

---
# Privacy configuration (bind processor enum by key)
src_ip : privacy_ip
pos_sn : privacy_keymsg
```

---

## Pipe Function Reference

| Function | Syntax | Description |
|----------|--------|-------------|
| `base64_encode` | `base64_encode` | Base64 encode |
| `base64_decode` | `base64_decode` / `base64_decode(encoding)` | Base64 decode |
| `html_escape` | `html_escape` | HTML escape |
| `html_unescape` | `html_unescape` | HTML unescape |
| `json_escape` | `json_escape` | JSON escape |
| `json_unescape` | `json_unescape` | JSON unescape |
| `str_escape` | `str_escape` | String escape |
| `Time::to_ts` | `Time::to_ts` | Time to timestamp (seconds, UTC+8) |
| `Time::to_ts_ms` | `Time::to_ts_ms` | Time to timestamp (milliseconds, UTC+8) |
| `Time::to_ts_us` | `Time::to_ts_us` | Time to timestamp (microseconds, UTC+8) |
| `Time::to_ts_zone` | `Time::to_ts_zone(timezone,unit)` | Time to timestamp with timezone |
| `nth` | `nth(index)` | Get array element |
| `get` | `get(field_name)` | Get object field |
| `path` | `path(name\|path)` | Extract file path component |
| `url` | `url(domain\|host\|uri\|path\|params)` | Extract URL component |
| `starts_with` | `starts_with('prefix')` | Check if string starts with prefix |
| `map_to` | `map_to(value)` | Map to constant value (string/number/boolean) |
| `extract_main_word` | `extract_main_word` | Extract main word (first non-empty word) |
| `extract_subject_object` | `extract_subject_object` | Extract log subject-object structure (subject/action/object/status) |
| `to_str` | `to_str` | Convert to string |
| `to_json` | `to_json` | Convert to JSON |
| `ip4_to_int` | `ip4_to_int` | IPv4 to integer |
| `skip_empty` | `skip_empty` | Skip empty values |

### Match Function Reference (for match conditions)

| Function | Syntax | Description |
|----------|--------|-------------|
| `starts_with` | `starts_with('prefix')` | Prefix matching |
| `ends_with` | `ends_with('suffix')` | Suffix matching |
| `contains` | `contains('substring')` | Substring matching |
| `regex_match` | `regex_match('pattern')` | Regular expression matching |
| `iequals` | `iequals('value')` | Case-insensitive equality |
| `is_empty` | `is_empty()` | Empty value check |
| `gt` | `gt(number)` | Greater than |
| `lt` | `lt(number)` | Less than |
| `eq` | `eq(number)` | Equal (float tolerance) |
| `in_range` | `in_range(min, max)` | Range check (closed interval) |

---

## Syntax Summary

### Required Elements

1. **Configuration name**: `name : <name>`
2. **Separator**: `---`
3. **Semicolons**: Every top-level entry must end with `;`

### Optional Elements

1. **Type declaration**: `field : <type> = ...` (defaults to `auto`)
2. **rule field**: `rule : <rule_path>`
3. **enable field**: `enable : true|false` (defaults to `true`)
4. **static block**: `static { ... }`
5. **Default value**: `read() { _ : <default> }`
6. **pipe keyword**: `pipe read() | func` can be shortened to `read() | func`

### Comments

```oml
# Single-line comment (using # or //)
// C++ style comment also supported
```

### Target Wildcards

```oml
* = take() ;           # Take all fields
alert* = take() ;      # Take all fields starting with alert
*_log = take() ;       # Take all fields ending with _log
```

### Temporary Fields

```oml
__temp = chars(value) ;      # Starts with __, automatically ignored in output
result = read(__temp) ;      # Can be referenced in other expressions
```

### Read Semantics

- **read**: Non-destructive (can read repeatedly, does not remove from src)
- **take**: Destructive (removed from src after taking, cannot be taken again)

---

## Next Steps

- [Core Concepts](./02-core-concepts.md) - Understand the design philosophy
- [Practical Guide](./03-practical-guide.md) - See real-world examples
- [Functions Reference](./04-functions-reference.md) - Browse all available functions
- [Quick Start](./01-quickstart.md) - Get started with OML
