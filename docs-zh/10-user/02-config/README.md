# 配置指南
<!-- 角色：使用配置者 | 最近验证：2025-12-21 -->

本文聚焦 wparse 运行所依赖的配置。建议从“运行主配置（wparse.toml）”开始，随后按需阅读源/汇与连接器章节。

推荐阅读顺序
- Wparse 运行配置（主配置）：wparse.toml（本目录）
  - [Wparse 运行配置规范（wparse.toml）](01-wparse.md)
- 配置变量与安全字典
  - [配置变量与安全字典（`${VAR}` / `sec_key.toml`）](08-variables_and_sec_key.md)
- 源（Sources）与连接器
  - [源配置总览（sources）](02-sources.md)
  - 连接器（source.d）见“源配置总览”内的查找规则与示例
- 汇（Sinks）与连接器
  - [Sink 配置](03-sinks.md)
  - 连接器（sink.d）与 route 细节见“设计与配置”
- Wpgen 生成配置
  - [Wpgen 配置](04-wpgen.md)

相关参考
- 参考参数与规格：docs/80-reference 下各 Source/Sink/Spec 文档
- CLI：docs/cli/wparse.md（快速查看常用选项）

提示
- 使用 `wproj conf init --work-root .` 可初始化标准目录与模板（conf/、connectors/ 与部分 models 目录）。若需要知识库（KnowDB）模板，请另行执行 `wproj knowdb init`。
- 修改场景流程后，建议运行 `usecase/core/getting_started/case_verify.sh` 验证端到端产出。
- 涉及账号、密码、Token、DSN 等敏感值时，建议统一通过外部变量或安全字典注入，不要把明文直接写入 route / connector 配置。
