# LAL 智能搜尋服務架構設計

## 🎯 系統目標

**LAL (LiveaLittle) 智能搜尋服務**旨在為用戶提供最優化的 Delta Neutral 投資方案，通過以下步驟：

1. **戴維斯雙擊分析** - 識別潛在優質 LP 池
2. **Delta Neutral 配對** - 找出最佳對沖配對
3. **成本效益計算** - 計算 Gas Fee 和淨收益
4. **智能優化** - 選出前 5 個最佳方案
5. **用戶選擇** - 提供詳細分析供用戶決策

---

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                     用戶界面 (Frontend)                      │
│                  輸入: 代幣、資本、風險偏好                   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              LAL 智能搜尋服務 (Smart Search)                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  步驟 1: 戴維斯雙擊分析引擎                          │  │
│  │  - 獲取所有相關 LP 池                                │  │
│  │  - 計算費用增長率 vs TVL 增長率                     │  │
│  │  - 識別資本效率提升的池                             │  │
│  │  - 評分並排序（0-100 分）                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  步驟 2: Delta Neutral 配對優化器                    │  │
│  │  - 為每個 LP 池找出最佳對沖方案                     │  │
│  │  - 計算對沖比率                                      │  │
│  │  - 匹配最佳資金費率來源                             │  │
│  │  - 評估無常損失風險                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  步驟 3: 成本效益計算器                              │  │
│  │  - Gas Fee 估算（鏈上操作成本）                     │  │
│  │  - 滑點成本估算                                      │  │
│  │  - 總成本計算                                        │  │
│  │  - 淨收益計算（收益 - 成本）                        │  │
│  │  - ROI 和回本期分析                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  步驟 4: 智能優化器                                  │  │
│  │  - 綜合評分（戴維斯雙擊 + Delta Neutral + 成本）    │  │
│  │  - 風險調整收益計算                                 │  │
│  │  - 多維度排序                                        │  │
│  │  - 選出前 5 個最佳方案                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  步驟 5: 結果生成器                                  │  │
│  │  - 生成詳細分析報告                                 │  │
│  │  - 風險評估                                          │  │
│  │  - 執行步驟指南                                      │  │
│  │  - 監控建議                                          │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┬─────────────┐
        ↓                ↓                ↓             ↓
   DeFiLlama        CoinGecko       Hyperliquid   Etherscan
   (LP 池歷史)      (價格歷史)      (資金費率)    (Gas 價格)
```

---

## 📊 核心模組詳細設計

### 1. 戴維斯雙擊分析引擎

**目標**: 識別費用增長快於 TVL 增長的優質 LP 池

**數據需求**:
- LP 池歷史數據（7 天、30 天）
- TVL 變化趨勢
- 費用收入變化趨勢
- APY 歷史數據

**計算邏輯**:

```python
# 戴維斯雙擊評分公式
davis_score = (fee_growth_rate / tvl_growth_rate) * weight_factor

# 特殊情況
if tvl_growth_rate == 0 and fee_growth_rate > 0:
    davis_score = 100  # 極佳機會：資本效率提升

if tvl_growth_rate < 0 and fee_growth_rate > 0:
    davis_score = 80  # 優質機會：TVL 下降但費用增長
