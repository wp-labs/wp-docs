# WPL Functions Reference (aligned with `src/parser/wpl_fun.rs` and `src/eval/builtins`)

This document describes only functions that are implemented in the current codebase. Outdated signatures have been removed.

Authoritative implementation:

- `src/parser/wpl_fun.rs`
- `src/ast/processor/function.rs`
- `src/eval/builtins/pipe_fun.rs`
- `src/eval/builtins/mod.rs`

---

## Quick Reference

### Preprocess pipeline

| Name | Behavior | Notes |
|------|----------|-------|
| `decode/base64` | Base64-decodes the whole input line | Built-in |
| `decode/hex` | Hex-decodes the whole input line | Built-in |
| `unquote/unescape` | Applies quote / escape processing to the whole input line | Built-in |
| `strip/bom` | Removes UTF BOM from the beginning of the input | Built-in |
| `json_like` | Passes through only inputs that look like JSON | Built-in |
| `plg_pipe/<name>` | Calls a registered custom preprocess stage | `plg_pipe(name)` also works |

### Selectors

| Function | Behavior |
|----------|----------|
| `take(field)` | Selects a specific field as the active field |
| `last()` | Selects the last field as the active field |

### Target-field functions (`f_` prefix)

| Function | Behavior |
|----------|----------|
| `f_has(name)` | Succeeds if the target field exists |
| `f_chars_has(name, value)` | Succeeds if the target field equals a string |
| `f_chars_not_has(name, value)` | Succeeds if the target field does not equal a string |
| `f_chars_in(name, [...])` | Succeeds if the target field is in a string set |
| `f_digit_has(name, number)` | Succeeds if the target field equals a number |
| `f_digit_in(name, [...])` | Succeeds if the target field is in a numeric set |
| `f_ip_in(name, [...])` | Succeeds if the target field is in an IP set |

### Active-field functions

| Function | Behavior |
|----------|----------|
| `has()` | Succeeds if the active field exists |
| `chars_has(value)` | Succeeds if the active field equals a string |
| `chars_not_has(value)` | Succeeds if the active field does not equal a string |
| `chars_in([...])` | Succeeds if the active field is in a string set |
| `digit_has(number)` | Succeeds if the active field equals a number |
| `digit_in([...])` | Succeeds if the active field is in a numeric set |
| `digit_range(begin, end)` | Succeeds if the active field is within the closed range `[begin, end]` |
| `ip_in([...])` | Succeeds if the active field is in an IP set |

### Transform and match functions

| Function | Behavior |
|----------|----------|
| `json_unescape()` | JSON-unescapes the active string field |
| `base64_decode()` | Base64-decodes the active string field |
| `chars_replace(from, to)` | Replaces all occurrences in the active string field |
| `regex_match(pattern)` | Applies a regex match to the active string field |
| `starts_with(prefix)` | Checks a prefix; on mismatch, converts the field to `ignore` |
| `not(inner_fun)` | Inverts success / failure of the inner field function |

---

## Preprocess Pipeline

### `decode/base64`

Applies Base64 decoding to the whole input line.

```wpl
rule demo {
  |decode/base64|
  (chars:payload)
}
```

Notes:

- It operates on the raw input line, not on an individual field
- If decoding fails, the current rule fails

### `decode/hex`

Applies hexadecimal decoding to the whole input line.

```wpl
rule demo {
  |decode/hex|
  (chars:payload)
}
```

### `unquote/unescape`

Applies quote / escape processing to the whole input line.

```wpl
rule demo {
  |unquote/unescape|
  (chars:message)
}
```

### `strip/bom`

Removes BOM from the beginning of the input.

```wpl
rule demo {
  |strip/bom|
  (json(chars@msg))
}
```

### `json_like`

Allows only text that looks like JSON to continue.

```wpl
rule maybe_bad_json {
  |json_like|
  (bad_json:raw)
}
```

Notes:

- This is a lightweight filter, not a full JSON parse
- The current implementation treats input as JSON-like only if:
  - after trimming leading whitespace/BOM it starts with `{` and contains both `:` and `"`
  - after trimming leading whitespace/BOM it starts with `[` and contains `,`, `]`, or `{`

### `plg_pipe/<name>` / `plg_pipe(name)`

Calls a custom preprocess stage registered in the pipeline registry.

```wpl
rule demo {
  |plg_pipe/dayu|
  (chars:data)
}
```

Notes:

- `plg_pipe(name)` is normalized to `plg_pipe/name` after parsing
- Availability depends on whether that stage is registered at runtime

---

## Selectors

### `take(field)`

Sets the specified field as the active field.

```wpl
rule demo {
  (
    json(chars@name, digit@age)
    |take(name)
    |chars_has(admin)
  )
}
```

Supported argument forms:

- bare field names: `take(name)`
- double-quoted strings: `take("@special")`
- single-quoted strings: `take('@special')`

Failure condition:

- the target field does not exist

### `last()`

Sets the last field as the active field.

```wpl
rule demo {
  (
    json(chars@a, chars@b, chars@c)
    |last()
    |chars_has(done)
  )
}
```

Failure condition:

- the current field list is empty

---

## Target-field Functions (`f_` Prefix)

These functions auto-select the target field by name, so you do not need `take(...)` first.

### `f_has(name)`

Succeeds if the target field exists.

```wpl
|f_has(status)|
```

### `f_chars_has(name, value)`

Succeeds if the target field is `Chars` and equals `value`.

```wpl
|f_chars_has(status, success)|
```

Notes:

- The first argument supports `_`, meaning the current active field
- The second argument is currently parsed as a bare string and is best used with simple values like `success` or `GET`

### `f_chars_not_has(name, value)`

