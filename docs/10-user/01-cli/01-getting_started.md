# GettingStarted
<<<<<<< HEAD
=======

本文基于 `wp-example/core/getting_started` 用例，梳理一次从初始化到运行、统计与校验的完整配置流程，适合首次接入与本地自测。
>>>>>>> 67a6813c4c73265246df81e69b2f9addd4e01b62

## 前置准备
- [下载 wparse](https://github.com/wp-labs/warp-parse/releases)
- copy到可执行路径下。如 /usr/local/bin 或 /${HOME}/bin

## 一、初始化工作目录
- 清理并初始化配置与模板
  ```bash
  wproj init --mode full
  wproj check 
  ```

执行完成后，工作目录将包含：
```
├── conf
│   ├── wparse.toml
│   └── wpgen.toml
├── connectors
│   ├── sink.d
│   └── source.d
├── data
│   ├── in_dat
│   ├── logs
│   ├── out_dat
│   └── rescue
├── models
│   ├── knowledge
│   ├── oml
│   └── wpl
└── topology
    ├── sinks
    └── sources
```

## 二、生成数据与清理
```bash
<<<<<<< HEAD
wproj data clean 
wpgen data clean 
=======
# 清理输出（文件型 sink、本地数据）
wproj data clean 
wpgen  data clean 
>>>>>>> 67a6813c4c73265246df81e69b2f9addd4e01b62

# 生成样本（示例 3000 行，3 秒统计间隔）
wpgen sample -n 3000 --stat 3
```

## 三、运行解析
```bash
# 批处理（-n 指定条数，-p 打印统计；失败时查看 ./logs/ 下日志）
wparse batch --stat 3 -p  
```
## 四、统计与校验
```bash
<<<<<<< HEAD
wproj stat file
=======
# 同时统计源与文件型 sink
wproj  data stat
>>>>>>> 67a6813c4c73265246df81e69b2f9addd4e01b62
```
