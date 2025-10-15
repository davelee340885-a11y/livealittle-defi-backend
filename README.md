# LiveaLittle DeFi 監控系統

**LAL 智能搜尋服務** - 尋找最佳 Delta Neutral 投資方案

## 🎯 系統特色

### 1. 戴維斯雙擊分析引擎
- 識別費用增長快於 TVL 增長的優質 LP 池
- 智能評分系統（0-100 分）
- 多維度分析（APY、TVL、穩定性）

### 2. Delta Neutral 策略優化
- 自動配對最佳對沖方案
- 整合 LP 收益 + 資金費率收益
- 風險調整收益計算

### 3. 成本效益分析
- 精確 Gas Fee 估算（支持多鏈）
- 滑點成本計算
- 淨收益和 ROI 分析

### 4. 智能優化排序
- 綜合評分算法
- 風險偏好調整
- 多樣化方案推薦

## 🚀 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 啟動 API 服務器

```bash
cd backend
python3.11 lal_api_server.py
```

API 文檔: http://localhost:8001/docs

### 使用示例

#### Python

```python
import requests

response = requests.get(
    "http://localhost:8001/api/v1/lal/smart-search",
    params={
        "token": "ETH",
        "capital": 10000,
        "risk_tolerance": "medium",
        "top_n": 5
    }
)

opportunities = response.json()["data"]["opportunities"]
print(f"找到 {len(opportunities)} 個最佳方案")
```

#### cURL

```bash
curl "http://localhost:8001/api/v1/lal/smart-search?token=ETH&capital=10000&top_n=5"
```

## 📊 API 端點

### 1. LAL 智能搜尋

```
GET /api/v1/lal/smart-search
```

**參數**:
- `token`: 目標代幣（默認: "ETH"）
- `capital`: 投資資本（默認: 10000）
- `risk_tolerance`: 風險偏好（"low"/"medium"/"high"，默認: "medium"）
- `min_tvl`: 最小 TVL（默認: 5000000）
- `min_apy`: 最小 APY（默認: 5.0）
- `top_n`: 返回前 N 個方案（默認: 5）

**返回示例**:

```json
{
  "success": true,
  "data": {
    "opportunities": [
      {
        "protocol": "uniswap-v3",
        "symbol": "WETH-USDT",
        "chain": "Ethereum",
        "tvl": 161935438,
        "net_apy": 83.41,
        "net_profit": 8341,
        "final_score": 99.84,
        "davis_score": 100
      }
    ]
  }
}
```

### 2. 戴維斯雙擊分析

```
GET /api/v1/lal/davis-analysis
```

**參數**:
- `token`: 目標代幣
- `min_tvl`: 最小 TVL
- `min_apy`: 最小 APY
- `top_n`: 返回前 N 個池

## 📁 項目結構

```
defi_system/
├── backend/
│   ├── davis_double_click_analyzer.py    # 戴維斯雙擊分析引擎
│   ├── unified_data_aggregator.py        # 統一數據聚合器
│   ├── delta_neutral_calculator.py       # Delta Neutral 計算器
│   ├── lal_smart_search.py               # LAL 智能搜尋服務
│   ├── lal_api_server.py                 # LAL API 服務器
│   ├── api_server_v2.py                  # 完整 API 服務器
│   └── test_api_endpoints.py             # API 測試腳本
├── frontend/
│   └── src/
│       └── components/
│           └── Dashboard.js              # 前端儀表板
├── docs/
│   ├── LAL_SMART_SEARCH_ARCHITECTURE.md  # 架構設計文檔
│   ├── DELTA_NEUTRAL_DATA_REQUIREMENTS.md # 數據需求分析
│   ├── DELTA_NEUTRAL_API_GUIDE.md        # API 使用指南
│   └── DEPLOYMENT_GUIDE_V2.md            # 部署指南
└── README.md
```

## 🔧 核心模組

### 1. DavisDoubleClickAnalyzer

識別潛在優質 LP 池

```python
from davis_double_click_analyzer import DavisDoubleClickAnalyzer

analyzer = DavisDoubleClickAnalyzer()
results = analyzer.analyze_token_pools(
    token="ETH",
    min_tvl=5_000_000,
    min_apy=5.0,
    top_n=10
)
```

### 2. UnifiedDataAggregator

獲取實時市場數據

```python
from unified_data_aggregator import UnifiedDataAggregator

aggregator = UnifiedDataAggregator()

# 獲取代幣價格
price = aggregator.get_token_price("ETH")

# 獲取資金費率
funding_rate = aggregator.get_funding_rate("ETH")

# 獲取 LP 池
pools = aggregator.get_lp_pools("ETH")
```

### 3. LALSmartSearch

完整智能搜尋服務

```python
from lal_smart_search import LALSmartSearch

lal = LALSmartSearch()
opportunities = lal.search(
    token="ETH",
    capital=10000,
    risk_tolerance="medium",
    top_n=5
)
```

## 📈 數據源

| 數據類型 | 數據源 | 更新頻率 |
|---------|-------|---------|
| LP 池數據 | DeFiLlama | 5 分鐘 |
| 代幣價格 | CoinGecko | 即時 |
| 資金費率 | Hyperliquid | 每小時 |
| 市場情緒 | Alternative.me | 每天 |

## 🎯 使用場景

### 場景 1: 尋找最佳投資機會

```python
lal = LALSmartSearch()
opportunities = lal.search(
    token="ETH",
    capital=10000,
    risk_tolerance="medium"
)

# 查看最佳方案
best = opportunities[0]
print(f"協議: {best['protocol']}")
print(f"池: {best['symbol']}")
print(f"淨 APY: {best['net_apy']:.2f}%")
print(f"預期年收益: ${best['net_profit']:,.0f}")
```

### 場景 2: 分析特定池

```python
analyzer = DavisDoubleClickAnalyzer()
results = analyzer.analyze_token_pools(
    token="BTC",
    min_tvl=10_000_000,
    min_apy=10.0
)

for pool in results[:5]:
    print(f"{pool['symbol']}: {pool['davis_score']:.2f}/100")
```

### 場景 3: 監控市場數據

```python
aggregator = UnifiedDataAggregator()

# 獲取多個代幣的價格
tokens = ["ETH", "BTC", "USDC"]
for token in tokens:
    price_data = aggregator.get_token_price(token)
    print(f"{token}: ${price_data['price']:,.2f}")
```

## 🚀 部署

### 本地部署

```bash
cd backend
python3.11 lal_api_server.py
```

### Docker 部署

```bash
docker build -t lal-api .
docker run -p 8001:8001 lal-api
```

### Render 部署

參見 [DEPLOYMENT_GUIDE_V2.md](docs/DEPLOYMENT_GUIDE_V2.md)

## 📊 性能指標

- **搜尋時間**: < 10 秒
- **數據新鮮度**: < 5 分鐘
- **準確率**: > 90%
- **可用性**: > 99%

## 🔐 安全考慮

- API Rate Limiting
- 數據驗證
- 錯誤處理
- 審計日誌

## 📝 許可證

MIT License

## 👥 貢獻

歡迎提交 Issue 和 Pull Request！

## 📞 聯繫方式

- GitHub: [davelee340885-a11y](https://github.com/davelee340885-a11y)
- Email: davelee340885@gmail.com

---

**LiveaLittle DeFi** - 讓 DeFi 投資更智能 🚀

