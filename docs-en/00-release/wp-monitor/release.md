# Wp-Monitor Release Notes

## Download

```
curl -sSf https://get.warpparse.ai/inst-x.sh | bash -s -- monitor-docker alpha
curl -sSf https://get.warpparse.ai/inst-x.sh | bash -s -- monitor-docker beta
```

Quick start
```
git clone https://github.com/wp-labs/wp-examples.git
cd wp-examples/long-demo
./run.sh
```

Open http://localhost:10428/

## 0.6.0

### Added
- Visualization: Unified view of Source, Parse, and Sink processing statistics
- MISS data observation: Identify unmatched data and support export for analysis
- Time window observation: View real-time or historical data performance
- Trend observation: Determine whether traffic changes are transient fluctuations or sustained anomalies
