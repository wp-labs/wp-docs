# WPL Grammar Reference (aligned with `src/parser`)

This document is aligned with the current implementation in `wp-lang/src/parser`. It focuses on:

- the real parser entry points for packages, rules, and expressions
- how groups, fields, separators, and field pipes compose
- the constraints and limits that the current parser actually enforces

Authoritative implementation:

- `src/parser/wpl_pkg.rs`
- `src/parser/wpl_rule.rs`
- `src/parser/parse_code.rs`
- `src/parser/wpl_group.rs`
- `src/parser/wpl_field.rs`
- `src/parser/wpl_fun.rs`

---

## Navigation

| Section | Description |
|---------|-------------|
| [Complete EBNF](#complete-ebnf) | Syntax summary aligned with current parser behavior |
| [Implementation Constraints](#implementation-constraints) | Important parser/eval limitations |
| [Related Sources](#related-sources) | Relevant source files |

---

## Complete EBNF

```ebnf
; The top-level entry is usually a package; some internal APIs also parse a single rule or express directly

package_decl     = [ annotation ] "package" wsp1 key wsp? "{" wsp? rule_decl+ wsp? "}" ;
rule_decl        = [ annotation ] "rule" wsp? exact_path wsp? "{" wsp? express wsp? "}" ;

express          = [ preproc ] group { wsp? "," wsp? group } ;

; Preprocess pipeline: at least one step and must end with '|'
preproc          = preproc_item { preproc_item } "|" ;
preproc_item     = "|" wsp? preproc_step wsp? ;
preproc_step     = key
                 | "plg_pipe" ( "/" wsp? key | "(" wsp? key wsp? ")" ) ;

group            = [ group_meta wsp? ] "(" wsp? field_list_opt wsp? ")"
                   [ "[" number "]" ]
                   [ group_sep ] ;

group_meta       = "alt" | "opt" | "some_of" | "seq" | "not" ;
group_sep        = shortcut_sep ;    ; Group-level separators currently support only `\x` style, not `{...}` pattern separators

field_list_opt   = [ field { wsp? "," wsp? field } [ wsp? "," ] ] ;

field            = [ repeat ] meta_token
                   [ symbol_content ]
                   [ subfields ]
                   [ ":" wsp? var_name ]
                   [ "[" number "]" ]
                   [ format ]
                   [ field_sep ]
                   { pipe } ;

repeat           = [ number ] "*" ;  ; `*meta` or `3*meta`

; Subfield definitions inside composite fields such as json/kv/kvarr
subfields         = "(" wsp? subfield_list_opt wsp? ")" ;
subfield_list_opt = [ subfield { wsp? "," wsp? subfield } [ wsp? "," ] ] ;

subfield         = [ subfield_meta ]
                   [ symbol_content ]
                   [ "@" ref_path_or_quoted ]
                   [ ":" wsp? var_name ]
                   [ format ]
                   [ field_sep ]
                   { pipe } ;

subfield_meta    = meta_token | "opt" "(" wsp? key wsp? ")" ;
; If a subfield omits meta, it defaults to chars

; meta_token is controlled by `resolve_meta()` in the implementation:
; 1. `bad_json`
; 2. or anything recognized by `wp_model_core::model::DataType::from(token)`
meta_token       = meta_char { meta_char } ;

; Only symbol / peek_symbol may carry content, e.g. `symbol(OK)`
symbol_content   = "(" symbol_chars ")" ;

format           = scope_format | quote_format ;
scope_format     = "<" scope_chars "," scope_chars ">" ;
quote_format     = '"' ;      ; shorthand for double-quote on both sides

field_sep        = shortcut_sep | pattern_sep ;

shortcut_sep     = sep_char { sep_char } ;
sep_char         = '\' any_char ;

pattern_sep      = "{" pattern_content "}" ;
pattern_content  = pattern_unit { pattern_unit } [ preserve ] ;
pattern_unit     = literal_char | wildcard | escape_seq ;
wildcard         = "*" | "?" ;
escape_seq       = '\' ( '\' | "*" | "?" | "{" | "}" | "(" | ")" | "s" | "S" | "h" | "H" | "0" | "n" | "t" | "r" ) ;
preserve         = "(" pattern_unit { pattern_unit } ")" ;

pipe             = "|" wsp? ( fun_call | group ) ;

fun_call         = "take" "(" wsp? take_target wsp? ")"
                 | "last" "(" wsp? ")"
                 | "f_has" "(" wsp? key wsp? ")"
                 | "f_chars_has" "(" wsp? key wsp? "," wsp? bare_string wsp? ")"
                 | "f_chars_not_has" "(" wsp? key wsp? "," wsp? bare_string wsp? ")"
                 | "f_chars_in" "(" wsp? key wsp? "," wsp? bare_string_array wsp? ")"
                 | "f_digit_has" "(" wsp? key wsp? "," wsp? number wsp? ")"
                 | "f_digit_in" "(" wsp? key wsp? "," wsp? number_array wsp? ")"
                 | "f_ip_in" "(" wsp? key wsp? "," wsp? ip_array wsp? ")"
                 | "has" "(" wsp? ")"
                 | "chars_has" "(" wsp? bare_string wsp? ")"
                 | "chars_not_has" "(" wsp? bare_string wsp? ")"
                 | "chars_in" "(" wsp? bare_string_array wsp? ")"
                 | "digit_has" "(" wsp? number wsp? ")"
                 | "digit_in" "(" wsp? number_array wsp? ")"
                 | "digit_range" "(" wsp? number wsp? "," wsp? number wsp? ")"
                 | "ip_in" "(" wsp? ip_array wsp? ")"
                 | "json_unescape" "(" wsp? ")"
                 | "base64_decode" "(" wsp? ")"
                 | "chars_replace" "(" wsp? string_or_quoted wsp? "," wsp? string_or_quoted wsp? ")"
                 | "regex_match" "(" wsp? string_or_quoted wsp? ")"
                 | "starts_with" "(" wsp? string_or_quoted wsp? ")"
                 | "not" "(" wsp? fun_call wsp? ")" ;

annotation       = "#[" wsp? annotation_item { wsp? "," wsp? annotation_item } wsp? "]" ;
annotation_item  = tag_annotation | copy_raw_annotation ;
tag_annotation   = "tag" "(" wsp? tag_kv { wsp? "," wsp? tag_kv } wsp? ")" ;
copy_raw_annotation = "copy_raw" "(" wsp? tag_kv wsp? ")" ;
tag_kv           = key wsp? ":" wsp? ( quoted_string | raw_string ) ;

take_target      = key | quoted_string ;
ref_path_or_quoted = ref_path | single_quoted_raw ;

bare_string_array = "[" wsp? bare_string { wsp? "," wsp? bare_string } wsp? "]" ;
number_array     = "[" wsp? number { wsp? "," wsp? number } wsp? "]" ;
ip_array         = "[" wsp? ip_addr { wsp? "," wsp? ip_addr } wsp? "]" ;

key              = key_char { key_char } ;
exact_path       = key ;
var_name         = var_char { var_char } ;
ref_path         = ref_char { ref_char } ;

quoted_string    = double_quoted | single_quoted ;
raw_string       = 'r#"' { any_char } '"#' | 'r"' { any_char } '"' ;
single_quoted_raw = "'" { single_raw_char } "'" ;
string_or_quoted = bare_string | quoted_string ;

bare_string      = bare_char { bare_char } ;
number           = digit { digit } ;
ip_addr          = ipv4 | ipv6 | quoted_string ;

key_char         = letter | digit | "_" | "." | "/" | "-" ;
var_char         = letter | digit | "_" | "." | "-" ;
ref_char         = key_char | "[" | "]" | "*" ;
meta_char        = letter | digit | "_" | "/" ;

bare_char        = ? non-delimiter text as parsed by `take_string`; typically used for bare string arguments ? ;
scope_chars      = ? any non-empty content, captured as a `<..., ...>` pair ? ;
symbol_chars     = ? any chars, allowing `\)` to escape a closing paren ? ;
single_raw_char  = ? any char; only `\'` is special ? ;
literal_char     = ? any non-special character ? ;
double_quoted    = '"' { escaped | dq_char } '"' ;
single_quoted    = "'" { escaped | sq_char } "'" ;
escaped          = '\' ( '"' | "'" | '\' | "n" | "t" | "r" | "x" hex hex ) ;
dq_char          = ? any character except `"` and `\` ? ;
sq_char          = ? any character except `'` and `\` ? ;
digit            = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
hex              = digit | "a".."f" | "A".."F" ;
letter           = "A".."Z" | "a".."z" ;
wsp              = { " " | "\t" | "\n" | "\r" } ;
wsp1             = ( " " | "\t" | "\n" | "\r" ) { wsp } ;
```

---

## Implementation Constraints

### Top-level entry points

- `wpl_package()` parses `package ... { rule ... }`
- `wpl_rule()` can parse a single `rule`
- `wpl_express()` parses only the expression inside a rule body

### Preprocess pipeline

- Preprocess syntax is parsed by `src/parser/wpl_rule.rs::pip_proc`
- Syntactically it accepts any `key`, plus `plg_pipe/<name>` and `plg_pipe(<name>)`
- Built-in registered stages currently include:
  - `decode/base64`
  - `decode/hex`
  - `unquote/unescape`
  - `strip/bom`
  - `json_like`
- `plg_pipe(<name>)` is normalized to `plg_pipe/<name>` after parsing

### Groups

- Group meta is limited to: `alt`, `opt`, `some_of`, `seq`, `not`
- A group may be followed by `[n]`; the parser applies that length to each field in the group
- Group-level separators currently support only `\...` shortcut separators, not `{...}` pattern separators

### Fields

- Top-level fields must explicitly provide a `meta_token`
- Subfields inside composite fields may omit meta; omitted meta defaults to `chars`
- Only subfields support `opt(type)` today; top-level fields do not
- `peek_symbol(...)` is normalized to `symbol(...)` during parsing, while preserving peek semantics
- `bad_json` is a local alias: its underlying type is treated as `Chars`, but `meta_name` remains `bad_json`

### Type names

- This document no longer hardcodes the full type list
- Available type names are whatever `wp_model_core::model::DataType::from(token)` accepts
- So whether a `meta_token` is valid depends on the actual `DataType` implementation in the dependency version in use

### Formats and separators

- `"` is the shorthand format for a double-quoted scope
- `<beg,end>` is the generic boundary format; nested bracket content is handled by `interval_impl()`
- Field-level separators support two forms:
  - `\...` shortcut separators
  - `{...}` pattern separators
- Pattern separators support:
  - `*`
  - `?`
  - `\s` `\S` `\h` `\H` `\0` `\n` `\t` `\r`
  - a trailing `(...)` preserve segment

### Annotations

- There are only two annotation functions today:
  - `tag(k: "v")`
  - `copy_raw(name: "raw_field")`
- Annotation values support:
  - normal quoted strings
  - raw strings `r#"..."#`
  - the legacy compatible form `r"..."`

### Field pipes

- Parsing entry point: `src/parser/wpl_fun.rs`
- The current parser supports three common argument styles:
  - bare-value-only functions, such as `chars_has(ok)`
  - array-taking functions, such as `digit_in([200, 201])`
  - functions that accept either bare or quoted strings, such as `chars_replace("a,b", "c d")`
- `not(...)` can wrap only field functions, not selectors or groups
- The right-hand side of a `pipe` may be either a function or a nested group, e.g. `|(time, ip)`

### Quotes and references

- `take(...)` supports bare identifiers, double-quoted strings, and single-quoted strings
- Subfield `@ref` supports:
  - bare paths: `@payload/data`
  - single-quoted raw strings: `@'@special-field'`
- Annotation values and some function parameters support escaped strings; not every string-taking function supports quoted input

---

## Related Sources

- Package parsing: [src/parser/wpl_pkg.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/parser/wpl_pkg.rs)
- Rule parsing: [src/parser/wpl_rule.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/parser/wpl_rule.rs)
- Expression parsing: [src/parser/parse_code.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/parser/parse_code.rs)
- Group parsing: [src/parser/wpl_group.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/parser/wpl_group.rs)
- Field parsing: [src/parser/wpl_field.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/parser/wpl_field.rs)
- Function parsing: [src/parser/wpl_fun.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/parser/wpl_fun.rs)
- Built-in preprocess registration: [src/eval/builtins/mod.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/eval/builtins/mod.rs)