```

**評分標準**:
- **90-100 分**: 極佳機會（費用增長 >> TVL 增長）
- **70-89 分**: 優質機會（費用增長 > TVL 增長）
- **50-69 分**: 良好機會（費用增長 ≈ TVL 增長）
- **30-49 分**: 一般機會（費用增長 < TVL 增長）
- **0-29 分**: 不推薦（費用下降或 TVL 大幅增長）

**輸出**:
```json
{
  "pool_id": "...",
  "protocol": "curve-dex",
  "symbol": "OETH-WETH",
  "davis_score": 85.5,
  "fee_growth_7d": 12.5,
  "tvl_growth_7d": 2.3,
  "capital_efficiency": "improving",
  "recommendation": "極佳機會"
}
```

---

### 2. Delta Neutral 配對優化器

**目標**: 為每個優質 LP 池找出最佳對沖方案

**配對邏輯**:

1. **識別池中資產**
   - 例如: OETH-WETH 池 → 需對沖 ETH 敞口

2. **尋找最佳對沖來源**
   - Hyperliquid 永續合約
   - dYdX 永續合約
   - Binance 永續合約（如可用）

3. **計算對沖比率**
   - 考慮池的資產比例（50/50 或其他）
   - 計算需要的空單大小

4. **評估資金費率**
   - 選擇資金費率最優的平台
   - 考慮歷史穩定性

**輸出**:
```json
{
  "lp_pool": "OETH-WETH",
  "hedge_asset": "ETH",
  "hedge_platform": "Hyperliquid",
  "hedge_ratio": 1.0,
  "funding_rate_apy": 10.95,
  "combined_apy": 13.44,
  "risk_level": "low"
}
```

---

### 3. 成本效益計算器

**目標**: 精確計算所有成本並評估淨收益

**成本項目**:

#### A. Gas Fee 估算

```python
# Ethereum Gas Fee 計算
gas_operations = {
    "approve_token": 50000,      # Gas units
    "add_liquidity": 200000,
    "remove_liquidity": 150000,
    "open_short": 100000,
    "close_short": 80000
}

# 獲取當前 Gas 價格（Gwei）
gas_price = get_current_gas_price()  # 例如: 30 Gwei

# 計算單次操作成本
total_gas = sum(gas_operations.values())
gas_cost_eth = (total_gas * gas_price) / 1e9
gas_cost_usd = gas_cost_eth * eth_price

# 年化 Gas 成本（假設每月轉倉一次）
annual_gas_cost = gas_cost_usd * 12
```

#### B. 滑點成本

```python
# 滑點估算（基於流動性深度）
slippage_rate = 0.001  # 0.1% for high liquidity pools
slippage_cost = capital * slippage_rate * 2  # 進出各一次
```

#### C. 其他成本

```python
# 協議費用
protocol_fee = lp_apy * 0.1  # 10% 的 LP 收益作為協議費

# 總成本
total_cost = annual_gas_cost + slippage_cost + protocol_fee
```

**淨收益計算**:

```python
# 總收益
total_revenue = lp_revenue + funding_rate_revenue

# 淨收益
net_profit = total_revenue - total_cost

# 淨 APY
net_apy = (net_profit / capital) * 100

# ROI
roi = (net_profit / total_cost) * 100
```

**輸出**:
```json
{
  "capital": 10000,
  "total_revenue": 1344,
  "total_cost": 200,
  "net_profit": 1144,
  "net_apy": 11.44,
  "roi": 572,
  "payback_days": 64,
  "cost_breakdown": {
    "gas_fee": 150,
    "slippage": 20,
    "protocol_fee": 30
  }
}
```

---

### 4. 智能優化器

**目標**: 綜合所有因素，選出最佳方案

**綜合評分公式**:

```python
# 權重配置
weights = {
    "davis_score": 0.30,        # 戴維斯雙擊評分
    "net_apy": 0.25,            # 淨 APY
    "risk_adjusted_return": 0.20,  # 風險調整收益
    "liquidity": 0.15,          # 流動性（TVL）
    "cost_efficiency": 0.10     # 成本效率
}

# 計算綜合評分
final_score = (
    davis_score * weights["davis_score"] +
    normalize(net_apy) * weights["net_apy"] +
    risk_adjusted_return * weights["risk_adjusted_return"] +
    normalize(tvl) * weights["liquidity"] +
    cost_efficiency * weights["cost_efficiency"]
)
```

**風險調整收益**:

```python
# 夏普比率簡化版
risk_free_rate = 0.05  # 5% 無風險利率
volatility = calculate_volatility(historical_apy)
sharpe_ratio = (net_apy - risk_free_rate) / volatility

