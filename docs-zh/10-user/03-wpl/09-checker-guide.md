# Checker 实现指南

本文档说明如何在 `wp-lang` 中实现一个可复用的 `checker`，以及为什么当前实现采用 `库能力 + CLI 壳` 的分层方式。

适用场景：

- 为 `wp-lang` 增加新的检查入口
- 给下游 crate 暴露可复用的 WPL 检查能力
- 维护 `wpl-check` 或其他基于 WPL 的校验工具

---

## 1. 设计目标

`checker` 的职责不是“解析命令行”，而是“接收请求、加载输入、校验规则、执行 sample，并返回结构化结果”。

当前实现分为两层：

- `src/check/`
  提供可复用的检查能力，供库内和下游直接调用
- `wpl-check`
  作为独立 companion 仓库承载 CLI、examples 和 agent skill

这个边界的好处是：

- 下游可以直接复用，不需要依赖 `wpl-check` 命令
- CLI 只是表现层，后续可以替换成 HTTP、WASM、IDE 插件等入口
- 核心检查逻辑只维护一份

---

## 2. 推荐目录结构

推荐把 checker 代码组织在如下目录中：

```text
src/check/
  mod.rs
  model.rs
  source.rs
  sample.rs
  input.rs
  runner.rs
```

其中：

- `model.rs`
  定义请求与结果类型
- `source.rs`
  负责 WPL 源码解析
- `sample.rs`
  负责 sample 执行和错误格式化
- `input.rs`
  负责文件输入与默认路径约定
- `runner.rs`
  负责高层执行编排

当前库层实现可直接参考：

- [`src/check/mod.rs`](../../src/check/mod.rs)
- [`src/check/model.rs`](../../src/check/model.rs)
- [`src/check/source.rs`](../../src/check/source.rs)
- [`src/check/sample.rs`](../../src/check/sample.rs)
- [`src/check/input.rs`](../../src/check/input.rs)
- [`src/check/runner.rs`](../../src/check/runner.rs)

---

## 3. 公共 API 设计

一个可复用的 checker 至少应暴露三类 API：

1. 请求类型
2. 低层能力
3. 高层执行入口

### 3.1 请求类型

请求类型建议放在 `model.rs` 中。

当前最小集合如下：

```rust
pub enum Mode {
    Auto,
    Package,
    Rule,
    Expr,
}

pub struct SourceRequest {
    pub mode: Mode,
    pub input: Option<PathBuf>,
}

pub enum SampleInput {
    Inline(String),
    DefaultFile,
    File(PathBuf),
}

pub struct SampleRequest {
    pub source: SourceRequest,
    pub rule_name: Option<String>,
    pub sample: SampleInput,
}
```

对应实现见：

- [`src/check/model.rs`](../../src/check/model.rs)

这些类型解决的是“调用者想做什么”，而不是“CLI 传了哪些参数”。

### 3.2 低层能力

低层能力建议独立暴露，方便更细粒度复用：

- `validate_source`
- `source_summary`
- `normalized_output`
- `validate_sample_target`
- `evaluate_sample`

对应实现见：

- [`src/check/source.rs`](../../src/check/source.rs)
- [`src/check/sample.rs`](../../src/check/sample.rs)

### 3.3 高层入口

高层入口应该直接接收 request，并完成一次完整检查。

当前实现是：

```rust
pub fn run_syntax_request(request: &SourceRequest) -> Result<ParseResult, String>;
pub fn run_sample_request(request: &SampleRequest) -> Result<SampleCheckResult, String>;
```

对应实现见：

- [`src/check/runner.rs`](../../src/check/runner.rs)

CLI、集成测试或下游服务应优先调用这一层。

---

## 4. 各模块职责

### 4.1 `model.rs`

只定义数据结构，不放业务逻辑。

建议包含：

- 默认文件名常量
- mode 枚举
- request / result 类型

不建议在这里放：

- 文件读取
- 命令行解析
- 打印逻辑

### 4.2 `source.rs`

负责“把 WPL 源码变成可执行语义对象”。

