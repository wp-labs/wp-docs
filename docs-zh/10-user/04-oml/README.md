# OML 对象模型语言

OML (Object Modeling Language) 是 Warp Parse 使用的数据转换语言，用于对 WPL 解析后的结构化数据进行转换、聚合和富化。

---

## 📚 文档导航

### 按学习路径

```
🆕 新手入门
   ↓
01-quickstart.md ────────→ 5分钟上手，复制即用
   ↓
07-complete-example.md ──→ 🌟 完整功能演示（强烈推荐）
   ↓
02-core-concepts.md ─────→ 理解设计理念和核心概念
   ↓
03-practical-guide.md ───→ 按任务查找解决方案
   ↓
04-functions-reference.md → 查阅函数
   ↓
05-integration.md ───────→ 集成到数据流
```

### 按用户角色

| 我是... | 推荐阅读 |
|---------|---------|
| **OML 新手** | [01-quickstart.md](./01-quickstart.md) → [07-complete-example.md](./07-complete-example.md) |
| **日常使用者** | [03-practical-guide.md](./03-practical-guide.md) - 按任务查找 |
| **开发者/集成** | [07-complete-example.md](./07-complete-example.md) + [04-functions-reference.md](./04-functions-reference.md) |
| **系统集成** | [05-integration.md](./05-integration.md) - WPL/OML/Sink 关联 |

### 按任务查找