# 風險調整評分
risk_adjusted_return = sharpe_ratio * 10  # 歸一化到 0-100
```

**排序邏輯**:

1. 按綜合評分排序
2. 過濾掉不符合最低要求的方案
3. 選出前 5 個
4. 確保多樣性（不同協議、不同鏈）

**輸出**:
```json
{
  "rank": 1,
  "pool": "OETH-WETH",
  "protocol": "Curve",
  "chain": "Ethereum",
  "final_score": 87.5,
  "davis_score": 85.5,
  "net_apy": 11.44,
  "risk_level": "low",
  "recommendation": "強烈推薦"
}
```

---

### 5. 結果生成器

**目標**: 生成用戶友好的詳細報告

**報告內容**:

#### A. 執行摘要

```
🏆 最佳方案 #1: Curve OETH-WETH

預期年收益: $1,144 (11.44% APY)
風險等級: 低
投資建議: 強烈推薦

為什麼選擇這個方案？
✅ 戴維斯雙擊評分 85.5 - 費用增長遠超 TVL 增長
✅ 高流動性 - TVL $104.6M
✅ 低無常損失風險 - OETH 與 WETH 高度相關
✅ 穩定資金費率 - Hyperliquid 10.95% APY
```

#### B. 詳細分析

```json
{
  "opportunity_analysis": {
    "davis_double_click": {
      "score": 85.5,
      "fee_growth_7d": 12.5,
      "tvl_growth_7d": 2.3,
      "interpretation": "費用增長顯著快於 TVL 增長，資本效率提升"
    },
    "delta_neutral_setup": {
      "lp_position": {
        "pool": "OETH-WETH",
        "capital": 10000,
        "expected_lp_apy": 2.49
      },
      "hedge_position": {
        "asset": "ETH",
        "platform": "Hyperliquid",
        "size": 5000,
        "funding_rate_apy": 10.95
      }
    },
    "cost_benefit": {
      "total_revenue": 1344,
      "total_cost": 200,
      "net_profit": 1144,
      "roi": 572,
      "payback_days": 64
    }
  },
  "risk_assessment": {
    "smart_contract_risk": "low",
    "liquidity_risk": "low",
    "funding_rate_volatility": "medium",
    "overall_risk": "low"
  },
  "execution_steps": [
    "1. 在 Curve 添加 $10,000 流動性到 OETH-WETH 池",
    "2. 在 Hyperliquid 開設 $5,000 ETH 空單（1x 槓桿）",
    "3. 監控資金費率和 LP APY 變化",
    "4. 每週檢查是否需要轉倉"
  ]
}
```

---

## 🔄 工作流程

### 完整搜尋流程

```python
def smart_search(token: str, capital: float, risk_tolerance: str):
    """
    LAL 智能搜尋主函數
    
    Args:
        token: 目標代幣（如 "ETH"）
        capital: 投資資本（USD）
        risk_tolerance: 風險偏好（"low", "medium", "high"）
    
    Returns:
        前 5 個最佳方案
    """
    
    # 步驟 1: 戴維斯雙擊分析
    print("🔍 步驟 1: 分析潛在優質 LP 池...")
    davis_candidates = davis_double_click_analyzer.analyze(
        token=token,
        lookback_days=7
    )
    # 輸出: 50+ 個池，按戴維斯評分排序
    
    # 步驟 2: Delta Neutral 配對
    print("🎯 步驟 2: 尋找最佳對沖配對...")
    paired_opportunities = []
    for pool in davis_candidates[:20]:  # 取前 20 個
        hedge_config = delta_neutral_optimizer.find_best_hedge(
            pool=pool,
            capital=capital
        )
        paired_opportunities.append({
            "pool": pool,
            "hedge": hedge_config,
            "combined_apy": pool.apy + hedge_config.funding_apy
        })
    
    # 步驟 3: 成本效益計算
    print("💰 步驟 3: 計算成本和淨收益...")
    for opp in paired_opportunities:
        cost_analysis = cost_calculator.calculate(
            pool=opp["pool"],
            hedge=opp["hedge"],
            capital=capital
        )
        opp["cost_analysis"] = cost_analysis
        opp["net_apy"] = cost_analysis.net_apy
    
    # 步驟 4: 智能優化
    print("🧠 步驟 4: 智能優化和排序...")
    for opp in paired_opportunities:
        opp["final_score"] = smart_optimizer.calculate_score(
            davis_score=opp["pool"].davis_score,
            net_apy=opp["net_apy"],
            tvl=opp["pool"].tvl,
            risk_level=opp["pool"].risk_level,
            risk_tolerance=risk_tolerance
        )
    
    # 排序並選出前 5
    paired_opportunities.sort(key=lambda x: x["final_score"], reverse=True)
    top_5 = paired_opportunities[:5]
    
    # 步驟 5: 生成報告
    print("📊 步驟 5: 生成詳細報告...")
    reports = []
    for i, opp in enumerate(top_5, 1):
        report = report_generator.generate(
            rank=i,
            opportunity=opp,
            capital=capital
        )
        reports.append(report)
    
    return reports
