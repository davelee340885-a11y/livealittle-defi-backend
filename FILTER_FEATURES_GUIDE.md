# LAL 智能搜尋 - LP 篩選器功能指南

## 🎯 概述

LAL 智能搜尋服務 V2 現在支持強大的多維度 LP 池篩選功能，讓您可以精確控制搜尋條件，快速找到最符合需求的投資機會。

---

## 📋 支持的篩選維度

### 1. TVL（總鎖倉量）篩選

**參數**: `min_tvl`, `max_tvl`

控制流動性池的規模範圍。

**示例**:
```bash
# 只要大池（TVL > 50M）
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&min_tvl=50000000"

# 中小池（1M - 10M）
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&min_tvl=1000000&max_tvl=10000000"
```

### 2. APY（年化收益率）篩選

**參數**: `min_apy`, `max_apy`

控制收益率範圍。

**示例**:
```bash
# 高收益（APY >= 50%）
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&min_apy=50"

# 穩健收益（10% - 30%）
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&min_apy=10&max_apy=30"
```

### 3. 協議篩選

**參數**: `protocols`（逗號分隔）

只搜尋指定協議的池。

**支持的協議**:
- uniswap-v3
- uniswap-v2
- curve-dex
- balancer-v2
- pancakeswap
- sushiswap
- aerodrome
- velodrome
- trader-joe
- quickswap
- spookyswap
- spiritswap

**示例**:
```bash
# 只要 Uniswap V3
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&protocols=uniswap-v3"

# 多個協議
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&protocols=uniswap-v3,curve-dex,balancer-v2"
```

### 4. 區塊鏈篩選

**參數**: `chains`（逗號分隔）

只搜尋指定鏈上的池。

**支持的鏈**:
- Ethereum
- Arbitrum
- Optimism
- Base
- Polygon
- BSC
- Avalanche
- Fantom
- Gnosis
- Celo

**示例**:
```bash
# 只要 L2
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&chains=Arbitrum,Optimism,Base"

# 只要主網
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&chains=Ethereum"
```

### 5. 代幣篩選

**參數**: `include_tokens`, `exclude_tokens`（逗號分隔）

控制池中必須包含或排除的代幣。

**示例**:
```bash
# 必須包含 USDC
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&include_tokens=USDC"

# 排除穩定幣
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&exclude_tokens=USDC,USDT,DAI"
```

### 6. 戴維斯雙擊篩選

**參數**: `min_davis_score`, `max_davis_score`, `davis_categories`

基於戴維斯雙擊評分和評級篩選。

**評級**: 極佳、優質、良好、一般、不推薦

**示例**:
```bash
# 只要極佳評分（>= 90）
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&min_davis_score=90"

# 只要極佳和優質評級
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&davis_categories=極佳,優質"
```

### 7. 穩定性篩選

**參數**: `min_base_apy_ratio`

控制基礎 APY 佔總 APY 的最小比例（0-100）。

**示例**:
```bash
# 只要穩定收益（80%+ 來自基礎 APY）
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&min_base_apy_ratio=80"
```

### 8. 風險篩選

**參數**: `il_risk`

基於無常損失風險篩選。

**風險等級**:
- `low`: 穩定幣對（如 USDC-USDT）
- `medium`: 一個穩定幣（如 ETH-USDC）
- `high`: 兩個波動代幣（如 ETH-BTC）

**示例**:
```bash
# 只要低風險池
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=USDC&il_risk=low"
```

### 9. Gas 成本篩選

**參數**: `max_gas_cost`

控制最大年化 Gas 成本（USD）。

**示例**:
```bash
# 低 Gas（< $100/年）
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&max_gas_cost=100"

# 極低 Gas（< $10/年，主要是 L2）
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&max_gas_cost=10"
```

### 10. 排序選項

**參數**: `sort_by`, `sort_order`

控制結果排序方式。

**排序字段**:
- `final_score`: 綜合評分（默認）
- `net_apy`: 淨 APY
- `tvl`: TVL
- `davis_score`: 戴維斯評分
- `roi`: ROI
- `net_profit`: 預期淨收益
- `lp_apy`: LP APY
- `total_apy`: 總 APY

