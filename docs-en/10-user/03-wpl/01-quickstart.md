# WPL Quick Start

Start writing valid WPL in a few minutes.

For the complete Chinese guide, see [../zh/01-quickstart.md](../zh/01-quickstart.md).

---

## What WPL Looks Like

```wpl
package nginx {
  rule access_log {
    (
      ip:client_ip,
      2*_,
      time/clf:time<[,]>,
      http/request:request",
      digit:status,
      digit:bytes
    )
  }
}
```

The important syntax order is:

```text
type [subfields] [:name] [format] [separator] {| pipe}
```

Use `time/clf:time<[,]>`, not `time/clf<[,]>:time`.
Use `http/request:request"`, not `http/request":request`.

---

## Three Common Patterns

### Space-separated text

```wpl
package demo {
  rule simple_log {
    (digit:code, ip:client, time:ts, chars:action)
  }
}
```

### JSON subfields

```wpl
package api {
  rule response {
    (json(
      chars@user,
      digit@code,
      opt(chars)@message
    ))
  }
}
```

`opt(type)@key` is valid for JSON/KV subfields.

### Optional groups

```wpl
package web {
  rule log_line {
    (ip:client_ip, digit:status),
    opt(chars:tag")
  }
}
```

`opt(...)`, `alt(...)`, `some_of(...)`, and `not(...)` are group-level constructs.
Do not put them inside another field list as if they were field types.

---

## Debugging Rule Syntax

- Start with one simple group.
- Add one field at a time.
- Verify separators and formats first.
- If one segment may be missing, split it into its own group and wrap that group with `opt(...)`.

Authoritative syntax reference: [06-grammar-reference.md](./06-grammar-reference.md)