Also succeeds when the field does not exist; it fails only when the field exists and exactly equals `value`.

```wpl
|f_chars_not_has(level, error)|
```

This is intentionally more permissive than a strict "missing means failure" predicate.

### `f_chars_in(name, [...])`

Succeeds if the target field is `Chars` and belongs to the provided string array.

```wpl
|f_chars_in(method, [GET, POST, PUT])|
```

### `f_digit_has(name, number)`

Succeeds if the target field is `Digit` and equals the provided number.

```wpl
|f_digit_has(code, 200)|
```

### `f_digit_in(name, [...])`

Succeeds if the target field is `Digit` and belongs to the provided number array.

```wpl
|f_digit_in(code, [200, 201, 204])|
```

### `f_ip_in(name, [...])`

Succeeds if the target field is `IpAddr` and belongs to the provided IP array.

```wpl
|f_ip_in(client_ip, [127.0.0.1, ::1])|
```

Notes:

- Both IPv4 and IPv6 are supported

---

## Active-field Functions

These functions operate directly on the current active field. They are usually used after `take(...)` or `last()`.

### `has()`

Succeeds if the active field exists.

```wpl
|take(name)|has()|
```

### `chars_has(value)`

Succeeds if the active field is `Chars` and equals `value`.

```wpl
|take(status)|chars_has(success)|
```

### `chars_not_has(value)`

Also succeeds when the active field does not exist; it fails only when the field exists and equals `value`.

```wpl
|take(level)|chars_not_has(error)|
```

### `chars_in([...])`

Succeeds if the active field is `Chars` and belongs to the provided string array.

```wpl
|take(method)|chars_in([GET, POST])|
```

### `digit_has(number)`

Succeeds if the active field is `Digit` and equals the provided number.

```wpl
|take(code)|digit_has(200)|
```

### `digit_in([...])`

Succeeds if the active field is `Digit` and belongs to the provided number array.

```wpl
|take(code)|digit_in([200, 201, 204])|
```

### `digit_range(begin, end)`

Succeeds if the active field is `Digit` and falls within the closed range `[begin, end]`.

```wpl
|take(code)|digit_range(200, 299)|
```

Notes:

- There is currently only the active-field version; there is no `f_digit_range(...)`

### `ip_in([...])`

Succeeds if the active field is an IP value and belongs to the provided list.

```wpl
|take(client_ip)|ip_in([127.0.0.1, ::1])|
```

---

## Transform and Match Functions

### `json_unescape()`

Applies JSON unescaping to the active string field.

```wpl
|take(message)|json_unescape()|
```

Behavior:

- Only works on `Chars`
- If the field contains no backslash, it succeeds immediately
- It fails on invalid JSON escape sequences

### `base64_decode()`

Applies Base64 decoding to the active string field.

```wpl
|take(payload)|base64_decode()|
```

Behavior:

- Only works on `Chars`
- It fails if decoding fails or if the decoded bytes are not valid UTF-8

### `chars_replace(from, to)`

Executes `String::replace(from, to)` on the active string field.

```wpl
|take(message)|chars_replace(old, new)|
|take(message)|chars_replace("hello world", "hi")|
```

Supported argument forms:

- bare strings
- single-quoted or double-quoted strings

Notes:

- This replaces all occurrences, not just the first one
- If `from` is an empty string, `to` is inserted at every character boundary

### `regex_match(pattern)`

Applies a regex match to the active string field.

```wpl
|take(email)|regex_match('^\\w+@\\w+\\.\\w+$')|
```

Supported argument forms:

- bare strings
- single-quoted or double-quoted strings
- regex syntax is compiled by Rust's `regex` crate

Failure conditions:

- there is no active field
- the active field is not a string
- the regex is invalid
- the regex does not match

### `starts_with(prefix)`

Checks whether the active string field starts with the given prefix.

```wpl
|take(path)|starts_with('/api/')|
```

Supported argument forms:

- bare strings
- single-quoted or double-quoted strings

Important current behavior:

- If the field is a string and starts with the prefix, it succeeds and keeps the field unchanged
- If the field is not a string, or the prefix does not match, it does not fail; instead it converts the field to `ignore` and returns success

So `starts_with(...)` currently behaves more like "filter out the field" than "strictly assert failure".

### `not(inner_fun)`

Inverts success / failure of the wrapped inner field function.

```wpl
|not(chars_has(error))|
|not(f_chars_has(level, error))|
```

Notes:

- It can wrap only field functions
- It cannot wrap selector functions such as `not(take(name))`
- It reuses the inner function's auto-selection logic

---

## Usage Guidance

### Target-field vs active-field functions

| Scenario | Recommended form |
|----------|------------------|
| Check whether a field exists | `f_has(name)` |
| Select a field and then perform multiple steps | `take(name)` + active-field functions |
| Transform a field value | `take(name)` + `json_unescape()` / `base64_decode()` / `chars_replace()` |
| Negate a condition | `not(...)` |

### Current gotchas

- `chars_not_has(...)` and `f_chars_not_has(...)` succeed when the field is missing
- `starts_with(...)` turns the field into `ignore` on mismatch instead of failing directly
- Not every string-taking function supports quoted input
  - clearly supports quoted strings: `take`, `chars_replace`, `regex_match`, `starts_with`
  - for others such as `chars_has` and `f_chars_has`, prefer bare values today

---

## Related Sources

- Function parser: [src/parser/wpl_fun.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/parser/wpl_fun.rs)
- Function AST: [src/ast/processor/function.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/ast/processor/function.rs)
- Field-pipe execution: [src/eval/builtins/pipe_fun.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/eval/builtins/pipe_fun.rs)
- Built-in preprocess registration: [src/eval/builtins/mod.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/eval/builtins/mod.rs)
