# LP 篩選器設計文檔

## 🎯 目標

為 LAL 智能搜尋服務添加強大的多維度篩選功能，讓用戶可以根據各種條件精確篩選 LP 池。

---

## 📋 篩選器參數設計

### 1. 基礎篩選

#### TVL 範圍
- **參數**: `min_tvl`, `max_tvl`
- **類型**: float
- **默認值**: min_tvl=5,000,000, max_tvl=無限制
- **用途**: 過濾流動性規模
- **示例**: 
  - 只要大池: `min_tvl=50000000` (50M+)
  - 中小池: `min_tvl=1000000&max_tvl=10000000` (1M-10M)

#### APY 範圍
- **參數**: `min_apy`, `max_apy`
- **類型**: float
- **默認值**: min_apy=5.0, max_apy=無限制
- **用途**: 過濾收益率
- **示例**:
  - 高收益: `min_apy=50` (50%+)
  - 穩健收益: `min_apy=10&max_apy=30` (10%-30%)

### 2. 協議篩選

#### 協議列表
- **參數**: `protocols`
- **類型**: string (逗號分隔)
- **默認值**: 全部
- **可選值**:
  - `uniswap-v3`
  - `uniswap-v2`
  - `curve-dex`
  - `balancer-v2`
  - `pancakeswap`
  - `sushiswap`
  - `aerodrome`
  - `velodrome`
  - 等等...
- **示例**:
  - 只要 Uniswap: `protocols=uniswap-v3`
  - 多個協議: `protocols=uniswap-v3,curve-dex,balancer-v2`

### 3. 區塊鏈篩選

#### 鏈列表
- **參數**: `chains`
- **類型**: string (逗號分隔)
- **默認值**: 全部
- **可選值**:
  - `Ethereum`
  - `Arbitrum`
  - `Optimism`
  - `Base`
  - `Polygon`
  - `BSC` (Binance Smart Chain)
  - `Avalanche`
  - 等等...
- **示例**:
  - 只要 L2: `chains=Arbitrum,Optimism,Base`
  - 只要主網: `chains=Ethereum`

### 4. 代幣對篩選

#### 包含代幣
- **參數**: `include_tokens`
- **類型**: string (逗號分隔)
- **默認值**: 無
- **用途**: 池中必須包含指定代幣
- **示例**:
  - 必須有 USDC: `include_tokens=USDC`
  - 必須有穩定幣: `include_tokens=USDC,USDT,DAI`

#### 排除代幣
- **參數**: `exclude_tokens`
- **類型**: string (逗號分隔)
- **默認值**: 無
- **用途**: 池中不能包含指定代幣
- **示例**:
  - 排除穩定幣: `exclude_tokens=USDC,USDT,DAI`
  - 排除某個代幣: `exclude_tokens=SHIB`

### 5. 戴維斯雙擊篩選

#### 評分範圍
- **參數**: `min_davis_score`, `max_davis_score`
- **類型**: float (0-100)
- **默認值**: min_davis_score=0, max_davis_score=100
- **用途**: 過濾戴維斯雙擊評分
- **示例**:
  - 只要極佳: `min_davis_score=90`
  - 優質以上: `min_davis_score=70`

#### 評級
- **參數**: `davis_categories`
- **類型**: string (逗號分隔)
- **默認值**: 全部
- **可選值**: `極佳`, `優質`, `良好`, `一般`, `不推薦`
- **示例**:
  - 只要極佳和優質: `davis_categories=極佳,優質`

### 6. 穩定性篩選

#### 基礎 APY 比例
- **參數**: `min_base_apy_ratio`
- **類型**: float (0-100)
- **默認值**: 0
- **用途**: 基礎 APY 佔總 APY 的最小比例
- **示例**:
  - 只要穩定收益: `min_base_apy_ratio=80` (80%+ 來自基礎 APY)

### 7. 風險篩選

#### 無常損失風險
- **參數**: `il_risk`
- **類型**: string
- **默認值**: 全部
- **可選值**: `low`, `medium`, `high`
- **用途**: 過濾無常損失風險等級
- **邏輯**:
  - `low`: 穩定幣對（如 USDC-USDT）
  - `medium`: 一個穩定幣（如 ETH-USDC）
  - `high`: 兩個波動代幣（如 ETH-BTC）

### 8. Gas 成本篩選

#### 最大年化 Gas 成本
- **參數**: `max_gas_cost`
- **類型**: float
- **默認值**: 無限制
- **用途**: 過濾年化 Gas 成本
- **示例**:
  - 低 Gas: `max_gas_cost=100` (< $100/年)
  - 極低 Gas: `max_gas_cost=10` (< $10/年，主要是 L2)

### 9. 排序選項

#### 排序字段
- **參數**: `sort_by`
- **類型**: string
- **默認值**: `final_score`
- **可選值**:
  - `final_score` - 綜合評分（默認）
  - `net_apy` - 淨 APY
  - `tvl` - TVL
  - `davis_score` - 戴維斯評分
  - `roi` - ROI
  - `net_profit` - 預期淨收益
- **示例**:
  - 按 APY 排序: `sort_by=net_apy`
  - 按 TVL 排序: `sort_by=tvl`

#### 排序方向
- **參數**: `sort_order`
- **類型**: string
- **默認值**: `desc`
- **可選值**: `asc`, `desc`
- **示例**:
  - 降序: `sort_order=desc`
  - 升序: `sort_order=asc`

### 10. 結果限制

