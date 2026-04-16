# `starts_with(...)`: Prefix Filtering for Strings

`starts_with(...)` is an OML pipe function that checks whether a string field starts with a given prefix.

## Syntax

```oml
field_name = pipe take(source_field) | starts_with('prefix') ;
```

## Parameters

- `prefix`: the prefix string to check, and it must be quoted

## Behavior

- if the field value starts with the prefix, the original value is kept and passed to the next pipe step
- if the field value does not start with the prefix, it becomes `ignore`
- if the field is not a string, it becomes `ignore`
- matching is case-sensitive

## Example Use Cases

### Filter HTTPS URLs

```oml
secure_url = pipe take(url) | starts_with('https://') ;
```

### Extract API paths

```oml
api_path = pipe take(request_path) | starts_with('/api/v1/') ;
```

### Classify log levels

```oml
error_message = pipe take(log_message) | starts_with('ERROR') ;
warning_message = pipe take(log_message) | starts_with('WARN') ;
```

### Combine with `map_to`

```oml
is_secure = pipe take(url) | starts_with('https://') | map_to(true) ;
security_level = pipe take(url) | starts_with('https://') | map_to(3) ;
```

If the prefix check fails, the downstream `map_to(...)` also keeps the value as `ignore`.

## Comparison

| Function | Match Position | Typical Use |
|----------|----------------|-------------|
| `starts_with(prefix)` | beginning of string | fast prefix checks |
| `regex_match(pattern)` | anywhere, depending on regex | more complex matching |

## Notes

- strings must be quoted: `starts_with('https://')`
- matching is case-sensitive
- once a value becomes `ignore`, later pipe stages keep it as `ignore`
- a common pattern is `starts_with(...) | map_to(...)`
