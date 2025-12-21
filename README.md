# 文档导航（Warp Parse）

新用户阅读路径（建议 3-4 步）
1) 快速入门：user/getting_started/quickstart.md（能跑起来）
2) 实操配置：user/config/sources.md 与 user/config/sinks_design_and_config.md（最小示例与常见错误）
3) 角色化入口：user/（配置）、decision/（选型）、dev/（开发）
4) 骨架实践：user/config/sinks_minimal.md（可复制的目录骨架）

快速入口
- 入门与用例：
  - user/getting_started/quickstart.md
  - user/getting_started/case-verify.md
- 统一配置与模型：
  - user/sinks/sinks_routing.md, user/sinks/sinks_connectors.md, user/sinks/sinks_defaults_expect.md
- 具体配置：
  - user/config/sources.md, user/config/sinks_design_and_config.md
  - user/config/wpgen_output_connectors.md, user/sinks/sinks_defaults_expect.md
- CLI 与工具：
  - user/cli/wpkit.md, user/cli/wparse.md, user/cli/wpgen.md
- 参考与参数：
  - reference/schemas/*, reference/params/*
- 设计与 ADR：
  - decision/architecture.md
  - decision/adr/2025-io-config.md, decision/adr/2025-syslog-source.md
- 迁移与指南：
  - user/guides/troubleshooting.md
  - user/guides/migration/source_wpl_to_new.md
  - user/guides/migration/sinks_v1_to_new.md
- 规划与待办：
  - TODO.md
- 现有完整文档与示例：
  - decision/adr/syslog_source_design_decision.md
  - user/config/sinks_minimal.md

说明
- 统一入口文档整合了源/汇的目录结构、Schema、Factory 流程、白名单覆写与 tags 注入等内容。
- 专题文档（例如 Syslog 设计、迁移指南）提供深入背景与最佳实践。
建议从角色入口开始阅读；如需权威参数与 Schema，请以 user/config/ 与 reference/ 为准。

## 术语对齐表（简）
- Source（源）：数据输入组件，配置文件位于 `models/sources/wpsrc.toml`，连接器在 `connectors/source.d/`。
- Sink（汇）：数据输出组件，路由位于 `models/sinks/{business.d,infra.d}`，连接器在 `connectors/sink.d/`。
- Connector（连接器）：复用的连接定义，包含 `id/type/params/allow_override`，业务通过 `connect` 引用并在白名单内覆写。
- Factory（工厂）：按 `kind` 构建 Source/Sink 实例的插件接口（运行期），注册于应用入口。
- ResolvedSpec（解析规格）：装配后的统一输入，包含 `group/name/kind/connector_id/params/...`。
- Group（组）：业务组（business.d）与基础组（infra.d）。业务组支持 `parallel` 并行（多协程消费、可文件分片）；基础组不支持 `parallel`，也不支持文件分片（replica_shard/file_template）。
- OML（对象模型）：对象模型目录，默认 `./oml`，用于匹配与注入公共字段。

常见故障定位（Quick Triage）
- connectors 未找到：确认工作目录下存在 `connectors/source.d` 或 `connectors/sink.d`，并符合“从 models/<side> 向上查找最近目录（≤32 层）”规则。
- 工厂未注册：确保 CLI 在启动时调用 `plugins::register_sinks()` 与 `register_sources_factory_only()`；`wpkit` 会默认注册，定制 CLI 需手动注册。
- 覆写报错：核对对应 connector 的 `allow_override` 列表；覆写表内禁止再嵌套 `params/params_override`（需扁平书写）。
- tags 校验未过：数量 ≤4；key `[A-Za-z0-9_.-]{1,32}`；value `[A-Za-z0-9_.:/=@+,-]{0,64}`；建议减少高基数。
- feature 缺失：Kafka/DB 等需按 Cargo feature 启用；未启用会在校验/构建阶段快速失败。
