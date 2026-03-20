# OML 函数参考

本文档提供所有内置函数和管道函数的完整参考，采用标准化格式便于查找。

---


## 📚 详细文档导航

- [内置函数](#内置函数) - 可直接使用的函数
- [管道函数](#管道函数) - 通过管道操作符调用的函数
  - [编码函数](#编码函数) - Base64 编解码
  - [转义函数](#转义函数) - HTML/JSON/字符串转义
  - [时间函数](#时间函数) - 时间戳转换
  - [数据访问函数](#数据访问函数) - 数组/对象/URL/路径访问
  - [转换函数](#转换函数) - 类型转换
  - [控制函数](#控制函数) - 流程控制
- [使用示例](#使用示例) - 完整示例

---

## 📋 OML 所有函数速查

### 内置函数

| 函数 | 说明 | 示例 |
|------|------|------|
| [`calc(...)`](#calc) | 执行显式算术表达式 | `score = calc(read(cpu) * 0.7 + read(mem) * 0.3) ;` |
| [`lookup_nocase(...)`](#lookup_nocase) | 对静态 object 做忽略大小写查表 | `score = lookup_nocase(status_score, read(status), 40.0) ;` |
| [`Now::time()`](#nowtime-1) | 获取当前时间 | `event_time = Now::time() ;` |
| [`Now::date()`](#nowdate-1) | 获取当前日期（YYYYMMDD） | `today = Now::date() ;` |
| [`Now::hour()`](#nowhour-1) | 获取当前小时（YYYYMMDDHH） | `current_hour = Now::hour() ;` |

### 管道函数

| 功能分类 | 函数 | 说明 | 示例 |
|---------|------|------|------|
| **编码** | [`base64_encode`](#base64_encode-1) | Base64 编码 | `read(data) \| base64_encode` |
| | [`base64_decode`](#base64_decode-1) | Base64 解码（支持 Utf8/Gbk） | `read(data) \| base64_decode(Utf8)` |
| **转义** | [`html_escape`](#html_escape) | HTML 转义 | `read(text) \| html_escape` |
| | [`html_unescape`](#html_unescape) | HTML 反转义 | `read(html) \| html_unescape` |
| | [`json_escape`](#json_escape) | JSON 转义 | `read(text) \| json_escape` |
| | [`json_unescape`](#json_unescape) | JSON 反转义 | `read(json) \| json_unescape` |
| | [`str_escape`](#str_escape) | 字符串转义 | `read(str) \| str_escape` |
| **时间** | [`Time::to_ts`](#timeto_ts-1) | 转时间戳（秒，UTC+8） | `read(time) \| Time::to_ts` |
| | [`Time::to_ts_ms`](#timeto_ts_ms-1) | 转时间戳（毫秒，UTC+8） | `read(time) \| Time::to_ts_ms` |
| | [`Time::to_ts_us`](#timeto_ts_us-1) | 转时间戳（微秒，UTC+8） | `read(time) \| Time::to_ts_us` |
| | [`Time::to_ts_zone`](#timeto_ts_zone-1) | 转指定时区时间戳 | `read(time) \| Time::to_ts_zone(0, ms)` |
| **数据访问** | [`nth(index)`](#nth-1) | 获取数组元素 | `read(arr) \| nth(0)` |
| | [`get(key)`](#get-1) | 获取对象字段 | `read(obj) \| get(name)` |
| | [`path(part)`](#path-1) | 提取文件路径（name/path） | `read(path) \| path(name)` |
| | [`url(part)`](#url-1) | 提取 URL（domain/host/path/params/uri） | `read(url) \| url(domain)` |
| | [`sxf_get(field)`](#sxf_get) | 提取特殊格式字段 | `read(log) \| sxf_get(status)` |
| **转换** | [`to_str`](#to_str-1) | 转换为字符串 | `read(ip) \| to_str` |
| | [`to_json`](#to_json-1) | 转换为 JSON | `read(arr) \| to_json` |
| | [`ip4_to_int`](#ip4_to_int) | IPv4 转整数 | `read(ip) \| ip4_to_int` |
| **控制** | [`skip_empty`](#skip_empty-1) | 跳过空值 | `read(field) \| skip_empty` |

### 常用场景速查

| 我想做什么 | 使用方法 |
|-----------|---------|
| **获取当前时间** | `event_time = Now::time() ;` |
| **时间转时间戳** | `ts = read(time) \| Time::to_ts_zone(0, ms) ;` |
| **Base64 解码** | `decoded = read(data) \| base64_decode(Utf8) ;` |
| **HTML 转义** | `escaped = read(text) \| html_escape ;` |
| **解析 URL** | `domain = read(url) \| url(domain) ;` |
| **提取文件名** | `filename = read(path) \| path(name) ;` |
| **获取数组第一个元素** | `first = read(arr) \| nth(0) ;` |
| **获取对象字段** | `name = read(obj) \| get(name) ;` |
| **IP 转整数** | `ip_int = read(ip) \| ip4_to_int ;` |
| **跳过空值** | `result = read(field) \| skip_empty ;` |
| **链式处理** | `result = read(data) \| to_json \| base64_encode ;` |
| **字符串格式化** | `msg = fmt("{}:{}", @ip, @port) ;` |
| **条件匹配** | `level = match read(status) { ... } ;` |
| **忽略大小写多值匹配** | `iequals_any('success', 'ok', 'done') => chars(good)` |
| **静态字典查表** | `lookup_nocase(status_score, read(status), 40.0)` |
| **创建对象** | `info : obj = object { ... } ;` |
| **创建数组** | `items : array = collect read(keys:[...]) ;` |
| **提供默认值** | `country = read(country) { _ : chars(CN) } ;` |
| **选择性读取** | `id = read(option:[id, uid, user_id]) ;` |
| **批量收集** | `metrics = collect read(keys:[cpu_*]) ;` |
| **算术计算** | `risk = calc(read(cpu) * 0.7 + read(mem) * 0.3) ;` |

---

## 内置函数

内置函数可以直接在赋值表达式中使用，无需 `pipe` 关键字。

### calc(...)

执行显式算术表达式。

**语法**：
```oml
calc(<expr>)
```

**支持能力**：
- 运算符：`+ - * / %`
- 函数：`abs(...)`、`round(...)`、`floor(...)`、`ceil(...)`
- 操作数：数值字面量、`read(...)`、`take(...)`、`@field`

**返回类型**：
- `+ - *`：若存在浮点操作数则返回 `float`，否则返回 `digit`
- `/`：始终返回 `float`
- `%`：仅支持整数取模，返回 `digit`

**失败行为**：
- 除零、字段缺失、非数值输入、浮点 `%`、整数溢出、`NaN/inf` 都返回 `ignore`

**示例**：
```oml
risk_score : float = calc(read(cpu) * 0.7 + read(mem) * 0.3) ;
delta      : digit = calc(read(cur) - read(prev)) ;
distance   : float = calc(abs(read(actual) - read(expect))) ;
error_pct  : digit = calc(round((read(err_cnt) * 100) / read(total_cnt))) ;
```

---

### lookup_nocase(...)

基于 `static` 中定义的 object 做忽略大小写查表。

**语法**：
```oml
lookup_nocase(<dict_symbol>, <key_expr>, <default_expr>)
```

**参数**：
- `dict_symbol`：`static` 中定义的 object 符号
- `key_expr`：待查 key，通常是 `read(...)`
- `default_expr`：未命中时返回的默认值

**查表规则**：
- key 会先做 `trim + lowercase`
- 命中后返回字典中的对应值
- 未命中或 key 不是字符串时，返回 `default_expr`

**示例**：
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

**更多说明**：
- `iequals_any(...)` 详见 [functions/match_functions.md](./functions/match_functions.md)
- `lookup_nocase(...)` 详见 [functions/lookup_nocase.md](./functions/lookup_nocase.md)

---

### Now::time()

获取当前时间。

**语法**：
```oml
Now::time()
```

**参数**：无

**返回类型**：`time`

**示例**：
```oml
event_time : time = Now::time() ;
# 输出：2024-01-15 14:30:45
```

---

### Now::date()

获取当前日期，格式为 `YYYYMMDD` 的整数。

**语法**：
```oml
Now::date()
```

**参数**：无

**返回类型**：`digit`

**示例**：
```oml
today : digit = Now::date() ;
# 输出：20240115
```

---

### Now::hour()

获取当前时间精确到小时，格式为 `YYYYMMDDHH` 的整数。

**语法**：
```oml
Now::hour()
```

**参数**：无

**返回类型**：`digit`

**示例**：
```oml
current_hour : digit = Now::hour() ;
# 输出：2024011514
```

---

## 管道函数

管道函数通过 `pipe` 关键字和 `|` 操作符链式调用（`pipe` 关键字可省略）。

**基本语法**：
```oml
# 使用 pipe 关键字
result = pipe read(field) | function1 | function2(param) ;

# 省略 pipe 关键字
result = read(field) | function1 | function2(param) ;
```

---

## 编码函数

### base64_encode

将字符串进行 Base64 编码。

**语法**：
```oml
| base64_encode
```

**参数**：无

**输入类型**：`chars`
**输出类型**：`chars`

**示例**：
```oml
encoded = read(payload) | base64_encode ;
# 输入："Hello, OML!"
# 输出："SGVsbG8sIE9NTCE="
```

---

### base64_decode

将 Base64 编码的字符串解码。

**语法**：
```oml
| base64_decode
| base64_decode(<encoding>)
```

**参数**：
- `encoding`（可选）：字符编码类型，默认为 `Utf8`

**支持的编码**：
- `Utf8` - UTF-8 编码（默认）
- `Gbk` - GBK 中文编码
- `Imap` - IMAP Base64 变体（将非 ASCII 字节转义为 `\xNN` 格式）
- 更多编码请参阅源码文档

**输入类型**：`chars`
**输出类型**：`chars`

**示例**：
```oml
# 标准 UTF-8 解码
decoded = read(data) | base64_decode ;
# 输入："SGVsbG8sIE9NTCE="
# 输出："Hello, OML!"

# GBK 中文解码
gbk_text = read(gbk_data) | base64_decode(Gbk) ;

# IMAP 变体解码（处理二进制数据）
raw = read(binary_data) | base64_decode(Imap) ;
```

---

## 转义函数

### html_escape

对 HTML 特殊字符进行转义。

**语法**：
```oml
| html_escape
```

**参数**：无

**转义规则**：
- `<` → `&lt;`
- `>` → `&gt;`
- `&` → `&amp;`
- `"` → `&quot;`
- `'` → `&#x27;`

**输入类型**：`chars`
**输出类型**：`chars`

**示例**：
```oml
safe_html = read(user_input) | html_escape ;
# 输入："<script>alert('xss')</script>"
# 输出："&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
```

---

### html_unescape

将 HTML 实体还原为原始字符。

**语法**：
```oml
| html_unescape
```

**参数**：无

**输入类型**：`chars`
**输出类型**：`chars`

**示例**：
```oml
original = read(escaped_html) | html_unescape ;
# 输入："&lt;div&gt;Hello&lt;/div&gt;"
# 输出："<div>Hello</div>"
```

---

### json_escape

对 JSON 字符串中的特殊字符进行转义。

**语法**：
```oml
| json_escape
```

**参数**：无

**输入类型**：`chars`
**输出类型**：`chars`

**示例**：
```oml
json_safe = read(text) | json_escape ;
# 转义引号、反斜杠、换行符等 JSON 特殊字符
```

---

### json_unescape

将 JSON 转义序列还原为原始字符。

**语法**：
```oml
| json_unescape
```

**参数**：无

**输入类型**：`chars`
**输出类型**：`chars`

**示例**：
```oml
original = read(escaped_json) | json_unescape ;
# 还原 \n、\t、\"等转义序列
```

---

### str_escape

对字符串中的特殊字符进行转义（主要是引号和反斜杠）。

**语法**：
```oml
| str_escape
```

**参数**：无

**输入类型**：`chars`
**输出类型**：`chars`

**示例**：
```oml
escaped = read(raw_string) | str_escape ;
# 输入：'hello"world'
# 输出：'hello\"world'
```

---

## 时间函数

### Time::to_ts

将时间转换为 Unix 时间戳（秒），使用 UTC+8 时区。

**语法**：
```oml
| Time::to_ts
```

**参数**：无

**输入类型**：`time`
**输出类型**：`digit`

**示例**：
```oml
timestamp = read(occur_time) | Time::to_ts ;
# 输入：2024-01-15 14:30:00
# 输出：1705304400（UTC+8）
```

---

### Time::to_ts_ms

将时间转换为 Unix 时间戳（毫秒），使用 UTC+8 时区。

**语法**：
```oml
| Time::to_ts_ms
```

**参数**：无

**输入类型**：`time`
**输出类型**：`digit`

**示例**：
```oml
timestamp_ms = read(occur_time) | Time::to_ts_ms ;
# 输入：2024-01-15 14:30:00
# 输出：1705304400000
```

---

### Time::to_ts_us

将时间转换为 Unix 时间戳（微秒），使用 UTC+8 时区。

**语法**：
```oml
| Time::to_ts_us
```

**参数**：无

**输入类型**：`time`
**输出类型**：`digit`

**示例**：
```oml
timestamp_us = read(occur_time) | Time::to_ts_us ;
# 输入：2024-01-15 14:30:00
# 输出：1705304400000000
```

---

### Time::to_ts_zone

将时间转换为指定时区的 Unix 时间戳。

**语法**：
```oml
| Time::to_ts_zone(<timezone_offset>, <unit>)
```

**参数**：
- `timezone_offset`：时区偏移（小时）
  - `0`：UTC
  - `8`：UTC+8（北京时间）
  - `-5`：UTC-5（美东时间）
- `unit`：时间戳单位
  - `s` 或 `ss`：秒
  - `ms`：毫秒
  - `us`：微秒

**输入类型**：`time`
**输出类型**：`digit`

**示例**：
```oml
# UTC 时间戳（秒）
utc_ts = read(occur_time) | Time::to_ts_zone(0, s) ;

# UTC+8 时间戳（毫秒）
beijing_ts_ms = read(occur_time) | Time::to_ts_zone(8, ms) ;

# UTC-5 时间戳（秒）
eastern_ts = read(occur_time) | Time::to_ts_zone(-5, ss) ;

# UTC 时间戳（微秒）
utc_ts_us = read(occur_time) | Time::to_ts_zone(0, us) ;
```

---

## 数据访问函数

### nth

获取数组中指定索引的元素。

**语法**：
```oml
| nth(<index>)
```

**参数**：
- `index`：数组索引（从 0 开始）

**输入类型**：`array`
**输出类型**：元素类型

**示例**：
```oml
first_item = read(items) | nth(0) ;
second_item = read(items) | nth(1) ;
# 输入：[10, 20, 30]
# nth(0) 输出：10
# nth(1) 输出：20
```

---

### get

获取对象中指定键的值。

**语法**：
```oml
| get(<key>)
```

**参数**：
- `key`：对象的字段名

**输入类型**：`obj`
**输出类型**：字段值类型

**示例**：
```oml
# 获取对象的字段
name = read(user) | get(name) ;

# 链式调用
first_name = read(users) | nth(0) | get(name) ;
# 输入：[{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
# 输出："John"
```

---

### path

从文件路径中提取指定部分。

**语法**：
```oml
| path(<part>)
```

**参数**：
- `part`：要提取的部分
  - `name`：文件名（含扩展名）
  - `path`：目录路径

**输入类型**：`chars`
**输出类型**：`chars`

**示例**：
```oml
# 输入："C:\Users\test\file.txt"
filename = read(file_path) | path(name) ;
# 输出："file.txt"

parent = read(file_path) | path(path) ;
# 输出："C:/Users/test"
```

---

### url

从 URL 中提取指定部分。

**语法**：
```oml
| url(<part>)
```

**参数**：
- `part`：要提取的部分
  - `domain`：域名（不含端口）
  - `host`：主机（含端口）
  - `path`：路径
  - `uri`：完整 URI（路径 + 查询 + 片段）
  - `params`：查询参数

**输入类型**：`chars`
**输出类型**：`chars`

**示例**：
```oml
# 输入："https://api.example.com:8080/v1/users?id=1&type=admin#section"

domain = read(http_url) | url(domain) ;
# 输出："api.example.com"

host = read(http_url) | url(host) ;
# 输出："api.example.com:8080"

path = read(http_url) | url(path) ;
# 输出："/v1/users"

uri = read(http_url) | url(uri) ;
# 输出："/v1/users?id=1&type=admin#section"

params = read(http_url) | url(params) ;
# 输出："id=1&type=admin"
```

---

### sxf_get

从特殊格式的文本中提取字段值。

**语法**：
```oml
| sxf_get(<field_name>)
```

**参数**：
- `field_name`：要提取的字段名

**输入类型**：`chars`
**输出类型**：`chars`

**示例**：
```oml
# 从格式化文本中提取字段
status = read(log_line) | sxf_get(statusCode) ;
username = read(log_line) | sxf_get(username) ;
```

---

## 转换函数

### to_str

将值转换为字符串。

**语法**：
```oml
| to_str
```

**参数**：无

**输入类型**：任意类型
**输出类型**：`chars`

**示例**：
```oml
ip_str = read(src_ip) | to_str ;
# 输入：192.168.1.100（IP 类型）
# 输出："192.168.1.100"

num_str = read(count) | to_str ;
# 输入：42（digit 类型）
# 输出："42"
```

---

### to_json

将值转换为 JSON 字符串。

**语法**：
```oml
| to_json
```

**参数**：无

**输入类型**：任意类型
**输出类型**：`chars`

**示例**：
```oml
# 数组转 JSON
ports_json = read(ports) | to_json ;
# 输入：[80, 443]
# 输出："[80,443]"

# 对象转 JSON
user_json = read(user) | to_json ;
# 输入：{name: "John", age: 30}
# 输出：'{"name":"John","age":30}'
```

---

### ip4_to_int

将 IPv4 地址转换为整数。

**语法**：
```oml
| ip4_to_int
```

**参数**：无

**输入类型**：`ip` 或 `chars`
**输出类型**：`digit`

**示例**：
```oml
ip_int = read(src_ip) | ip4_to_int ;
# 输入：192.168.1.100
# 输出：3232235876

# 用于 IP 范围比较
ip_int = read(src_ip) | ip4_to_int ;
in_range = match read(ip_int) {
    in (digit(3232235776), digit(3232236031)) => chars(True) ;
    _ => chars(False) ;
} ;
```

---

## 控制函数

### skip_empty

如果输入值为空，则跳过该字段的输出。

**语法**：
```oml
| skip_empty
```

**参数**：无

**输入类型**：任意类型
**输出类型**：原类型或跳过

**何时被视为"空"**：
- 空字符串 `""`
- 空数组 `[]`
- 数值 `0`
- 空对象 `{}`

**示例**：
```oml
# 如果 optional_field 为空，则不输出 result 字段
result = read(optional_field) | skip_empty ;

# 常用于过滤空数组
items = read(items_array) | skip_empty ;
```

---

---

## 下一步

- **[🌟 完整功能示例](./07-complete-example.md)** - 查看所有功能的完整演示
- [实战指南](./03-practical-guide.md) - 查看实际应用场景
- [核心概念](./02-core-concepts.md) - 深入理解函数工作原理
- [快速入门](./01-quickstart.md) - 回顾基础用法
- [语法参考](./06-grammar-reference.md) - 查看完整语法定义
