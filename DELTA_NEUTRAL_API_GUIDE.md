# Delta Neutral API 使用指南

## 📋 概述

本指南介紹如何使用 LiveaLittle DeFi API v2 來獲取 Delta Neutral 策略所需的真實數據。

---

## 🚀 快速開始

### API 基礎信息

- **Base URL**: `http://localhost:8000`
- **API 文檔**: `http://localhost:8000/docs`
- **版本**: v2.0.0
- **數據源**:
  - LP 池數據: DeFiLlama
  - 代幣價格: CoinGecko
  - 資金費率: Hyperliquid
  - 市場情緒: Alternative.me

---

## 📊 API 端點列表

### 1. 健康檢查

**端點**: `GET /`

**描述**: 檢查 API 服務器狀態

**示例**:
```bash
curl http://localhost:8000/
```

**響應**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-15T09:45:28.103154",
  "version": "2.0.0"
}
```

---

### 2. 獲取代幣價格

**端點**: `GET /api/v1/market/tokens`

**描述**: 獲取一個或多個代幣的即時價格

**參數**:
- `symbols` (string): 逗號分隔的代幣符號，例如 "ETH,BTC,USDC"

**示例**:
```bash
curl "http://localhost:8000/api/v1/market/tokens?symbols=ETH,BTC"
```

**響應**:
```json
[
  {
    "symbol": "ETH",
    "price": 4081.37,
    "change_24h": 3.67,
    "volume_24h": 54879548086.28,
    "updated_at": "2025-10-15T09:45:52.912866"
  },
  {
    "symbol": "BTC",
    "price": 111506.0,
    "change_24h": 0.95,
    "volume_24h": 78732652325.52,
    "updated_at": "2025-10-15T09:45:53.908356"
  }
]
```

---

### 3. 獲取 LP 池列表

**端點**: `GET /api/v1/market/pools`

**描述**: 獲取高收益 LP 池列表

**參數**:
- `min_tvl` (float): 最小 TVL 過濾（USD），默認 1,000,000
- `limit` (int): 返回數量限制，默認 50

**示例**:
```bash
curl "http://localhost:8000/api/v1/market/pools?min_tvl=5000000&limit=10"
```

**響應**:
```json
[
  {
    "pool_id": "pool-uuid",
    "protocol": "curve-dex",
    "chain": "Ethereum",
    "symbol": "OETH-WETH",
    "tvl": 104640093.0,
    "apy": 2.49,
    "apy_base": 2.49,
    "apy_reward": 0.0
  }
]
```

---

### 4. 獲取資金費率

**端點**: `GET /api/v1/market/funding-rates`

**描述**: 獲取永續合約資金費率（來自 Hyperliquid）

**參數**:
- `coins` (string): 逗號分隔的代幣符號，例如 "ETH,BTC"

**示例**:
```bash
curl "http://localhost:8000/api/v1/market/funding-rates?coins=ETH,BTC"
```

**響應**:
```json
[
  {
    "coin": "ETH",
    "current_rate_pct": 0.00125,
    "avg_rate_pct": 0.00125,
    "annualized_rate_pct": 10.95,
    "source": "Hyperliquid",
    "updated_at": "2025-10-15T09:46:05.986522"
  },
  {
    "coin": "BTC",
    "current_rate_pct": 0.00125,
    "avg_rate_pct": 0.00125,
    "annualized_rate_pct": 10.95,
    "source": "Hyperliquid",
    "updated_at": "2025-10-15T09:46:06.269131"
  }
]
```

**說明**:
- `current_rate_pct`: 當前資金費率（%）
- `avg_rate_pct`: 平均資金費率（%）
- `annualized_rate_pct`: 年化資金費率（%）
- Hyperliquid 每小時結算一次，年化公式: `avg_rate * 24 * 365 * 100`

---

### 5. 獲取市場情緒

**端點**: `GET /api/v1/market/sentiment`

**描述**: 獲取恐懼與貪婪指數

**示例**:
```bash
curl "http://localhost:8000/api/v1/market/sentiment"
```

**響應**:
```json
{
  "value": 34,
  "classification": "Fear",
  "timestamp": "2025-10-15T00:00:00"
}
```

**分類**:
- 0-24: Extreme Fear（極度恐懼）
- 25-49: Fear（恐懼）
- 50-74: Greed（貪婪）
- 75-100: Extreme Greed（極度貪婪）

---

### 6. 獲取 Delta Neutral 機會 ⭐

**端點**: `GET /api/v1/delta-neutral/opportunities`

**描述**: 尋找最佳 Delta Neutral 策略機會

**參數**:
- `token` (string): 目標代幣，默認 "ETH"
- `capital` (float): 投入資本（USD），默認 10000
- `min_tvl` (float): 最小 TVL（USD），默認 1000000
- `top_n` (int): 返回前 N 個機會，默認 10

**示例**:
```bash
curl "http://localhost:8000/api/v1/delta-neutral/opportunities?token=ETH&capital=10000&top_n=5"
```

**響應**:
```json
[
  {
    "pool_id": "077b47b8-76c9-4081-97f2-9ca43ebdbaa0",
    "protocol": "curve-dex",
    "chain": "Ethereum",
    "symbol": "OETH-WETH",
    "tvl": 104640093.0,
    "lp_apy": 2.49,
    "funding_apy": 10.95,
    "total_apy": 11.44,
    "annual_yield": 1144.28,
    "score": 45.72
  }
]
```

**說明**:
- `total_apy` = `lp_apy` + `funding_apy`
- `annual_yield` = `capital` * (`total_apy` / 100)
- `score`: 綜合評分（0-100），考慮 APY、TVL、無常損失風險

---

### 7. 生成策略報告 ⭐⭐⭐

**端點**: `GET /api/v1/delta-neutral/report`

**描述**: 生成完整的 Delta Neutral 策略報告

**參數**:
- `token` (string): 目標代幣，默認 "ETH"
- `capital` (float): 投入資本（USD），默認 10000

**示例**:
```bash
curl "http://localhost:8000/api/v1/delta-neutral/report?token=ETH&capital=10000"
```

**響應**:
```json
{
  "token": "ETH",
  "capital": 10000.0,
  "timestamp": "2025-10-15T09:46:39.844994",
  "market_data": {
    "token_price": 4083.0,
    "price_change_24h": 3.71,
    "fear_greed_index": 34,
    "market_sentiment": "Fear"
  },
  "best_opportunity": {
    "pool_id": "077b47b8-76c9-4081-97f2-9ca43ebdbaa0",
    "protocol": "curve-dex",
    "chain": "Ethereum",
    "symbol": "OETH-WETH",
    "tvl": 104640093.0,
    "lp_apy": 2.49,
    "funding_apy": 10.95,
    "total_apy": 11.44,
    "annual_yield": 1144.28,
    "il_risk": "no",
    "score": 45.72
  },
  "hedge_info": {
    "lp_value": 10000.0,
    "token_value_in_lp": 5000.0,
    "token_amount": 1.22,
    "token_price": 4083.0,
    "hedge_position_size": 5000.0,
    "hedge_leverage": 1.0
  },
  "top_opportunities": [...],
  "recommendation": "穩健機會（風險等級：低）。市場恐懼，可能是進場好時機"
}
```

---

### 8. 計算對沖比率

**端點**: `POST /api/v1/delta-neutral/calculate-hedge`

**描述**: 計算 Delta Neutral 對沖比率

**參數**:
- `lp_value` (float): LP 倉位價值（USD）
- `token_price` (float): 代幣價格（USD）
- `pool_composition` (float): 池中代幣比例，默認 0.5

**示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/delta-neutral/calculate-hedge?lp_value=10000&token_price=4000&pool_composition=0.5"
```

