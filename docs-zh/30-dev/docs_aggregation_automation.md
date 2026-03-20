# 文档聚合自动化方案

## 目标

当前仓库承担的是“文档聚合层”，问题不在 mdBook 构建，而在上游内容进入本仓库的过程仍然依赖手工执行脚本、手工比对和手工提交。自动化方案需要解决 4 件事：

1. 上游来源可配置，而不是把逻辑写死在某一个 shell 脚本里。
2. 本地调试和 CI 拉取要走同一条路径，避免两套流程。
3. 聚合完成后自动更新 `SUMMARY.md`，减少人工漏项。
4. 变更要通过 PR 进入主分支，避免机器人直接覆盖线上文档。

## 方案结构

方案落地为三个组件：

1. `docs-sources.json`
   - 维护所有上游文档源。
   - 每个 source 声明仓库地址、分支、本地调试目录、以及“源目录 -> 目标目录”的映射。
2. `scripts/sync_docs.py`
   - 统一执行同步逻辑。
   - 优先支持本地目录调试，也支持在 CI 中直接 `git clone` 上游仓库。
   - 同步策略默认只做“新增 + 更新”，不主动删除目标目录中的文件，降低误删风险。
3. `.github/workflows/sync-docs.yml`
   - 定时触发、手工触发，或由上游仓库发起 `repository_dispatch`。
   - 同步完成后自动创建 PR。

## 当前配置示例

当前已经把 `wp-motor/docs/usage` 收敛为第一条配置：

```json
{
  "sources": [
    {
      "name": "wp-motor-usage",
      "repo": "https://github.com/wp-labs/wp-motor.git",
      "ref": "main",
      "checkout_subdir": "docs/usage",
      "local_path": "../wp-motor/docs/usage",
      "mappings": [
        { "from": "zh", "to": "docs-zh/10-user" },
        { "from": "en", "to": "docs-en/10-user" }
      ]
    }
  ]
}
```

后续新增来源时，只需要继续追加新的 source 对象即可，不需要再复制一份 shell 脚本。

## 运行方式

本地开发：

```bash
make sync
```

预览但不落盘：

```bash
make sync-dry-run
```

只同步一个来源，且临时指定本地目录：

```bash
python3 scripts/sync_docs.py \
  --source wp-motor-usage \
  --local-override wp-motor-usage=../wp-motor/docs/usage \
  --generate-summary
```

兼容老入口：

```bash
bash sync-usage-docs.sh ../wp-motor/docs/usage
```

## CI 建议

`sync-docs.yml` 推荐保留三种触发方式：

1. `schedule`
   - 兜底同步，避免上游忘记发事件。
2. `workflow_dispatch`
   - 便于人工补跑。
3. `repository_dispatch`
   - 上游项目在文档目录发生变更后，主动通知当前仓库拉取。

如果上游仓库是私有仓库，需要配置 `DOCS_SYNC_TOKEN`，供同步脚本拉取跨仓代码。

## 推荐的上游触发方式

在每个上游仓库增加一个轻量工作流：当 `docs/` 或指定目录发生变化时，向本仓库发送 `repository_dispatch`。这样文档聚合链路就变成：

`上游仓库文档变更 -> 通知 wp-docs -> wp-docs 拉取最新内容 -> 自动建 PR`

这样做比“上游直接推送到聚合仓库”更稳，原因有两个：

1. 聚合逻辑只保留在一个仓库里，避免多处散落。
2. 所有聚合结果都经过 PR，可审计、可回滚。

## 后续扩展建议

后续如果来源继续增多，建议按下面的优先级扩展：

1. 增加 `delete = true/false` 的显式配置，逐个来源决定是否允许删除目标中的陈旧文件。
2. 增加“路径白名单校验”，限制目标目录只能写入 `docs-zh/`、`docs-en/` 下的受控区域。
3. 在同步后增加 Markdown lint、链接检查和 mdBook build，确保 PR 在合并前可直接发布。
4. 为每个来源记录最后同步的 commit SHA，并在 PR 描述中输出“从哪个上游版本同步到了哪个版本”。

## 为什么这套方案比现状更合适

现有方案的问题是：同步逻辑只覆盖一个项目、依赖本地目录结构、没有统一配置入口、没有自动 PR。新方案把“来源声明”“同步执行”“变更入库”拆开后，后续扩展更多仓库不会继续放大维护成本。
