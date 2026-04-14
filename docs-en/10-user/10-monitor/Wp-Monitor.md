# Wp-Monitor

![Wp-Monitor](../../images/Wp-Monitor.jpg)

## 1. Document Overview

This document explains what the Wp-Monitor application is used for, its applicable scenarios, how to use it, and the preparations required before production use.

## 2. Application Introduction

Wp-Monitor is a unified monitoring application for the WarpParse data pipeline. It helps users quickly understand the runtime status of log traffic across the full processing chain.

It focuses on the operating results and abnormal behavior of the whole pipeline, rather than a single component. It mainly answers the following questions:

- Whether the current pipeline is processing data normally.
- Where data traffic is mainly distributed across the pipeline.
- Whether MISS data that is not matched by rules exists.
- Whether downstream output is stable, and whether there is obvious loss or abnormal behavior.

For routine inspections, troubleshooting, and incident reviews, Wp-Monitor provides a unified entry point instead of requiring users to check multiple scattered systems.

## 3. Core Value

The core value of Wp-Monitor is mainly reflected in the following aspects:

- Full-pipeline visualization: displays Source, Parse, Sink, and Miss in a unified view.
- Fast anomaly location: supports drilling down from hierarchy-level observation to node-level observation, shortening the troubleshooting path.
- Incident review support: allows users to inspect abnormal fluctuations and MISS data within a time window.
- Unified understanding: provides a consistent observation entry point for business, platform, and operations teams.

## 4. Main Capabilities

### 4.1 Pipeline Overview

The application home page provides a unified pipeline view for observing the main levels and runtime status of the entire data processing flow, including:

- Source layer
- Parse layer
- Output layer
- Miss area

Users can first check whether the overall pipeline is stable, then gradually drill down into local areas to locate abnormal points.

### 4.2 Time Window Observation

The application supports viewing pipeline status by time range.

This means users can:

- View the current real-time or near-real-time status.
- View data behavior within a specific historical time window.
- Compare pipeline changes against the time when an incident occurred.

The time window is one of the most important observation entry points when using this application. It is recommended to determine the troubleshooting time range first, then view the corresponding pipeline status.

### 4.3 MISS Data Observation

The application supports viewing MISS data.

Here, MISS mainly refers to data that does not match rules and does not enter the expected processing path normally. Through the MISS view, users can:

- Determine whether there is obvious unmatched data.
- Export related data for analysis when needed.

### 4.4 Trend Observation

The application supports observing trend changes based on time windows.

This capability is suitable for:

- Checking whether traffic continues to increase or decrease.
- Determining whether a fluctuation is a transient jitter or a persistent anomaly.
- Assisting analysis of trend changes before and after an issue occurs.

## 5. Prerequisites

Required components include:

- VictoriaMetrics: used to store and query metric data.
- VictoriaLogs: used to store and query MISS data.
- WarpParse: used to process data and is the main monitoring target of this project.

This project is a monitoring application based on the WarpParse data pipeline. The WarpParse data pipeline must be deployed before using it.

### 5.1 Install VictoriaMetrics and VictoriaLogs

The repository provides a `docker-compose.yml` configuration file for VictoriaMetrics and VictoriaLogs, which can be used for quick deployment: [docker-compose.yml](../docker-compose.yml)

### 5.2 Required Configuration in WarpParse

Configure the VictoriaMetrics and VictoriaLogs `sink` connections in `connectors` to send data to these two components.

- VictoriaMetrics: used to store and query metric data.

```toml
[[connectors]]
id = "victoriametrics_sink"
type = "victoriametrics"
allow_override = ["insert_url", "flush_interval_secs"]
[connectors.params]
insert_url = "http://127.0.0.1:8428/api/v1/import/prometheus"   # VictoriaMetrics API address
flush_interval_secs = 1                                         # Interval for pushing data to VictoriaMetrics
```

- VictoriaLogs: used to store and query MISS data.

```toml
[[connectors]]
id = "victorialogs_sink"
type = "victorialogs"
allow_override = ["endpoint", "insert_path", "flush_interval_secs", "create_time_field","batch_size", "tags"]
[connectors.params]
endpoint = "http://127.0.0.1:9428"   # VictoriaLogs API address
insert_path = "/insert/jsonline"     # VictoriaLogs API path
flush_interval_secs = 1              # Interval for pushing data to VictoriaLogs
```

Configure VictoriaMetrics in `infra.d/monitor.toml`:

```toml
[[sink_group.sinks]]
name = "victoriametrics"
connect = "victoriametrics_sink"
```

Configure VictoriaLogs in `infra.d/miss.toml`:

```toml
[[sink_group.sinks]]
name = "victorialogs_output"
connect = "victorialogs_sink"
params = { endpoint = "http://127.0.0.1:9428", insert_path = "/insert/jsonline", tags = ["wp_stage:miss"] }     # tags must be configured here and must include wp_stage:miss; otherwise, data cannot be queried
```

WarpParse startup command:

```bash
wparse daemon --stat 1
```

## 6. Summary

Wp-Monitor is positioned as a unified observation entry point for the WarpParse data pipeline.

Its core role can be summarized in three points:

- Tell users what is currently happening in the pipeline.
- Help users quickly determine the approximate location of an issue.
- Support further analysis of anomalies and MISS data around a time window.

After prerequisite integration and environment preparation are complete, users can use this application for routine inspections, troubleshooting, and other related work.
