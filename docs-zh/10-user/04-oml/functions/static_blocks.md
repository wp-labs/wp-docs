# `static` 块：模型级常量

`static { ... }` 用于在 OML 模型中声明一次性构建、后续重复复用的常量。它位于头部 `---` 之后、普通聚合语句之前。

## 基本示例

```oml
name : apache_error_template
rule : /apache/error/e1
---
static {
    e1_template = object {
        id = chars(E1);
        tpl = chars("jk2_init() Found child <*> in scoreboard slot <*>");
    };
    score_map = object {
        error = float(90.0);
        warning = float(70.0);
        info = float(20.0);
    };
    default_score = float(40.0);
}

message = read(Content) ;

target_template = match read(message) {
    starts_with('jk2_init() Found child') => e1_template ;
    _ => e1_template ;
} ;

event_id = read(target_template) | get(id) ;
event_tpl = read(target_template) | get(tpl) ;
risk_score : float = lookup_nocase(score_map, read(level), default_score) ;
```

## 当前实现允许的表达式

`static` 内部只支持纯表达式：

- 值字面量：`chars(...)`、`digit(...)`、`float(...)`、`bool(...)`、`time(...)` 等
- `object { ... }`
- `calc(...)`，但参与计算的操作数也必须都是常量

## 当前实现明确不支持的内容

以下表达式在 `static` 中会被解析阶段直接拒绝：

- `read(...)`、`take(...)`、`collect ...`
- `pipe ...`
- `fmt(...)`
- `match ... { ... }`
- `lookup_nocase(...)`
- `select ... where ... ;`
- `Now::time()`、`Now::date()`、`Now::hour()`
- 引用其他 `static` 符号

这意味着 `static` 不是“任意表达式但不能读输入”，而是更严格的“只能写纯常量对象”。

## 使用规则

- `static` 块可以出现 0 个或多个，都会在普通聚合语句之前处理
- 每条 `static` 绑定必须是单目标赋值，并以 `;` 结束
- 同一模型内静态符号名不能重复
- 普通聚合阶段直接写静态符号名即可引用，例如 `score = default_score ;`
- 如果静态符号保存的是对象，后续需要通过 `read(symbol) | get(key)` 之类的方式继续取值

## 适合放进 `static` 的内容

- 状态码或等级到分值的映射表
- 事件模板对象
- 不依赖输入记录的固定默认值
- 需要被多个 `match` 分支复用的常量对象
