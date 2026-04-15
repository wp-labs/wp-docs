# WPL 语法参考（EBNF）

本文档提供 WPL 的形式化语法定义，适合：
- 编译器/解析器开发者
- 精确理解语法规则
- 工具集成开发

**普通用户请参考：**
- 快速入门：[01-quickstart.md](./01-quickstart.md)
- 核心概念：[02-core-concepts.md](./02-core-concepts.md)
- 实战指南：[03-practical-guide.md](./03-practical-guide.md)
- 语言参考：[04-language-reference.md](./04-language-reference.md)

---

## 📑 文档导航

| 章节 | 说明 |
|------|------|
| [完整 EBNF 定义](#完整-ebnf-定义) | 形式化语法定义 |
| [语义说明](#语义说明) | 语法规则的语义解释 |
| [实现参考](#实现参考) | 源代码位置 |

---

## 完整 EBNF 定义

权威实现以当前仓库中的 `src/parser/` 解析器为准；此处与源代码保持同步。

```ebnf
; WPL 语法（EBNF）
; 基于当前仓库 src/parser 下解析实现（winnow）整理
; 说明：本文件给出语法产生式与必要的词法约定。除显式标注外，token 之间允许可选空白 `ws`。

wpl_document     = { package_decl } ;

package_decl     = [ annotation ] "package" ws? ident ws? "{" ws? rule_decl+ ws? "}" ;

rule_decl        = [ annotation ] "rule" ws? rule_name ws? "{" ws? statement ws? "}" ;

statement        = plg_pipe_block | express ;

plg_pipe_block   = ["@"]? "plg_pipe" ws? "(" ws? "id" ws? ":" ws? key ws? ")" ws? "{" ws? express ws? "}" ;

express          = [ preproc ] group { ws? "," ws? group } ;

preproc          = "|" ws? preproc_step { ws? "|" ws? preproc_step } ws? "|" ;   ; 至少一个步骤，且以 '|' 结尾
preproc_step     = builtin_preproc | plg_pipe_step ;
builtin_preproc  = ns "/" name ;
plg_pipe_step    = "plg_pipe" ws? "/" ws? key ;                   ; 通过注册表查找自定义扩展
ns               = "decode" | "unquote" | "strip" ;              ; 命名空间白名单
name             = ("base64" | "hex") | "unescape" | "bom" ;     ; 步骤名白名单
; 支持的预处理器：
;   decode/base64 - Base64 解码
;   decode/hex - 十六进制解码
;   unquote/unescape - URL 转义解码
;   strip/bom - 移除 BOM（字节顺序标记）

group            = [ group_meta ] ws? "(" ws? field_list_opt ws? ")" [ ws? group_len ] [ ws? group_sep ] ;
group_meta       = "alt" | "opt" | "some_of" | "seq" | "not" ;
group_len        = "[" number "]" ;
group_sep        = sep ;

; 列表：允许空、允许尾随逗号
field_list_opt   = [ field { ws? "," ws? field } [ ws? "," ] ] ;

field            = [ repeat ] data_type [ symbol_content ]
                   [ subfields ]
                   [ ":" ws? var_name ]
                   [ length ]
                   [ format ]
                   [ sep ]
                   { pipe } ;                              ; 允许多个管道

repeat           = [ number ] "*" ;                        ; "*ip" 或 "3*ip"
length           = "[" number "]" ;                       ; 仅顶层字段支持（子字段不支持）

; 复合字段（如 kvarr/json 等）的子字段列表
subfields        = "(" ws? subfields_opt ws? ")" ;
subfields_opt    = [ subfield { ws? "," ws? subfield } [ ws? "," ] ] ;
subfield         = [ opt_datatype | data_type ]
                   [ symbol_content ]
                   [ "@" ref_path ]
                   [ ":" ws? var_name ]
                   [ format ]
                   [ sep ]
                   { pipe } ;

opt_datatype     = "opt" "(" ws? data_type ws? ")" ;     ; 声明该子字段为可选

; 字段数据类型（与外部 crate wp-model-core::DataType 对应）
data_type        = builtin_type | ns_type | array_type ;

builtin_type     = "auto" | "bool" | "chars" | "symbol" | "peek_symbol"
                   | "digit" | "float" | "_" | "sn"
                   | "time" | "time/clf" | "time_iso" | "time_3339" | "time_2822" | "time_timestamp"
                   | "ip" | "ip_net" | "domain" | "email" | "port"
                   | "hex" | "base64"
                   | "kv" | "kvarr" | "json" | "exact_json"
                   | "url"
                   | "proto_text" | "obj"
                   | "id_card" | "mobile_phone" ;

ns_type          = path_ident ;                               ; 例如 http/request、http/status 等
; 注：实现层面建议对白名单前缀（如 "http/"）做校验，以避免任意路径膨胀语言面。
; 支持的命名空间类型：
;   http/request, http/status, http/agent (或 http/user_agent), http/method
;   time/clf (或 time/apache, time/httpd, time/nginx)
;   time/rfc3339 (别名 time_3339), time/rfc2822 (别名 time_2822)
;   time/timestamp (或 time/epoch, 别名 time_timestamp)
;   proto/text (别名 proto_text)

array_type       = "array" [ "/" subtype ] ;                 ; 如："array" 或 "array/ip" 或 "array/chars"
subtype          = key ;                                      ; 可以是任意已支持的类型名

; 仅当 data_type 为 symbol/peek_symbol 时允许携带内容
symbol_content   = "(" symbol_chars ")" ;

; 字段显示/抽取格式
format           = scope_fmt | quote_fmt ;
scope_fmt        = "<" any_chars "," any_chars ">" ;   ; 作用域首尾定界，如 <[,]>
quote_fmt        = '"' ;                                ; 等价首尾均为 '"'


; 分隔符（两种形式）
sep              = shortcut_sep | pattern_sep ;

; 快捷分隔符：反斜杠转义的字符序列
shortcut_sep     = sep_char , { sep_char } ;             ; 例："\\," => ","；"\\!\\|" => "!|"
sep_char         = '\\' , any_char ;

; 模式分隔符：花括号包裹的模式表达式
pattern_sep      = "{" pattern_content "}" ;
pattern_content  = glob_segments [ preserve ] ;
glob_segments    = glob_segment { glob_segment } ;
glob_segment     = literal_char | wildcard | escape_seq ;

; 通配符
wildcard         = "*" | "?" ;                          ; "*" - 零或多个任意字符（非贪婪）；"?" - 恰好一个任意字符
; 约束：模式中 "*" 最多出现一次

; 转义序列
escape_seq       = "\\" ( special_char | macro_char ) ;
special_char     = "\\" | "*" | "?" | "{" | "}" | "(" | ")" ;  ; 字面转义
macro_char       = "s" | "S" | "h" | "H" | "0" | "n" | "t" | "r" ;  ; 宏字符
; 支持的宏：
;   \s - 一个或多个连续空白字符 [ \t\r\n]+
;   \S - 一个或多个连续非空白字符 [^ \t\r\n]+
;   \h - 一个或多个连续水平空白 [ \t]+
;   \H - 一个或多个连续非水平空白 [^ \t]+
;   \0 - 空字节
;   \n - 换行
;   \t - 制表符
;   \r - 回车

; 保留标记
preserve         = "(" glob_segments ")" ;              ; 匹配但不消费，仅在模式末尾
; 约束：
;   1. preserve 只能出现在 pattern_content 的末尾
;   2. preserve 内不允许包含 "*" 通配符
;   3. preserve 不允许嵌套

; 字面字符（非特殊字符的任意字符）
literal_char     = any_char_except_special ;            ; 排除 '\', '*', '?', '{', '}', '(', ')' 的任意字符

; 字段级管道：函数调用或嵌套分组
pipe             = "|" ws? ( fun_call | group ) ;

; 预置函数（wpl_fun.rs）：
; - 选择器函数：take, last
; - f_ 前缀表示字段集合操作（需指定字段名）
; - 无前缀表示活跃字段操作
; - 转换函数：json_unescape, base64_decode, chars_replace
; - 包装器函数：not
fun_call         = selector_fun | target_fun | active_fun | transform_fun | wrapper_fun ;

; 选择器函数
selector_fun     = take_fun | last_fun ;
take_fun         = "take" "(" ws? key ws? ")" ;
last_fun         = "last" "(" ws? ")" ;

; 字段集合操作函数（f_ 前缀）
target_fun       = f_has | f_chars_has | f_chars_not_has | f_chars_in
                 | f_digit_has | f_digit_in | f_ip_in ;
f_has            = "f_has" "(" ws? key ws? ")" ;
f_chars_has      = "f_chars_has" "(" ws? key ws? "," ws? path ws? ")" ;
f_chars_not_has  = "f_chars_not_has" "(" ws? key ws? "," ws? path ws? ")" ;
f_chars_in       = "f_chars_in" "(" ws? key ws? "," ws? path_array ws? ")" ;
f_digit_has      = "f_digit_has" "(" ws? key ws? "," ws? number ws? ")" ;
f_digit_in       = "f_digit_in" "(" ws? key ws? "," ws? number_array ws? ")" ;
f_ip_in          = "f_ip_in" "(" ws? key ws? "," ws? ip_array ws? ")" ;

; 活跃字段操作函数（无前缀）
active_fun       = has_fun | chars_has | chars_not_has | chars_in | starts_with | regex_match
                 | digit_has | digit_in | digit_range | ip_in ;
has_fun          = "has" "(" ws? ")" ;
chars_has        = "chars_has" "(" ws? path ws? ")" ;
chars_not_has    = "chars_not_has" "(" ws? path ws? ")" ;
chars_in         = "chars_in" "(" ws? path_array ws? ")" ;
starts_with      = "starts_with" "(" ws? quoted_string ws? ")" ;
regex_match      = "regex_match" "(" ws? quoted_string ws? ")" ;
digit_has        = "digit_has" "(" ws? number ws? ")" ;
digit_in         = "digit_in" "(" ws? number_array ws? ")" ;
digit_range      = "digit_range" "(" ws? number ws? "," ws? number ws? ")" ;
ip_in            = "ip_in" "(" ws? ip_array ws? ")" ;

; 转换函数
transform_fun    = json_unescape | base64_decode | chars_replace ;
json_unescape    = "json_unescape" "(" ws? ")" ;
base64_decode    = "base64_decode" "(" ws? ")" ;
chars_replace    = "chars_replace" "(" ws? path ws? "," ws? path ws? ")" ;

; 包装器函数
wrapper_fun      = not_fun ;
not_fun          = "not" "(" ws? fun_call ws? ")" ;

path_array       = "[" ws? path { ws? "," ws? path } ws? "]" ;
number_array     = "[" ws? number { ws? "," ws? number } ws? "]" ;
ip_array         = "[" ws? ip_addr { ws? "," ws? ip_addr } ws? "]" ;

annotation       = "#[" ws? ann_item { ws? "," ws? ann_item } ws? "]" ;
ann_item         = tag_anno | copy_raw_anno ;
tag_anno         = "tag" "(" ws? tag_kv { ws? "," ws? tag_kv } ws? ")" ;
tag_kv           = ident ":" ( quoted_string | raw_string ) ;      ; 键为标识符；值为字符串
copy_raw_anno    = "copy_raw" "(" ws? "name" ws? ":" ws? ( quoted_string | raw_string ) ws? ")" ;

; 词法与辅助记号 --------------------------------------------------------
field_name       = var_name ;
rule_name        = exact_path ;
key              = key_char { key_char } ;              ; [A-Za-z0-9_./-]+
var_name         = var_char { var_char } ;              ; [A-Za-z0-9_.-]+
ref_path         = ref_char { ref_char } ;              ; [A-Za-z0-9_./\-.[\]*]+
; 标识符与路径标识符（推荐写法）
ident            = ( letter | '_' ) { letter | digit | '_' | '.' | '-' } ;
path_ident       = ident { "/" ident } ;

exact_path       = exact_path_char { exact_path_char } ; ; 不含 '[' ']' '*'
exact_path_char  = letter | digit | '_' | '.' | '/' | '-' ;
path             = key | ref_path ;

number           = digit { digit } ;
digit            = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' ;

key_char         = letter | digit | '_' | '.' | '/' | '-' ;
var_char         = letter | digit | '_' | '.' | '-' ;
ref_char         = key_char | '[' | ']' | '*' ;

letter           = 'A'..'Z' | 'a'..'z' ;

quoted_string    = '"' { escaped | char_no_quote_backslash } '"' ;
raw_string       = 'r' '#' '"' { any_char } '"' '#' ;          ; r#"..."#，内部不处理转义（内容可包含 '"'）
char_no_quote    = ? any char except '"' ? ;
escaped          = '\\' ( '"' | '\\' | 'n' | 't' | 'r' | 'x' hex hex ) ;
char_no_quote_backslash = ? any char except '"' and '\\' ? ;
hex              = '0'..'9' | 'a'..'f' | 'A'..'F' ;

free_string      = { fchar } ;                          ; 直至 ',' 或 ')'（不含）
fchar            = ? any char except ',' and ')' ? ;

symbol_chars     = { schar } ;                          ; 允许除 ')' 与 '\\' 外字符，或使用 '\)' 转义
schar            = char_no_close_paren_backslash | '\\' ')' ;
char_no_close_paren_backslash = ? any char except ')' and '\\' ? ;
any_chars        = { any_char } ;
any_char         = ? any character ? ;

ip_addr          = quoted_string | ipv4 | ipv6 ;        ; 支持 IPv4/IPv6 裸字面量或带引号
ipv4             = digit1 "." digit1 "." digit1 "." digit1 ;
digit1           = digit { digit } ;
ipv6             = ? valid IPv6 literal (RFC 4291), including compressed forms like "::1" ? ;

ws               = { ' ' | '\t' | '\n' | '\r' } ;

;保留关键字（不可作为标识符使用；由实现侧进行冲突校验）
ReservedKeyword  = "package" | "rule" | "alt" | "opt" | "some_of" | "seq" | "not" | "order"
                 | "tag" | "copy_raw" | "include" | "macro" ;


```

---

## 语义说明

### 预处理管道
- `preproc` 管道（例如 `|decode/base64|unquote/unescape|`）出现在 `express` 起始处，独立于字段级 `pipe`
- 作用于整行输入，在字段解析前执行
- 执行顺序：从左到右
- 必须以 `|` 结尾
- 支持的预处理器：
  - `decode/base64` - Base64 解码
  - `decode/hex` - 十六进制解码
  - `unquote/unescape` - URL 转义解码
  - `strip/bom` - 移除 BOM（字节顺序标记）

### 分组元数据（Group Meta）
- `group_meta` 用于指定分组的行为模式
- `alt` - 选择性匹配，匹配组内任意一个字段即可
- `opt` - 可选分组，整个分组可以不存在
- `some_of` - 部分匹配，匹配组内部分字段
- `seq` - 序列匹配，按顺序匹配组内所有字段
- `not` - 否定匹配，匹配除组内字段外的其他内容

### 分组长度和分隔符
- `group` 后可跟 `[n]` 与分隔符 `sep`
- 长度会应用到组内所有字段
- `sep` 仅存储在组上，具体组合策略见实现



### 符号类型
- `symbol/peek_symbol` 可携带 `symbol_content`，如 `symbol(boy)`
- `peek_symbol` 等价于 `symbol`，且仅改变"窥探"语义（预读但不消费）

### 子字段
- `subfields` 中未显式 `"@ref"` 时，键默认为 `"*"`（通配键）
- 子字段支持 `opt(type)` 标记为可选

### 分隔符
分隔符支持两种形式：

#### 快捷分隔符
- 使用反斜杠转义的单个或多个字符
- 例如 `\\,` 代表逗号 `,`，`\\!\\|` 代表字符串 `"!|"`
- 优先级：字段级 > 组级 > 上游

#### 模式分隔符
- 使用花括号 `{...}` 包裹的模式表达式
- 支持通配符、空白匹配宏和保留标记
- 适用于复杂场景的分隔

**通配符：**
- `*` - 零或多个任意字符（非贪婪，最短匹配）
- `?` - 恰好一个任意字符
- 约束：模式中 `*` 最多出现一次

**空白匹配宏：**
- `\s` - 一个或多个连续空白字符 `[ \t\r\n]+`
- `\S` - 一个或多个连续非空白字符 `[^ \t\r\n]+`
- `\h` - 一个或多个连续水平空白 `[ \t]+`
- `\H` - 一个或多个连续非水平空白 `[^ \t]+`

**保留标记：**
- `(...)` - 匹配但不消费，将匹配的内容留给下一阶段
- 只能出现在模式末尾
- 内部不允许包含 `*` 通配符

**示例：**
- `chars{*=}` - 匹配到第一个 `=` 符号
- `chars{\s=}` - 跳过空白后匹配 `=`
- `chars{*(key=)}` - 匹配到 `key=` 并保留 `key=` 给下一个字段
- `chars{field?:\s}` - 匹配 `field` + 任意字符 + `:` + 空白

**约束：**
- 模式中 `*` 最多出现一次
- `()` 只能在模式末尾
- `()` 内不允许 `*`
- `()` 不允许嵌套
- 不能与 upstream separator 混用

### 注解
- `annotation` 可用于 `package` 与 `rule`
- 若同时存在，会在 `rule` 侧合并（`rule` 优先）

### 管道函数
- 字段级管道函数包括：选择器、条件检查、转换、包装器
- `not()` 包装器可反转任何管道函数的成功/失败结果
- `starts_with()` 检查字符串字段是否以指定前缀开始
- `regex_match()` 支持正则表达式模式匹配
- `digit_range()` 支持数值范围检查（闭区间）
- `chars_replace()` 执行字符串替换操作

---

## 相关文档

- 快速入门：[01-quickstart.md](./01-quickstart.md)
- 核心概念：[02-core-concepts.md](./02-core-concepts.md)
- 实战指南：[03-practical-guide.md](./03-practical-guide.md)
- 语言参考：[04-language-reference.md](./04-language-reference.md)
- 函数参考：[05-functions-reference.md](./05-functions-reference.md)

---

## 实现参考

- 语法实现：`src/parser/`
- 管道函数：`src/parser/wpl_fun.rs`
- 数据类型：外部 crate `wp-model-core`
