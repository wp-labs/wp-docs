# Wp-Monitor

![Wp-Monitor](../../images/Wp-Monitor.jpg)

## 1. 文档说明

本文档用于说明 Wp-Monitor 这个应用的用途、适用场景、使用方式，以及正式使用前需要完成的准备工作。

## 2. 应用简介

Wp-Monitor 是一个面向 WarpParse 数据链路的统一监控应用，用来帮助使用方快速了解日志流量在整条处理链路中的运行状态。

它关注的不是单个组件本身，而是整条链路的运行结果和异常表现，重点回答以下问题：

- 当前链路是否在正常处理数据。
- 数据流量主要分布在哪些环节。
- 是否存在未被规则命中的 MISS 数据。
- 下游输出是否稳定、是否存在明显损耗或异常。

对于日常巡检、问题排查和故障复盘，Wp-Monitor 提供的是一个统一入口，而不是分散查看多套系统。

## 3. 核心价值

Wp-Monitor 的核心价值主要体现在以下几个方面：

- 全链路可视化：将 Source、Parse、Sink、Miss 统一放在一个视图中展示。
- 快速定位异常：支持从层级观察进入节点观察，缩短排障路径。
- 支撑问题复盘：可以围绕时间窗口查看异常波动和 MISS 数据。
- 统一认知口径：让业务、平台和运维对链路状态有一致的观察入口。

## 4. 应用主要能力

### 4.1 链路总览

应用首页提供统一链路视图，可用于观察整个数据处理过程中的主要层级和运行状态，包括：

- 来源层
- Parse 层
- 输出层
- Miss 区域

使用者可以先从整体看链路是否平稳，再逐步进入局部定位异常点。

### 4.2 时间窗口观察

应用支持按时间范围查看链路状态。

这意味着使用者可以：

- 查看当前实时或近实时状态。
- 查看某一段历史时间窗口内的数据表现。
- 对照故障发生时间回看链路变化。

时间窗口是使用本应用时最重要的观察入口之一，建议先确定排查时间范围，再查看对应链路状态。

### 4.3 MISS 数据观察

应用支持对 MISS 数据进行查看。

这里的 MISS，主要指未命中规则、未正常进入预期处理路径的数据。通过 MISS 视图，使用者可以：

- 判断是否存在明显未命中数据。
- 在需要时导出相关数据用于分析。

### 4.4 趋势观察

应用支持基于时间窗口观察趋势变化。

这类能力适用于：

- 查看流量是否持续增长或下降。
- 判断波动是瞬时抖动还是持续异常。
- 辅助分析问题发生前后的变化趋势。

## 5. 使用前提准备

必要组件包括：

- VictoriaMetrics: 用于存储和查询指标数据。
- VictoriaLogs: 用于存储和查询 MISS 数据。
- WarpParse: 用于处理数据,是本项目的主要监控对象。

本项目是基于 WarpParse 数据链路的监控应用，需要先部署 WarpParse 数据链路才能使用。

### 5.1 安装 VictoriaMetrics 以及 VictoriaLogs

仓库中提供了 VictoriaMetrics 和 VictoriaLogs 的 `docker-compose.yml` 配置文件，可用于快速部署：[docker-compose.yml](../docker-compose.yml)

### 5.2 WarpParse 中的必要配置

需要在 `connectors` 中配置 VictoriaMetrics 和 VictoriaLogs 的 `sink` 连接，用于将数据发送到这两个组件中。

- VictoriaMetrics: 用于存储和查询指标数据。

```toml
[[connectors]]
id = "victoriametrics_sink"
type = "victoriametrics"
allow_override = ["insert_url", "flush_interval_secs"]
[connectors.params]
insert_url = "http://127.0.0.1:8428/api/v1/import/prometheus"   # VictoriaMetrics 接口地址
flush_interval_secs = 1                                         # 推送至 VictoriaMetrics 的时间间隔
```

- VictoriaLogs: 用于存储和查询 MISS 数据。

```toml
[[connectors]]
id = "victorialogs_sink"
type = "victorialogs"
allow_override = ["endpoint", "insert_path", "flush_interval_secs", "create_time_field","batch_size", "tags"]
[connectors.params]
endpoint = "http://127.0.0.1:9428"   # VictoriaLogs 接口地址
insert_path = "/insert/jsonline"     # VictoriaLogs 接口路径
flush_interval_secs = 1              # 推送至 VictoriaLogs 的时间间隔
```

在 `infra.d/monitor.toml` 中配置 VictoriaMetrics：

```toml
[[sink_group.sinks]]
name = "victoriametrics"
connect = "victoriametrics_sink"
```

在 `infra.d/miss.toml` 中配置 VictoriaLogs：

```toml
[[sink_group.sinks]]
name = "victorialogs_output"
connect = "victorialogs_sink"
params = { endpoint = "http://127.0.0.1:9428", insert_path = "/insert/jsonline", tags = ["wp_stage:miss"] }     # 注意这里必须配置 tags，且 tags 中必须包含 wp_stage:miss，否则查询不到数据
```

warp-parse启动命令：

```bash
wparse daemon --stat 1
```

## 6. 总结

Wp-Monitor 的定位是一个面向 WarpParse 数据链路的统一观察入口。

它的核心作用可以概括为三点：

- 告诉使用者这个链路当前在发生什么。
- 帮助使用者快速判断问题大致出在哪里。
- 支持围绕时间窗口对异常和 MISS 数据进行进一步分析。

只要前置接入和环境准备完成，使用者就可以借助这一应用完成日常巡检、问题排查等工作。
