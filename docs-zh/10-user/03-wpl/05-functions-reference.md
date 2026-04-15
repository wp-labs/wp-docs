# WPL 函数参考（对齐 `src/parser/wpl_fun.rs` 与 `src/eval/builtins`）

本文档只描述当前代码里已经实现的函数和行为，不再保留过时签名。

权威实现位置：

- `src/parser/wpl_fun.rs`
- `src/ast/processor/function.rs`
- `src/eval/builtins/pipe_fun.rs`
- `src/eval/builtins/mod.rs`

---

## 速查

### 预处理管道

| 名称 | 作用 | 备注 |
|------|------|------|
| `decode/base64` | 对整行输入做 Base64 解码 | 内置 |
| `decode/hex` | 对整行输入做十六进制解码 | 内置 |
| `unquote/unescape` | 对整行输入做引号/转义处理 | 内置 |
| `strip/bom` | 去掉 UTF BOM | 内置 |
| `json_like` | 只放行“看起来像 JSON”的输入 | 内置 |
| `plg_pipe/<name>` | 调用注册的自定义预处理器 | `plg_pipe(name)` 也可 |

### 选择器

| 函数 | 作用 |
|------|------|
| `take(field)` | 选中指定字段作为活跃字段 |
| `last()` | 选中最后一个字段作为活跃字段 |

### 目标字段函数（`f_` 前缀）

| 函数 | 作用 |
|------|------|
| `f_has(name)` | 指定字段存在 |
| `f_chars_has(name, value)` | 指定字段等于某字符串 |
| `f_chars_not_has(name, value)` | 指定字段不等于某字符串 |
| `f_chars_in(name, [...])` | 指定字段属于字符串集合 |
| `f_digit_has(name, number)` | 指定字段等于某数字 |
| `f_digit_in(name, [...])` | 指定字段属于数字集合 |
| `f_ip_in(name, [...])` | 指定字段属于 IP 集合 |

### 活跃字段函数

| 函数 | 作用 |
|------|------|
| `has()` | 活跃字段存在 |
| `chars_has(value)` | 活跃字段等于某字符串 |
| `chars_not_has(value)` | 活跃字段不等于某字符串 |
| `chars_in([...])` | 活跃字段属于字符串集合 |
| `digit_has(number)` | 活跃字段等于某数字 |
| `digit_in([...])` | 活跃字段属于数字集合 |
| `digit_range(begin, end)` | 活跃字段落在闭区间 `[begin, end]` |
| `ip_in([...])` | 活跃字段属于 IP 集合 |

### 转换与匹配

| 函数 | 作用 |
|------|------|
| `json_unescape()` | 对活跃字符串字段做 JSON 反转义 |
| `base64_decode()` | 对活跃字符串字段做 Base64 解码 |
| `chars_replace(from, to)` | 对活跃字符串字段做全量替换 |
| `regex_match(pattern)` | 对活跃字符串字段做正则匹配 |
| `starts_with(prefix)` | 检查前缀；不匹配时把字段改成 `ignore` |
| `not(inner_fun)` | 反转内层字段函数的成功/失败 |

---

## 预处理管道

### `decode/base64`

整行输入做 Base64 解码。

```wpl
rule demo {
  |decode/base64|
  (chars:payload)
}
```

说明：

- 作用对象是原始整行，不是单个字段
- 解码失败时当前规则失败

### `decode/hex`

整行输入做十六进制解码。

```wpl
rule demo {
  |decode/hex|
  (chars:payload)
}
```

### `unquote/unescape`

整行输入执行引号/转义处理。

```wpl
rule demo {
  |unquote/unescape|
  (chars:message)
}
```

### `strip/bom`

去掉输入开头的 BOM。

```wpl
rule demo {
  |strip/bom|
  (json(chars@msg))
}
```

### `json_like`

只允许看起来像 JSON 的文本继续往下走。

```wpl
rule maybe_bad_json {
  |json_like|
  (bad_json:raw)
}
```

