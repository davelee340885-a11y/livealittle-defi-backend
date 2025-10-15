# LAL 智能搜尋服務 - 完整指南

## 🎯 系統概覽

**LAL (LiveaLittle) 智能搜尋服務**是一個完整的 DeFi 投資分析系統，專門用於尋找最佳的 Delta Neutral 投資方案。

### 核心功能

1. **戴維斯雙擊分析** - 識別費用增長快於 TVL 增長的優質 LP 池
2. **Delta Neutral 配對** - 自動匹配最佳對沖方案
3. **成本效益計算** - 精確計算 Gas Fee 和淨收益
4. **智能優化排序** - 綜合評分並推薦最佳方案

### 系統架構

```
用戶請求 → LAL API → 智能搜尋引擎 → 數據聚合器 → 外部 API
                           ↓
                    戴維斯雙擊分析
                           ↓
                    Delta Neutral 配對
                           ↓
                    成本效益計算
                           ↓
                    智能優化排序
                           ↓
                    返回最佳方案
```

---

## 🚀 快速開始

### 1. 本地運行

```bash
# 克隆倉庫
git clone https://github.com/davelee340885-a11y/livealittle-defi-backend.git
cd livealittle-defi-backend

# 安裝依賴
pip install -r requirements.txt

# 啟動服務
python backend/lal_api_server_deploy.py
```

訪問: http://localhost:8001/docs

### 2. 使用部署的 API

**Render 部署地址**: https://lal-smart-search-api.onrender.com

```bash
# 測試 API
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&capital=10000&top_n=3"
```

---

## 📊 API 使用指南

### 端點 1: LAL 智能搜尋

**最核心的功能**：一鍵尋找最佳投資方案

#### GET 請求

```bash
GET /api/v1/lal/smart-search
```

**參數**:

| 參數 | 類型 | 默認值 | 說明 |
|-----|------|--------|------|
| token | string | "ETH" | 目標代幣 |
| capital | float | 10000 | 投資資本（USD） |
| risk_tolerance | string | "medium" | 風險偏好（low/medium/high） |
| min_tvl | float | 5000000 | 最小 TVL 過濾 |
| min_apy | float | 5.0 | 最小 APY 過濾 |
| top_n | int | 5 | 返回前 N 個方案 |

**示例請求**:

```bash
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&capital=10000&risk_tolerance=medium&top_n=5"
```

**響應示例**:

```json
{
  "success": true,
  "data": {
    "query": {
      "token": "ETH",
      "capital": 10000,
      "risk_tolerance": "medium"
    },
    "opportunities": [
      {
        "pool_id": "fc9f488e-8183-416f-a61e-4e5c571d4395",
        "protocol": "uniswap-v3",
        "chain": "Ethereum",
        "symbol": "WETH-USDT",
        "tvl": 161935438,
        "lp_apy": 80.94,
        "funding_apy": 10.95,
        "total_apy": 91.89,
        "gas_cost_annual": 847.58,
        "net_apy": 83.41,
        "net_profit": 8341.19,
        "roi": 984.11,
        "davis_score": 100,
        "davis_category": "極佳",
        "final_score": 99.84
      }
    ],
    "count": 1
  }
}
```

**字段說明**:

- `pool_id`: 池的唯一標識
- `protocol`: 協議名稱（如 uniswap-v3）
- `chain`: 區塊鏈（如 Ethereum, Arbitrum）
- `symbol`: 交易對符號
- `tvl`: 總鎖倉價值（USD）
- `lp_apy`: LP 收益率（%）
- `funding_apy`: 資金費率年化收益率（%）
- `total_apy`: 總收益率（%）
- `gas_cost_annual`: 年化 Gas 成本（USD）
- `net_apy`: 淨收益率（%）
- `net_profit`: 預期淨收益（USD/年）
- `roi`: 投資回報率（%）
- `davis_score`: 戴維斯雙擊評分（0-100）
- `davis_category`: 評級（極佳/優質/良好/一般/不推薦）
- `final_score`: 綜合評分（0-100）

#### POST 請求

```bash
POST /api/v1/lal/smart-search
Content-Type: application/json

{
  "token": "ETH",
  "capital": 10000,
  "risk_tolerance": "medium",
  "min_tvl": 5000000,
  "min_apy": 5.0,
  "top_n": 5
}
```

---

### 端點 2: 戴維斯雙擊分析

**單獨使用戴維斯雙擊分析**

```bash
GET /api/v1/lal/davis-analysis
```

**參數**:

| 參數 | 類型 | 默認值 | 說明 |
|-----|------|--------|------|
| token | string | "ETH" | 目標代幣 |
| min_tvl | float | 5000000 | 最小 TVL |
| min_apy | float | 5.0 | 最小 APY |
| top_n | int | 10 | 返回前 N 個池 |

**示例**:

```bash
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/davis-analysis?token=ETH&min_tvl=10000000&min_apy=10&top_n=10"
```

**響應示例**:

