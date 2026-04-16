# OML 函数与专题索引

本目录收录的是 OML 中几个需要单独展开说明的表达式和专题页面。完整函数列表请以 [04-functions-reference.md](../04-functions-reference.md) 为准。

## 表达式与专题

| 名称 | 说明 | 文档 |
|------|------|------|
| `calc(...)` | 显式数值表达式，支持 `+ - * / %` 与 `abs/round/floor/ceil` | [calc.md](./calc.md) |
| `lookup_nocase(...)` | 基于 `static object` 的忽略大小写查表 | [lookup_nocase.md](./lookup_nocase.md) |
| `match` 条件函数 | `starts_with`、`iequals_any` 等 `match` 条件能力 | [match_functions.md](./match_functions.md) |
| `map_to(...)` | 管道中的常量映射 | [map_to.md](./map_to.md) |
| `starts_with(...)` | 管道前缀判断 | [starts_with.md](./starts_with.md) |
| `extract_main_word` | 文本主词提取 | [extract_main_word.md](./extract_main_word.md) |
| `extract_subject_object` | 文本主客体结构提取 | [extract_subject_object.md](./extract_subject_object.md) |
| `static { ... }` | 静态常量块、可用表达式与限制 | [static_blocks.md](./static_blocks.md) |

## 当前实现中的函数边界

- 内置函数当前只有 `Now::time()`、`Now::date()`、`Now::hour()`
- 顶层内置表达式包括 `calc(...)`、`match ... { ... }`、`lookup_nocase(...)`、`fmt(...)`、`object { ... }`、`collect ...`、`select ... where ... ;`
- 管道函数集合以 [04-functions-reference.md](../04-functions-reference.md) 中列出的解析器实际支持项为准
- 历史文档中出现过的 `sxf_get(...)`、隐私段、`query ...` 等写法不属于当前 `wp-oml` 解析实现
