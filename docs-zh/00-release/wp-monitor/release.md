# Wp-Monitor 发布说明

## 下载

```
curl -sSf https://get.warpparse.ai/inst-x.sh | bash -s -- monitor-docker alpha
curl -sSf https://get.warpparse.ai/inst-x.sh | bash -s -- monitor-docker beta
```
体验
```
git clone https://github.com/wp-labs/wp-examples.git
cd  wp-examples/long-demo
run.sh 

```
打开 http://localhost:10428/


## 0.6.0
### Added
- 可视化：统一查看 Source、Parse、Sink 处理统计数据
- MISS 数据观察：识别未命中规则的数据，并支持导出分析。
- 时间窗口观察：查看实时或历史时间段内的数据表现。
- 趋势观察：判断流量变化是瞬时波动还是持续异常。