```json
{
  "success": true,
  "data": {
    "token": "ETH",
    "pools": [
      {
        "pool_id": "...",
        "protocol": "uniswap-v3",
        "chain": "Ethereum",
        "symbol": "WETH-USDT",
        "tvl": 161935438,
        "apy": 80.94,
        "apy_base": 80.94,
        "apy_reward": 0,
        "davis_score": 100,
        "category": "極佳",
        "recommendation": "強烈推薦"
      }
    ],
    "count": 10
  }
}
```

---

### 端點 3: 健康檢查

```bash
GET /health
```

**響應**:

```json
{
  "status": "healthy",
  "service": "LAL Smart Search API",
  "version": "1.0.0"
}
```

---

## 💻 客戶端示例

### Python 客戶端

```python
import requests
import json

class LALClient:
    """LAL API 客戶端"""
    
    def __init__(self, base_url="https://lal-smart-search-api.onrender.com"):
        self.base_url = base_url
    
    def smart_search(
        self,
        token="ETH",
        capital=10000,
        risk_tolerance="medium",
        min_tvl=5_000_000,
        min_apy=5.0,
        top_n=5
    ):
        """智能搜尋最佳方案"""
        response = requests.get(
            f"{self.base_url}/api/v1/lal/smart-search",
            params={
                "token": token,
                "capital": capital,
                "risk_tolerance": risk_tolerance,
                "min_tvl": min_tvl,
                "min_apy": min_apy,
                "top_n": top_n
            }
        )
        return response.json()
    
    def davis_analysis(self, token="ETH", min_tvl=5_000_000, min_apy=5.0, top_n=10):
        """戴維斯雙擊分析"""
        response = requests.get(
            f"{self.base_url}/api/v1/lal/davis-analysis",
            params={
                "token": token,
                "min_tvl": min_tvl,
                "min_apy": min_apy,
                "top_n": top_n
            }
        )
        return response.json()
    
    def health_check(self):
        """健康檢查"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()


# 使用示例
if __name__ == "__main__":
    client = LALClient()
    
    # 1. 智能搜尋
    print("🔍 搜尋最佳 ETH 投資方案...")
    result = client.smart_search(token="ETH", capital=10000, top_n=3)
    
    if result["success"]:
        opportunities = result["data"]["opportunities"]
        print(f"\n找到 {len(opportunities)} 個最佳方案:\n")
        
        for i, opp in enumerate(opportunities, 1):
            print(f"{i}. {opp['protocol']} - {opp['symbol']}")
            print(f"   鏈: {opp['chain']}")
            print(f"   淨 APY: {opp['net_apy']:.2f}%")
            print(f"   預期年收益: ${opp['net_profit']:,.0f}")
            print(f"   綜合評分: {opp['final_score']:.2f}/100")
            print()
    
    # 2. 戴維斯雙擊分析
    print("\n📊 戴維斯雙擊分析...")
    davis_result = client.davis_analysis(token="BTC", top_n=5)
    
    if davis_result["success"]:
        pools = davis_result["data"]["pools"]
        print(f"\n找到 {len(pools)} 個優質 BTC 池:\n")
        
        for i, pool in enumerate(pools, 1):
            print(f"{i}. {pool['symbol']} - 評分: {pool['davis_score']:.2f}/100")
```

### JavaScript 客戶端

```javascript
class LALClient {
  constructor(baseUrl = "https://lal-smart-search-api.onrender.com") {
    this.baseUrl = baseUrl;
  }

  async smartSearch({
    token = "ETH",
    capital = 10000,
    riskTolerance = "medium",
    minTvl = 5000000,
    minApy = 5.0,
    topN = 5
  } = {}) {
    const params = new URLSearchParams({
      token,
      capital,
      risk_tolerance: riskTolerance,
      min_tvl: minTvl,
      min_apy: minApy,
      top_n: topN
    });

    const response = await fetch(
      `${this.baseUrl}/api/v1/lal/smart-search?${params}`
    );
    return await response.json();
  }

  async davisAnalysis({
    token = "ETH",
    minTvl = 5000000,
    minApy = 5.0,
    topN = 10
  } = {}) {
    const params = new URLSearchParams({
      token,
      min_tvl: minTvl,
      min_apy: minApy,
      top_n: topN
    });

    const response = await fetch(
      `${this.baseUrl}/api/v1/lal/davis-analysis?${params}`
    );
    return await response.json();
  }

  async healthCheck() {
    const response = await fetch(`${this.baseUrl}/health`);
    return await response.json();
  }
}

// 使用示例
const client = new LALClient();

// 智能搜尋
client.smartSearch({ token: "ETH", capital: 10000, topN: 3 })
  .then(result => {
    if (result.success) {
      const opportunities = result.data.opportunities;
      console.log(`找到 ${opportunities.length} 個最佳方案`);
      
      opportunities.forEach((opp, i) => {
        console.log(`\n${i + 1}. ${opp.protocol} - ${opp.symbol}`);
        console.log(`   淨 APY: ${opp.net_apy.toFixed(2)}%`);
        console.log(`   預期年收益: $${opp.net_profit.toFixed(0)}`);
      });
    }
  });
```

---

## 🎯 使用場景

### 場景 1: 尋找最佳投資機會

