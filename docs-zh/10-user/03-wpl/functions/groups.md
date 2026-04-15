# WPL Group 逻辑

WPL 的 `seq`、`opt`、`alt`、`some_of`、`not` 都是分组语义，不是字段类型。

## Group 类型

### seq - 顺序匹配

```wpl
(digit:id, chars:name, ip:addr)
seq(digit:id, chars:name, ip:addr)
```

要求所有字段按顺序成功匹配。

### opt - 可选分组

```wpl
opt(chars:tag")
```

整个分组可以不存在，失败时不影响规则继续匹配。

### alt - 择一分组

```wpl
alt(ip:addr, chars:addr)
```

依次尝试候选项，命中第一个成功的分组。

### some_of - 重复候选分组

```wpl
some_of(kvarr, ip, digit)
```

持续尝试候选项，直到没有任何候选还能继续匹配。

### not - 负向断言分组

```wpl
not(peek_symbol(ERROR):check)
```

内部字段不匹配时，`not(...)` 才成功。

## 关键规则

- 这些写法都作用在分组层。
- 如果某段内容可选，先把它拆成独立分组，再用 `opt(...)` 包起来。
- 当前语法不支持分组嵌套，例如 `opt(alt(...))`。

正确示例：

```wpl
(ip:client_ip, digit:status),
opt(chars:tag")
```

错误示例：

```wpl
(ip:client_ip, opt(chars:tag"))
opt(alt(ip:addr, chars:domain))
```

## 输入消费

- `not(symbol(...))` 是否消费输入，取决于内部 parser 的行为。
- `not(peek_symbol(...))` 更适合做不消费输入的前瞻判断。