说明：

- 这是轻量过滤，不会真正解析 JSON
- 当前实现认为下面两类输入才算“像 JSON”：
  - 去掉前导空白/BOM 后以 `{` 开头，且同时包含 `:` 和 `"`
  - 去掉前导空白/BOM 后以 `[` 开头，且包含 `,`、`]` 或 `{`

### `plg_pipe/<name>` / `plg_pipe(name)`

调用注册到预处理器注册表里的自定义处理器。

```wpl
rule demo {
  |plg_pipe/dayu|
  (chars:data)
}
```

说明：

- `plg_pipe(name)` 在解析后会归一化为 `plg_pipe/name`
- 是否可用取决于运行时是否注册了对应处理器

---

## 选择器

### `take(field)`

把指定字段设为活跃字段。

```wpl
rule demo {
  (
    json(chars@name, digit@age)
    |take(name)
    |chars_has(admin)
  )
}
```

参数格式：

- 支持裸字段名：`take(name)`
- 支持双引号：`take("@special")`
- 支持单引号：`take('@special')`

失败条件：

- 找不到目标字段

### `last()`

把最后一个字段设为活跃字段。

```wpl
rule demo {
  (
    json(chars@a, chars@b, chars@c)
    |last()
    |chars_has(done)
  )
}
```

失败条件：

- 当前字段列表为空

---

## 目标字段函数（`f_` 前缀）

这类函数会自动按字段名选择目标字段，不需要先 `take(...)`。

### `f_has(name)`

指定字段存在时成功。

```wpl
|f_has(status)|
```

### `f_chars_has(name, value)`

指定字段是 `Chars`，且值等于 `value` 时成功。

```wpl
|f_chars_has(status, success)|
```

说明：

- 第一个参数支持 `_`，表示“当前活跃字段”
- 第二个参数当前按裸字符串解析，适合 `success`、`GET` 这类简单值

### `f_chars_not_has(name, value)`

指定字段不存在时也会成功；只有“字段存在且值刚好等于 `value`”才失败。

```wpl
|f_chars_not_has(level, error)|
```

这和很多“严格不存在即失败”的谓词不同，当前实现是宽松语义。

### `f_chars_in(name, [...])`

指定字段是 `Chars`，且值属于给定字符串数组时成功。

```wpl
|f_chars_in(method, [GET, POST, PUT])|
```

### `f_digit_has(name, number)`

指定字段是 `Digit`，且值等于目标数字时成功。

```wpl
|f_digit_has(code, 200)|
```

### `f_digit_in(name, [...])`

指定字段是 `Digit`，且值属于数字数组时成功。

```wpl
|f_digit_in(code, [200, 201, 204])|
```

### `f_ip_in(name, [...])`

指定字段是 `IpAddr`，且值属于 IP 数组时成功。

```wpl
|f_ip_in(client_ip, [127.0.0.1, ::1])|
```

说明：

- 支持 IPv4 和 IPv6

---

## 活跃字段函数

这类函数直接作用于当前活跃字段。通常搭配 `take(...)` 或 `last()` 使用。

### `has()`

活跃字段存在即成功。

```wpl
|take(name)|has()|
```

### `chars_has(value)`

活跃字段必须是 `Chars`，且值等于 `value`。

```wpl
|take(status)|chars_has(success)|
```

### `chars_not_has(value)`

活跃字段不存在时也成功；只有“字段存在且值等于 `value`”才失败。

```wpl
|take(level)|chars_not_has(error)|
```

### `chars_in([...])`

活跃字段必须是 `Chars`，且值落在给定字符串数组中。

```wpl
|take(method)|chars_in([GET, POST])|
```

### `digit_has(number)`

活跃字段必须是 `Digit`，且值等于目标数字。

```wpl
|take(code)|digit_has(200)|
```

### `digit_in([...])`

活跃字段必须是 `Digit`，且值属于数字数组。

```wpl
|take(code)|digit_in([200, 201, 204])|
```

### `digit_range(begin, end)`

