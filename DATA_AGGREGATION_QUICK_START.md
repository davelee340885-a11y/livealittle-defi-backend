# 數據聚合與驗證系統：快速開始指南

本指南幫助您快速上手 LiveaLittle DeFi 的多源數據聚合與驗證系統。

---

## 🚀 快速開始

### 步驟 1：安裝依賴

```bash
pip3 install aiohttp
```

### 步驟 2：運行測試

```bash
cd /home/ubuntu/defi_system/backend
python3 multi_source_data_aggregator.py
```

您應該看到類似以下的輸出：

```
==================================================
Fetching consensus price for ETH...
==================================================
✅ Consensus Price: $4105.13
   Standard Deviation: $1.98
   Data Points: 2
   Sources: coingecko, defillama
```

---

## 📋 基本用法

### 獲取單個代幣的共識價格

```python
import asyncio
from multi_source_data_aggregator import MultiSourceAggregator

async def main():
    aggregator = MultiSourceAggregator()
    
    # 獲取 ETH 價格
    consensus = await aggregator.get_consensus_price("ETH")
    
    if consensus:
        print(f"Price: ${consensus['price']:.2f}")
        print(f"Data Points: {consensus['data_points']}")
        print(f"Sources: {', '.join(consensus['sources'])}")

asyncio.run(main())
```

### 批量獲取多個代幣價格

```python
import asyncio
from multi_source_data_aggregator import MultiSourceAggregator

async def get_multiple_prices():
    aggregator = MultiSourceAggregator()
    tokens = ["BTC", "ETH", "USDC"]
    
    results = {}
    for token in tokens:
        consensus = await aggregator.get_consensus_price(token)
        if consensus:
            results[token] = consensus['price']
    
    return results

# 運行
prices = asyncio.run(get_multiple_prices())
for token, price in prices.items():
    print(f"{token}: ${price:.2f}")
```

### 檢查數據質量

```python
import asyncio
from multi_source_data_aggregator import MultiSourceAggregator
from data_quality_monitor import DataQualityMonitor

async def check_data_quality():
    aggregator = MultiSourceAggregator()
    monitor = DataQualityMonitor()
    
    # 獲取數據
    token = "ETH"
    datapoints = await aggregator.fetch_all_sources(token)
    
    # 驗證
    for dp in datapoints:
        aggregator.validator.validate_datapoint(dp)
    
    # 計算共識
    consensus = aggregator.consensus_engine.calculate_consensus(datapoints)
    
    if consensus:
        # 監控質量
        report = monitor.monitor_consensus(
            token, consensus, datapoints, aggregator.sources
        )
        
        print(f"Overall Quality: {report['quality_metrics']['overall_quality']:.3f}")
        print(f"Freshness: {report['quality_metrics']['freshness']:.3f}")
        print(f"Availability: {report['quality_metrics']['availability']:.3f}")

asyncio.run(check_data_quality())
```

---

## 🔧 集成到 API 服務器

### 在 FastAPI 中使用

```python
from fastapi import FastAPI
from multi_source_data_aggregator import MultiSourceAggregator

app = FastAPI()
aggregator = MultiSourceAggregator()

@app.get("/api/v1/price/{token}")
async def get_token_price(token: str):
    consensus = await aggregator.get_consensus_price(token)
    
    if consensus:
        return {
            "token": token,
            "price": consensus["price"],
            "sources": consensus["sources"],
            "data_points": consensus["data_points"],
            "timestamp": consensus["timestamp"]
        }
    else:
        return {"error": "Failed to get price"}, 503
```

### 定時更新價格

```python
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from multi_source_data_aggregator import MultiSourceAggregator

aggregator = MultiSourceAggregator()
price_cache = {}

async def update_prices():
    """每 30 秒更新一次價格"""
    tokens = ["BTC", "ETH", "USDC"]
    
    for token in tokens:
        consensus = await aggregator.get_consensus_price(token)
        if consensus:
            price_cache[token] = consensus

# 設置調度器
scheduler = AsyncIOScheduler()
scheduler.add_job(update_prices, 'interval', seconds=30)
scheduler.start()

# 保持運行
asyncio.get_event_loop().run_forever()
```

---

## 📊 監控和警報

### 設置警報處理器

```python
from data_quality_monitor import DataQualityMonitor

monitor = DataQualityMonitor()

def handle_alerts(report):
    """處理警報"""
    alerts = report['alerts']
    
    if alerts['system_failure']:
        print("🚨 CRITICAL: System failure!")
        # 發送緊急通知
    
    if alerts['volatility']:
        print(f"⚠️  High volatility detected: {alerts['volatility']}")
        # 記錄到日誌
    
    if alerts['divergence']:
        print(f"⚠️  Data divergence: {alerts['divergence']}")
        # 觸發額外驗證

# 使用
# report = monitor.monitor_consensus(...)
# handle_alerts(report)
```

---

## 🎯 常見問題

### Q: 如何添加新的數據源？

創建一個繼承自 `DataSource` 的新類：

```python
class MyCustomSource(DataSource):
    def __init__(self):
        super().__init__("my_custom_source")
        self.api_url = "https://api.example.com"
    
    async def fetch_price(self, token: str) -> Optional[DataPoint]:
        # 實現獲取邏輯
        pass

# 添加到聚合器
aggregator = MultiSourceAggregator()
aggregator.sources.append(MyCustomSource())
```

### Q: 如何調整異常檢測的閾值？

在調用檢測函數時傳入自定義閾值：

```python
# 價格波動閾值設為 5%
volatility_alert = monitor.anomaly_detector.check_price_volatility(
    token, new_price, threshold=0.05
)

# 數據源分歧閾值設為 3%
divergence_alert = monitor.anomaly_detector.check_data_source_divergence(
    token, datapoints, consensus_price, threshold=0.03
)
```

### Q: 如何處理數據源失效？

系統會自動檢測並標記失效的數據源。您可以查看狀態：

```python
metrics = aggregator.get_data_quality_metrics()

for source_name, status in metrics['sources_status'].items():
    if not status['available']:
        print(f"❌ {source_name} is unavailable")
        print(f"   Error count: {status['error_count']}")
```

---

## 📈 性能優化

### 使用緩存

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

async def get_cached_price(token: str):
    # 檢查緩存
    cached = redis_client.get(f"price:{token}")
    if cached:
        return json.loads(cached)
    
    # 獲取新價格
    consensus = await aggregator.get_consensus_price(token)
    
    # 緩存 30 秒
    if consensus:
        redis_client.setex(
            f"price:{token}", 
            30, 
            json.dumps(consensus)
        )
    
    return consensus
```

### 並發獲取多個代幣

```python
async def get_all_prices(tokens: List[str]):
    tasks = [aggregator.get_consensus_price(token) for token in tokens]
    results = await asyncio.gather(*tasks)
    
    return {
        token: result 
        for token, result in zip(tokens, results) 
        if result is not None
    }
```

---

## 🔗 相關文檔

- **完整文檔**: `DATA_AGGREGATION_AND_VALIDATION_SYSTEM.md`
- **架構設計**: `data_aggregator_architecture.md`
- **實現代碼**: `multi_source_data_aggregator.py`, `data_quality_monitor.py`

---

**提示**：建議在生產環境中使用日誌記錄和監控工具（如 Sentry）來追蹤系統狀態和異常。

