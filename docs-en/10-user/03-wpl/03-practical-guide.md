# WPL Practical Guide

This page keeps a compact English checklist for writing working WPL.

For the full scenario guide, see [../zh/03-practical-guide.md](../zh/03-practical-guide.md).

---

## Common Patterns

### Nginx access log

```wpl
package nginx {
  rule access_log {
    (
      ip:client_ip,
      2*_,
      time/clf:time<[,]>,
      http/request:request",
      http/status:status,
      digit:bytes,
      chars:referer",
      http/agent:user_agent"
    )
  }
}
```

### JSON fields

```wpl
(json(
  chars@user,
  digit@code,
  opt(chars)@message
))
```

### Optional trailing segment

```wpl
(digit:code, time:ts),
opt(chars:tag")
```

Split optional content into its own group instead of trying to wrap a field inside another group.

---

## Quick Checks

- Put `:name` before the format.
- Put formats after the field name: `chars:msg"` and `time/clf:ts<[,]>`.
- Use `alt(...)` for alternatives. `one_of(...)` is not valid WPL.
- Use `opt(type)@key` only for JSON/KV subfields.
- Keep `opt(...)`, `alt(...)`, `some_of(...)`, `not(...)` at group level.

Primary syntax reference: [06-grammar-reference.md](./06-grammar-reference.md)