典型职责：

- 构造 `WplCode`
- 根据 `Mode` 选择 package/rule/expr 解析
- `Auto` 模式推断
- 生成人类可读的 source 摘要
- 返回 normalized WPL

推荐接口：

- `validate_source`
- `source_summary`
- `normalized_output`

### 4.3 `sample.rs`

负责“把 sample 数据跑进解析计划”。

典型职责：

- 根据 `ParseResult` 构建 evaluator
- 选择 package 中的 rule
- 执行 preprocess
- 运行 `parse_groups`
- 生成友好的错误信息

推荐接口：

- `validate_sample_target`
- `evaluate_sample`

其中 `validate_sample_target` 的目的很关键：先校验 rule 选择是否合法，再做后续 I/O 和执行。

### 4.4 `input.rs`

负责“checker 的输入约定”，不是 CLI 特有逻辑。

典型职责：

- `-` 表示 stdin
- 目录输入自动补为 `rule.wpl`
- 默认 sample 路径自动补为 `sample.txt`
- 读取源代码与 sample 文件

当前约定常量见：

- [`DEFAULT_RULE_FILE`](../../src/check/model.rs)
- [`DEFAULT_SAMPLE_FILE`](../../src/check/model.rs)

### 4.5 `runner.rs`

负责把各层能力串起来，形成稳定入口。

建议执行顺序：

1. 解析 source 输入
2. 加载 source
3. 解析 WPL
4. 校验 sample 目标
5. 解析 / 加载 sample
6. 执行 sample

这个顺序很重要，因为配置错误应该优先于无关 I/O 错误。

---

## 5. 一个正确的执行顺序

`run_sample_request` 的核心不是“能跑通”，而是“错误优先级正确”。

推荐顺序如下：

```rust
let source_input = resolve_source_path(...);
let sample_input = resolve_sample_input(...);
let (source, origin) = load_input(...)?;
let parsed = validate_source(...)?;
validate_rule_name_usage(&parsed, ...)?;
validate_sample_target(&parsed, ...)?;
let sample = load_sample_data(&sample_input)?;
let evaluation = evaluate_sample(&parsed, ..., &sample)?;
```

关键点：

- `validate_rule_name_usage`
  检查 `--rule-name` 是否只用于 package
- `validate_sample_target`
  检查 package 多 rule 时是否提供了 rule 名，或 rule 名是否存在
- `load_sample_data`
  必须放在上述预检之后

否则会出现这类错误行为：

- package 有多个 rule，但 sample 文件缺失时，先报“文件不存在”
- 用户传了错误 rule 名，但先报 sample 读取失败

这会掩盖真实配置问题。

---

## 6. 如何判断逻辑应放在库层还是 CLI 层

可以用一个很直接的判断：

如果一段逻辑不依赖以下内容，它大概率就应该在 `src/check/`：

- `env::args`
- `println!` / `eprintln!`
- help 文本
- 子命令名字符串

### 应放在 `src/check/` 的逻辑

- 默认 `rule.wpl` / `sample.txt` 路径规则
- stdin / 目录输入解析
- WPL 源校验
- sample 执行
- rule 选择校验
- 结构化结果返回

### 应放在 companion `wpl-check` 项目的逻辑

- `syntax` / `sample` 子命令解析
- `--help` 文本
- `--print` 控制是否打印 normalized source
- 最终 stdout/stderr 展示格式

当前 companion 项目实现可参考：

- <https://github.com/wp-labs/wpl-check/blob/main/src/main.rs>
- <https://github.com/wp-labs/wpl-check/blob/main/src/app.rs>
- <https://github.com/wp-labs/wpl-check/blob/main/src/cli.rs>

---

## 7. 错误处理建议

### 7.1 优先返回结构化错误

当前实现先使用 `String`，这是可接受的最小版本，但长期建议替换为专门的错误类型，例如：

```rust
pub enum CheckError {
    ReadSource { path: PathBuf, message: String },
    ReadSample { path: PathBuf, message: String },
    InvalidTarget(String),
    ParseSource(String),
    EvaluateSample(String),
}
```

