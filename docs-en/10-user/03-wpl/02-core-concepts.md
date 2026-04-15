# WPL Core Concepts

This page keeps the core writing rules in sync with the Chinese reference.

For the fuller Chinese document, see [../zh/02-core-concepts.md](../zh/02-core-concepts.md).

---

## Mental Model

WPL is a typed pattern language:

- A rule describes the expected field sequence.
- Each type both parses and validates data.
- Names are attached after the type or subfield path.

Example:

```wpl
(ip:client, digit:status, time:ts)
```

---

## Group Semantics

WPL groups control matching behavior:

```wpl
(ip, digit, time)              # seq, default
alt(ip:addr, chars:addr)       # choose one
opt(chars:tag")                # optional group
some_of(kvarr, ip, digit)      # keep matching candidates
not(peek_symbol(ERROR):check)  # negative assertion
```

Notes:

- `opt(...)`, `alt(...)`, `some_of(...)`, `not(...)`, and `seq(...)` are groups.
- They are not field types.
- Nested groups such as `opt(alt(...))` are not supported by the current grammar.

---

## Field Syntax Order

The order matters:

```text
type [subfields] [:name] [format] [separator] {| pipe}
```

Valid:

```wpl
time/clf:access_time<[,]>
http/request:request"
json(chars@user, opt(chars)@email)
```

Invalid:

```wpl
time/clf<[,]>:access_time
http/request":request
```

---

## Optional Data

There are two different patterns:

- Optional group: `opt(chars:tag")`
- Optional subfield: `opt(chars)@email`

Use the first for line-level segments and the second for JSON/KV members.

---

## Separators

Separator priority is:

```text
field-level > group-level > upstream/default
```

See [06-grammar-reference.md](./06-grammar-reference.md) and [../zh/08-sep-pattern.md](../zh/08-sep-pattern.md) for the exact grammar.
