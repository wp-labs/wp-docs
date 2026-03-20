# WPL Group Logic

WPL groups control matching behavior. They are not field types.

## Group Types

### seq - Sequence

```wpl
(digit:id, chars:name, ip:addr)
seq(digit:id, chars:name, ip:addr)
```

All fields must match in order.

### opt - Optional Group

```wpl
opt(chars:tag")
```

The whole group may be absent without failing the rule.

### alt - Alternative Group

```wpl
alt(ip:addr, chars:addr)
```

The first successful candidate wins.

### some_of - Repeated Candidate Matching

```wpl
some_of(kvarr, ip, digit)
```

WPL keeps trying the candidates until none match anymore.

### not - Negative Assertion Group

```wpl
not(peek_symbol(ERROR):check)
```

The group succeeds when the inner field does not match.

## Important Rules

- Group operators are `seq`, `opt`, `alt`, `some_of`, and `not`.
- They operate at group level.
- Do not write nested groups such as `opt(alt(...))`.
- If one segment is optional, split it into its own group first.

Valid:

```wpl
(ip:client_ip, digit:status),
opt(chars:tag")
```

Invalid:

```wpl
(ip:client_ip, opt(chars:tag"))
opt(alt(ip:addr, chars:domain))
```

## Input Consumption

- `not(symbol(...))` may consume input depending on the inner parser behavior.
- `not(peek_symbol(...))` is the safer lookahead form when you need non-consuming checks.
