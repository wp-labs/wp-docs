# WPL 语言参考

本文档提供 WPL 的完整语言元素参考，用于快速查阅类型、语法和结构。

---

## 📑 文档导航

| 章节 | 说明 |
|------|------|
| [类型系统](#-类型系统) | 所有数据类型速查表 |
| [语法元素](#-语法元素) | 基本结构、字段定义、格式控制 |
| [子字段语法](#-子字段语法) | JSON、KV、数组子字段 |
| [注解](#-注解) | tag、copy_raw 注解 |
| [语法速查](#-语法速查) | 常用模式快速参考 |

---

## 📋 类型系统

### 基础类型

| # | 类型 | 标识符 | 样例 | 说明 |
|---|------|--------|------|------|
| 1 | 预读符号 | `peek_symbol(xxx)` | `peek_symbol(GET)` | 预读但不消费 |
| 2 | 忽略 | `_` | `_`, `2*_`, `3*_` | 忽略该字段 |
| 3 | 符号 | `symbol(xxx)` | `symbol(HTTP)` | 精确匹配 |
| 4 | 布尔 | `bool` | `true`, `false` | 布尔值 |
| 5 | 字符串 | `chars` | `"hello"` | 任意字符串 |
| 6 | 整数 | `digit` | `123`, `8080` | 整数 |
| 7 | 浮点 | `float` | `3.14`, `0.01` | 浮点数 |
| 8 | 序列号 | `sn` | `ABC123XYZ` | 自动生成序列号 |

### 时间类型

| # | 类型 | 标识符 | 样例 | 说明 |
|---|------|--------|------|------|
| 9 | 通用时间 | `time` | `2023-05-15 07:09:12` | 自动识别多种格式 |
| 10 | ISO 8601 | `time_iso` | `2023-05-15T07:09:12Z` | ISO 8601 标准 |
| 11 | RFC 3339 | `time_3339` | `2022-03-21T12:34:56+00:00` | RFC3339 标准 |
| 12 | RFC 2822 | `time_2822` | `Mon, 07 Jul 2025 09:20:32 +0000` | 邮件时间格式 |
| 13 | CLF 时间 | `time/clf` | `06/Aug/2019:12:12:19 +0800` | Apache/Nginx 日志 |
| 14 | Unix时间戳 | `time_timestamp` | `1647849600` | Unix 秒级时间戳 |

### 网络类型

| # | 类型 | 标识符 | 样例 | 说明 |
|---|------|--------|------|------|
| 15 | IP地址 | `ip` | `192.168.1.100`, `::1` | IPv4/IPv6 地址 |
| 16 | IP网段 | `ip_net` | `192.168.0.0/24` | CIDR 网段 |
| 17 | 域名 | `domain` | `example.com` | 域名 |
| 18 | 邮箱 | `email` | `user@example.com` | 邮箱地址 |
| 19 | 端口 | `port` | `8080`, `443` | 端口号 |
| 20 | URL | `url` | `http://example.com/path` | 完整 URL |

### 编码类型

| # | 类型 | 标识符 | 样例 | 说明 |
|---|------|--------|------|------|
| 21 | 十六进制 | `hex` | `48656c6c6f` | 十六进制数据 |
| 22 | Base64 | `base64` | `aGVsbG8=` | Base64 编码 |

### 结构化类型

| # | 类型 | 标识符 | 样例 | 说明 |
|---|------|--------|------|------|
| 23 | 键值对 | `kvarr` | `key=value` | KV 格式 |
| 24 | JSON | `json` | `{"k":"v"}` | JSON 对象 |
| 25 | 严格JSON | `exact_json` | `{"k":"v"}` | 严格验证 JSON |
| 26 | 对象 | `obj` | 嵌套对象 | 通用对象 |
| 27 | 数组 | `array` | `[1,2,3]` | 数组 |
| 28 | 数字数组 | `array/digit` | `[1,2,3]` | 数字数组 |
| 29 | 字符串数组 | `array/chars` | `["a","b"]` | 字符串数组 |

### 协议类型

| # | 类型 | 标识符 | 样例 | 说明 |
|---|------|--------|------|------|
| 30 | HTTP请求 | `http/request` | `GET /path HTTP/1.1` | HTTP 请求行 |
| 31 | HTTP状态 | `http/status` | `200`, `404` | HTTP 状态码 |
| 32 | User-Agent | `http/agent` | `Mozilla/5.0...` | 浏览器 UA |
| 33 | HTTP方法 | `http/method` | `GET`, `POST` | HTTP 方法 |

### 特殊类型

| # | 类型 | 标识符 | 样例 | 说明 |
|---|------|--------|------|------|
| 34 | 身份证 | `id_card` | `110101199001011234` | 18 位身份证 |
| 35 | 手机号 | `mobile_phone` | `13800138000` | 11 位手机号 |
| 36 | 协议文本 | `proto_text` | 协议格式 | 协议文本解析 |
| 37 | 自动识别 | `auto` | 自动推断 | 自动类型推断 |

---

## 🔧 语法元素

### 基本结构

```wpl
package 包名 {
  rule 规则名 {
    |预处理管道|
    (字段列表)
  }
}
```

### 字段定义完整语法

```
[N*] DataType [ (symbol) ] [ (subfields) ] [:name] [ [len] ] [ format ] [ sep ] { | pipe }
```

| 部分 | 说明 | 示例 |
|------|------|------|
| `[N*]` | 重复计数 | `kvarr`, `3*ip` |
| `DataType` | 数据类型 | `digit`, `ip`, `json` |
| `(symbol)` | 符号内容 | `symbol(GET)` |
| `(subfields)` | 子字段列表 | `json(chars@name)` |
| `:name` | 字段命名 | `:status`, `:client_ip` |
| `[len]` | 长度限制 | `[100]` |
| `format` | 格式控制 | `<[,]>`, `"`, `^10` |
| `sep` | 分隔符 | `\,`, `\;`, `\0` |
| `\| pipe` | 管道函数 | `\|f_has(name)\|` |

### 格式控制

| 格式 | 语法 | 示例 | 说明 |
|------|------|------|------|
| 范围定界 | `<beg,end>` | `<[,]>`, `<{,}>` | 起止符号 |
| 引号 | `"` | `chars"` | 引号包裹 |
| 字符计数 | `N*` | `10*chars`, `5*_` | 按字符数 |

### 分组元信息

| 元信息 | 说明 | 示例 | 匹配行为 |
|--------|------|------|---------|
| `seq` | 顺序匹配（默认） | `seq(ip, digit, time)` | 按顺序依次匹配 |
| `alt` | 择一匹配 | `alt(ip, digit)` | 匹配其中一个 |
| `opt` | 可选匹配 | `opt(chars:tag)` | 分组失败不报错 |
| `some_of` | 尽可能多 | `some_of(ip, digit)` | 循环匹配 |

### 分隔符优先级

```
字段级(3) > 组级(2) > 上游(1)
```

| 分隔符 | 写法 | 说明 | 优先级 |
|--------|------|------|--------|
| 逗号 | `\,` | 逗号分隔 | 字段级 (3) |
| 分号 | `\;` | 分号分隔 | 字段级 (3) |
| 冒号 | `\:` | 冒号分隔 | 字段级 (3) |
| 空格 | `\s` | 空格分隔 | 字段级 (3) |
| 行尾 | `\0` | 读到行尾 | 字段级 (3) |
| 组分隔 | `(...)\sep` | 组级分隔 | 组级 (2) |
| 默认 | 无 | 继承上游 | 上游 (1) |

---

## 🎯 子字段语法

### JSON 子字段

```wpl
json(type@key, type@key, ...)
```

**示例：**
```wpl
# 基本提取
json(chars@name, digit@age)

# 嵌套路径
json(chars@user/name, digit@user/age)

# 可选字段
json(chars@name, opt(chars)@email)
```

### KV 子字段

```wpl
kvarr(type@key, type@key, ...)
```

**示例：**
```wpl
kvarr(chars@hostname, digit@port, opt(chars)@user)
```

### 数组

```wpl
array[/subtype]
```

**示例：**
```wpl
array/digit:nums          # [1,2,3]
array/chars:items         # ["a","b"]
array/array/digit         # 嵌套数组
```

---

## 📝 注解

### tag 注解

```wpl
#[tag(key1:"value1", key2:"value2")]
package demo {
  rule x { (digit, time) }
}
```

### copy_raw 注解

```wpl
#[copy_raw(name:"raw_log")]
rule nginx_log {
  (ip, time, chars)
}
```

### 原始字符串（避免转义）

```wpl
#[tag(path:r#"C:\Program Files\App"#)]
package demo {
  rule x { (digit) }
}
```

---

## 💡 语法速查

### 常用模式

```wpl
# 字段命名
type:name              # digit:status

# 忽略字段
_                      # 忽略 1 个
N*_                    # 忽略 N 个

# 重复模式
kvarr                  # 自动解析KV
N*ip                   # 固定 N 次

# 可选分组
opt(chars:tag)         # 单个可选分组
opt(kvarr)             # 可选 KV 分组

# 格式控制
<[,]>                  # 方括号包裹
"                      # 引号包裹
^10                    # 固定 10 字符

# 分隔符
\,                     # 逗号
\;                     # 分号
\0                     # 行尾

# 子字段
json(chars@key)        # JSON 字段
kvarr(digit@port)      # KV 字段
@path/to/field         # 嵌套路径
```

---

## 相关文档

- 快速入门：[01-quickstart.md](./01-quickstart.md)
- 核心概念：[02-core-concepts.md](./02-core-concepts.md)
- 实战指南：[03-practical-guide.md](./03-practical-guide.md)
- 函数参考：[05-functions-reference.md](./05-functions-reference.md)
- 语法规范：[06-grammar-reference.md](./06-grammar-reference.md)