**目標**: 投資 $10,000 到 ETH 相關的 LP 池

```python
client = LALClient()
result = client.smart_search(
    token="ETH",
    capital=10000,
    risk_tolerance="medium",
    top_n=5
)

# 選擇最佳方案
best = result["data"]["opportunities"][0]
print(f"最佳方案: {best['protocol']} - {best['symbol']}")
print(f"預期年收益: ${best['net_profit']:,.0f}")
print(f"淨 APY: {best['net_apy']:.2f}%")
```

### 場景 2: 比較不同代幣

```python
tokens = ["ETH", "BTC", "USDC"]

for token in tokens:
    result = client.smart_search(token=token, capital=10000, top_n=1)
    if result["success"] and result["data"]["opportunities"]:
        best = result["data"]["opportunities"][0]
        print(f"{token}: {best['net_apy']:.2f}% APY, ${best['net_profit']:,.0f}/年")
```

### 場景 3: 風險偏好調整

```python
# 低風險
low_risk = client.smart_search(
    token="ETH",
    capital=10000,
    risk_tolerance="low",
    min_tvl=50_000_000  # 只選擇大池
)

# 高風險
high_risk = client.smart_search(
    token="ETH",
    capital=10000,
    risk_tolerance="high",
    min_tvl=1_000_000,  # 允許小池
    min_apy=20.0        # 高收益要求
)
```

---

## 📈 理解評分系統

### 戴維斯雙擊評分（0-100）

**評分維度**:
1. **APY 評分**（40%）- 收益率高低
2. **TVL 評分**（30%）- 流動性規模
3. **穩定性評分**（30%）- 基礎 APY 佔比

**評級標準**:
- **90-100 分**: 極佳 - 強烈推薦
- **70-89 分**: 優質 - 推薦
- **50-69 分**: 良好 - 可考慮
- **30-49 分**: 一般 - 謹慎
- **0-29 分**: 不推薦 - 避免

### 綜合評分（0-100）

**評分維度**（根據風險偏好調整）:

**中等風險**:
- 淨 APY（40%）
- 戴維斯評分（30%）
- TVL（20%）
- ROI（10%）

**低風險**:
- 淨 APY（30%）
- 戴維斯評分（20%）
- TVL（30%）- 更重視流動性
- ROI（20%）

**高風險**:
- 淨 APY（50%）- 更重視收益
- 戴維斯評分（30%）
- TVL（10%）
- ROI（10%）

---

## 🔧 進階使用

### 自定義過濾條件

```python
# 只要 Arbitrum 上的池
result = client.smart_search(
    token="ETH",
    capital=10000,
    min_tvl=10_000_000,
    min_apy=20.0,  # 高收益
    top_n=10
)

# 手動過濾 Arbitrum
arbitrum_pools = [
    opp for opp in result["data"]["opportunities"]
    if opp["chain"] == "Arbitrum"
]
```

### 批量分析

```python
import concurrent.futures

def analyze_token(token):
    result = client.smart_search(token=token, capital=10000, top_n=1)
    if result["success"] and result["data"]["opportunities"]:
        return {
            "token": token,
            "best_apy": result["data"]["opportunities"][0]["net_apy"]
        }
    return None

tokens = ["ETH", "BTC", "USDC", "USDT", "DAI"]

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(analyze_token, tokens))

# 排序
results = [r for r in results if r]
results.sort(key=lambda x: x["best_apy"], reverse=True)

for r in results:
    print(f"{r['token']}: {r['best_apy']:.2f}% APY")
```

---

## 📊 性能優化

### 緩存策略

API 內部使用緩存：
- LP 池數據: 5 分鐘
- 代幣價格: 10 秒
- 資金費率: 5 分鐘

**建議**:
- 避免短時間內重複請求相同參數
- 使用客戶端緩存進一步優化

### 請求優化

```python
# ❌ 不好的做法
for i in range(100):
    result = client.smart_search(token="ETH")  # 重複請求

# ✅ 好的做法
result = client.smart_search(token="ETH", top_n=100)  # 一次獲取更多
```

---

## 🐛 錯誤處理

### 常見錯誤

**1. 服務休眠（Free 計劃）**

```python
import time

def smart_search_with_retry(client, max_retries=3):
    for i in range(max_retries):
        try:
            result = client.smart_search()
            return result
        except Exception as e:
            if i < max_retries - 1:
                print(f"重試 {i+1}/{max_retries}...")
                time.sleep(10)  # 等待服務喚醒
            else:
                raise
```

**2. 無可用方案**

```python
result = client.smart_search(token="UNKNOWN")

if result["success"]:
    if result["data"]["count"] == 0:
        print("未找到符合條件的方案，請調整過濾條件")
    else:
        # 處理結果
        pass
```

---

## 📞 支持和反饋

- **GitHub**: https://github.com/davelee340885-a11y/livealittle-defi-backend
- **Issues**: https://github.com/davelee340885-a11y/livealittle-defi-backend/issues
- **Email**: davelee340885@gmail.com

---

**LAL 智能搜尋服務 - 讓 DeFi 投資更智能！** 🚀

