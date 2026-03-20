# OML Functions 函数索引

本文档列出了 `docs/usage/zh/04-oml/functions/` 目录下的函数与专题文档。

## 内置表达式 / 内置函数

| 名称 | 语法 | 说明 | 文档 |
|------|------|------|------|
| `calc(...)` | `calc(expr)` | 显式数值表达式，支持 `+ - * / %` 与 `abs/round/floor/ceil` | [📖 详细文档](./calc.md) |
| `lookup_nocase(...)` | `lookup_nocase(dict, key, default)` | 对 `static` object 做忽略大小写查表 | [📖 详细文档](./lookup_nocase.md) |
| `iequals_any(...)` | `iequals_any(v1, v2, ...)` | 忽略大小写的多候选匹配，用于 `match` 条件 | [📖 详细文档](./match_functions.md) |

## Pipe Functions

以下为可通过管道调用的函数：

## 字段访问函数 (Field Accessors)

| 函数 | 语法 | 说明 | 文档 |
|------|------|------|------|
| `take` | `take(field_name)` | 从输入数据中提取指定字段 | - |
| `get` | `get(key)` | 从嵌套结构中获取指定键的值 | - |
| `nth` | `nth(index)` | 从数组中获取指定索引的元素 | - |

## 字符串匹配函数 (String Matching)

| 函数 | 语法 | 说明 | 文档 |
|------|------|------|------|
| `starts_with` | `starts_with('prefix')` | 检查字符串是否以指定前缀开始，否则转为 ignore | [📖 详细文档](./starts_with.md) |

## 值转换函数 (Value Transformation)

| 函数 | 语法 | 说明 | 文档 |
|------|------|------|------|
| `map_to` | `map_to(value)` | 将非 ignore 字段映射到指定值（支持多种类型） | [📖 详细文档](./map_to.md) |
| `to_str` | `to_str` | 将字段值转换为字符串 | - |
| `to_json` | `to_json` | 将字段值转换为 JSON 字符串 | - |

## 编码/解码函数 (Encoding/Decoding)

| 函数 | 语法 | 说明 | 文档 |
|------|------|------|------|
| `base64_encode` | `base64_encode` | Base64 编码字符串 | - |
| `base64_decode` | `base64_decode(encoding)` | Base64 解码字符串（可指定编码） | - |
| `html_escape` | `html_escape` | HTML 转义字符串 | - |
| `html_unescape` | `html_unescape` | HTML 反转义字符串 | - |
| `json_escape` | `json_escape` | JSON 转义字符串 | - |
| `json_unescape` | `json_unescape` | JSON 反转义字符串 | - |
| `str_escape` | `str_escape` | 通用字符串转义 | - |

## 时间转换函数 (Time Conversion)

| 函数 | 语法 | 说明 | 文档 |
|------|------|------|------|
| `Time::to_ts` | `Time::to_ts` | 将时间转换为秒级时间戳 | - |
| `Time::to_ts_ms` | `Time::to_ts_ms` | 将时间转换为毫秒级时间戳 | - |
| `Time::to_ts_us` | `Time::to_ts_us` | 将时间转换为微秒级时间戳 | - |
| `Time::to_ts_zone` | `Time::to_ts_zone(zone, unit)` | 将时间转换为指定时区的时间戳 | - |

## 网络函数 (Network)

| 函数 | 语法 | 说明 | 文档 |
|------|------|------|------|
| `ip4_to_int` | `ip4_to_int` | 将 IPv4 地址转换为整数 | - |

## URL/路径解析函数 (URL/Path Parsing)

| 函数 | 语法 | 说明 | 文档 |
|------|------|------|------|
| `path` | `path(type)` | 从路径字符串中提取指定部分 | - |
| `url` | `url(type)` | 从 URL 字符串中提取指定部分 | - |

## 控制流函数 (Control Flow)

| 函数 | 语法 | 说明 | 文档 |
|------|------|------|------|
| `skip_empty` | `skip_empty` | 跳过空值字段 | - |

## 函数分类总览

### 按功能分类

#### 1. 数据提取函数
从输入数据或嵌套结构中提取字段。

- `take(field)`: 提取顶层字段
- `get(key)`: 提取嵌套字段
- `nth(index)`: 提取数组元素

#### 2. 条件过滤函数
检查条件，不满足时转换为 ignore。

- `starts_with(prefix)`: 前缀匹配

#### 3. 值映射函数
修改字段值或类型。

- `map_to(value)`: 通用值映射
- `to_str`: 转字符串
- `to_json`: 转 JSON