活跃字段必须是 `Digit`，且值满足闭区间 `[begin, end]`。

```wpl
|take(code)|digit_range(200, 299)|
```

说明：

- 当前只有活跃字段版本，没有 `f_digit_range(...)`

### `ip_in([...])`

活跃字段必须是 IP，且值属于目标列表。

```wpl
|take(client_ip)|ip_in([127.0.0.1, ::1])|
```

---

## 转换与匹配函数

### `json_unescape()`

对活跃字符串字段做 JSON 反转义。

```wpl
|take(message)|json_unescape()|
```

行为：

- 只处理 `Chars`
- 字段里没有反斜杠时直接成功
- 遇到非法 JSON 转义时失败

### `base64_decode()`

对活跃字符串字段做 Base64 解码。

```wpl
|take(payload)|base64_decode()|
```

行为：

- 只处理 `Chars`
- 解码失败或结果不是 UTF-8 时失败

### `chars_replace(from, to)`

对活跃字符串字段执行 `String::replace(from, to)`。

```wpl
|take(message)|chars_replace(old, new)|
|take(message)|chars_replace("hello world", "hi")|
```

参数格式：

- 支持裸字符串
- 支持单引号或双引号字符串

说明：

- 替换是全量替换，不是只替换第一个
- `from` 为空字符串时，会在每个字符边界插入 `to`

### `regex_match(pattern)`

对活跃字符串字段执行正则匹配。

```wpl
|take(email)|regex_match('^\\w+@\\w+\\.\\w+$')|
```

参数格式：

- 支持裸字符串
- 支持单引号或双引号字符串
- 正则由 Rust `regex` crate 编译

失败条件：

- 活跃字段不存在
- 活跃字段不是字符串
- 正则不合法
- 正则未匹配

### `starts_with(prefix)`

检查活跃字符串字段是否以前缀开头。

```wpl
|take(path)|starts_with('/api/')|
```

参数格式：

- 支持裸字符串
- 支持单引号或双引号字符串

当前实现的关键行为：

- 若字段是字符串且以前缀开头：成功，字段保持原值
- 若字段不是字符串，或字符串不匹配：不会报错，而是把该字段改成 `ignore`，然后返回成功

这意味着 `starts_with(...)` 更像“筛掉当前字段”而不是“严格断言失败”。

### `not(inner_fun)`

反转内层字段函数的成功/失败结果。

```wpl
|not(chars_has(error))|
|not(f_chars_has(level, error))|
```

说明：

- 只能包裹字段函数
- 不能包裹选择器函数，例如 `not(take(name))` 不成立
- 会沿用内层函数的自动选字段逻辑

---

## 使用建议

### 目标字段函数 vs 活跃字段函数

| 场景 | 推荐写法 |
|------|----------|
| 只校验某个字段是否存在 | `f_has(name)` |
| 先定位字段，再连续做多步处理 | `take(name)` + 活跃字段函数 |
| 需要做字段值转换 | `take(name)` + `json_unescape()` / `base64_decode()` / `chars_replace()` |
| 需要否定一个条件 | `not(...)` |

### 当前实现里容易踩坑的点

- `chars_not_has(...)` 和 `f_chars_not_has(...)` 在字段缺失时会成功
- `starts_with(...)` 在不匹配时会把字段转成 `ignore`，不是直接失败
- 并不是所有字符串参数都支持带引号
  - 明确支持引号：`take`、`chars_replace`、`regex_match`、`starts_with`
  - 其余如 `chars_has`、`f_chars_has` 目前应优先写裸值

---

## 相关实现

- 函数解析：[src/parser/wpl_fun.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/parser/wpl_fun.rs)
- 函数 AST：[src/ast/processor/function.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/ast/processor/function.rs)
- 字段管道执行：[src/eval/builtins/pipe_fun.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/eval/builtins/pipe_fun.rs)
- 内置预处理器注册：[src/eval/builtins/mod.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/eval/builtins/mod.rs)
