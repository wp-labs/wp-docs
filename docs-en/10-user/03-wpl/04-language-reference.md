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
