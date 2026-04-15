# `map_to(...)`: Map a Value to a Constant

`map_to(...)` is an OML pipe function that replaces a non-`ignore` value with a fixed constant. It is commonly used after a filter-like pipe step such as `starts_with(...)`.

## Syntax

```oml
field_name = pipe take(source_field) | map_to(value) ;
```

## Supported Argument Types

The current parser supports these argument types:

- single-quoted string, for example `'text'`
- integer, for example `123` or `-456`
- floating-point number, for example `3.14` or `-2.5`
- boolean, `true` or `false`

## Behavior

- if the incoming value is not `ignore`, it is replaced with the constant argument
- if the incoming value is already `ignore`, it stays `ignore`
- the output field type is derived from the argument

## Type Mapping

| Argument | Inferred Type | Result Field Type |
|----------|---------------|-------------------|
| `'text'` | string | `chars` |
| `123` | integer | `digit` |
| `3.14` | float | `float` |
| `true` / `false` | boolean | `bool` |

## Examples

### Map to a string label

```oml
status_label = pipe take(http_code) | map_to('success') ;
```

### Map to an integer priority

```oml
priority = pipe take(log_level) | map_to(1) ;
```

### Map to a floating-point threshold

```oml
threshold = pipe take(category) | map_to(0.95) ;
```

### Map to a boolean flag

```oml
is_secure = pipe take(protocol) | map_to(true) ;
```

### Use together with `starts_with`

```oml
security_level = pipe take(url) | starts_with('https://') | map_to(3) ;
```

If the URL starts with `https://`, the result becomes `3`. Otherwise the result stays `ignore`.

## Notes

- strings must be quoted: use `map_to('text')`, not `map_to(text)`
- booleans must not be quoted: use `map_to(true)`, not `map_to('true')`
- the output type is determined by the constant argument, not by the original input type
- a common pattern is "filter first, then map"
