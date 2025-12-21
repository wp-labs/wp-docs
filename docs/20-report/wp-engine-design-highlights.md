# wp-engine 设计竞争力概览

> 信息来源：`wp-engine/docs/30-design`（01-architecture～09-rescue）。

## 高性能
- **架构分层**：核心链路被严格限定为 `Source → Parser/Rule → Sink`，所有 Source/Sink 通过 Factory + ResolvedSpec 构建，连接器、模型、主配置三层职责互不干扰；再加上“Monitor → Parser → Sink → Picker” 的启动顺序，确保消费者总是先于生产者上线（docs/30-design/01-architecture.md:4, docs/30-design/01-architecture.md:18）。这意味着扩容或变更时只需替换局部模块，不会拖垮全链路。
- **零拷贝数据通路**：TCP Source 读取到的 payload 直接包裹在 `Arc<Vec<u8>>` 中，BatchBuilder 以事件数/字节数控制批次，并在空闲期将缓冲从 1MB 缩回 256KB；SourceEvent 将此 ArcBytes 传入 Parser→Sink，使整条链路不再复制数据，实际压测中可减少 30–50% 内存分配和系统调用次数（docs/30-design/06-zero_copy.md:6, docs/30-design/06-zero_copy.md:92）。
- **全异步 IO 驱动**：接入端 `TcpServer::run_acceptor` 使用 `tokio::select!` 同时监听新连接与 stop 信号，每个连接由 ConnectionManager 使用 `tokio::spawn` 处理；解析/采集任务也都以 TaskGroup 形式运行在 Tokio runtime 上，通过异步 channel 传递批次，IO 等待被计算阶段完全掩盖（src/sources/net/tcp/server.rs:59, src/sources/net/tcp/connection.rs:62, src/runtime/tasks/parse.rs:45, src/runtime/tasks/pick.rs:21）。
- **并行流水线 + 预处理**：SourceEvent 在拆帧后附带 `preproc` 闭包，ActParser 在自身线程执行 normalize/strip/tag，从而“解析线程数 = 预处理并行度”；接收→预处理→解析→转换→路由以 channel 解耦、任务组并行，日志帧进入一次即可完成全流程（docs/30-design/02-event_prehook.md:3, src/runtime/tasks/pick.rs:21, src/runtime/tasks/parse.rs:45, src/runtime/collector/realtime/picker/worker.rs:18）。
- **线性解析算法**：WPL/OML 解析器建立在 winnow 组合子之上，`take_key`、`quot_str`、`take_parentheses` 等函数在 `&mut &str` 上顺序推进，不生成临时 AST；只有在需要反转义时才调用 `decode_escapes`，因此解析成本只和日志长度相关，与规则复杂度几乎无关（crates/wp-lang/src/parser/utils.rs:1, crates/wp-lang/src/parser/utils.rs:151, crates/wp-lang/src/parser/wpl_fun.rs:3）。
- **调度策略与调优**：ActPicker 将 post/pull 策略化，post 阶段用 burst 配额+指数退避控制发送节奏，pull 阶段以固定 LO/HI 水位决定是否补水，pending 队列既能当缓冲又不会失控；再配合“当前/内存优先/吞吐优先/均衡”四档参数模板，现场只需按场景选档即可稳定在目标水位（docs/30-design/03-pick_policy.md:5, docs/30-design/04-pick_tuning.md:12）。

## 高可靠
- **知识库多形态**：KnowDB 在小数据场景用线程克隆（每线程零锁访问）、中/大数据场景用 WAL+只读池（共享 OS 缓存）并保留纯内存模式；authority.sqlite 是统一快照，既可回滚也可跨环境复现（docs/30-design/08-knowledge_db.md:13）。
- **救急链路结构化回放**：RescueEntry V1 用带 version 的 JSON 行携带 `DataRecord/Raw`，恢复时重新调用 `send_record`/`send_raw`，从源头保证回放与实时输出一致；解析失败立即 fail-fast，避免悄悄写出坏数据（docs/30-design/09-rescue.md:16）。
- **统一监控通道**：TaskManager 控制 Monitor/Infra/Sink/Parser/Picker 的生命周期，MonSend 是唯一统计出口，确保任何阶段无人消费都会被立即发现，避免 silent failure（docs/30-design/01-architecture.md:18）。

## 好运维
- **配置安全默认 + 可回退**：面向用户的配置只有布尔/枚举开关，复杂阈值在代码中使用常量+自适应控制；SourceEvent 可保留旧式“recv 内 normalize”开关，ActPicker 可切换最保守策略，KnowDB 也能在三种模式间快速切换，出现问题即可即时回退（docs/30-design/01-architecture.md:29, docs/30-design/02-event_prehook.md:96, docs/30-design/03-pick_policy.md:50, docs/30-design/08-knowledge_db.md:29）。
- **扩展生态**：TCP Source Factory 支持一个 connector 根据 `instances` 配置生成多 SourceInstance，并将 AcceptorHandle 解耦，上层 orchestrator 易于按租户、端口部署；PipeProcessor 插件通过宏批量注册，自定义解析/转换链路无需 fork 引擎（docs/30-design/05-tcp_source.md:8, docs/30-design/07-pipe-processor.md:10）。