```

---

## 🎯 API 端點設計

### 主要端點

```python
# 1. 智能搜尋（核心功能）
POST /api/v1/lal/smart-search
{
  "token": "ETH",
  "capital": 10000,
  "risk_tolerance": "medium",
  "min_tvl": 1000000,
  "chains": ["Ethereum", "Arbitrum", "Optimism"]
}

# 2. 戴維斯雙擊分析
GET /api/v1/lal/davis-analysis?token=ETH&lookback_days=7

# 3. Delta Neutral 配對
POST /api/v1/lal/delta-neutral-pairing
{
  "pool_id": "...",
  "capital": 10000
}

# 4. 成本效益計算
POST /api/v1/lal/cost-benefit
{
  "pool_id": "...",
  "hedge_config": {...},
  "capital": 10000
}

# 5. 獲取單個方案詳情
GET /api/v1/lal/opportunity/{opportunity_id}
```

---

## 🔧 技術實現

### 數據源

| 數據類型 | 數據源 | API | 更新頻率 |
|---------|-------|-----|---------|
| LP 池歷史數據 | DeFiLlama | `/pools` | 5 分鐘 |
| 代幣價格歷史 | CoinGecko | `/coins/{id}/market_chart` | 即時 |
| 資金費率 | Hyperliquid | `/info` | 每小時 |
| Gas 價格 | Etherscan | `/api?module=gastracker` | 即時 |
| 市場情緒 | Alternative.me | `/fng/` | 每天 |

### 緩存策略

```python
cache_config = {
    "lp_pools_historical": 300,      # 5 分鐘
    "token_prices": 10,              # 10 秒
    "funding_rates": 300,            # 5 分鐘
    "gas_prices": 60,                # 1 分鐘
    "davis_analysis": 600,           # 10 分鐘
    "smart_search_results": 300      # 5 分鐘
}
```

---

## 📈 性能指標

### 目標性能

- **搜尋時間**: < 10 秒
- **數據新鮮度**: < 5 分鐘
- **準確率**: > 90%
- **可用性**: > 99%

### 優化策略

1. **並行處理**: 同時分析多個池
2. **智能緩存**: 減少 API 調用
3. **增量更新**: 只更新變化的數據
4. **預計算**: 提前計算常用指標

---

## 🔐 安全考慮

1. **API Rate Limiting**: 防止濫用
2. **數據驗證**: 檢查異常值
3. **錯誤處理**: 優雅降級
4. **審計日誌**: 記錄所有操作

---

## 🚀 下一步實現

1. ✅ 架構設計完成
2. ⏳ 實現戴維斯雙擊分析引擎
3. ⏳ 實現 Delta Neutral 配對優化器
4. ⏳ 實現成本效益計算器
5. ⏳ 整合所有模組
6. ⏳ 創建 API 端點
7. ⏳ 測試和優化

---

**設計完成！準備開始實現。** 🎉