**響應**:
```json
{
  "lp_value": 10000.0,
  "token_value_in_lp": 5000.0,
  "token_amount": 1.25,
  "token_price": 4000.0,
  "hedge_position_size": 5000.0,
  "hedge_leverage": 1.0
}
```

**說明**:
- `token_value_in_lp`: LP 中目標代幣的價值
- `token_amount`: 需要對沖的代幣數量
- `hedge_position_size`: 對沖倉位大小（USD）

---

### 9. 計算總收益

**端點**: `POST /api/v1/delta-neutral/calculate-yield`

**描述**: 計算 Delta Neutral 策略的總收益

**參數**:
- `lp_apy` (float): LP 池 APY（%）
- `funding_rate_apy` (float): 資金費率 APY（%）
- `capital` (float): 投入資本（USD）
- `gas_cost_annual` (float): 年化 Gas 成本（USD），默認 200

**示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/delta-neutral/calculate-yield?lp_apy=15.5&funding_rate_apy=10.95&capital=10000&gas_cost_annual=200"
```

**響應**:
```json
{
  "lp_apy": 15.5,
  "lp_yield_annual": 1550.0,
  "funding_rate_apy": 10.95,
  "funding_yield_annual": 1095.0,
  "gas_cost_apy": 2.0,
  "gas_cost_annual": 200.0,
  "total_apy": 24.45,
  "total_yield_annual": 2445.0,
  "capital": 10000.0
}
```

---

### 10. 轉倉決策

**端點**: `POST /api/v1/delta-neutral/rebalance-decision`

**描述**: 計算是否應該轉倉

**參數**:
- `current_apy` (float): 當前池 APY（%）
- `new_apy` (float): 新池 APY（%）
- `rebalance_cost` (float): 轉倉成本（USD）
- `capital` (float): 投入資本（USD）
- `min_apy_improvement` (float): 最小 APY 提升要求（%），默認 5.0
- `max_payback_days` (int): 最大回本天數，默認 7

**示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/delta-neutral/rebalance-decision?current_apy=20&new_apy=28&rebalance_cost=50&capital=10000"
```

