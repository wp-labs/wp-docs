# WPL Rule Language

WPL (Warp Processing Language) is the rule language used by the Warp Parse parsing subsystem (warp-parse) to describe field extraction, protocol parsing, and simple decision logic.

---

## 📚 Documentation Navigation

### By Learning Path

```
🆕 Beginners
   ↓
01-quickstart.md ────→ Get started in 5 minutes, copy and use
   ↓
07-complete-types-example.md ──→ 🌟 Complete feature demo (Highly recommended)
   ↓
02-core-concepts.md ──→ Understand design philosophy and core concepts
   ↓
03-practical-guide.md → Find solutions by task
   ↓
04-language-reference.md → Look up types and syntax
   ↓
05-functions-reference.md → Look up functions
```

### By User Role

| I am... | Recommended Reading |
|---------|---------------------|
| **WPL Beginner** | [01-quickstart.md](./01-quickstart.md) → [02-core-concepts.md](./02-core-concepts.md) |
| **Daily User** | [03-practical-guide.md](./03-practical-guide.md) - Find by task |
| **Developer/Integration** | [04-language-reference.md](./04-language-reference.md) + [05-functions-reference.md](./05-functions-reference.md) |
| **Compiler Developer** | [06-grammar-reference.md](./06-grammar-reference.md) - EBNF grammar |

### Find by Task

| I want to... | See Document |
|--------------|--------------|
| 🚀 Quick start | [01-quickstart.md](./01-quickstart.md) |
| 🎯 **View complete type examples** | **[07-complete-types-example.md](./07-complete-types-example.md)** |
| 💡 Understand concepts | [02-core-concepts.md](./02-core-concepts.md) |
| 📝 Parse Nginx logs | [03-practical-guide.md § 1](./03-practical-guide.md#1-parse-web-server-logs) |
| 📊 Parse JSON data | [03-practical-guide.md § 2](./03-practical-guide.md#2-parse-json-data) |
| 🧩 Distinguish valid vs broken JSON | [04-language-reference.md § JSON-like Routing](./04-language-reference.md#json-like-routing) |
| 🔑 Parse KV pairs | [03-practical-guide.md § 3](./03-practical-guide.md#3-parse-kv-pairs) |
| 🔐 Handle Base64 encoding | [03-practical-guide.md § 4](./03-practical-guide.md#4-handle-encoded-data) |
| ✅ Validate fields | [03-practical-guide.md § 5](./03-practical-guide.md#5-field-validation--filtering) |
| 🔍 Look up a type | [04-language-reference.md § Type System](./04-language-reference.md#-type-system) |
| ⚙️ Look up a function | [05-functions-reference.md](./05-functions-reference.md) |
| 📖 Look up syntax rules | [06-grammar-reference.md](./06-grammar-reference.md) |

---

## 📖 Document List

| Document | Content | Target Audience |
|----------|---------|-----------------|
| [01-quickstart.md](./01-quickstart.md) | 5-minute quick start + 3 most common scenarios + exercises | Everyone |
| **[07-complete-types-example.md](./07-complete-types-example.md)** | **Complete type system example - 23 types quick reference** | **Everyone** |
| [02-core-concepts.md](./02-core-concepts.md) | Design philosophy + type system + matching semantics + pipeline system | Users who want deep understanding |
| [03-practical-guide.md](./03-practical-guide.md) | Task-organized practical examples + common issues | Daily users |
| [04-language-reference.md](./04-language-reference.md) | Complete type list + syntax elements + quick reference | Developers |
| [05-functions-reference.md](./05-functions-reference.md) | Standardized reference for all functions | Developers |
| [06-grammar-reference.md](./06-grammar-reference.md) | EBNF formal grammar definition | Compiler developers |
| [../zh/09-checker-guide.md](../zh/09-checker-guide.md) | Checker layering, API design, and implementation conventions | Tooling / integration developers |

---

## ⚡ Quick Examples

### Nginx Access Log

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

### JSON API Response

```wpl
package api {
  rule response {
    (json(
      chars@user,
      digit@code,
      chars@message
    ))
  }
}
```

### Huawei Firewall Log (Base64)

```wpl
package firewall {
  rule huawei_log {
    |decode/base64|
    (
      digit:id,
      time:timestamp,
      sn:serial,
      chars:type\:,
      opt(kvarr),
      kvarr
    )
  }
}
```

For more examples, see: [01-quickstart.md](./01-quickstart.md) and [03-practical-guide.md](./03-practical-guide.md)

---

## Writing WPL Correctly

These rules reflect the current grammar:

- Field syntax order is `type [subfields] [:name] [format] [separator] {| pipe}`.
- Put the field name before the format: `time/clf:time<[,]>`.
- Quote format also comes after the name: `http/request:request"`.
- `opt(...)`, `alt(...)`, `some_of(...)`, `seq(...)`, and `not(...)` are group-level constructs.
- `opt(type)@key` is only for optional JSON/KV subfields.
- `one_of(...)` is not valid WPL. Use `alt(...)`.

For the authoritative grammar, see [06-grammar-reference.md](./06-grammar-reference.md).

---

## 🎯 Complete Type System Example

**Want to quickly understand all data types supported by WPL?**

👉 **[View Complete Type Example](./07-complete-types-example.md)** - One example demonstrating 23 major data types

This document includes:
- ✅ **Complete runnable** input data + WPL rules + output results
- ✅ **23 types**: Basic, time, network, structured, protocol, encoding
- ✅ **Detailed explanation for each type**: Syntax, examples, use cases
- ✅ **Common combination patterns**: Copy-and-use type combinations

**Suitable for:**
- 🆕 Beginners to quickly understand WPL capabilities
- 📚 Developers as a type quick reference manual
- 🔍 Quick lookup when encountering unfamiliar data formats

---

## 🎯 Core Features

- **Declarative**: Describe "what it is" rather than "how to do it"
- **Type-Safe**: Automatic validation and conversion (IP, time, JSON, etc.)
- **Composable**: Small rules combine into complex rules
- **Powerful Pipelines**: Preprocessing (Base64/Hex decoding) + field-level validation
- **Flexible Matching**: Sequential, alternative, optional, repetitive
- **Subfield Extraction**: JSON/KV nested fields

---

## 💬 Quick Help

### Common Questions

**Q: Where should I start learning?**
A: Start with [01-quickstart.md](./01-quickstart.md), get started in 5 minutes.

**Q: How do I parse my log format?**
A: Check [03-practical-guide.md](./03-practical-guide.md), find a similar scenario and adjust.

**Q: How do I use a specific type/function?**
A: See [04-language-reference.md](./04-language-reference.md) or [05-functions-reference.md](./05-functions-reference.md).

**Q: How do I debug parsing failures?**
A: Refer to [01-quickstart.md § Debugging Tips](./01-quickstart.md#quick-debugging-tips) or [03-practical-guide.md § Common Issues](./03-practical-guide.md#7-common-issues).

---

**Start Learning:** [01-quickstart.md](./01-quickstart.md) - 5-minute quick start
