# WPL 核心概念

本文档帮助你理解 WPL 的设计理念和核心概念，建立正确的思维模型。

---

## 📚 文档导航

### 快速导航

| 主题 | 内容 |
|------|------|
| [**设计理念**](#wpl-设计理念) | 为什么需要 WPL、核心思想、声明式设计 |
| [**类型系统**](#类型系统) | 类型的作用、类型层次、类型组合 |
| [**匹配语义**](#匹配语义) | seq 顺序、alt 择一、opt 可选、some_of 重复 |
| [**管道系统**](#管道系统) | 预处理管道、字段级管道、两者区别 |
| [**子字段与嵌套**](#子字段与嵌套) | JSON 子字段、KV 子字段、数组 |
| [**分隔符优先级**](#分隔符优先级) | 优先级规则、分隔符类型、实际应用 |
| [**设计原则**](#设计原则总结) | 声明式、类型安全、组合性、明确性 |
| [**常见误解**](#常见误解) | WPL vs 正则、字段连续性、格式灵活性 |

---

## WPL 设计理念

### 为什么需要 WPL？

**问题：** 如何从非结构化文本中提取结构化数据？

```
输入（文本）：192.168.1.1 - - [06/Aug/2019:12:12:19 +0800] "GET /index.html" 200
输出（结构）：
  client_ip: 192.168.1.1
  time: 2019-08-06 12:12:19
  request: GET /index.html
  status: 200
```

**传统方法的问题：**
- 正则表达式：难写、难读、难维护
- 手写解析器：代码冗长、容易出错
- 固定格式解析：不够灵活

**WPL 的解决方案：**
- **声明式**：描述"是什么"，而非"怎么做"
- **类型安全**：自动验证和转换
- **组合性**：小的规则组合成复杂规则

---

### 核心思想：规则 = 模式匹配 + 字段提取

```wpl
package demo {
  rule example {
    (ip:client, digit:status, time:ts)
  }
}
```

**这个规则表达：**
1. **模式**：数据格式是"IP 数字 时间"
2. **提取**：提取 3 个字段，分别命名为 client、status、ts
3. **验证**：自动验证 IP 格式、数字格式、时间格式
4. **转换**：自动转换为对应类型

---

## 类型系统

### 类型的作用

类型在 WPL 中有三个作用：

1. **验证**：确保数据符合预期格式
2. **转换**：自动转换为标准格式
3. **语义**：表达数据的含义

**示例：**

```wpl
# 输入：06/Aug/2019:12:12:19 +0800
time/clf:access_time

# 类型 time/clf 做了 3 件事：
# 1. 验证：是否符合 CLF 时间格式
# 2. 转换：转换为标准时间格式 2019-08-06 12:12:19
# 3. 语义：表达"这是访问时间"
```

---

### 类型的层次

```
基础类型 ────→ 结构化类型 ────→ 协议类型
   ↓              ↓               ↓
 digit          json          http/request
 chars           kvarr        http/status
  ip           array          time/clf
 time           obj
```

**基础类型**：原子数据
- `digit` - 整数
- `chars` - 字符串
- `ip` - IP 地址
- `time` - 时间

**结构化类型**：复合数据
- `json` - JSON 对象（包含多个字段）
- `kvarr` - 键值对
- `array` - 数组

**协议类型**：领域特定格式
- `http/request` - HTTP 请求行
- `http/status` - HTTP 状态码
- `time/clf` - CLF 时间格式

---

### 类型组合示例

```wpl
# 简单组合
(digit, ip, time)

# 嵌套组合
(digit, json(chars@name, digit@age), time)

# 数组组合
array/digit              # 数字数组
array/array/chars        # 二维字符串数组
```

---

## 匹配语义

WPL 提供 4 种匹配语义，满足不同场景需求。

### seq（顺序匹配）- 默认

**语义**：按顺序依次匹配每个字段

```wpl
# 显式写法
seq(ip, digit, time)

# 隐式写法（默认）
(ip, digit, time)
```

**匹配过程：**
```
输入：192.168.1.1 200 2023-01-01
      ↓           ↓   ↓
     ip         digit time
```

**何时使用：** 字段顺序固定（90% 的场景）

---

### alt（择一匹配）

**语义**：尝试多种类型，匹配其中一个

```wpl
alt(ip, digit)
```

**匹配过程：**
```
输入：192.168.1.1
尝试：ip ✓ → 成功，返回 ip
      digit ✗ → 不尝试

输入：12345
尝试：ip ✗ → 失败
      digit ✓ → 成功，返回 digit
```

**何时使用：** 同一位置可能是不同类型

**示例场景：**
```wpl
# 日志中 user_id 可能是数字或字符串
(time), alt(digit:user_id, chars:user_id), (chars:action)
```

---

### opt（可选匹配）

**语义**：分组可选，失败不报错

```wpl
opt(chars:tag)
```

**匹配过程：**
```
输入：有内容 → 尝试匹配，成功则提取
输入：无内容 → 跳过，继续下一个字段
```

**何时使用：** 某个分组可能不存在

**示例场景：**
```wpl
# HTTP 日志中 referer 分组可能不存在
(ip, time, http/request, digit), opt(chars:referer")
```

---

### some_of（尽可能多）

**语义**：循环匹配，尽可能多地消费字段

```wpl
some_of(kvarr, ip, digit)
```

**匹配过程：**
```
输入：k1=v1 192.168.1.1 200 k2=v2 300

循环 1：尝试 kvarr ✓ → 提取 k1=v1
循环 2：尝试 kvarr ✗, 尝试 ip ✓ → 提取 192.168.1.1
循环 3：尝试 kvarr ✗, 尝试 ip ✗, 尝试 digit ✓ → 提取 200
循环 4：尝试 kvarr ✓ → 提取 k2=v2
循环 5：尝试 kvarr ✗, 尝试 ip ✗, 尝试 digit ✓ → 提取 300
循环 6：全部失败 → 停止
```

**何时使用：** 不确定数量和顺序的混合字段

---

### 匹配语义对比

| 语义 | 用途 | 示例 | 匹配次数 |
|------|------|------|---------|
| `seq` | 顺序固定 | `(ip, digit, time)` | 每个字段 1 次 |
| `alt` | 类型不定 | `alt(ip, digit)` | 其中 1 个 |
| `opt` | 可选分组 | `opt(chars:tag)` | 0 或 1 次 |
| `some_of` | 混合重复 | `some_of(kvarr, ip)` | 尽可能多 |

---

## 管道系统

WPL 的管道系统分为两层：**预处理管道**（整行级）和**字段级管道**（字段级）。

### 预处理管道（整行级）

**语法：**
```wpl
|step1|step2|
(字段列表)
```

**作用域：** 整行原始输入

**执行时机：** 在字段解析之前

**常用场景：**
```wpl
# Base64 解码
|decode/base64|
(json)

# 多步处理
|decode/base64|unquote/unescape|
(json(chars@path))
```

**为什么需要预处理管道？**
- 某些日志整行都是 Base64 编码（如华为防火墙）
- 需要先解码，才能进行字段解析
- 预处理一次，所有字段都受益

---

### 字段级管道（字段级）

**语法：**
```wpl
(fields) |function1| |function2|
```

**作用域：** 解析后的字段集合

**执行时机：** 在字段解析之后

**常用场景：**
```wpl
# 验证字段
(json |f_has(status) |f_digit_in(status, [200, 201]))

# 转换字段
(json(chars@message) |take(message) |json_unescape())
```

**为什么需要字段级管道？**
- 需要验证某个字段是否存在
- 需要验证字段值是否符合条件
- 需要对特定字段进行转换

---

### 两种管道的区别

| 特性 | 预处理管道 | 字段级管道 |
|------|-----------|-----------|
| 作用域 | 整行输入 | 解析后字段 |
| 执行时机 | 解析前 | 解析后 |
| 语法 | `\|step\|` | `\|function()\|` |
| 典型用途 | 解码、反转义 | 验证、转换 |

**示例对比：**
```wpl
# 预处理管道：整行 Base64 解码
|decode/base64|
(json(chars@user))

# 字段级管道：单字段 Base64 解码
(json(chars@payload) |take(payload) |base64_decode())
```

---

## 子字段与嵌套

### 为什么需要子字段？

**问题：** JSON/KV 等结构化数据包含多个字段，如何提取？

```json
{"user":"admin","code":200,"data":{"result":"ok"}}
```

**解决方案：** 使用子字段语法

```wpl
json(
  chars@user,              # 提取 user 字段
  digit@code,              # 提取 code 字段
  chars@data/result        # 提取 data.result 字段
)
```

---

### JSON 子字段

**基本语法：**
```wpl
json(type@key, type@key, ...)
```

**示例：**
```wpl
# 提取指定字段
json(chars@name, digit@age)

# 嵌套路径
json(chars@user/name, digit@user/age)

# 可选字段
json(chars@name, opt(chars)@email)
```

**输入：**
```json
{"user":{"name":"Alice","age":25},"status":"active"}
```

**输出：**
```
user/name: Alice
user/age: 25
status: active
```

---

### KV 子字段

**基本语法：**
```wpl
kvarr(type@key, type@key, ...)
```

**示例：**
```wpl
kvarr(chars@hostname, digit@port, opt(chars)@user)
```

**输入：**
```
hostname=server1 port=3306 user=root
```

**输出：**
```
hostname: server1
port: 3306
user: root
```

---

### 数组

**基本语法：**
```wpl
array[/subtype]
```

**示例：**
```wpl
array/digit:nums          # [1,2,3] → nums/[0]=1, nums/[1]=2, nums/[2]=3
array/chars:items         # ["a","b"] → items/[0]="a", items/[1]="b"
array/array/digit         # [[1,2],[3,4]] → 嵌套数组
```

---

## 分隔符优先级

### 为什么需要优先级？

**问题：** 不同来源的分隔符可能冲突

```wpl
# 字段级分隔符
digit\,

# 组级分隔符
(digit, ip)\;

# 上游分隔符（来自 json/kvarr 等）
```

**解决方案：** 定义优先级规则

---

### 优先级规则

```
字段级(3) > 组级(2) > 上游(1)
```

**示例：**
```wpl
# 字段级覆盖组级
(digit\;, ip, chars)\,
# digit 用分号，ip 和 chars 用逗号

# 组级覆盖上游
json(...) (digit, ip)\;
# 即使 json 内部默认空格，组级分号生效
```

---

### 分隔符类型

| 分隔符 | 写法 | 说明 |
|--------|------|------|
| 逗号 | `\,` | 最常用 |
| 分号 | `\;` | 常用于 KV |
| 空格 | `\s` | 默认 |
| 冒号 | `\:` | 键值分隔 |
| 行尾 | `\0` | 读到行尾 |

---

### 实际应用

**场景 1：不同字段不同分隔符**
```wpl
(digit\;, ip\,, chars\s)
# digit 用分号，ip 用逗号，chars 用空格
```

**场景 2：组级统一分隔符**
```wpl
(digit, ip, time)\,
# 所有字段都用逗号
```

**场景 3：最后一个字段读到行尾**
```wpl
(digit, ip, chars\0)
# chars 读取所有剩余内容
```

---

## 设计原则总结

### 1. 声明式优于命令式

```wpl
# WPL（声明式）
(ip, digit, time)

# 命令式伪代码
ip = parse_ip(input)
digit = parse_digit(input)
time = parse_time(input)
```

---

### 2. 类型安全优于字符串匹配

```wpl
# 带类型验证
ip:client_ip              # 自动验证 IP 格式

# 纯字符串
chars:client_ip           # 不验证格式
```

---

### 3. 组合优于重复

```wpl
# 可组合
rule base_fields { (ip, time) }
rule extended { (ip, time, json) }   # 复用基础部分

# 不可组合
rule log1 { (ip, time, chars) }
rule log2 { (ip, time, json) }       # 重复 ip, time
```

---

### 4. 明确优于隐含

```wpl
# 明确指定
time/clf:access_time<[,]>

# 隐含（可能失败）
time:access_time
```

---

## 常见误解

### 误解 1：WPL 是正则表达式

**错误认知：** WPL 和正则表达式类似

**正确理解：** WPL 是类型化的模式匹配语言
- 正则：字符级匹配
- WPL：类型级匹配 + 验证 + 转换

---

### 误解 2：所有字段必须连续

**错误认知：** 字段之间不能有空隙

**正确理解：** 使用 `_` 跳过不需要的字段
```wpl
(ip, 3*_, time)           # 跳过 3 个字段
```

---

### 误解 3：只能解析固定格式

**错误认知：** WPL 只能解析固定格式的数据

**正确理解：** 支持可选、重复、择一等灵活模式
```wpl
opt(chars:tag)            # 单字段可选分组
kvarr                     # 自动解析 KV
alt(ip:addr, digit:id)    # 择一分组
```

---

## 下一步

### 实战应用
→ [03-practical-guide.md](./03-practical-guide.md) - 按任务查找解决方案

**你将学到：**
- 解析各种 Web 服务器日志
- 处理 JSON 和 KV 数据
- 使用预处理管道
- 字段验证与过滤
- 复杂场景处理

---

### 深入参考
→ [04-language-reference.md](./04-language-reference.md) - 完整类型和语法
→ [05-functions-reference.md](./05-functions-reference.md) - 所有函数详解

---

## 相关资源

- 快速入门：[01-quickstart.md](./01-quickstart.md)
- 实战指南：[03-practical-guide.md](./03-practical-guide.md)
- 语言参考：[04-language-reference.md](./04-language-reference.md)
