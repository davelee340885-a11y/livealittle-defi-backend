# Delta Neutral 策略數據需求分析

## 📋 概述

Delta Neutral 策略需要整合多種實時數據來源，以實現自動化的收益優化和風險管理。本文檔詳細列出所有必需的數據類型、數據源和更新頻率。

---

## 🎯 Delta Neutral 策略核心邏輯

### 策略原理

**Delta Neutral 策略**通過以下方式實現市場中性收益：

1. **LP 倉位**：在 DEX（如 Uniswap、Curve）提供流動性，賺取交易手續費和流動性挖礦獎勵
2. **對沖倉位**：在 CEX（如 Binance、OKX）開設永續合約空單，對沖 LP 倉位的價格風險
3. **收益來源**：
   - LP 手續費收益
   - LP 流動性挖礦獎勵
   - 資金費率收益（當市場做多時，空單收取資金費）
4. **風險管理**：通過對沖消除價格波動風險，實現穩定收益

---

## 📊 必需數據類型

### 1. LP 池數據 🔴 **核心數據**

#### 1.1 基礎信息
- **池地址** (Pool Address)
- **協議名稱** (Protocol): Uniswap V3, Curve, Balancer 等
- **鏈名稱** (Chain): Ethereum, Arbitrum, Optimism 等
- **代幣對** (Token Pair): ETH-USDC, BTC-USDT 等
- **池類型** (Pool Type): Concentrated Liquidity, Stable Pool 等

#### 1.2 流動性數據
- **總鎖倉量 TVL** (Total Value Locked)
  - 單位：USD
  - 更新頻率：每 5 分鐘
  - 數據源：DeFiLlama, The Graph

- **TVL 變化率**
  - 24小時變化
  - 7天變化
  - 30天變化

#### 1.3 收益數據
- **APY (年化收益率)**
  - 交易手續費 APY
  - 流動性挖礦 APY
  - 總 APY
  - 更新頻率：每 10 分鐘
  - 數據源：DeFiLlama, Defillama Yields API

- **手續費收入**
  - 24小時手續費收入
  - 7天手續費收入
  - 手續費增長率

- **流動性挖礦獎勵**
  - 獎勵代幣種類
  - 獎勵 APR
  - 獎勵代幣價格

#### 1.4 交易數據
- **24小時交易量** (24h Volume)
- **交易量/TVL 比率** (Volume/TVL Ratio)
- **交易次數** (Number of Transactions)

#### 1.5 無常損失數據
- **歷史無常損失** (Impermanent Loss)
- **價格範圍** (Price Range) - 適用於 Concentrated Liquidity
- **利用率** (Utilization Rate)

---

### 2. 代幣價格數據 🔴 **核心數據**

#### 2.1 現貨價格
- **當前價格** (Current Price)
  - 更新頻率：每 10 秒
  - 數據源：CoinGecko, Binance API

- **歷史價格**
  - 1小時、24小時、7天、30天價格
  - 用於計算移動平均線

#### 2.2 價格變化
- **價格變化率**
  - 1小時變化
  - 24小時變化
  - 7天變化

#### 2.3 技術指標
- **移動平均線** (Moving Averages)
  - MA50 (50天移動平均)
  - MA200 (200天移動平均)
  - EMA (指數移動平均)

- **波動率** (Volatility)
  - 24小時波動率
  - 7天波動率
  - 30天波動率

---

### 3. 資金費率數據 🔴 **核心數據**

#### 3.1 當前資金費率
- **資金費率** (Funding Rate)
  - 更新頻率：每 8 小時（跟隨交易所結算週期）
  - 數據源：Binance, OKX, Bybit API

- **年化資金費率** (Annualized Funding Rate)
  - 計算公式：當前費率 × 3 × 365

#### 3.2 歷史資金費率
- **平均資金費率**
  - 24小時平均
  - 7天平均
  - 30天平均

- **資金費率趨勢**
  - 是否持續為正（利於空單）
  - 是否持續為負（不利於空單）

#### 3.3 多空比數據
- **多空持倉比** (Long/Short Ratio)
- **大戶持倉** (Top Trader Positions)
- **清算數據** (Liquidation Data)

---

### 4. Gas 費用數據 🟡 **重要數據**

#### 4.1 鏈上 Gas 費
- **當前 Gas 價格** (Current Gas Price)
  - Ethereum: Gwei
  - L2: 通常較低
  - 更新頻率：每分鐘

