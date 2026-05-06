# WPL 语法参考（对齐 `src/parser`）

本文档按 `wp-lang/src/parser` 的当前实现整理，重点说明：

- 包、规则、表达式的真实语法入口
- 组、字段、分隔符、字段管道的组合顺序
- 解析器当前支持的约束和限制

权威实现位置：

- `src/parser/wpl_pkg.rs`
- `src/parser/wpl_rule.rs`
- `src/parser/parse_code.rs`
- `src/parser/wpl_group.rs`
- `src/parser/wpl_field.rs`
- `src/parser/wpl_fun.rs`

---

## 文档导航

| 章节 | 说明 |
|------|------|
| [完整 EBNF](#完整-ebnf) | 以当前解析器行为为准的语法摘要 |
| [实现约束](#实现约束) | 当前 parser/eval 的关键限制 |
| [相关实现](#相关实现) | 对应源码位置 |

---

## 完整 EBNF

```ebnf
; 顶层通常从 package 开始；某些内部 API 也允许单独解析 rule / express

package_decl     = [ annotation ] "package" wsp1 key wsp? "{" wsp? rule_decl+ wsp? "}" ;
rule_decl        = [ annotation ] "rule" wsp? exact_path wsp? "{" wsp? express wsp? "}" ;

express          = [ preproc ] group { wsp? "," wsp? group } ;

; 预处理管道：至少一个步骤，并且必须以 '|' 结尾
preproc          = preproc_item { preproc_item } "|" ;
preproc_item     = "|" wsp? preproc_step wsp? ;
preproc_step     = key
                 | "plg_pipe" ( "/" wsp? key | "(" wsp? key wsp? ")" ) ;

group            = [ group_meta wsp? ] "(" wsp? field_list_opt wsp? ")"
                   [ "[" number "]" ]
                   [ group_sep ] ;

group_meta       = "alt" | "opt" | "some_of" | "seq" | "not" ;
group_sep        = shortcut_sep ;    ; 当前组级分隔符只支持 `\x` 风格，不支持 `{...}` 模式分隔符

field_list_opt   = [ field { wsp? "," wsp? field } [ wsp? "," ] ] ;

field            = [ repeat ] meta_token
                   [ symbol_content ]
                   [ subfields ]
                   [ ":" wsp? var_name ]
                   [ "[" number "]" ]
                   [ format ]
                   [ field_sep ]
                   { pipe } ;

repeat           = [ number ] "*" ;  ; `*meta` 或 `3*meta`

; 复合字段（如 json/kv/kvarr）中的子字段定义
subfields        = "(" wsp? subfield_list_opt wsp? ")" ;
subfield_list_opt = [ subfield { wsp? "," wsp? subfield } [ wsp? "," ] ] ;

subfield         = [ subfield_meta ]
                   [ symbol_content ]
                   [ "@" ref_path_or_quoted ]
                   [ ":" wsp? var_name ]
                   [ format ]
                   [ field_sep ]
                   { pipe } ;

subfield_meta    = meta_token | "opt" "(" wsp? key wsp? ")" ;
; 若 subfield 未显式声明 meta，则默认是 chars

; meta_token 由实现中的 `resolve_meta()` 决定：
; 1. `bad_json`
; 2. 或 `wp_model_core::model::DataType::from(token)` 可识别的类型
meta_token       = meta_char { meta_char } ;

; 仅 symbol / peek_symbol 允许内容，例如 `symbol(OK)`
symbol_content   = "(" symbol_chars ")" ;

format           = scope_format | quote_format ;
scope_format     = "<" scope_chars "," scope_chars ">" ;
quote_format     = '"' ;      ; 等价于首尾都用双引号

field_sep        = shortcut_sep | pattern_sep ;

shortcut_sep     = sep_char { sep_char } ;
sep_char         = '\' any_char ;

pattern_sep      = "{" pattern_content "}" ;
pattern_content  = pattern_unit { pattern_unit } [ preserve ] ;
pattern_unit     = literal_char | wildcard | escape_seq ;
wildcard         = "*" | "?" ;
escape_seq       = '\' ( '\' | "*" | "?" | "{" | "}" | "(" | ")" | "s" | "S" | "h" | "H" | "0" | "n" | "t" | "r" ) ;
preserve         = "(" pattern_unit { pattern_unit } ")" ;

pipe             = "|" wsp? ( fun_call | group ) ;

fun_call         = "take" "(" wsp? take_target wsp? ")"
                 | "last" "(" wsp? ")"
                 | "f_has" "(" wsp? key wsp? ")"
                 | "f_chars_has" "(" wsp? key wsp? "," wsp? bare_string wsp? ")"
                 | "f_chars_not_has" "(" wsp? key wsp? "," wsp? bare_string wsp? ")"
                 | "f_chars_in" "(" wsp? key wsp? "," wsp? bare_string_array wsp? ")"
                 | "f_digit_has" "(" wsp? key wsp? "," wsp? number wsp? ")"
                 | "f_digit_in" "(" wsp? key wsp? "," wsp? number_array wsp? ")"
                 | "f_ip_in" "(" wsp? key wsp? "," wsp? ip_array wsp? ")"
                 | "has" "(" wsp? ")"
                 | "chars_has" "(" wsp? bare_string wsp? ")"
                 | "chars_not_has" "(" wsp? bare_string wsp? ")"
                 | "chars_in" "(" wsp? bare_string_array wsp? ")"
                 | "digit_has" "(" wsp? number wsp? ")"
                 | "digit_in" "(" wsp? number_array wsp? ")"
                 | "digit_range" "(" wsp? number wsp? "," wsp? number wsp? ")"
                 | "ip_in" "(" wsp? ip_array wsp? ")"
                 | "json_unescape" "(" wsp? ")"
                 | "base64_decode" "(" wsp? ")"
                 | "chars_replace" "(" wsp? string_or_quoted wsp? "," wsp? string_or_quoted wsp? ")"
                 | "regex_match" "(" wsp? string_or_quoted wsp? ")"
                 | "starts_with" "(" wsp? string_or_quoted wsp? ")"
                 | "not" "(" wsp? fun_call wsp? ")" ;

annotation       = "#[" wsp? annotation_item { wsp? "," wsp? annotation_item } wsp? "]" ;
annotation_item  = tag_annotation | copy_raw_annotation ;
tag_annotation   = "tag" "(" wsp? tag_kv { wsp? "," wsp? tag_kv } wsp? ")" ;
copy_raw_annotation = "copy_raw" "(" wsp? tag_kv wsp? ")" ;
tag_kv           = key wsp? ":" wsp? ( quoted_string | raw_string ) ;

take_target      = key | quoted_string ;
ref_path_or_quoted = ref_path | single_quoted_raw ;

bare_string_array = "[" wsp? bare_string { wsp? "," wsp? bare_string } wsp? "]" ;
number_array     = "[" wsp? number { wsp? "," wsp? number } wsp? "]" ;
ip_array         = "[" wsp? ip_addr { wsp? "," wsp? ip_addr } wsp? "]" ;

key              = key_char { key_char } ;
exact_path       = key ;
var_name         = var_char { var_char } ;
ref_path         = ref_char { ref_char } ;

quoted_string    = double_quoted | single_quoted ;
raw_string       = 'r#"' { any_char } '"#' | 'r"' { any_char } '"' ;
single_quoted_raw = "'" { single_raw_char } "'" ;
string_or_quoted = bare_string | quoted_string ;

bare_string      = bare_char { bare_char } ;
number           = digit { digit } ;
ip_addr          = ipv4 | ipv6 | quoted_string ;

key_char         = letter | digit | "_" | "." | "/" | "-" ;
var_char         = letter | digit | "_" | "." | "-" ;
ref_char         = key_char | "[" | "]" | "*" ;
meta_char        = letter | digit | "_" | "/" ;

bare_char        = ? 由 `take_string` 决定的非分隔文本；通常用于裸字符串参数 ? ;
scope_chars      = ? 任意非空内容，按 `<..., ...>` 成对截取 ? ;
symbol_chars     = ? 任意字符，允许 `\)` 转义右括号 ? ;
single_raw_char  = ? 任意字符；仅 `\'` 具有特殊意义 ? ;
literal_char     = ? 任意非特殊字符 ? ;
double_quoted    = '"' { escaped | dq_char } '"' ;
single_quoted    = "'" { escaped | sq_char } "'" ;
escaped          = '\' ( '"' | "'" | '\' | "n" | "t" | "r" | "x" hex hex ) ;
dq_char          = ? 非 `"` 且非 `\` 的字符 ? ;
sq_char          = ? 非 `'` 且非 `\` 的字符 ? ;
digit            = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
hex              = digit | "a".."f" | "A".."F" ;
letter           = "A".."Z" | "a".."z" ;
wsp              = { " " | "\t" | "\n" | "\r" } ;
wsp1             = ( " " | "\t" | "\n" | "\r" ) { wsp } ;
```

---

## 实现约束

### 顶层入口

- `wpl_package()` 解析 `package ... { rule ... }`
- `wpl_rule()` 可以单独解析一个 `rule`
- `wpl_express()` 只解析规则体内部的表达式

### 预处理管道

- 预处理语法由 `src/parser/wpl_rule.rs::pip_proc` 解析
- 形式上支持任意 `key`，以及 `plg_pipe/<name>` / `plg_pipe(<name>)`
- 内置注册项目前在 `src/eval/builtins/mod.rs` 中包括：
  - `decode/base64`
  - `decode/hex`
  - `unquote/unescape`
  - `strip/bom`
  - `json_like`
- `plg_pipe(<name>)` 在解析后会规范化成 `plg_pipe/<name>`

### 分组

- 组元信息仅支持：`alt`、`opt`、`some_of`、`seq`、`not`
- 组后可接 `[n]`，解析器会把这个长度写回组内每个字段
- 当前组级分隔符只支持 `\...` 快捷分隔符，不支持 `{...}` 模式分隔符

### 字段

- 顶层字段必须显式写出 `meta_token`
- 复合字段里的子字段可以省略 meta，省略时默认是 `chars`
- 只有子字段支持 `opt(type)`，当前顶层字段不支持 `opt(type)`
- `peek_symbol(...)` 在解析后会被规整为 `symbol(...)`，但保留 peek 语义
- `bad_json` 是本地别名：底层类型按 `Chars` 处理，但 `meta_name` 保留为 `bad_json`

### 类型名

- 文档不再硬编码完整类型列表
- 当前可用类型由 `wp_model_core::model::DataType::from(token)` 决定
- 因此是否支持某个 `meta_token`，要以实际依赖版本中的 `DataType` 实现为准

### 格式与分隔符

- `"` 是快捷格式，等价于首尾都用双引号
- `<beg,end>` 是通用边界格式，支持嵌套括号内容，由 `interval_impl()` 处理
- 字段级分隔符支持两类：
  - `\...` 快捷分隔符
  - `{...}` 模式分隔符
- 模式分隔符支持：
  - `*`
  - `?`
  - `\s` `\S` `\h` `\H` `\0` `\n` `\t` `\r`
  - 末尾 `(...)` preserve 片段

### 注解

- 当前只有两个注解函数：
  - `tag(k: "v")`
  - `copy_raw(name: "raw_field")`
- 注解值支持：
  - 普通引号字符串
  - 原始字符串 `r#"..."#`
  - 兼容旧写法 `r"..."`

### 字段管道

- 解析入口在 `src/parser/wpl_fun.rs`
- 支持三类参数风格：
  - 只能接裸值的函数，如 `chars_has(ok)`
  - 接数组的函数，如 `digit_in([200, 201])`
  - 接裸值或引号字符串的函数，如 `chars_replace("a,b", "c d")`
- `not(...)` 只能包裹字段函数，不能包裹选择器或分组
- `pipe` 右侧除了函数，也可以直接接一个嵌套分组，例如 `|(time, ip)`

### 引号与路径

- `take(...)` 支持裸标识符、双引号字符串、单引号字符串
- 子字段 `@ref` 支持：
  - 裸路径：`@payload/data`
  - 单引号原始字符串：`@'@special-field'`
- 注解值和某些函数参数支持转义字符串；并不是所有字符串参数都支持带引号写法

---

## 相关实现

- 包解析：[src/parser/wpl_pkg.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/parser/wpl_pkg.rs)
- 规则解析：[src/parser/wpl_rule.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/parser/wpl_rule.rs)
- 表达式解析：[src/parser/parse_code.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/parser/parse_code.rs)
- 分组解析：[src/parser/wpl_group.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/parser/wpl_group.rs)
- 字段解析：[src/parser/wpl_field.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/parser/wpl_field.rs)
- 函数解析：[src/parser/wpl_fun.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/parser/wpl_fun.rs)
- 内置预处理器注册：[src/eval/builtins/mod.rs](/Users/zuowenjian/devspace/wp-labs/dev/wparse/wp-lang/src/eval/builtins/mod.rs)
