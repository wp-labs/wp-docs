# `calc(...)`：显式数值表达式

`calc(expr)` 用于在 OML 中执行显式算术表达式，适合比例、差值、分桶、取整百分比等场景。

## 语法

```oml
calc(<expr>)
```

## 支持能力

- 运算符：`+ - * / %`
- 函数：`abs(...)`、`round(...)`、`floor(...)`、`ceil(...)`
- 操作数：
  - 数值字面量
  - `read(...)`
  - `take(...)`
  - `@field`

## 示例

```oml
risk_score : float = calc(read(cpu) * 0.7 + read(mem) * 0.3) ;
delta      : digit = calc(read(cur) - read(prev)) ;
ratio      : float = calc(read(ok_cnt) / read(total_cnt)) ;
bucket     : digit = calc(read(uid) % 16) ;
distance   : float = calc(abs(read(actual) - read(expect))) ;
error_pct  : digit = calc(round((read(err_cnt) * 100) / read(total_cnt))) ;
```

## 类型规则

- `+ - *`
  - `digit op digit -> digit`
  - 只要任一操作数是 `float`，结果就是 `float`
- `/`
  - 始终返回 `float`
- `%`
  - 仅支持 `digit % digit -> digit`
- `round/floor/ceil`
  - 返回 `digit`
- `abs`
  - `abs(digit) -> digit`
  - `abs(float) -> float`

## 失败行为

以下情况都会返回 `ignore`：

- 除零
- 字段缺失
- 非数值输入
- 整数溢出
- `NaN` / `inf` 输入或结果
- 对浮点数使用 `%`

这意味着 `calc(...)` 不会隐式返回 `0`，也不会把非法结果继续传下去。

如果业务需要兜底值，可以再显式加默认值：

```oml
raw_ratio : float = calc(read(ok_cnt) / read(total_cnt)) ;
safe_ratio : float = read(raw_ratio) { _ : float(0.0) } ;
```

## 使用建议

- 适合放在顶层绑定中，先把结果算成字段，再给后续 `match` / `object` / `pipe` 使用
- 如果表达式失败后仍需要业务默认值，配合 `read(...) { _ : ... }`
- `%` 仅用于整数分桶，不要拿浮点做取模