**排序方向**: `asc`（升序）, `desc`（降序，默認）

**示例**:
```bash
# 按 APY 降序
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&sort_by=net_apy&sort_order=desc"

# 按 TVL 升序
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&sort_by=tvl&sort_order=asc"
```

### 11. 分頁

**參數**: `limit`, `offset`

控制返回結果數量和偏移量。

**示例**:
```bash
# 第一頁（前 10 個）
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&limit=10&offset=0"

# 第二頁（11-20）
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&limit=10&offset=10"
```

---

## 🎨 使用場景

### 場景 1: 保守投資者

**需求**: 大池、低風險、穩定收益

```bash
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?\
token=ETH&\
capital=10000&\
min_tvl=50000000&\
min_base_apy_ratio=80&\
il_risk=low&\
chains=Ethereum&\
protocols=uniswap-v3,curve-dex&\
limit=5"
```

### 場景 2: 激進投資者

**需求**: 高收益、可接受高風險

```bash
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?\
token=ETH&\
capital=10000&\
min_apy=50&\
min_davis_score=90&\
il_risk=high&\
chains=Arbitrum,Optimism,Base&\
limit=10"
```

### 場景 3: L2 專注

**需求**: 只要 L2、低 Gas

```bash
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?\
token=ETH&\
capital=10000&\
chains=Arbitrum,Optimism,Base&\
max_gas_cost=50&\
min_apy=20&\
limit=10"
```

### 場景 4: 穩定幣對

**需求**: 只要穩定幣對、低風險

```bash
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?\
token=USDC&\
capital=10000&\
include_tokens=USDT,DAI&\
il_risk=low&\
min_tvl=10000000&\
limit=5"
```

### 場景 5: 特定協議

**需求**: 只要 Uniswap V3、高評分

```bash
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?\
token=ETH&\
capital=10000&\
protocols=uniswap-v3&\
min_davis_score=90&\
min_apy=30&\
sort_by=net_apy&\
limit=10"
```

---

## 💻 程式化使用

### Python 示例

```python
import requests

BASE_URL = "https://lal-smart-search-api.onrender.com"

# 場景: L2 高收益低 Gas
params = {
    "token": "ETH",
    "capital": 10000,
    "chains": "Arbitrum,Optimism,Base",
    "min_apy": 50,
    "max_gas_cost": 50,
    "sort_by": "net_apy",
    "limit": 5
}

response = requests.get(f"{BASE_URL}/api/v1/lal/smart-search", params=params)
result = response.json()

if result["success"]:
    opportunities = result["data"]["opportunities"]
    filter_summary = result["data"]["filter_summary"]
    
    print(f"篩選前: {filter_summary['total_before_filter']} 個池")
    print(f"篩選後: {filter_summary['total_after_filter']} 個池")
    print(f"\n最佳機會:")
    
    for i, opp in enumerate(opportunities, 1):
        print(f"{i}. {opp['symbol']} ({opp['chain']})")
        print(f"   淨 APY: {opp['net_apy']:.2f}%")
        print(f"   預期年收益: ${opp['net_profit']:,.0f}")
        print(f"   Gas 成本: ${opp['gas_cost_annual']:.2f}/年")
        print()
```

### JavaScript 示例

```javascript
const BASE_URL = "https://lal-smart-search-api.onrender.com";

async function searchOpportunities() {
  const params = new URLSearchParams({
    token: "ETH",
    capital: 10000,
    chains: "Arbitrum,Optimism,Base",
    min_apy: 50,
    max_gas_cost: 50,
    sort_by: "net_apy",
    limit: 5
  });
  
  const response = await fetch(`${BASE_URL}/api/v1/lal/smart-search?${params}`);
  const result = await response.json();
  
  if (result.success) {
    const { opportunities, filter_summary } = result.data;
    
    console.log(`篩選前: ${filter_summary.total_before_filter} 個池`);
    console.log(`篩選後: ${filter_summary.total_after_filter} 個池`);
    console.log("\n最佳機會:");
    
    opportunities.forEach((opp, i) => {
      console.log(`${i + 1}. ${opp.symbol} (${opp.chain})`);
      console.log(`   淨 APY: ${opp.net_apy.toFixed(2)}%`);
      console.log(`   預期年收益: $${opp.net_profit.toFixed(0)}`);
      console.log(`   Gas 成本: $${opp.gas_cost_annual.toFixed(2)}/年\n`);
    });
  }
}

searchOpportunities();
```

