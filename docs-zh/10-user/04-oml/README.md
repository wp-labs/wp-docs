# OML 对象模型语言

OML（Object Modeling Language）用于对 WPL 解析后的结构化记录做字段提取、聚合、匹配、计算和富化。

> 本目录已按 `wp-motor/crates/wp-oml/src` 的当前解析实现整理。历史文档中出现过但当前实现未解析的能力，例如隐私段、`query ...`、`sxf_get(...)`，不再作为正式语法介绍。

---

## 阅读顺序

| 场景 | 建议文档 |
|------|---------|
| 先快速上手 | [01-quickstart.md](./01-quickstart.md) |
| 理解读取语义、类型和批量模式 | [02-core-concepts.md](./02-core-concepts.md) |
| 按任务找示例 | [03-practical-guide.md](./03-practical-guide.md) |
| 查当前实现支持的函数 | [04-functions-reference.md](./04-functions-reference.md) |
| 看完整语法边界 | [06-grammar-reference.md](./06-grammar-reference.md) |
| 查专题说明 | [functions/function_index.md](./functions/function_index.md) |
| 了解接入方式 | [05-integration.md](./05-integration.md) |

---

## 一个最小示例

```oml
name : nginx_access
rule : /nginx/access_log
---
client_ip : ip = read(client_ip) ;
status : digit = read(status) ;
uri = read(request_uri) ;
event_time : time = Now::time() ;
```

这段 OML 展示了当前实现最核心的几个点：

- 头部必须先声明 `name`
- `rule` 和 `enable` 可选，且顺序不限
- 头部与主体之间必须有一行 `---`
- 主体里至少要有一条聚合语句，且每条都以 `;` 结尾

---

## 当前实现支持什么

- 顶层表达式：`read(...)`、`take(...)`、`fmt(...)`、`calc(...)`、`match ... { ... }`
- 聚合表达式：`object { ... }`、`collect ...`
- 管道表达式：`pipe read(...) | ...`，也支持省略 `pipe` 写成 `read(...) | ...`
- 查表：`lookup_nocase(...)`
- 内置函数：`Now::time()`、`Now::date()`、`Now::hour()`
- SQL：`select ... from ... where ... ;`
- `static { ... }`：仅用于纯常量对象和常量计算

## 当前实现不应当这样写

- 不要把隐私段当作 OML 正式语法
- 不要写 `query ...` 作为 SQL 入口，当前入口关键字是 `select`
- 不要引用未在 [04-functions-reference.md](./04-functions-reference.md) 中列出的函数
- 不要假设 `static` 可以执行 `read/take/match/pipe/sql`

---

## 常用文档入口

| 目标 | 文档 |
|------|------|
| 学 `read` / `take` / `option` / `keys` | [02-core-concepts.md](./02-core-concepts.md) |
| 看 `calc(...)`、`lookup_nocase(...)`、`Now::*` | [04-functions-reference.md](./04-functions-reference.md) |
| 看 `match` 条件函数 | [functions/match_functions.md](./functions/match_functions.md) |
| 看 `static` 的限制 | [functions/static_blocks.md](./functions/static_blocks.md) |
| 看 EBNF 风格语法摘要 | [06-grammar-reference.md](./06-grammar-reference.md) |
