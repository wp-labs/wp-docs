# OML 语法参考

本文档提供 OML 的完整语法定义（EBNF 格式），用于精确理解语法规则。

> 基于源码 `crates/wp-oml` 的解析实现，词法细节复用 `wp_parser` 与 `wpl` 的既有解析能力。

---

## 📚 文档导航

| 章节 | 内容 |
|------|------|
| [EBNF 符号说明](#ebnf-符号说明) | 语法符号含义 |
| [顶层结构](#顶层结构) | OML 文件结构 |
| [求值表达式](#求值表达式) | 表达式类型、值表达式、函数调用等 |
| [高级表达式](#高级表达式) | 格式化字符串、管道、match、聚合 |
| [SQL 表达式](#sql-表达式) | SQL 查询语法 |
| [静态绑定](#静态绑定) | static 常量定义与引用 |
| [临时字段](#临时字段) | `__` 前缀中间字段 |
| [隐私段](#隐私段) | 数据脱敏语法 |
| [词法与约定](#词法与约定) | 标识符、字面量、注释 |
| [数据类型](#数据类型) | 数据类型 |
| [完整示例](#完整示例) | 综合示例 |
| [管道函数速查](#管道函数速查) | 常用管道函数 |
| [语法要点](#语法要点) | 必需元素、可选元素、注意事项 |

---

## EBNF 符号说明

- `=` : 定义
- `,` : 连接（序列）
- `|` : 或（选择）
- `[ ]` : 可选（0 或 1 次）
- `{ }` : 重复（0 或多次）
- `( )` : 分组
- `"text"` : 字面量
- `(* ... *)` : 注释

---

## 顶层结构

```ebnf
oml              = header, sep_line, [ static_blocks ], aggregate_items,
                   [ sep_line, privacy_items ] ;

header           = "name", ":", name, eol,
                   [ "rule", ":", rule_path, { rule_path }, eol ],
                   [ "enable", ":", ("true" | "false"), eol ] ;

sep_line         = "---" ;

static_blocks    = { "static", "{", static_item, { static_item }, "}" } ;
static_item      = target, "=", eval, ";" ;

name             = path ;                       (* 例如: test *)
rule_path        = wild_path ;                  (* 例如: wpx/abc, wpx/efg *)

aggregate_items  = aggregate_item, { aggregate_item } ;
aggregate_item   = target_list, "=", eval, ";" ;

target_list      = target, { ",", target } ;
target           = target_name, [ ":", data_type ] ;
target_name      = wild_key | "_" ;            (* 允许带通配符 '*'；'_' 表示匿名/丢弃 *)
data_type        = type_ident ;                (* auto|ip|chars|digit|float|time|bool|obj|array 等 *)
```

**说明**：
- `name : <配置名称>` - 必需的配置名称声明
- `rule : <规则路径>` - 可选的规则关联，支持空格或换行分隔多个规则
- `enable : true|false` - 可选的启用开关（默认 `true`）；`rule` 与 `enable` 的顺序不限
- `static { ... }` - 可选的静态绑定块，位于 `---` 分隔线之后、主绑定之前
- `---` - 分隔符，区分声明区和配置区
- 每个配置条目必须以 `;` 结束

---

## 求值表达式

### 表达式类型

```ebnf
eval             = take_expr
                 | read_expr
                 | fmt_expr
                 | pipe_expr
                 | map_expr
                 | collect_expr
                 | calc_expr
                 | match_expr
                 | sql_expr
                 | value_expr
                 | fun_call
                 | static_ref ;
```

### 读取表达式

```ebnf
(* 变量获取：take/read 支持统一参数形态；可跟缺省体 *)
take_expr        = "take", "(", [ arg_list ], ")", [ default_body ] ;
read_expr        = "read", "(", [ arg_list ], ")", [ default_body ] ;

arg_list         = arg, { ",", arg } ;
arg              = "option", ":", "[", key, { ",", key }, "]"
                 | ("in"|"keys"), ":", "[", key, { ",", key }, "]"
                 | "get",    ":", simple
                 | json_path ;                 (* 见 wp_parser::atom::take_json_path *)

default_body     = "{", "_", ":", gen_acq, [ ";" ], "}" ;
gen_acq          = take_expr | read_expr | value_expr | fun_call | static_ref ;
```

**说明**：
- `@` 仅作为变量获取语法糖用于 fmt/pipe/collect 的 var_get 位置
- `@ref` 等价于 `read(ref)`，但不支持缺省体
- 不作为独立求值表达式

**示例**：
```oml
# 基本读取
value = read(field) ;

# 带默认值
value = read(field) { _ : chars(default) } ;

# option 参数
value = read(option:[id, uid, user_id]) ;

# keys 参数
values = collect read(keys:[field1, field2]) ;

# JSON 路径
name = read(/user/info/name) ;
item = read(/data/[0]/name) ;
```

### 值表达式

```ebnf
(* 常量值：类型名+括号包裹的字面量 *)
value_expr       = data_type, "(", literal, ")" ;
```

**示例**：
```oml
text = chars(hello) ;
text2 = chars('hello world') ;
count = digit(42) ;
ratio = float(3.14) ;
address = ip(192.168.1.1) ;
flag = bool(true) ;
ts = time(2020-10-01 12:30:30) ;
```

### 函数调用

```ebnf
(* 内置函数（零参占位）：Now::* 家族 *)
fun_call         = ("Now::time"
                   |"Now::date"
                   |"Now::hour"), "(", ")" ;
```

**示例**：
```oml
now = Now::time() ;
today = Now::date() ;
hour = Now::hour() ;
```

### 静态符号引用

```ebnf
(* 引用 static 块中定义的常量，直接使用标识符 *)
static_ref       = ident ;                     (* 必须在 static { } 中已定义 *)
```

**示例**：
```oml
static {
    tpl = object { id = chars(E1) ; } ;
}
target = tpl ;                                 # 引用 static 中的 tpl
```

---

## 高级表达式

### 格式化字符串

```ebnf
(* 字符串格式化，至少 1 个参数 *)
fmt_expr         = "fmt", "(", string, ",", var_get, { ",", var_get }, ")" ;
var_get          = ("read" | "take"), "(", [ arg_list ], ")"
                 | "@", ident ;                  (* '@ref' 等价 read(ref)，不支持缺省体 *)
```

**示例**：
```oml
message = fmt("{}-{}", @user, read(city)) ;
id = fmt("{}:{}", read(host), read(port)) ;
```

### 管道表达式

```ebnf
(* 管道：可省略 pipe 关键字 *)
pipe_expr        = ["pipe"], var_get, "|", pipe_fun, { "|", pipe_fun } ;

pipe_fun         = "nth",           "(", unsigned, ")"
                 | "get",           "(", ident,   ")"
                 | "base64_decode", "(", [ encode_type ], ")"
                 | "path",          "(", ("name"|"path"), ")"
                 | "url",           "(", ("domain"|"host"|"uri"|"path"|"params"), ")"
                 | "Time::to_ts_zone", "(", [ "-" ], unsigned, ",", ("ms"|"us"|"ss"|"s"), ")"
                 | "starts_with",   "(", string, ")"
                 | "map_to",        "(", (string | number | bool), ")"
                 | "base64_encode" | "html_escape" | "html_unescape"
                 | "str_escape" | "json_escape" | "json_unescape"
                 | "Time::to_ts" | "Time::to_ts_ms" | "Time::to_ts_us"
                 | "to_json" | "to_str" | "skip_empty" | "ip4_to_int"
                 | "extract_main_word" | "extract_subject_object" ;

encode_type      = ident ;                     (* 例如: Utf8/Gbk/Imap/... *)
```

**示例**：
```oml
# 使用 pipe 关键字
result = pipe read(data) | to_json | base64_encode ;

# 省略 pipe 关键字
result = read(data) | to_json | base64_encode ;

# 时间转换
ts = read(time) | Time::to_ts_zone(0, ms) ;

# URL 解析
host = read(url) | url(host) ;

# 字符串前缀检查
is_http = read(url) | starts_with('http://') ;

# 映射到常量值
status = read(code) | map_to(200) ;

# 提取主要单词
keyword = read(message) | extract_main_word ;

# 提取主客体结构
log_struct = read(message) | extract_subject_object ;
```

### 对象聚合

```ebnf
(* 聚合到对象：object 内部为子赋值序列；分号可选但推荐 *)
map_expr         = "object", "{", map_item, { map_item }, "}" ;
map_item         = map_targets, "=", sub_acq, [ ";" ] ;
map_targets      = ident, { ",", ident }, [ ":", data_type ] ;
sub_acq          = take_expr | read_expr | value_expr | fun_call | static_ref ;
```

**示例**：
```oml
info : obj = object {
    name : chars = read(name) ;
    age : digit = read(age) ;
    city : chars = read(city) ;
} ;
```

### 数组聚合

```ebnf
(* 聚合到数组：从 VarGet 收集（支持 keys/option 通配） *)
collect_expr     = "collect", var_get ;
```

**示例**：
```oml
# 收集多个字段
ports = collect read(keys:[sport, dport]) ;

# 使用通配符
metrics = collect read(keys:[cpu_*]) ;
```

### 算术表达式

```ebnf
calc_expr         = "calc", "(", calc_add_expr, ")" ;
calc_add_expr     = calc_mul_expr, { ("+" | "-"), calc_mul_expr } ;
calc_mul_expr     = calc_unary_expr, { ("*" | "/" | "%"), calc_unary_expr } ;
calc_unary_expr   = [ "-" ], calc_primary_expr ;
calc_primary_expr = number
                  | var_get
                  | calc_fun_expr
                  | "(", calc_add_expr, ")" ;
calc_fun_expr     = calc_fun, "(", calc_add_expr, ")" ;
calc_fun          = "abs" | "round" | "floor" | "ceil" ;
```

**说明**：
- `var_get` 支持 `read(...)`、`take(...)`，也支持 `@field` 语法糖
- 操作数仅接受数值字面量或数值字段；`/` 始终返回 `float`
- `%` 仅支持整数取模；除零、字段缺失、非数值输入、非法 `%` 都会返回 `ignore`
- 当前 `match` 分支值仍沿用既有子表达式，不直接接受 `calc(...)`；如需复用，先绑定到临时字段

**示例**：
```oml
risk_score : float = calc(read(cpu) * 0.7 + read(mem) * 0.3) ;
delta      : digit = calc(read(cur) - read(prev)) ;
ratio      : float = calc(read(ok_cnt) / read(total_cnt)) ;
bucket     : digit = calc(read(uid) % 16) ;
error_pct  : digit = calc(round((read(err_cnt) * 100) / read(total_cnt))) ;
```

### 模式匹配

```ebnf
(* 模式匹配：单源/多源两种形态，支持 in/!=/OR/函数匹配 与缺省分支 *)
match_expr       = "match", match_source, "{", case1, { case1 }, [ default_case ], "}"
                 | "match", "(", var_get, ",", var_get, { ",", var_get }, ")", "{", case_multi, { case_multi }, [ default_case ], "}" ;

match_source     = var_get ;
case1            = cond1, "=>", match_value, [ "," ], [ ";" ] ;
case_multi       = "(", cond1, ",", cond1, { ",", cond1 }, ")", "=>", match_value, [ "," ], [ ";" ] ;
default_case     = "_", "=>", match_value, [ "," ], [ ";" ] ;
match_value      = read_expr | take_expr | value_expr | collect_expr | static_ref ;

cond1            = cond1_atom, { "|", cond1_atom }   (* OR：多个条件用 | 分隔 *)
cond1_atom       = "in", "(", value_expr, ",", value_expr, ")"
                 | "!", value_expr
                 | match_fun                           (* 函数匹配 *)
                 | value_expr ;                        (* 省略运算符表示等于 *)

match_fun        = "starts_with",  "(", string, ")"   (* 前缀匹配 *)
                 | "ends_with",    "(", string, ")"   (* 后缀匹配 *)
                 | "contains",     "(", string, ")"   (* 子串匹配 *)
                 | "regex_match",  "(", string, ")"   (* 正则匹配 *)
                 | "iequals",      "(", string, ")"   (* 忽略大小写等于 *)
                 | "is_empty",     "(", ")"            (* 空值判断 *)
                 | "gt",           "(", number, ")"    (* 大于 *)
                 | "lt",           "(", number, ")"    (* 小于 *)
                 | "eq",           "(", number, ")"    (* 等于（浮点容差） *)
                 | "in_range",     "(", number, ",", number, ")" ; (* 范围判断 *)
```

**说明**：
- **多源匹配**：`match (src1, src2, ...)` 支持任意数量的源字段（≥2），不再限于双源
- **OR 语法**：在条件位置使用 `|` 分隔多个备选条件，任一匹配即成功
- **函数匹配**：支持 11 种内置匹配函数，用于字符串、数值的灵活判断

**示例**：
```oml
# 单源匹配
level = match read(status) {
    in (digit(200), digit(299)) => chars(success) ;
    in (digit(400), digit(499)) => chars(error) ;
    _ => chars(other) ;
} ;

# 单源 OR 匹配
tier = match read(city) {
    chars(bj) | chars(sh) | chars(gz) => chars(tier1) ;
    chars(cd) | chars(wh) => chars(tier2) ;
    _ => chars(other) ;
} ;

# 多源匹配（双源）
result = match (read(a), read(b)) {
    (digit(1), digit(2)) => chars(case1) ;
    _ => chars(default) ;
} ;

# 多源匹配（三源）
zone = match (read(city), read(region), read(country)) {
    (chars(bj), chars(north), chars(cn)) => chars(result1) ;
    _ => chars(default) ;
} ;

# 多源 + OR 匹配
priority = match (read(city), read(level)) {
    (chars(bj) | chars(sh), chars(high)) => chars(priority) ;
    (chars(gz), chars(low) | chars(mid)) => chars(normal) ;
    _ => chars(default) ;
} ;

# 函数匹配
event = match read(Content) {
    starts_with('[ERROR]') => chars(error) ;
    starts_with('[WARN]') => chars(warning) ;
    contains('timeout') => chars(timeout) ;
    ends_with('.failed') => chars(failure) ;
    regex_match('^\d{4}-\d{2}-\d{2}') => chars(dated) ;
    is_empty() => chars(empty) ;
    _ => chars(other) ;
} ;

# 数值函数匹配
grade = match read(score) {
    gt(90) => chars(excellent) ;
    in_range(60, 90) => chars(pass) ;
    lt(60) => chars(fail) ;
    _ => chars(unknown) ;
} ;

# 忽略大小写匹配
status = match read(result) {
    iequals('success') => chars(ok) ;
    iequals('error') => chars(fail) ;
    _ => chars(other) ;
} ;

# 忽略大小写多值匹配
status_class = match read(status) {
    iequals_any('success', 'ok', 'done') => chars(good) ;
    iequals_any('error', 'failed', 'timeout') => chars(bad) ;
    _ => chars(other) ;
} ;
```

### `lookup_nocase`

`lookup_nocase(dict_symbol, key_expr, default_expr)` 用于基于静态 object 做忽略大小写查表。

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

- `dict_symbol` 必须引用 `static` 中定义的 object
- `key_expr` 会按 `trim + lowercase` 归一化后查表
- 未命中或 key 不是字符串时，返回 `default_expr`

### `calc(...)`

`calc(expr)` 用于显式执行数值算术表达式。

```oml
risk_score : float = calc(read(cpu) * 0.7 + read(mem) * 0.3) ;
bucket     : digit = calc(read(uid) % 16) ;
distance   : float = calc(abs(read(actual) - read(expect))) ;
error_pct  : digit = calc(round((read(err_cnt) * 100) / read(total_cnt))) ;
```

- 支持运算符：`+ - * / %`
- 支持函数：`abs(...)`、`round(...)`、`floor(...)`、`ceil(...)`
- 支持字段访问：`read(...)`、`take(...)`、`@field`
- 除零、字段缺失、非数值输入、浮点 `%` 都返回 `ignore`

---

## SQL 表达式

```ebnf
sql_expr        = "select", sql_body, "where", sql_cond, ";" ;
sql_body        = sql_safe_body ;              (* 源码对白名单化：仅 [A-Za-z0-9_.] 与 '*' *)
sql_cond        = cond_expr ;

cond_expr       = cmp, { ("and" | "or"), cmp }
                 | "not", cond_expr
                 | "(", cond_expr, ")" ;

cmp             = ident, sql_op, cond_rhs ;
sql_op          = sql_cmp_op ;                 (* 见 wp_parser::sql_symbol::symbol_sql_cmp *)
cond_rhs        = read_expr | take_expr | fun_call | sql_literal ;
sql_literal     = number | string ;
```

### 严格模式说明

- **严格模式（默认开启）**：当主体 `<cols from table>` 不满足白名单规则时，解析报错
- **兼容模式**：设置环境变量 `OML_SQL_STRICT=0`，若主体非法则回退原文（不推荐）
- **白名单规则**：
  - 列清单：`*` 或由 `[A-Za-z0-9_.]+` 组成的列名（允许点号作限定）
  - 表名：`[A-Za-z0-9_.]+`（单表，不支持 join/子查询）
  - `from` 大小写不敏感；多余空白允许

**示例**：
```oml
# 正确示例
name, email = select name, email from users where id = read(user_id) ;

# 使用字符串常量
data = select * from table where type = 'admin' ;

# IP 范围查询
zone = select zone from ip_geo
    where ip_start_int <= ip4_int(read(src_ip))
      and ip_end_int >= ip4_int(read(src_ip)) ;
```

**错误示例（严格模式）**：
```oml
# ❌ 表名含非法字符
data = select a, b from table-1 where ... ;

# ❌ 列清单含函数
data = select sum(a) from t where ... ;

# ❌ 不支持 join
data = select a from t1 join t2 ... ;
```

---

## 静态绑定

`static` 块用于定义编译期常量，可在主绑定和 match 表达式中引用。

```ebnf
static_blocks    = { "static", "{", static_item, { static_item }, "}" } ;
static_item      = target, "=", eval, ";" ;
```

**说明**：
- `static` 块位于 `---` 分隔线之后、主绑定之前
- 块内每个绑定会在编译期求值为 `DataField`
- 主绑定中通过标识符直接引用：`result = symbol_name ;`
- 支持在 `match` 的条件和结果、`object` 子绑定、`read/take` 的缺省体中引用
- 同名符号不允许重复定义

**示例**：
```oml
name : model_with_static
---
static {
    tpl = object {
        id = chars(E1) ;
        type = chars(default) ;
    } ;
    fallback = chars(N/A) ;
}

# 直接引用 static 符号
template = tpl ;

# 在 match 结果中引用
target = match read(Content) {
    starts_with('foo') => tpl ;
    _ => tpl ;
} ;

# 在缺省体中引用
value = take(Value) { _ : fallback } ;

# 在 object 子绑定中引用
result = object {
    clone = tpl ;
} ;
```

---

## 临时字段

以 `__`（双下划线）开头的字段名被标记为临时字段，在输出时自动转换为 `Ignore` 类型（不出现在最终数据中）。

**用途**：中间计算结果，不希望出现在输出记录中。

**示例**：
```oml
name : temp_example
---
# 临时字段：参与中间计算，不输出
__temp_type = chars(error) ;

# 引用临时字段进行匹配
result = match read(__temp_type) {
    chars(error) => chars(failed) ;
    _ => chars(ok) ;
} ;
```

输出记录中 `result` 正常输出，`__temp_type` 被自动忽略。

---

## 隐私段

> 注：引擎默认不启用运行期隐私/脱敏处理；以下为 DSL 语法能力说明，供需要的场景参考。

```ebnf
privacy_items   = privacy_item, { privacy_item } ;
privacy_item    = ident, ":", privacy_type ;

privacy_type    = "privacy_ip"
                 | "privacy_specify_ip"
                 | "privacy_id_card"
                 | "privacy_mobile"
                 | "privacy_mail"
                 | "privacy_domain"
                 | "privacy_specify_name"
                 | "privacy_specify_domain"
                 | "privacy_specify_address"
                 | "privacy_specify_company"
                 | "privacy_keymsg" ;
```

**示例**：
```oml
name : privacy_example
---
field = read() ;
---
src_ip : privacy_ip
pos_sn : privacy_keymsg
```

---

## 词法与约定

```ebnf
path            = ident, { ("/" | "."), ident } ;
wild_path       = path | path, "*" ;          (* 允许通配 *)
wild_key        = ident, { ident | "*" } ;    (* 允许 '*' 出现在键名中 *)
type_ident      = ident ;                      (* 如 auto/ip/chars/digit/float/time/bool/obj/array *)
ident           = letter, { letter | digit | "_" } ;
key             = ident ;

string          = "\"", { any-but-quote }, "\""
                | "'", { any-but-quote }, "'" ;

literal         = string | number | ip | bool | datetime | ... ;
json_path       = "/" , ... ;                 (* 如 /a/b/[0]/1 *)
simple          = ident | number | string ;
unsigned        = digit, { digit } ;
eol             = { " " | "\t" | "\r" | "\n" } ;

letter          = "A" | ... | "Z" | "a" | ... | "z" ;
digit           = "0" | ... | "9" ;
alnum           = letter | digit ;
```

---

## 数据类型

OML 类型注解支持以下值（由 `DataType::from()` 解析）：

### 常用类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `auto` | 自动推断（默认） | `field = read() ;` |
| `chars` | 字符串 | `name : chars = read() ;` |
| `digit` | 整数 | `count : digit = read() ;` |
| `float` | 浮点数 | `ratio : float = read() ;` |
| `ip` | IP 地址 | `addr : ip = read() ;` |
| `time` | 时间 | `timestamp : time = Now::time() ;` |
| `bool` | 布尔值 | `flag : bool = read() ;` |
| `obj` | 对象 | `info : obj = object { ... } ;` |
| `array` | 数组 | `items : array = collect read(...) ;` |

### 扩展类型

| 类型 | 说明 |
|------|------|
| `time_iso` | ISO 格式时间 |
| `time_3339` | RFC 3339 时间 |
| `time_2822` | RFC 2822 时间 |
| `time_timestamp` | Unix 时间戳 |
| `time_clf` | CLF 日志时间（Apache/Nginx） |
| `time/apache` | CLF 别名 |
| `time/timestamp` | 时间戳别名 |
| `time/rfc3339` | RFC 3339 别名 |
| `url` | URL |
| `domain` | 域名 |
| `ip_net` | 网段 |
| `kv` | Key-Value 文本 |
| `json` | JSON 文本 |
| `base64` | Base64 编码文本 |
| `array/<sub>` | 带子类型的数组（如 `array/digit`） |

---

## 完整示例

```oml
name : csv_example
rule : /csv/data
enable : true
---
static {
    ERROR_TPL = object {
        type = chars(error) ;
        level = digit(0) ;
    } ;
}

# 基本取值与缺省
version : chars = Now::time() ;
pos_sn = read() { _ : chars(FALLBACK) } ;

# 临时字段（不出现在输出中）
__raw_type = read(type) ;

# object 聚合
values : obj = object {
    cpu_free, memory_free : digit = read() ;
} ;

# collect 数组聚合 + 管道
ports : array = collect read(keys:[sport, dport]) ;
ports_json = pipe read(ports) | to_json ;
first_port = pipe read(ports) | nth(0) ;

# 省略 pipe 关键字的管道写法
url_host = read(http_url) | url(host) ;

# match
quarter : chars = match read(month) {
    in (digit(1), digit(3))   => chars(Q1) ;
    in (digit(4), digit(6))   => chars(Q2) ;
    in (digit(7), digit(9))   => chars(Q3) ;
    in (digit(10), digit(12)) => chars(Q4) ;
    _ => chars(QX) ;
} ;

# 双源 match
X : chars = match (read(city1), read(city2)) {
    (ip(127.0.0.1), ip(127.0.0.100)) => chars(bj) ;
    _ => chars(sz) ;
} ;

# 三源 match
zone : chars = match (read(city), read(region), read(country)) {
    (chars(bj), chars(north), chars(cn)) => chars(zone1) ;
    (chars(sh), chars(east), chars(cn)) => chars(zone2) ;
    _ => chars(unknown) ;
} ;

# OR 匹配（单源）
tier : chars = match read(city) {
    chars(bj) | chars(sh) | chars(gz) => chars(tier1) ;
    chars(cd) | chars(wh) => chars(tier2) ;
    _ => chars(other) ;
} ;

# OR 匹配（多源）
priority : chars = match (read(city), read(level)) {
    (chars(bj) | chars(sh), chars(high)) => chars(priority) ;
    (chars(gz), chars(low) | chars(mid)) => chars(normal) ;
    _ => chars(default) ;
} ;

# 函数匹配
event = match read(log_line) {
    starts_with('[ERROR]') => chars(error) ;
    ends_with('.failed') => chars(failure) ;
    contains('timeout') => chars(timeout) ;
    regex_match('^\d{4}-\d{2}-\d{2}') => chars(dated) ;
    is_empty() => chars(empty) ;
    _ => chars(other) ;
} ;

# 数值函数匹配
grade = match read(score) {
    gt(90) => chars(excellent) ;
    in_range(60, 90) => chars(pass) ;
    lt(60) => chars(fail) ;
    _ => chars(unknown) ;
} ;

# 忽略大小写匹配
result = match read(status) {
    iequals('success') => chars(ok) ;
    _ => chars(fail) ;
} ;

# static 引用
error_info = match read(__raw_type) {
    chars(error) => ERROR_TPL ;
    _ => chars(normal) ;
} ;

# SQL（where 中可混用 read/take/Now::time/常量）
name, pinying = select name, pinying from example where pinying = read(py) ;
_, _ = select name, pinying from example where pinying = 'xiaolongnu' ;

---
# 隐私配置（按键绑定处理器枚举）
src_ip : privacy_ip
pos_sn : privacy_keymsg
```

---

## 管道函数速查

| 函数 | 语法 | 说明 |
|------|------|------|
| `base64_encode` | `base64_encode` | Base64 编码 |
| `base64_decode` | `base64_decode` / `base64_decode(编码)` | Base64 解码 |
| `html_escape` | `html_escape` | HTML 转义 |
| `html_unescape` | `html_unescape` | HTML 反转义 |
| `json_escape` | `json_escape` | JSON 转义 |
| `json_unescape` | `json_unescape` | JSON 反转义 |
| `str_escape` | `str_escape` | 字符串转义 |
| `Time::to_ts` | `Time::to_ts` | 时间转时间戳（秒，UTC+8） |
| `Time::to_ts_ms` | `Time::to_ts_ms` | 时间转时间戳（毫秒，UTC+8） |
| `Time::to_ts_us` | `Time::to_ts_us` | 时间转时间戳（微秒，UTC+8） |
| `Time::to_ts_zone` | `Time::to_ts_zone(时区,单位)` | 时间转指定时区时间戳 |
| `nth` | `nth(索引)` | 获取数组元素 |
| `get` | `get(字段名)` | 获取对象字段 |
| `path` | `path(name\|path)` | 提取文件路径部分 |
| `url` | `url(domain\|host\|uri\|path\|params)` | 提取 URL 部分 |
| `starts_with` | `starts_with('前缀')` | 检查字符串是否以指定前缀开始 |
| `map_to` | `map_to(值)` | 映射到指定常量值（字符串/数字/布尔） |
| `extract_main_word` | `extract_main_word` | 提取主要单词（第一个非空单词） |
| `extract_subject_object` | `extract_subject_object` | 提取日志主客体结构（subject/action/object/status） |
| `to_str` | `to_str` | 转换为字符串 |
| `to_json` | `to_json` | 转换为 JSON |
| `ip4_to_int` | `ip4_to_int` | IPv4 转整数 |
| `skip_empty` | `skip_empty` | 跳过空值 |

### 匹配函数速查（用于 match 条件）

| 函数 | 语法 | 说明 |
|------|------|------|
| `starts_with` | `starts_with('前缀')` | 前缀匹配 |
| `ends_with` | `ends_with('后缀')` | 后缀匹配 |
| `contains` | `contains('子串')` | 子串匹配 |
| `regex_match` | `regex_match('正则')` | 正则表达式匹配 |
| `iequals` | `iequals('值')` | 忽略大小写等于 |
| `is_empty` | `is_empty()` | 值为空判断 |
| `gt` | `gt(数值)` | 大于 |
| `lt` | `lt(数值)` | 小于 |
| `eq` | `eq(数值)` | 等于（浮点容差） |
| `in_range` | `in_range(最小值, 最大值)` | 范围判断（闭区间） |

---

## 语法要点

### 必需元素

1. **配置名称**：`name : <名称>`
2. **分隔符**：`---`
3. **分号**：每个顶层条目必须以 `;` 结束

### 可选元素

1. **类型声明**：`field : <type> = ...`（默认为 `auto`）
2. **rule 字段**：`rule : <规则路径>`
3. **enable 字段**：`enable : true|false`（默认为 `true`）
4. **static 块**：`static { ... }`
5. **默认值**：`read() { _ : <默认值> }`
6. **pipe 关键字**：`pipe read() | func` 可简写为 `read() | func`

### 注释

```oml
# 单行注释（使用 # 或 //）
// 也支持 C++ 风格注释
```

### 目标通配

```oml
* = take() ;           # 取走所有字段
alert* = take() ;      # 取走所有以 alert 开头的字段
*_log = take() ;       # 取走所有以 _log 结尾的字段
```

### 临时字段

```oml
__temp = chars(value) ;      # 以 __ 开头，输出时自动忽略
result = read(__temp) ;      # 可在其他表达式中引用
```

### 读取语义

- **read**：非破坏性（可反复读取，不从 src 移除）
- **take**：破坏性（取走后从 src 移除，后续不可再取）

---

## 下一步

- [核心概念](./02-core-concepts.md) - 理解语法设计理念
- [实战指南](./03-practical-guide.md) - 查看实际应用示例
- [函数参考](./04-functions-reference.md) - 查阅所有可用函数
- [快速入门](./01-quickstart.md) - 快速上手 OML
