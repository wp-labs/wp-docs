# WPL 快速入门

5 分钟上手 WPL，立即解析你的日志数据。

---

## 📚 快速导航

| 主题 | 内容 |
|------|------|
| [**什么是 WPL**](#什么是-wpl) | WPL 简介、核心特点、适用场景 |
| [**完整类型系统**](#-完整类型系统) | 23 种数据类型总览 |
| [**最简示例**](#最简示例nginx-日志) | Nginx 日志解析 |
| [**3 个最常用场景**](#3-个最常用场景) | 空格分隔、JSON、KV 键值对 |
| [**基本语法速览**](#基本语法速览) | 结构、类型、匹配模式 |
| [**常见模式速查**](#常见模式速查) | 引号字段、可选字段、重复字段等 |
| [**快速调试技巧**](#快速调试技巧) | 调试方法 |
| [**实战练习**](#实战练习) | 3 个练习题 |

---

## 什么是 WPL

WPL (Warp Processing Language) 是一种**声明式规则语言**，用于描述如何从日志、消息等文本数据中**提取字段**和**解析结构**。

### 核心特点

- **声明式**：描述"数据是什么"，而非"如何提取"
- **类型安全**：自动验证和转换（IP、时间、JSON 等 37 种类型）
- **强大灵活**：支持 JSON/KV 嵌套提取、Base64 解码、字段验证等
- **易于学习**：5 分钟即可上手基础用法

### 适用场景

- 解析 Web 服务器日志（Nginx、Apache）
- 提取 JSON/KV 结构化数据
- 处理编码数据（Base64、Hex）
- 防火墙、安全设备日志解析
- 自定义日志格式解析

---

## 📚 完整类型系统

**WPL 支持 23 种主要数据类型**，涵盖基础类型、时间、网络、结构化数据、协议和编码等。

👉 **查看完整示例：** [07-complete-types-example.md](./07-complete-types-example.md)

该文档包含：
- ✅ 所有 23 种类型的完整示例代码
- ✅ 可运行的输入数据和 WPL 规则
- ✅ 每种类型的详细说明和使用建议
- ✅ 常见类型组合模式

**快速预览主要类型：**
- **基础**：`digit`、`float`、`chars`、`bool`
- **时间**：`time/clf`、`time_3339`、`time_2822`、`time_timestamp`
- **网络**：`ip`、`ip_net`、`port`、`domain`、`url`
- **结构化**：`json`、`kvarr`、`array`
- **协议**：`http/request`、`http/status`、`http/method`、`http/agent`
- **编码**：`hex`、`base64`

---

## 最简示例：Nginx 日志

**输入数据：**
```
192.168.1.2 - - [06/Aug/2019:12:12:19 +0800] "GET /index.html HTTP/1.1" 200 1024
```

**WPL 规则：**
```wpl
package nginx {
  rule access_log {
    (
      ip:client_ip,
      2*_,
      time/clf:time<[,]>,
      http/request:request",
      digit:status,
      digit:bytes
    )
  }
}
```

**输出结果：**
```
client_ip: 192.168.1.2
time: 2019-08-06 12:12:19
request: GET /index.html HTTP/1.1
status: 200
bytes: 1024
```

**说明：**
- `ip:client_ip` - 提取 IP 地址，命名为 client_ip
- `2*_` - 忽略 2 个字段（两个 `-`）
- `time/clf<[,]>` - 提取方括号包裹的 CLF 时间
- `http/request"` - 提取引号包裹的 HTTP 请求
- `digit` - 提取数字

---

## 3 个最常用场景

### 场景 1：空格分隔的日志

**输入：**
```
200 192.168.1.1 2023-01-01T12:00:00 login_success
```

**WPL：**
```wpl
package demo {
  rule simple_log {
    (digit:code, ip:client, time:ts, chars:action)
  }
}
```

**输出：**
```
code: 200
client: 192.168.1.1
ts: 2023-01-01 12:00:00
action: login_success
```

---

### 场景 2：JSON 数据

**输入：**
```json
{"user":"admin","code":200,"message":"success"}
```

**WPL：**
```wpl
package api {
  rule json_response {
    (json(
      chars@user,
      digit@code,
      chars@message
    ))
  }
}
```

**输出：**
```
user: admin
code: 200
message: success
```

---

### 场景 3：KV 键值对

**输入：**
```
host=server1;port=8080;user=admin;status=online
```

**WPL：**
```wpl
package config {
  rule kv_log {
    (kvarr)
  }
}
```

**输出：**
```
host: server1
port: 8080
user: admin
status: online
```

---

## 基本语法速览

### 结构

```wpl
package 包名 {
  rule 规则名 {
    (字段列表)
  }
}
```

### 常用字段类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `digit` | 整数 | `200`, `8080` |
| `chars` | 字符串 | `"hello"`, `admin` |
| `ip` | IP 地址 | `192.168.1.1` |
| `time` | 时间 | `2023-01-01 12:00:00` |
| `time/clf` | CLF 时间 | `[06/Aug/2019:12:12:19 +0800]` |
| `json` | JSON 对象 | `{"key":"value"}` |
| `kv` | 键值对 | `key=value` |
| `http/request` | HTTP 请求 | `GET /path HTTP/1.1` |
| `http/status` | HTTP 状态码 | `200` |

### 字段命名

```wpl
type:name              # 命名字段
digit:status           # status = 数字
ip:client_ip           # client_ip = IP地址
```

### 忽略字段

```wpl
_                      # 忽略 1 个字段
2*_                    # 忽略 2 个字段
5*_                    # 忽略 5 个字段
```

### 格式控制

```wpl
<[,]>                  # 方括号包裹：[content]
<{,}>                  # 花括号包裹：{content}
"                      # 引号包裹："content"
^N                     # 固定 N 个字符
```

### 重复模式

```wpl
kvarr                  # 自动解析所有KV
3*ip                   # 重复 3 次
12*digit               # 重复 12 次
```

### 子字段提取

```wpl
# JSON 子字段
json(chars@name, digit@age)

# KV 子字段
kvarr(chars@host, digit@port)

# 嵌套字段
json(chars@user/name, digit@user/age)
```

---

## 常见模式速查

### 解析带引号的字段

```wpl
chars":url             # "http://example.com"
http/agent":ua         # "Mozilla/5.0..."
```

### 解析带特殊分隔符的数据

```wpl
# 逗号分隔
(digit, ip, chars)\,

# 分号分隔
(digit, ip, chars)\;

# 字段级分隔符（优先级更高）
digit\,, ip\;, chars\s
```

### 可选分组

```wpl
opt(chars:tag)         # 单字段可选分组
(digit, time), opt(chars:tag)
```

### Base64 解码

```wpl
|decode/base64|
(json(chars@data))
```

---

## 快速调试技巧

### 1. 从简单开始

```wpl
# 第 1 步：最简单
(digit)

# 第 2 步：添加字段
(digit, ip)

# 第 3 步：添加命名
(digit:status, ip:client)

# 第 4 步：添加复杂类型
(digit:status, ip:client, json(chars@name))
```

### 2. 使用 opt() 定位问题

```wpl
# 如果某个部分导致失败，把它拆成独立分组再用 opt 包裹
(digit), opt(ip), (time, chars)
# 如果 ip 解析失败，其他分组仍然可以继续定位问题
```

### 3. 检查分隔符

打印原始数据，确认字段间的分隔符：
```
数据：200,192.168.1.1,admin
分隔符：逗号
规则：(digit, ip, chars)\,
```

---

## 下一步

### 理解概念
→ [02-core-concepts.md](./02-core-concepts.md) - 理解 WPL 的设计理念

**你将学到：**
- 为什么 WPL 这样设计？
- 类型系统的作用
- 匹配语义（seq/alt/opt/some_of）
- 管道系统原理
- 分隔符优先级

---

### 解决实际问题
→ [03-practical-guide.md](./03-practical-guide.md) - 按任务查找解决方案

**你将学到：**
- 解析 Web 服务器日志（Nginx/Apache）
- 解析 JSON 数据（嵌套、反转义）
- 解析 KV 键值对（多种分隔符）
- 处理编码数据（Base64/Hex）
- 字段验证与过滤
- 复杂场景（重复模式、可选字段）

---

### 查阅参考
→ [04-language-reference.md](./04-language-reference.md) - 完整类型和语法参考
→ [05-functions-reference.md](./05-functions-reference.md) - 所有函数参考

---

## 实战练习

### 练习 1：解析自定义日志

**数据：**
```
[2023-01-01 12:00:00] INFO 192.168.1.1 user=admin action=login
```

**提示：**
- 时间在方括号中
- INFO 可以忽略
- 后面是 IP 和 KV

<details>
<summary>查看答案</summary>

```wpl
package practice {
  rule custom_log {
    (
      time:timestamp<[,]>,
      _,
      ip:client,
      kvarr
    )
  }
}
```
</details>

---

### 练习 2：解析嵌套 JSON

**数据：**
```json
{"user":{"name":"Alice","age":25},"status":"active"}
```

**提示：**
- 使用 @path/to/field 提取嵌套字段

<details>
<summary>查看答案</summary>

```wpl
package practice {
  rule nested_json {
    (json(
      chars@user/name,
      digit@user/age,
      chars@status
    ))
  }
}
```
</details>

---

### 练习 3：解析 Base64 编码日志

**数据（Base64）：**
```
eyJ1c2VyIjoiYWRtaW4iLCJjb2RlIjoyMDB9
```

**解码后：**
```json
{"user":"admin","code":200}
```

**提示：**
- 使用 `|decode/base64|` 预处理

<details>
<summary>查看答案</summary>

```wpl
package practice {
  rule base64_log {
    |decode/base64|
    (json(
      chars@user,
      digit@code
    ))
  }
}
```
</details>

---

## 相关资源

- 核心概念：[02-core-concepts.md](./02-core-concepts.md)
- 实战指南：[03-practical-guide.md](./03-practical-guide.md)
- 语言参考：[04-language-reference.md](./04-language-reference.md)
- 函数参考：[05-functions-reference.md](./05-functions-reference.md)
- 语法规范：[06-grammar-reference.md](./06-grammar-reference.md)