#### 返回數量
- **參數**: `limit`
- **類型**: int
- **默認值**: 5
- **範圍**: 1-100
- **用途**: 限制返回結果數量

#### 偏移量
- **參數**: `offset`
- **類型**: int
- **默認值**: 0
- **用途**: 分頁支持
- **示例**:
  - 第一頁: `limit=10&offset=0`
  - 第二頁: `limit=10&offset=10`

---

## 🔍 使用場景

### 場景 1: 保守投資者

**需求**: 大池、低風險、穩定收益

```
min_tvl=50000000
min_base_apy_ratio=80
il_risk=low
chains=Ethereum
protocols=uniswap-v3,curve-dex
```

### 場景 2: 激進投資者

**需求**: 高收益、可接受高風險

```
min_apy=50
min_davis_score=90
il_risk=high
chains=Arbitrum,Optimism,Base
```

### 場景 3: L2 專注

**需求**: 只要 L2、低 Gas

```
chains=Arbitrum,Optimism,Base
max_gas_cost=50
min_apy=20
```

### 場景 4: 穩定幣對

**需求**: 只要穩定幣對、低風險

```
include_tokens=USDC,USDT,DAI
il_risk=low
min_tvl=10000000
```

### 場景 5: 特定協議

**需求**: 只要 Uniswap V3、高評分

```
protocols=uniswap-v3
min_davis_score=90
min_apy=30
sort_by=net_apy
```

---

## 📊 API 端點設計

### 更新的智能搜尋端點

```
GET /api/v1/lal/smart-search
```

**完整參數列表**:

```
# 基礎參數
token: string = "ETH"
capital: float = 10000
risk_tolerance: string = "medium"

# TVL 篩選
min_tvl: float = 5000000
max_tvl: float = None

# APY 篩選
min_apy: float = 5.0
max_apy: float = None

# 協議篩選
protocols: string = None  # 逗號分隔

# 鏈篩選
chains: string = None  # 逗號分隔

# 代幣篩選
include_tokens: string = None  # 逗號分隔
exclude_tokens: string = None  # 逗號分隔

# 戴維斯篩選
min_davis_score: float = 0
max_davis_score: float = 100
davis_categories: string = None  # 逗號分隔

# 穩定性篩選
min_base_apy_ratio: float = 0

# 風險篩選
il_risk: string = None  # low/medium/high

# Gas 篩選
max_gas_cost: float = None

# 排序
sort_by: string = "final_score"
sort_order: string = "desc"

# 分頁
limit: int = 5
offset: int = 0
```

### 示例請求

#### 1. 保守投資
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

#### 2. L2 高收益
```bash
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?\
token=ETH&\
capital=10000&\
min_apy=50&\
chains=Arbitrum,Optimism,Base&\
max_gas_cost=50&\
sort_by=net_apy&\
limit=10"
```

#### 3. 穩定幣對
```bash
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?\
token=USDC&\
capital=10000&\
include_tokens=USDT,DAI&\
il_risk=low&\
min_tvl=10000000&\
limit=5"
```

---

## 🛠️ 實現計劃

### 階段 1: 核心篩選器類

創建 `LPFilter` 類：
- 驗證參數
- 應用篩選邏輯
- 返回篩選結果

### 階段 2: 整合到 LAL 搜尋

更新 `LALSmartSearch.search()` 方法：
- 接受篩選參數
- 應用篩選器
- 返回篩選後的結果

### 階段 3: 更新 API

更新 `lal_api_server_deploy.py`：
- 添加新參數
- 更新文檔
- 添加參數驗證

### 階段 4: 測試和部署

- 本地測試所有篩選組合
- 更新文檔
- 推送到 GitHub
- Render 自動部署

---

## 📝 響應格式

### 成功響應

```json
{
  "success": true,
  "data": {
    "query": {
      "token": "ETH",
      "capital": 10000,
      "filters": {
        "min_tvl": 50000000,
        "chains": ["Ethereum"],
        "protocols": ["uniswap-v3", "curve-dex"],
        "il_risk": "low"
      }
    },
    "opportunities": [...],
    "count": 5,
    "total_found": 25,
    "filters_applied": {
      "tvl": true,
      "chains": true,
      "protocols": true,
      "il_risk": true
    }
  }
}
```

### 錯誤響應

```json
{
  "success": false,
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Invalid chain: InvalidChain",
    "details": {
      "parameter": "chains",
      "value": "InvalidChain",
      "valid_values": ["Ethereum", "Arbitrum", "Optimism", ...]
    }
  }
}
```

---

## 🎯 預期效果

### 用戶體驗提升

1. **精確控制**: 用戶可以精確控制搜尋條件
2. **快速篩選**: 快速找到符合需求的池
3. **靈活組合**: 可以組合多個條件
4. **分頁支持**: 支持大量結果的分頁瀏覽

### 性能優化

1. **提前過濾**: 在戴維斯分析前就過濾掉不符合條件的池
2. **減少計算**: 只計算符合條件的池
3. **緩存友好**: 常見篩選組合可以緩存

---

## 📈 未來擴展

### 高級篩選

1. **時間範圍**: 過濾特定時間範圍的數據
2. **歷史表現**: 基於歷史 APY 穩定性篩選
3. **流動性深度**: 基於訂單簿深度篩選
4. **交易量**: 基於 24h 交易量篩選

### 智能推薦

1. **相似池推薦**: 基於用戶選擇推薦相似池
2. **風險匹配**: 自動匹配用戶風險偏好
3. **組合優化**: 推薦最佳池組合

---

**下一步**: 開始實現 LPFilter 類和更新 API