这样做的好处是：

- CLI 可以格式化输出
- 下游服务可以按错误种类分类处理
- 测试更稳，不必完全依赖字符串匹配

### 7.2 不要 panic

所有外部输入都应视为不可信：

- WPL 源文本
- sample 文本
- 文件路径
- rule 名

因此优先返回 `Result`，避免 panic。

### 7.3 错误要尽量包含上下文

好的错误应包含：

- 失败阶段
- 目标对象
- 行列号或 offset
- 附近内容
- 可执行提示

sample 错误格式化的实现可参考：

- [`src/check/sample.rs`](../../src/check/sample.rs)

---

## 8. 测试策略

checker 的测试不要全部堆在 CLI 层。

推荐分布如下：

### 8.1 `source.rs`

覆盖：

- `Auto` 模式推断
- 注解前缀跳过
- package / rule / expr 三种解析
- 错误位置是否包含行列号

### 8.2 `sample.rs`

覆盖：

- rule sample 执行成功
- package 多 rule 选择
- 非 package 下 `rule_name` 报错
- 友好的 sample 错误输出
- Unicode 列号与长行裁剪

### 8.3 `input.rs`

覆盖：

- 目录输入解析
- 默认 sample 文件推导
- relative sample 路径不重写
- 保留换行

### 8.4 `runner.rs`

重点覆盖错误优先级：

- 非 package 使用 `rule_name` 时，应先报配置错误
- 多 rule package 缺少 `rule_name` 时，应先报配置错误
- 错误 `rule_name` 时，应先报目标错误

### 8.5 CLI

CLI 只测试：

- 参数解析
- 默认值
- 非法选项
- 子命令边界

不要在 CLI 层重复验证库里的业务逻辑。

---

## 9. feature 建议

如果 checker 需要给下游复用，推荐用 feature 做显式分层。

当前 `wp-lang` 只保留：

- `check`
  开启库能力

对应配置可参考 [`Cargo.toml`](../../Cargo.toml)。

推荐模式：

```toml
[features]
default = []
check = []
```

这样下游可以只启用：

```toml
wp-lang = { version = "...", default-features = false, features = ["check"] }
```

然后直接使用：

```rust
use wpl::check::{Mode, SampleInput, SampleRequest, SourceRequest, run_sample_request};
```

---

## 10. 最小实现清单

如果要从零实现一个 checker，建议按以下顺序推进：

1. 在 `model.rs` 定义 request / result 类型
2. 在 `source.rs` 实现 `validate_source`
3. 在 `sample.rs` 实现 `evaluate_sample`
4. 在 `input.rs` 实现默认路径与文件加载
5. 在 `runner.rs` 实现 `run_syntax_request` / `run_sample_request`
6. 在 `mod.rs` 统一导出公共 API
7. 最后在 companion `wpl-check` 项目里写 CLI 壳

不要反过来从 CLI 开始堆逻辑。

---

## 11. 一个简单调用示例

下面是下游调用 checker 的最小示例：

```rust
use std::path::PathBuf;

use wpl::check::{Mode, SampleInput, SampleRequest, SourceRequest, run_sample_request};

fn main() -> Result<(), String> {
    let result = run_sample_request(&SampleRequest {
        source: SourceRequest {
            mode: Mode::Auto,
            input: Some(PathBuf::from("examples/wpl-check/csv_demo/rule.wpl")),
        },
        rule_name: None,
        sample: SampleInput::File(PathBuf::from("examples/wpl-check/csv_demo/sample.txt")),
    })?;

    println!("{}", wpl::check::source_summary(&result.parsed));
    println!("{}", result.evaluation.record);
    Ok(())
}
```

---

## 12. 结论

实现 checker 时，核心原则只有三条：

1. checker 是库能力，不是命令行能力
2. 配置错误优先于无关 I/O 错误
3. CLI 只负责参数和展示，不承载业务语义

如果新的实现仍然需要直接操作 `println!`、`env::args`、子命令文本，那通常说明分层还不够干净。