**響應**:
```json
{
  "current_apy": 20.0,
  "new_apy": 28.0,
  "apy_improvement": 8.0,
  "yield_improvement_annual": 800.0,
  "yield_improvement_daily": 2.19,
  "rebalance_cost": 50.0,
  "payback_days": 22.83,
  "roi": 1600.0,
  "should_rebalance": true,
  "reason": "建議轉倉：APY 提升 8.00%，22.8 天回本，ROI 1600%"
}
```

**決策邏輯**:
- APY 提升 >= `min_apy_improvement`
- 回本天數 <= `max_payback_days`
- ROI >= 200%

---

## 🔧 Python 客戶端示例

### 安裝依賴

```bash
pip install requests
```

### 基礎使用

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 獲取代幣價格
response = requests.get(f"{BASE_URL}/api/v1/market/tokens?symbols=ETH,BTC")
prices = response.json()
print(f"ETH 價格: ${prices[0]['price']:,.2f}")

# 2. 獲取資金費率
response = requests.get(f"{BASE_URL}/api/v1/market/funding-rates?coins=ETH")
funding = response.json()
print(f"ETH 資金費率: {funding[0]['annualized_rate_pct']:.2f}% (年化)")

# 3. 獲取最佳機會
response = requests.get(
    f"{BASE_URL}/api/v1/delta-neutral/opportunities",
    params={"token": "ETH", "capital": 10000, "top_n": 5}
)
opportunities = response.json()
best = opportunities[0]
print(f"\n最佳機會:")
print(f"  協議: {best['protocol']}")
print(f"  總 APY: {best['total_apy']:.2f}%")
print(f"  預期年收益: ${best['annual_yield']:,.0f}")

# 4. 生成完整報告
response = requests.get(
    f"{BASE_URL}/api/v1/delta-neutral/report",
    params={"token": "ETH", "capital": 10000}
)
report = response.json()
print(f"\n策略報告:")
print(f"  當前價格: ${report['market_data']['token_price']:,.2f}")
print(f"  市場情緒: {report['market_data']['market_sentiment']}")
print(f"  建議: {report['recommendation']}")
```

---

## 📈 JavaScript/TypeScript 客戶端示例

### 使用 Fetch API

```javascript
const BASE_URL = "http://localhost:8000";

// 獲取 Delta Neutral 機會
async function getDeltaNeutralOpportunities(token = "ETH", capital = 10000) {
  const response = await fetch(
    `${BASE_URL}/api/v1/delta-neutral/opportunities?token=${token}&capital=${capital}&top_n=5`
  );
  const opportunities = await response.json();
  return opportunities;
}

