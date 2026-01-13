# OML 对象模型语言

OML（Object Modeling Language）用于在 Warp Parse 中对解析后的记录进行组装与聚合，提供 read/take 取值、对象与数组聚合（object/collect）、条件匹配（match）、字符串格式化（fmt）、管道转换（pipe）与 SQL 查询拼装等能力。

注意：从当前版本起，引擎默认不启用"隐私/脱敏"运行期处理；本章中涉及"隐私段"的语法仅作为 DSL 能力说明，若需要脱敏，请在业务侧或自定义插件/管道中实现。

## 内容概览

- [OML 语言基础](./01-oml_basics.md)
- [OML 使用示例](./02-oml_examples.md)
- [OML 函数参考](./03-oml_functions.md)
- [OML 语法（EBNF）](./04-oml_grammar.md)

## 特性概览

- 取值与缺省：`read(...)`（非破坏）/`take(...)`（破坏）+ 默认体 `{ _ : <值/函数> }`
- 对象/数组聚合：`object { ... }`、`collect read(keys:[...])`
- 条件匹配：`match read(x) { ... }` 与二元匹配 `match (read(a), read(b)) { ... }`
- 管道与格式化：`read(x) | to_json | base64_encode`，`fmt("{}-{}", @a, read(b))`
- SQL：`select <cols from table> where <cond>;`（主体白名单校验，严格模式可通过 `OML_SQL_STRICT=0` 关闭）
- 批量目标：目标名含 `*` 时按批量模式求值（仅支持 take/read）
- 隐私段：末尾通过第二个 `---` 声明字段隐私处理器映射

## 快速示例

```oml
name : example
---
user_id        = read(user_id) ;
occur_time:time= Now::time() ;
values : obj   = object {
  cpu_free, memory_free : digit = take() ;
};
ports : array  = collect read(keys:[sport,dport]) ;
ports_json     = pipe read(ports) | to_json ;
full           = fmt("{}-{}", @user, read(city)) ;
name,pinying   = select name,pinying from example where pinying = read(py) ;
---
src_ip : privacy_ip
pos_sn : privacy_keymsg
```

## 内置函数

| 函数 | 说明 | 返回类型 |
|------|------|----------|
| `Now::time()` | 获取当前时间 | `time` |
| `Now::date()` | 获取当前日期（YYYYMMDD） | `digit` |
| `Now::hour()` | 获取当前时间精确到小时（YYYYMMDDHH） | `digit` |

## 管道函数

| 函数 | 说明 |
|------|------|
| `base64_encode` | Base64 编码 |
| `base64_decode` | Base64 解码（支持多种字符编码） |
| `html_escape` / `html_unescape` | HTML 转义/反转义 |
| `json_escape` / `json_unescape` | JSON 转义/反转义 |
| `str_escape` | 字符串转义 |
| `Time::to_ts` / `Time::to_ts_ms` / `Time::to_ts_us` | 时间转时间戳（秒/毫秒/微秒，UTC+8） |
| `Time::to_ts_zone(时区,单位)` | 时间转指定时区时间戳 |
| `nth(索引)` | 获取数组元素 |
| `get(字段名)` | 获取对象字段 |
| `path(name\|path)` | 提取文件路径部分 |
| `url(domain\|host\|uri\|path\|params)` | 提取 URL 部分 |
| `sxf_get(字段名)` | 提取特殊格式字段 |
| `to_str` / `to_json` | 转换为字符串/JSON |
| `ip4_to_int` | IPv4 转整数 |
| `skip_empty` | 跳过空值 |

详细说明请参阅 [OML 函数参考](./03-oml_functions.md)。

## 数据类型

| 类型 | 说明 |
|------|------|
| `auto` | 自动推断（默认） |
| `chars` | 字符串 |
| `digit` | 整数 |
| `float` | 浮点数 |
| `ip` | IP 地址 |
| `time` | 时间 |
| `bool` | 布尔值 |
| `obj` | 对象 |
| `array` | 数组 |

## 相关文档

- [WPL 规则语言](../06-wpl/README.md)
- [配置指南概述](../02-config/README.md)
- [Schema 参考文档](../../80-reference/schemas/README.md)

提示：read/take 的差异见《OML 语言基础》；完整语法见《OML 语法（EBNF）》；端到端示例见《OML 使用示例》。
