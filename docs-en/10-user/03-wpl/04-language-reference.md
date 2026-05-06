# WPL Language Reference

This page summarizes the syntax details that are easy to get wrong when writing WPL.

For the fuller Chinese reference, see [../zh/04-language-reference.md](../zh/04-language-reference.md).

---

## Field Syntax

Full order:

```text
[N*] type [symbol_content] [subfields] [:name] [length] [format] [separator] {| pipe}
```

Examples:

```wpl
digit:status
time/clf:time<[,]>
http/request:request"
json(chars@name, opt(chars)@email)
```

---

## Group Syntax

```wpl
(field1, field2, field3)
seq(field1, field2, field3)
alt(ip:addr, chars:addr)
opt(chars:tag")
some_of(kvarr, ip, digit)
not(peek_symbol(ERROR):check)
```

Rules:

- Group operators are `seq`, `alt`, `opt`, `some_of`, and `not`.
- They apply to groups, not to field types.
- Nested groups are not supported.

---

## Subfields

JSON and KV subfields support optional member types:

```wpl
json(chars@name, opt(chars)@email)
kvarr(chars@host, digit@port, opt(chars)@user)
```

This is different from group-level `opt(...)`.

---

## JSON-like Routing

### `json_like`

```wpl
|json_like|
```

- `json_like` is a preorder line pipe
- It only does a lightweight sniff to check whether the input looks like JSON
- It does not extract fields and does not run full JSON parsing

Use it in fallback rules before `bad_json`.

### `json`

`json(...)` now has built-in JSON-like sniffing, so this is enough:

```wpl
rule good_json {
  (json(chars@host, chars@method))
}
```

You do not need to add an extra `|json_like|` in front of `json(...)`.

### `bad_json`

```wpl
(bad_json:raw)
```

- `bad_json` outputs the original input as a `chars` field
- It is intended for inputs that look like JSON but fail strict JSON parsing
- It should usually be guarded by `|json_like|`

### Recommended Pattern

```wpl
rule good_json {
  (json(chars@host, chars@method))
}

rule broken_json {
  |json_like|
  (bad_json:raw)
}
```

Behavior:

- Valid JSON is handled by `json(...)`
- Broken but JSON-like payloads fall back to `json_like + bad_json`
- Plain text will not be accidentally consumed by `bad_json`

---

## Valid and Invalid Forms

Valid:

```wpl
time/clf:time<[,]>
http/request:request"
alt(ip:addr, chars:addr)
```

Invalid:

```wpl
time/clf<[,]>:time
http/request":request
one_of(ip, chars)
```

Authoritative grammar: [06-grammar-reference.md](./06-grammar-reference.md)
