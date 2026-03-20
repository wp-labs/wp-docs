# `lookup_nocase(...)`：忽略大小写静态字典查表

`lookup_nocase(dict_symbol, key_expr, default_expr)` 用于对 `static` 中定义的 object 做忽略大小写查表。

## 语法

```oml
lookup_nocase(<dict_symbol>, <key_expr>, <default_expr>)
```

## 参数说明

- `dict_symbol`
  - 必须引用 `static` 中定义的 object
- `key_expr`
  - 待查 key，通常是 `read(status)` 这类字符串字段
- `default_expr`
  - 未命中时返回的默认值

## 示例

```oml
static {
    status_score = object {
        error = float(90.0);
        warning = float(70.0);
        success = float(20.0);
    };
}

risk_score : float = lookup_nocase(status_score, read(status), 40.0) ;
```

## 查表规则

- key 会先执行 `trim + lowercase`
- 然后在静态 object 中查找对应字段名
- 命中则返回字典值
- 未命中则返回 `default_expr`
- 如果 `key_expr` 不是字符串，也返回 `default_expr`

## 适用场景

- 状态值映射为风险分数
- 等级、动作、结果码等固定枚举的标准化
- 输入值大小写不稳定，但映射表希望只维护一份小写键

## 使用建议

- 字典尽量统一用小写 key，和 `lookup_nocase(...)` 的归一化规则保持一致
- 如果需要在多个地方复用同一映射表，优先放到 `static` 中
- 如果只是二三选一的条件分支，优先考虑 `match + iequals_any(...)`