- **預估交易成本**
  - 添加流動性成本
  - 移除流動性成本
  - Swap 成本

#### 4.2 Gas 費趨勢
- **歷史 Gas 價格**
- **Gas 費預測** (高峰/低谷時段)

---

### 5. 市場狀態數據 🟡 **重要數據**

#### 5.1 市場情緒指標
- **恐懼與貪婪指數** (Fear & Greed Index)
  - 數據源：Alternative.me
  - 更新頻率：每天

- **BTC 市佔率** (BTC Dominance)
  - 數據源：CoinGecko

#### 5.2 市場總覽
- **總市值** (Total Market Cap)
- **24小時總交易量** (24h Total Volume)
- **市場趨勢** (牛市/熊市/橫盤)

---

### 6. 協議風險數據 🟢 **輔助數據**

#### 6.1 安全性數據
- **審計狀態** (Audit Status)
- **TVL 歷史** (TVL History)
- **協議年齡** (Protocol Age)

#### 6.2 流動性健康度
- **流動性深度** (Liquidity Depth)
- **滑點** (Slippage)
- **流動性集中度** (Liquidity Concentration)

---

## 🔌 數據源整合方案

### 主要數據源

| 數據類型 | 數據源 | API 端點 | 免費額度 | 備註 |
|---------|--------|----------|---------|------|
| **LP 池數據** | DeFiLlama | `https://yields.llama.fi/pools` | 無限制 | 最全面的 DeFi 數據 |
| **代幣價格** | CoinGecko | `https://api.coingecko.com/api/v3/` | 50次/分鐘 | 需要實現緩存 |
| **資金費率** | Binance | `https://fapi.binance.com/fapi/v1/fundingRate` | 2400次/分鐘 | 最準確的資金費率 |
| **Gas 費用** | Etherscan | `https://api.etherscan.io/api` | 5次/秒 | Ethereum Gas 數據 |
| **市場情緒** | Alternative.me | `https://api.alternative.me/fng/` | 無限制 | Fear & Greed Index |

### 備用數據源

| 數據類型 | 備用數據源 | 用途 |
|---------|-----------|------|
| **LP 池數據** | The Graph, Dune Analytics | 數據驗證和補充 |
| **代幣價格** | Binance API, CoinMarketCap | 價格交叉驗證 |
| **資金費率** | OKX, Bybit | 多交易所平均 |

---

## 📈 數據更新頻率建議

### 高頻更新（每 10-30 秒）
- 代幣現貨價格
- 資金費率（接近結算時）

### 中頻更新（每 5-10 分鐘）
- LP 池 TVL
- LP 池 APY
- Gas 費用

### 低頻更新（每 1-24 小時）
- 歷史數據
- 市場情緒指標
- 協議風險數據

---

## 🗄️ 數據存儲方案

### 緩存策略

```python
# 數據緩存時間建議
CACHE_DURATION = {
    "token_prices": 10,        # 10秒
    "lp_pools": 300,           # 5分鐘
    "funding_rates": 300,      # 5分鐘
    "gas_prices": 60,          # 1分鐘
    "market_sentiment": 3600,  # 1小時
    "protocol_info": 86400,    # 24小時
}
```

### 數據庫結構

```sql
-- LP 池數據表
CREATE TABLE lp_pools (
    pool_id VARCHAR(100) PRIMARY KEY,
    protocol VARCHAR(50),
    chain VARCHAR(50),
    token0 VARCHAR(20),
    token1 VARCHAR(20),
    tvl DECIMAL(20, 2),
    apy DECIMAL(10, 4),
    volume_24h DECIMAL(20, 2),
    fees_24h DECIMAL(20, 2),
    updated_at TIMESTAMP
);

-- 代幣價格表
CREATE TABLE token_prices (
    token_symbol VARCHAR(20) PRIMARY KEY,
    price DECIMAL(20, 8),
    change_24h DECIMAL(10, 4),
    volume_24h DECIMAL(20, 2),
    updated_at TIMESTAMP
);

-- 資金費率表
CREATE TABLE funding_rates (
    symbol VARCHAR(20),
    exchange VARCHAR(20),
    funding_rate DECIMAL(10, 8),
    next_funding_time TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY (symbol, exchange)
);
```

---

## 🔄 數據流程圖