// 生成策略報告
async function getStrategyReport(token = "ETH", capital = 10000) {
  const response = await fetch(
    `${BASE_URL}/api/v1/delta-neutral/report?token=${token}&capital=${capital}`
  );
  const report = await response.json();
  return report;
}

// 使用示例
getDeltaNeutralOpportunities("ETH", 10000).then(opportunities => {
  console.log("最佳機會:", opportunities[0]);
});

getStrategyReport("ETH", 10000).then(report => {
  console.log("策略報告:", report);
});
```

### 使用 Axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// 獲取代幣價格
const getTokenPrices = async (symbols) => {
  const response = await api.get('/api/v1/market/tokens', {
    params: { symbols: symbols.join(',') }
  });
  return response.data;
};

// 獲取資金費率
const getFundingRates = async (coins) => {
  const response = await api.get('/api/v1/market/funding-rates', {
    params: { coins: coins.join(',') }
  });
  return response.data;
};

// 獲取機會
const getOpportunities = async (token, capital) => {
  const response = await api.get('/api/v1/delta-neutral/opportunities', {
    params: { token, capital, top_n: 5 }
  });
  return response.data;
};

// 使用示例
async function main() {
  const prices = await getTokenPrices(['ETH', 'BTC']);
  console.log('代幣價格:', prices);
  
  const funding = await getFundingRates(['ETH']);
  console.log('資金費率:', funding);
  
  const opportunities = await getOpportunities('ETH', 10000);
  console.log('最佳機會:', opportunities[0]);
}

main();
```

---

## 🎯 實際應用場景

### 場景 1: 尋找最佳投資機會

```python
import requests

BASE_URL = "http://localhost:8000"

def find_best_investment(token="ETH", capital=10000):
    """尋找最佳 Delta Neutral 投資機會"""
    
    # 獲取完整報告
    response = requests.get(
        f"{BASE_URL}/api/v1/delta-neutral/report",
        params={"token": token, "capital": capital}
    )
    report = response.json()
    
    # 提取關鍵信息
    best_opp = report["best_opportunity"]
    market = report["market_data"]
    hedge = report["hedge_info"]
    
    print(f"{'='*60}")
    print(f"Delta Neutral 投資建議 - {token}")
    print(f"{'='*60}\n")
    
    print(f"📊 市場狀況:")
    print(f"  當前價格: ${market['token_price']:,.2f}")
    print(f"  24h 變化: {market['price_change_24h']:+.2f}%")
    print(f"  市場情緒: {market['market_sentiment']} ({market['fear_greed_index']})")
    
    print(f"\n🏆 最佳機會:")
    print(f"  協議: {best_opp['protocol']}")
    print(f"  池: {best_opp['symbol']}")
    print(f"  鏈: {best_opp['chain']}")
    print(f"  TVL: ${best_opp['tvl']:,.0f}")
    
    print(f"\n💰 收益預估:")
    print(f"  LP APY: {best_opp['lp_apy']:.2f}%")
    print(f"  資金費率 APY: {best_opp['funding_apy']:.2f}%")
    print(f"  總 APY: {best_opp['total_apy']:.2f}%")
    print(f"  預期年收益: ${best_opp['annual_yield']:,.0f}")
    
    print(f"\n🛡️ 對沖設置:")
    print(f"  需對沖代幣數量: {hedge['token_amount']:.4f} {token}")
    print(f"  對沖倉位大小: ${hedge['hedge_position_size']:,.0f}")
    print(f"  槓桿: {hedge['hedge_leverage']}x")
    
    print(f"\n💡 建議: {report['recommendation']}")
    print(f"{'='*60}\n")
    
    return report

# 使用
report = find_best_investment("ETH", 10000)
```

### 場景 2: 監控多個代幣