---

## 📊 響應格式

### 成功響應

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
        "pool_id": "...",
        "protocol": "uniswap-v3",
        "chain": "Arbitrum",
        "symbol": "WETH-USDC",
        "tvl": 86476153,
        "lp_apy": 101.47,
        "funding_apy": 10.95,
        "total_apy": 112.42,
        "gas_cost_annual": 2.84,
        "net_apy": 112.39,
        "net_profit": 11239.49,
        "roi": 395970.21,
        "davis_score": 100,
        "davis_category": "極佳",
        "final_score": 97.3
      }
    ],
    "count": 3,
    "pagination": {
      "limit": 5,
      "offset": 0,
      "total": 3
    },
    "filter_summary": {
      "total_before_filter": 20,
      "total_after_filter": 3,
      "filtered_out": 17,
      "filters_applied": {
        "tvl": {"min": 5000000, "max": null},
        "apy": {"min": 50, "max": null},
        "chains": ["Arbitrum", "Optimism", "Base"],
        "max_gas_cost": 50
      },
      "sort_by": "final_score",
      "sort_order": "desc"
    }
  }
}
```

### 錯誤響應

```json
{
  "success": false,
  "detail": {
    "error": "Invalid filter criteria",
    "errors": [
      "不支持的鏈: InvalidChain"
    ]
  }
}
```

---

## 🔍 獲取支持的篩選選項

```bash
curl https://lal-smart-search-api.onrender.com/api/v1/lal/filters
```

**響應**:
```json
{
  "success": true,
  "data": {
    "protocols": ["uniswap-v3", "curve-dex", ...],
    "chains": ["Ethereum", "Arbitrum", ...],
    "davis_categories": ["極佳", "優質", ...],
    "il_risk_levels": ["low", "medium", "high"],
    "sort_fields": ["final_score", "net_apy", ...]
  }
}
```

---

## 📈 性能提示

1. **組合篩選**: 組合多個篩選條件可以快速縮小搜尋範圍
2. **分頁**: 使用分頁可以避免一次加載過多數據
3. **排序**: 選擇合適的排序字段可以快速找到最佳機會
4. **緩存**: 相同的搜尋條件會被緩存，重複請求會更快

---

## 🎯 最佳實踐

1. **從寬到窄**: 先用寬鬆的條件搜尋，再逐步收緊
2. **關注重點**: 根據投資目標選擇最重要的篩選條件
3. **驗證結果**: 檢查 `filter_summary` 確認篩選效果
4. **測試組合**: 嘗試不同的篩選組合找到最佳方案

---

## 🆘 常見問題

### Q: 如何找到最安全的投資機會？

A: 使用以下組合:
```bash
il_risk=low&min_tvl=50000000&min_base_apy_ratio=80&chains=Ethereum
```

### Q: 如何找到最高收益的機會？

A: 使用以下組合:
```bash
min_apy=100&min_davis_score=90&sort_by=net_apy&sort_order=desc
```

### Q: 如何避免高 Gas 費？

A: 使用以下組合:
```bash
chains=Arbitrum,Optimism,Base&max_gas_cost=10
```

### Q: 如何只搜尋特定協議？

A: 使用 `protocols` 參數:
```bash
protocols=uniswap-v3,curve-dex
```

---

## 📞 支持

- **API 文檔**: https://lal-smart-search-api.onrender.com/docs
- **GitHub**: https://github.com/davelee340885-a11y/livealittle-defi-backend
- **問題反饋**: GitHub Issues

---

**開始使用 LAL 智能搜尋的強大篩選功能，找到最適合您的 DeFi 投資機會！** 🚀