```
┌─────────────────────────────────────────────────────────────┐
│                    外部數據源                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │DeFiLlama │  │CoinGecko │  │ Binance  │  │Etherscan │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  數據聚合層 (Data Aggregator)                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  - API 調用管理                                       │  │
│  │  - Rate Limit 處理                                    │  │
│  │  - 數據驗證和清洗                                     │  │
│  │  - 多源數據整合                                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  緩存層 (Cache Layer)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  - Redis / In-Memory Cache                           │  │
│  │  - 分級緩存策略                                       │  │
│  │  - 自動過期和更新                                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  業務邏輯層 (Business Logic)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │Delta Neutral │  │ Rebalancer   │  │ Risk Manager │     │
│  │   Engine     │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     API 層 (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  GET /api/v1/market/pools                            │  │
│  │  GET /api/v1/market/tokens                           │  │
│  │  GET /api/v1/strategies/delta-neutral                │  │
│  │  GET /api/v1/execution/opportunities                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      前端 (Frontend)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Dashboard │  │ Strategy │  │ Backtest │  │Rebalance │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Delta Neutral 策略計算公式

### 1. 對沖比率計算

```python
# LP 倉位價值
lp_value = tvl * user_share_percentage

# 需要對沖的代幣數量（假設 ETH-USDC 池）
eth_amount_in_lp = lp_value * 0.5 / eth_price

# 對沖倉位大小（永續合約）
hedge_position_size = eth_amount_in_lp * eth_price  # USD 價值
```

### 2. 總收益計算

```python
# LP 收益
lp_fee_apy = pool_data["fee_apy"]
lp_reward_apy = pool_data["reward_apy"]
total_lp_apy = lp_fee_apy + lp_reward_apy

# 資金費率收益（空單收取正費率）
funding_rate_apy = avg_funding_rate * 3 * 365  # 每天3次結算

# 總收益
total_apy = total_lp_apy + funding_rate_apy - gas_cost_apy
```

### 3. 轉倉決策

```python
# 當前池收益
current_yield = current_pool_apy + current_funding_rate_apy

# 新池收益
new_yield = new_pool_apy + new_funding_rate_apy

# 轉倉成本
rebalance_cost = gas_fee + slippage + il_cost

# 收益提升
yield_improvement = new_yield - current_yield

# 轉倉決策
should_rebalance = (
    yield_improvement > threshold  # 例如 5% APY 提升
    and yield_improvement * capital > rebalance_cost * 2  # ROI > 200%
    and payback_period < 7_days  # 回本期 < 7天
)
```

---

## 📋 實現檢查清單

### 階段 1：基礎數據整合 ✅
- [ ] 整合 DeFiLlama API 獲取 LP 池數據
- [ ] 整合 CoinGecko API 獲取代幣價格
- [ ] 整合 Binance API 獲取資金費率
- [ ] 實現數據緩存機制
- [ ] 實現錯誤處理和重試邏輯

### 階段 2：數據處理和計算 ✅
- [ ] 實現 Delta Neutral 對沖比率計算
- [ ] 實現總收益計算
- [ ] 實現轉倉成本估算
- [ ] 實現轉倉決策邏輯

### 階段 3：API 端點實現 ✅
- [ ] 創建 `/api/v1/delta-neutral/pools` 端點
- [ ] 創建 `/api/v1/delta-neutral/calculate` 端點
- [ ] 創建 `/api/v1/delta-neutral/opportunities` 端點
- [ ] 添加 API 文檔

### 階段 4：測試和優化 ✅
- [ ] 單元測試
- [ ] 整合測試
- [ ] 性能優化
- [ ] 錯誤處理測試

---

## 🚀 快速開始

接下來我會創建：

1. **數據聚合器** (`unified_data_aggregator.py`)
   - 整合所有數據源
   - 實現緩存機制
   - 處理 Rate Limit

2. **Delta Neutral 計算器** (`delta_neutral_calculator.py`)
   - 實現所有計算邏輯
   - 提供簡單的 API

3. **更新的 API 伺服器** (`api_server.py`)
   - 整合真實數據
   - 新增 Delta Neutral 端點

4. **測試腳本** (`test_delta_neutral.py`)
   - 測試數據流
   - 驗證計算結果

---

## 📞 需要的 API Keys

為了使用某些數據源，您可能需要註冊並獲取 API Key：

1. **CoinGecko** (可選，免費版有限制)
   - https://www.coingecko.com/en/api

2. **Etherscan** (可選，用於 Gas 數據)
   - https://etherscan.io/apis

3. **Binance** (可選，用於更高的 Rate Limit)
   - https://www.binance.com/en/binance-api

**注意**：DeFiLlama 和 Alternative.me 不需要 API Key！

