# `calc(...)`: Explicit Numeric Expressions

`calc(expr)` executes explicit arithmetic expressions in OML. It is useful for ratios, deltas, bucketing, and rounded percentages.

## Syntax

```oml
calc(<expr>)
```

## Supported Features

- operators: `+ - * / %`
- functions: `abs(...)`, `round(...)`, `floor(...)`, `ceil(...)`
- operands:
  - numeric literals
  - `read(...)`
  - `take(...)`
  - `@field`

## Examples

```oml
risk_score : float = calc(read(cpu) * 0.7 + read(mem) * 0.3) ;
delta : digit = calc(read(cur) - read(prev)) ;
ratio : float = calc(read(ok_cnt) / read(total_cnt)) ;
bucket : digit = calc(read(uid) % 16) ;
distance : float = calc(abs(read(actual) - read(expect))) ;
error_pct : digit = calc(round((read(err_cnt) * 100) / read(total_cnt))) ;
```

## Type Rules

- `+ - *`
  - `digit op digit -> digit`
  - if either operand is `float`, the result becomes `float`
- `/`
  - always returns `float`
- `%`
  - only supports `digit % digit -> digit`
- `round/floor/ceil`
  - return `digit`
- `abs`
  - `abs(digit) -> digit`
  - `abs(float) -> float`

## Failure Behavior

The result becomes `ignore` in these cases:

- division by zero
- missing fields
- non-numeric input
- integer overflow
- `NaN` / `inf` as input or result
- `%` used with floating-point values

So `calc(...)` does not implicitly return `0`, and it does not propagate invalid numeric results as normal values.

If business logic requires a fallback value, add it explicitly:

```oml
raw_ratio : float = calc(read(ok_cnt) / read(total_cnt)) ;
safe_ratio : float = read(raw_ratio) { _ : float(0.0) } ;
```

## Usage Notes

- it works well as a top-level binding: compute a field first, then reuse it in `match`, `object`, or `pipe`
- if you need a business fallback after calculation failure, combine it with `read(...) { _ : ... }`
- `%` is intended for integer bucketing; do not use it with floats
