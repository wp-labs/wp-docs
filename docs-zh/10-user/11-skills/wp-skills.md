# wp-skills

`wp-skills` 是面向 WarpParse 的 AI 技能集合，在使用skills之前，您需要具备使用AI agent的基础知识，并且已经安装了支持skills的AI工具（如Claude、Codex等）。`wp-skills` 目前包含以下技能：

### `wp-deploy`

用于 WarpParse 的部署和配置指导，主要处理：

- `connectors/source.d` / `connectors/sink.d`
- `topology/sources` / `topology/sinks`
- `conf/wparse.toml`
- `conf/wpgen.toml`
- `wp-monitor/config/app.toml`
- 联调接线、部署说明、观察链路是否跑通

适合这样的问题：

- 帮我加一个 `file source`
- 帮我把 `source` 和 `sink` 接起来
- 帮我补一个 `wpgen` 做回放
- 帮我接上 `wp-monitor` 看指标和 MISS

### `wpl-rule-check`

用于根据日志样本编写和验证 `WPL` / `OML`，主要处理：

- 分析原始日志样本
- 编写 `parse.wpl`
- 编写 `.oml`
- 使用 `wpl-check` 验证规则
- 排查规则为什么匹配不上

适合这样的问题：

- 这条日志帮我写规则
- 这个字段怎么提取
- 帮我写 `OML`
- 这条规则为什么匹配失败

## 安装命令

安装 `wp-skills alpha`：

```bash
curl -sSf https://get.warpparse.ai/inst-x.sh | bash -s -- wp-skills alpha
```

该命令会提示你选择需要的skill，选择后，会安装到如下目录中:
- `~/.claude/skills`
- `~/.codex/skills`

## 怎么使用

安装完成后，就可以在支持 skills 的 AI 工具(codex、claude、opencode)中直接描述你的目标。

例如：

- 帮我配一个 `file source`，把样本跑进 WarpParse
- 帮我增加一个 `file sink`，把结果输出成 JSON
- 帮我接一个 `wpgen`，往 `tcp source` 发送测试数据
- 帮我给链路接上 `wp-monitor`
- 这条日志帮我写 `WPL` 和 `OML`，并验证一下

建议：

- 配置和部署问题优先使用 `wp-deploy`
- 规则编写和验证问题优先使用 `wpl-rule-check`