| 我想... | 查看文档 |
|---------|---------|
| 🚀 快速上手 | [01-quickstart.md](./01-quickstart.md) |
| 🌟 查看完整示例 | [07-complete-example.md](./07-complete-example.md) |
| 💡 理解概念 | [02-core-concepts.md](./02-core-concepts.md) |
| 📝 提取字段 | [03-practical-guide.md § 数据提取](./03-practical-guide.md#数据提取) |
| 🔄 类型转换 | [03-practical-guide.md § 数据转换](./03-practical-guide.md#数据转换) |
| 🧮 数值计算 | [03-practical-guide.md § 数值计算](./03-practical-guide.md#数值计算) |
| 🔤 忽略大小写匹配 | [functions/match_functions.md](./functions/match_functions.md) |
| 📚 静态字典查表 | [functions/lookup_nocase.md](./functions/lookup_nocase.md) |
| 📦 创建对象/数组 | [03-practical-guide.md § 数据聚合](./03-practical-guide.md#数据聚合) |
| ✅ 条件判断 | [03-practical-guide.md § 条件处理](./03-practical-guide.md#条件处理) |
| 🔍 SQL 查询 | [03-practical-guide.md § 数据富化](./03-practical-guide.md#数据富化-sql-查询) |
| ⚙️ 查某个函数 | [04-functions-reference.md](./04-functions-reference.md) |
| 🔗 集成到流水线 | [05-integration.md](./05-integration.md) |
| 📖 查语法规则 | [06-grammar-reference.md](./06-grammar-reference.md) |

---

## 📖 文档列表

| 文档 | 内容 | 适合人群 |
|------|------|---------|
| [01-quickstart.md](./01-quickstart.md) | 5 分钟快速入门 + 3 个最常用操作 | 所有人 |
| [🌟 07-complete-example.md](./07-complete-example.md) | 完整功能演示（强烈推荐） | 所有人 |
| [02-core-concepts.md](./02-core-concepts.md) | 设计理念 + 类型系统 + 读取语义 | 想深入理解的用户 |
| [03-practical-guide.md](./03-practical-guide.md) | 按任务组织的实战示例 | 日常使用者 |
| [04-functions-reference.md](./04-functions-reference.md) | 所有函数的标准化参考 | 开发者 |
| [05-integration.md](./05-integration.md) | WPL/OML/Sink 集成指南 | 系统集成者 |
| [06-grammar-reference.md](./06-grammar-reference.md) | EBNF 形式化语法定义 | 编译器开发者 |

---

## ⚡ 快速示例

### 基础字段提取

```oml
name : nginx_access
rule : /nginx/access_log
---
user_id = read(user_id) ;
uri = read(request_uri) ;
status : digit = read(status) ;
```

### 数据聚合

```oml
name : system_metrics
rule : /system/metrics
---
metrics : obj = object {
    hostname : chars = read(hostname) ;
    cpu : float = read(cpu_usage) ;
    memory : float = read(mem_usage) ;
} ;
```

### 条件处理

```oml
name : log_classifier
rule : /app/logs
---
level = match read(status_code) {
    in (digit(200), digit(299)) => chars(success) ;
    in (digit(400), digit(499)) => chars(client_error) ;
    in (digit(500), digit(599)) => chars(server_error) ;
    _ => chars(unknown) ;
} ;
```

### 管道转换

```oml
name : data_transform
rule : /data/raw
---
# 时间转时间戳
ts = read(event_time) | Time::to_ts_zone(0, ms) ;

# URL 解析
domain = read(url) | url(domain) ;
path = read(url) | url(path) ;

# Base64 解码
decoded = read(base64_data) | base64_decode(Utf8) ;
```

### 数值计算

```oml
name : risk_score
rule : /system/metrics
---
risk_score : float = calc(read(cpu) * 0.7 + read(mem) * 0.3) ;
error_pct  : digit = calc(round((read(err_cnt) * 100) / read(total_cnt))) ;
bucket     : digit = calc(read(uid) % 16) ;
```

### 忽略大小写匹配

```oml
name : status_class
rule : /app/status
---
status_class = match read(status) {
    iequals_any('success', 'ok', 'done') => chars(good) ;
    iequals_any('error', 'failed', 'timeout') => chars(bad) ;
    _ => chars(other) ;
} ;
```

### 静态字典查表

```oml
name : status_score
rule : /app/status
---
static {
    score_map = object {
        error = float(90.0);
        warning = float(70.0);
        success = float(20.0);
    };
}

risk_score : float = lookup_nocase(score_map, read(status), 40.0) ;
```

### SQL 数据富化

```oml
name : user_enrichment
rule : /app/user_activity
---
user_id = read(user_id) ;

# 从数据库查询用户信息
user_name, user_level =
    select name, level
    from users
    where id = read(user_id) ;
```

更多示例请查看：[🌟 完整功能示例](./07-complete-example.md) 和 [实战指南](./03-practical-guide.md)

---

## 🎯 核心特性

- **声明式**：描述"想要什么"，而非"怎么做"
- **类型安全**：8 种数据类型，自动推断或显式声明
- **WPL 关联**：通过 `rule` 字段匹配 WPL 解析规则
- **读取模式**：read（非破坏性）vs take（破坏性）
- **强大的管道**：链式转换（时间/编解码/URL 解析等）
- **条件匹配**：match 表达式支持范围、否定、多源匹配、OR 条件
- **数值表达式**：`calc(...)` 支持 `+ - * / %` 与 `abs/round/floor/ceil`
- **忽略大小写匹配**：`iequals` / `iequals_any(...)` 用于字符串状态归类
- **静态字典查表**：`lookup_nocase(...)` 支持对 `static` object 做忽略大小写查表
- **数据聚合**：object（对象）和 collect（数组）
- **SQL 集成**：直接查询数据库进行数据富化

---

## 🔗 WPL 与 OML 关联

OML 通过 `rule` 字段与 WPL 的 `package/rule` 建立关联：

```
原始数据
    ↓
[WPL 解析] → 生成结构化数据 + rule 标识
    ↓
数据携带: rule = "/nginx/access_log"
    ↓
[查找匹配的 OML] → 匹配 rule 字段
    ↓
[执行 OML 转换]
    ↓
[输出到 Sink]
```

**示例**：

WPL 规则：
```wpl
package nginx {
    rule access_log {
        (ip:client_ip, chars:uri, digit:status)
    }
}
```

OML 配置：
```oml
name : nginx_handler
rule : /nginx/access_log    # 匹配 WPL 的 package/rule
---
client : ip = read(client_ip) ;
uri : chars = read(uri) ;
status : digit = read(status) ;
```

---

## 💬 快速帮助

### 常见问题

**Q: 从哪里开始学习？**
A: 从 [01-quickstart.md](./01-quickstart.md) 开始，然后查看 [🌟 完整功能示例](./07-complete-example.md)。

**Q: 如何将 OML 与 WPL 关联？**
A: 使用 `rule` 字段匹配 WPL 的 `package/rule` 值，详见 [05-integration.md](./05-integration.md)。

**Q: read 和 take 有什么区别？**
A: `read` 是非破坏性的（可重复读取），`take` 是破坏性的（读取后移除），详见 [02-core-concepts.md](./02-core-concepts.md#读取语义read-vs-take)。

**Q: 某个函数怎么用？**
A: 查看 [04-functions-reference.md](./04-functions-reference.md) 或 [🌟 完整功能示例](./07-complete-example.md)。

**Q: `calc(...)` 失败时会怎样？**
A: 除零、缺失字段、非数值输入、整数溢出、`NaN/inf` 都会返回 `ignore`，详见 [04-functions-reference.md](./04-functions-reference.md) 和 [03-practical-guide.md](./03-practical-guide.md#数值计算)。

**Q: 状态值大小写不稳定，怎么匹配？**
A: 用 `iequals(...)` 或 `iequals_any(...)`，详见 [functions/match_functions.md](./functions/match_functions.md)。

**Q: 想做状态到分值的映射，但不区分大小写？**
A: 用 `static` + `lookup_nocase(...)`，详见 [functions/lookup_nocase.md](./functions/lookup_nocase.md)。

**Q: 如何调试 OML 转换？**
A: 参考 [05-integration.md § 故障排查](./05-integration.md#故障排查)。

---

## 📝 相关文档

- [WPL 规则语言](../03-wpl/README.md) - 数据解析
- [Sink 配置](../05-connectors/02-sinks/README.md) - 数据输出
- [配置指南](../02-config/README.md) - 系统配置

---

**开始学习：** [01-quickstart.md](./01-quickstart.md) - 5分钟快速入门  
**完整示例：** [🌟 07-complete-example.md](./07-complete-example.md) - 所有功能演示
