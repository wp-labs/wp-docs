# WPL 完整类型系统示例

> 一个示例展示 WPL 支持的所有主要数据类型

本文档提供一个完整的、可运行的 WPL 规则示例，展示 23 种主要数据类型的使用方法。这是学习 WPL 类型系统的**最佳参考**。

---

## 📑 文档导航

| 章节 | 说明 |
|------|------|
| [类型覆盖清单](#-类型覆盖清单) | 本示例包含的所有类型 |
| [完整示例](#-完整示例) | 输入数据、WPL 规则、输出结果 |
| [类型详解](#-类型详解) | 每种类型的详细说明 |
| [使用建议](#-使用建议) | 学习路径和实战建议 |
| [快速导航](#-快速导航) | 快速跳转到需要的内容 |

---

## 📋 类型覆盖清单

本示例包含以下类型：

| 类别 | 包含类型 | 数量 |
|------|---------|------|
| **基础类型** | `peek_symbol`、`symbol`、`bool`、`chars`、`digit`、`float`、`_` | 7 |
| **时间类型** | `time_3339`、`time_2822`、`time/clf`、`time_timestamp` | 4 |
| **网络类型** | `ip`、`ip_net`、`port` | 3 |
| **结构化类型** | `kvarr`、`json` | 2 |
| **协议类型** | `http/request`、`http/status`、`http/agent`、`http/method` | 4 |
| **编码类型** | `hex`、`base64` | 2 |
| **特殊类型** | `sn` | 1 |
| **总计** | | **23 种类型** |

---

## 🚀 完整示例

### 输入数据

```
peek_symbol symbol true "hello world" 123 3.14 2026-01-19T12:34:56Z 2022-03-21T12:34:56+00:00 Mon, 07 Jul 2025 09:20:32 +0000 [06/Aug/2019:12:12:19 +0800] 1647849600 192.168.1.100 192.168.0.0/24 name=test {"strict":true} "GET /api/users HTTP/1.1" 200 "Mozilla/5.0" "POST" 8080 ABC123XYZ 0x1A2B YmFzZTY0ZGF0YQ==
```

### WPL 规则

```wpl
package wpl_example {
  rule full_types {
    (
      // 1. peek_symbol - 预读符号（不消费）
      peek_symbol(peek_symbol):peek_sym,

      // 2. symbol - 精确匹配符号
      symbol(symbol):sym,

      // 3. bool - 布尔值
      bool:bool_val,

      // 4. chars - 字符串（带引号）
      chars:quoted_str",

      // 5. digit - 整数
      digit:integer,

      // 6. float - 浮点数
      float:float_val,

      // 7. time_3339 - ISO 8601 / RFC3339
      time_3339:time_iso,

      // 8. time_3339 - RFC3339（带时区）
      time_3339:time_rfc3339,

      // 9. time_2822 - RFC2822（邮件时间格式）
      time_2822:time_rfc2822,

      // 10. time/clf - Common Log Format（Apache/Nginx）
      time/clf:time_clf<[,]>,

      // 11. time_timestamp - Unix 时间戳
      time_timestamp:timestamp,

      // 12. ip - IP 地址
      ip:ip_addr,

      // 13. ip_net - IP 网段（CIDR）
      ip_net:ip_network,

      // 14. kvarr - 键值对
      kvarr(chars@name):kv_data,

      // 15. json - JSON 对象
      json(bool@strict):json_data,

      // 16. http/request - HTTP 请求行
      http/request:http_req",

      // 17. http/status - HTTP 状态码
      http/status:http_status,

      // 18. http/agent - User-Agent
      http/agent:user_agent",

      // 19. http/method - HTTP 方法
      http/method:http_method",

      // 20. port - 端口号
      port:port_num,

      // 21. sn - 序列号
      sn:serial,

      // 22. hex - 十六进制
      hex:hex_data,

      // 23. base64 - Base64 编码
      base64:base64_data
    )
  }
}
```

### 输出结果

```json
{
  "peek_sym": "peek_symbol",
  "sym": "symbol",
  "bool_val": true,
  "quoted_str": "hello world",
  "integer": 123,
  "float_val": 3.14,
  "time_iso": "2026-01-19 12:34:56",
  "time_rfc3339": "2022-03-21 12:34:56",
  "time_rfc2822": "2025-07-07 09:20:32",
  "time_clf": "2019-08-06 12:12:19",
  "timestamp": 1647849600,
  "ip_addr": "192.168.1.100",
  "ip_network": "192.168.0.0/24",
  "kv_data": {"name": "test"},
  "json_data": {"strict": true},
  "http_req": "GET /api/users HTTP/1.1",
  "http_status": 200,
  "user_agent": "Mozilla/5.0",
  "http_method": "POST",
  "port_num": 8080,
  "serial": "ABC123XYZ",
  "hex_data": "0x1A2B",
  "base64_data": "YmFzZTY0ZGF0YQ=="
}
```

---

## 📖 类型详解

### 基础类型

#### 1. peek_symbol - 预读符号
```wpl
peek_symbol(peek_symbol):peek_sym
```
- **作用**：预读匹配但不消费输入
- **用途**：用于向前查看而不影响后续解析

#### 2. symbol - 精确匹配符号
```wpl
symbol(symbol):sym
```
- **作用**：精确匹配指定字符串
- **用途**：匹配固定关键字、分隔符等

#### 3. bool - 布尔值
```wpl
bool:bool_val
```
- **匹配**：`true` 或 `false`
- **输出**：布尔类型

#### 4. chars - 字符串
```wpl
chars:quoted_str"
```
- **格式**：支持引号包裹 `"hello"` 或裸字符串 `hello`
- **用途**：提取任意字符串

#### 5. digit - 整数
```wpl
digit:integer
```
- **匹配**：整数，如 `123`、`-456`
- **输出**：整数类型

#### 6. float - 浮点数
```wpl
float:float_val
```
- **匹配**：浮点数，如 `3.14`、`-0.5`
- **输出**：浮点数类型

---

### 时间类型

#### 7-8. time_3339 - RFC3339/ISO 8601
```wpl
time_3339:time_iso           // 2026-01-19T12:34:56Z
time_3339:time_rfc3339       // 2022-03-21T12:34:56+00:00
```
- **格式**：ISO 8601 / RFC3339 标准
- **支持**：带时区或不带时区

#### 9. time_2822 - RFC2822（邮件时间）
```wpl
time_2822:time_rfc2822
```
- **格式**：`Mon, 07 Jul 2025 09:20:32 +0000`
- **用途**：邮件头、RSS 等

#### 10. time/clf - Common Log Format
```wpl
time/clf:time_clf<[,]>
```
- **格式**：`[06/Aug/2019:12:12:19 +0800]`
- **用途**：Apache/Nginx 日志

#### 11. time_timestamp - Unix 时间戳
```wpl
time_timestamp:timestamp
```
- **格式**：秒级时间戳，如 `1647849600`
- **输出**：时间类型

---

### 网络类型

#### 12. ip - IP 地址
```wpl
ip:ip_addr
```
- **支持**：IPv4（`192.168.1.100`）和 IPv6（`::1`）

#### 13. ip_net - IP 网段
```wpl
ip_net:ip_network
```
- **格式**：CIDR 表示法，如 `192.168.0.0/24`

#### 14. port - 端口号
```wpl
port:port_num
```
- **范围**：1-65535

---

### 结构化类型

#### 15. kvarr - 键值对
```wpl
kvarr(chars@name):kv_data
```
- **格式**：`key=value`
- **支持**：自动解析或指定键提取
- **示例**：`name=test` → `{name: "test"}`

#### 16. json - JSON 对象
```wpl
json(bool@strict):json_data
```
- **支持**：完整 JSON 解析
- **子字段**：可提取嵌套字段
- **示例**：`{"strict":true}` → `{strict: true}`

---

### 协议类型

#### 17. http/request - HTTP 请求行
```wpl
http/request:http_req"
```
- **格式**：`"GET /api/users HTTP/1.1"`
- **提取**：方法 + 路径 + 协议版本

#### 18. http/status - HTTP 状态码
```wpl
http/status:http_status
```
- **格式**：`200`、`404`、`500` 等

#### 19. http/agent - User-Agent
```wpl
http/agent:user_agent"
```
- **格式**：`"Mozilla/5.0..."`
- **用途**：浏览器标识

#### 20. http/method - HTTP 方法
```wpl
http/method:http_method"
```
- **支持**：`GET`、`POST`、`PUT`、`DELETE` 等

---

### 编码类型

#### 21. hex - 十六进制
```wpl
hex:hex_data
```
- **格式**：`0x1A2B` 或 `1A2B`
- **输出**：十六进制字符串

#### 22. base64 - Base64 编码
```wpl
base64:base64_data
```
- **格式**：`YmFzZTY0ZGF0YQ==`
- **输出**：Base64 编码字符串

---

### 特殊类型

#### 23. sn - 序列号
```wpl
sn:serial
```
- **格式**：字母数字组合，如 `ABC123XYZ`
- **用途**：设备序列号、订单号等

---

## 💡 使用建议

### 学习路径

1. **第一步**：先理解基础类型（`digit`、`chars`、`ip`）
2. **第二步**：掌握时间类型（根据日志格式选择）
3. **第三步**：学习结构化类型（`json`、`kvarr`）
4. **第四步**：了解协议类型（`http/*`）

### 实战建议

- **快速查阅**：遇到不认识的数据格式，先在本页面搜索
- **复制即用**：直接复制对应类型的语法到你的规则中
- **类型组合**：多种类型可以自由组合使用

### 常见组合

```wpl
// Web 日志
(ip, time/clf<[,]>, http/request", http/status, digit)

// API 日志
(time_3339, chars, json(chars@user, digit@code))

// 防火墙日志
(ip, port, time, kvarr)
```

---

## 🔗 相关文档

- **快速入门**：[01-quickstart.md](./01-quickstart.md) - 5 分钟上手
- **核心概念**：[02-core-concepts.md](./02-core-concepts.md) - 深入理解类型系统
- **实战指南**：[03-practical-guide.md](./03-practical-guide.md) - 按任务查找解决方案
- **语言参考**：[04-language-reference.md](./04-language-reference.md) - 完整类型列表
- **函数参考**：[05-functions-reference.md](./05-functions-reference.md) - 所有函数详解

---

## 📌 快速导航

| 我想... | 查看章节 |
|---------|---------|
| 查看完整示例代码 | [完整示例](#-完整示例) |
| 了解某个类型详情 | [类型详解](#-类型详解) |
| 学习如何使用 | [使用建议](#-使用建议) |
| 查找常见组合 | [常见组合](#常见组合) |

---

**提示**：将本页面加入书签，作为 WPL 类型系统的速查手册！
