# `lookup_nocase(...)`: Case-Insensitive Static Dictionary Lookup

`lookup_nocase(dict_symbol, key_expr, default_expr)` performs a case-insensitive lookup against an object defined inside `static`.

## Syntax

```oml
lookup_nocase(<dict_symbol>, <key_expr>, <default_expr>)
```

## Parameters

- `dict_symbol`
  - must reference an object defined in `static`
- `key_expr`
  - the key to look up, typically a string field such as `read(status)`
- `default_expr`
  - the fallback value returned when no entry matches

## Example

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

## Lookup Rules

- the key is normalized with `trim + lowercase`
- lookup is then performed against field names in the static object
- if a match is found, the mapped value is returned
- if no match is found, `default_expr` is returned
- if `key_expr` is not a string, `default_expr` is also returned

## Common Use Cases

- mapping status values to risk scores
- normalizing fixed enums such as levels, actions, or result codes
- handling inputs whose casing is unstable while keeping a single lowercase mapping table

## Recommendations

- prefer lowercase keys in the dictionary so they match the normalization rule directly
- if the same mapping table is reused in multiple places, keep it in `static`
- if you only need two or three branches, `match + iequals_any(...)` may be simpler