```python
import requests
import time

BASE_URL = "http://localhost:8000"

def monitor_opportunities(tokens=["ETH", "BTC"], capital=10000, interval=300):
    """監控多個代幣的 Delta Neutral 機會"""
    
    while True:
        print(f"\n{'='*80}")
        print(f"Delta Neutral 機會監控 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        for token in tokens:
            response = requests.get(
                f"{BASE_URL}/api/v1/delta-neutral/opportunities",
                params={"token": token, "capital": capital, "top_n": 1}
            )
            opportunities = response.json()
            
            if opportunities:
                opp = opportunities[0]
                print(f"{token}:")
                print(f"  最佳池: {opp['protocol']} - {opp['symbol']}")
                print(f"  總 APY: {opp['total_apy']:.2f}%")
                print(f"  預期年收益: ${opp['annual_yield']:,.0f}")
                print()
        
        print(f"下次更新: {interval} 秒後...\n")
        time.sleep(interval)

# 使用（每 5 分鐘更新一次）
monitor_opportunities(["ETH", "BTC"], 10000, 300)
```

### 場景 3: 轉倉決策

```python
import requests

BASE_URL = "http://localhost:8000"

def should_rebalance(current_pool_apy, new_pool_apy, capital=10000):
    """判斷是否應該轉倉"""
    
    # 估算轉倉成本（Gas + 滑點）
    rebalance_cost = 100  # USD
    
    response = requests.post(
        f"{BASE_URL}/api/v1/delta-neutral/rebalance-decision",
        params={
            "current_apy": current_pool_apy,
            "new_apy": new_pool_apy,
            "rebalance_cost": rebalance_cost,
            "capital": capital
        }
    )
    decision = response.json()
    
    print(f"轉倉決策分析:")
    print(f"  當前 APY: {decision['current_apy']:.2f}%")
    print(f"  新池 APY: {decision['new_apy']:.2f}%")
    print(f"  APY 提升: {decision['apy_improvement']:.2f}%")
    print(f"  轉倉成本: ${decision['rebalance_cost']:.2f}")
    print(f"  回本天數: {decision['payback_days']:.1f} 天")
    print(f"  ROI: {decision['roi']:.0f}%")
    print(f"\n決策: {'✅ 建議轉倉' if decision['should_rebalance'] else '❌ 不建議轉倉'}")
    print(f"原因: {decision['reason']}")
    
    return decision['should_rebalance']

# 使用
should_rebalance(20, 28, 10000)
```

---

## 🔄 數據更新頻率

| 數據類型 | 更新頻率 | 緩存時間 |
|---------|---------|---------|
| 代幣價格 | 即時 | 10 秒 |
| LP 池數據 | 5 分鐘 | 5 分鐘 |
| 資金費率 | 每小時 | 5 分鐘 |
| 市場情緒 | 每天 | 1 小時 |

---

## ⚠️ 注意事項

1. **Rate Limiting**: 
   - CoinGecko 免費版: 50 次/分鐘
   - 建議使用緩存減少 API 調用

2. **數據準確性**:
   - 所有數據來自第三方 API
   - 建議交叉驗證重要決策

3. **風險提示**:
   - Delta Neutral 策略並非完全無風險
   - 需考慮智能合約風險、流動性風險等

4. **Gas 成本**:
   - 實際 Gas 成本會根據網絡狀況波動
   - 建議在低 Gas 時段操作

---

## 🐛 故障排除

### 問題 1: API 無響應

```bash
# 檢查服務器狀態
curl http://localhost:8000/

# 查看日誌
tail -f /tmp/api_v2.log
```

### 問題 2: 數據獲取失敗

可能原因:
- 第三方 API 暫時不可用
- 網絡連接問題
- Rate Limit 超限

解決方案:
- 等待幾分鐘後重試
- 檢查網絡連接
- 使用緩存數據

### 問題 3: 計算結果異常

可能原因:
- 輸入參數錯誤
- 數據源返回異常值

解決方案:
- 檢查輸入參數範圍
- 查看 API 響應中的錯誤信息

---

## 📞 技術支持

如有問題，請查看:
- API 文檔: `http://localhost:8000/docs`
- 系統日誌: `/tmp/api_v2.log`
- 數據需求文檔: `DELTA_NEUTRAL_DATA_REQUIREMENTS.md`

---

## 🎉 下一步

1. **前端整合**: 使用這些 API 構建前端儀表板
2. **自動化**: 設置定時任務監控機會
3. **通知系統**: 當發現好機會時發送通知
4. **回測**: 使用歷史數據驗證策略效果
5. **部署**: 將 API 部署到生產環境（Render, Railway 等）

---

**祝您投資順利！** 🚀