#### 4. 编码转换函数
在不同编码格式之间转换。

- Base64: `base64_encode`, `base64_decode`
- HTML: `html_escape`, `html_unescape`
- JSON: `json_escape`, `json_unescape`

#### 5. 时间处理函数
处理时间相关的转换。

- 时间戳转换: `Time::to_ts*`
- 时区转换: `Time::to_ts_zone`

#### 6. 网络处理函数
处理网络相关数据。

- IP 地址: `ip4_to_int`
- URL 解析: `url(type)`
- 路径解析: `path(type)`

## 使用示例

### 基本管道

```oml
name : basic_pipeline
---
# 1. 提取字段
result = pipe take(message)
    # 2. 过滤条件
    | starts_with('ERROR')
    # 3. 值映射
    | map_to('error_type');
```

### 复杂转换

```oml
name : complex_transformation
---
# 提取并转换时间
timestamp_ms = pipe take(time_str)
    | Time::to_ts_ms;

# Base64 编码
encoded = pipe take(message)
    | base64_encode;

# URL 解析
host = pipe take(url)
    | url(host);
```

### 条件分类

```oml
name : conditional_classification
---
# 根据 URL 前缀分类安全级别
high_security = pipe take(url)
    | starts_with('https://')
    | map_to(3);

low_security = pipe take(url)
    | starts_with('http://')
    | map_to(1);
```

### 数据清洗

```oml
name : data_cleaning
---
# 提取并清理数据
clean_message = pipe take(raw_message)
    | html_unescape
    | json_unescape
    | skip_empty;
```

## 性能参考

| 函数类型 | 典型性能 | 说明 |
|----------|----------|------|
| 字段访问 | < 100ns | 基于哈希表查找 |
| 字符串匹配 | < 1μs | 简单前缀比较 |
| 值映射 | < 100ns | 直接值替换 |
| Base64 编码 | 1-10μs | 取决于字符串长度 |
| 时间转换 | 1-5μs | 时间解析和转换 |
| URL 解析 | 1-10μs | URL 结构解析 |

## 最佳实践

### 1. 合理使用管道链

```oml
# ✅ 推荐：按逻辑顺序组织管道
result = pipe take(field)
    | starts_with('prefix')  # 先过滤
    | map_to('value');      # 再映射

# ⚠️ 避免：不必要的长管道
result = pipe take(field)
    | to_str
    | to_json
    | to_str  # 冗余操作
```

### 2. 利用 ignore 传播

```oml
# ✅ 推荐：利用 ignore 跳过后续处理
secure_flag = pipe take(url)
    | starts_with('https://')  # 失败返回 ignore
    | map_to(true);           # ignore 会跳过此步

# 这样可以安全地处理条件逻辑
```

### 3. 选择合适的函数

```oml
# ✅ 推荐：使用专用函数
result = pipe take(field) | map_to(123);  # 自动推断为整数

# ⚠️ 不推荐：手动转换
result = pipe take(field) | to_str | map_to('123');  # 额外开销
```

### 4. 避免重复提取

```oml
# ✅ 推荐：一次提取，多次使用
url_field = pipe take(url);
host = pipe take(url) | url(host);
path = pipe take(url) | url(path);

# ⚠️ 避免：每次都提取同一字段（性能影响小但不够清晰）
```

## 函数对比

### starts_with vs 正则表达式

| 特性 | starts_with | 正则表达式 |
|------|------------|------------|
| 性能 | 极快 | 较慢 |
| 功能 | 前缀匹配 | 复杂模式 |
| 使用难度 | 简单 | 需要学习 |
| 失败行为 | 转为 ignore | - |

### map_to vs to_str

| 特性 | map_to | to_str |
|------|--------|--------|
| 功能 | 值替换 | 类型转换 |
| 类型支持 | 多种 | 仅字符串 |
| ignore 保留 | 是 | 否 |
| 用途 | 条件赋值 | 类型转换 |

## 相关文档

- **开发指南**: [OML Pipe Function 开发指南](../../guide/oml_pipefun_development_guide.md)
- **语法参考**: [OML 语法指南](../../syntax/oml_syntax.md)

## 版本历史

- **1.13.4** (2026-02-03)
  - 新增 `starts_with` 函数
  - 新增 `map_to` 函数，支持多种类型自动推断
  - 完善文档体系

- **1.13.3** (2026-02-03)
  - 修复编译错误

- **1.13.2** (2026-02-03)
  - 完善 pipe 函数支持

---

**提示**: OML pipe 函数设计用于数据转换和映射。合理使用 ignore 机制可以实现灵活的条件逻辑。
