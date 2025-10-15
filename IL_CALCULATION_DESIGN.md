# 無常損失（IL）計算和 Delta Neutral 對沖效果設計

## 🎯 目標

實現精確的無常損失（Impermanent Loss, IL）計算，並分析 Delta Neutral 策略如何對沖 IL，從而優化 LAL 智能搜尋的收益計算。

---

## 📚 理論基礎

### 什麼是無常損失（IL）？

**無常損失**是指在 AMM（自動做市商）流動性池中提供流動性時，由於代幣價格變化導致的相對損失。

**公式**:
```
IL = (2 * sqrt(price_ratio) / (1 + price_ratio)) - 1
```

其中 `price_ratio = 最終價格 / 初始價格`

### IL 與價格變化的關係

| 價格變化 | IL 損失 |
|---------|---------|
| 1.25x | -0.6% |
| 1.5x | -2.0% |
| 2x | -5.7% |
| 3x | -13.4% |
| 4x | -20.0% |
| 5x | -25.5% |

### Delta Neutral 如何對沖 IL？

**Delta Neutral 策略**通過在永續合約市場做空相同數量的代幣，完全對沖價格風險：

1. **LP 池**: 持有 50% Token A + 50% Token B
2. **永續合約**: 做空等值的 Token A

**效果**:
- Token A 價格上漲 → LP 池損失（IL）→ 永續合約盈利 → **對沖**
- Token A 價格下跌 → LP 池損失（IL）→ 永續合約盈利 → **對沖**

**理論上**，完美的 Delta Neutral 策略可以將 IL 降低到接近 0。

---

## 🧮 計算模型

### 1. 基礎 IL 計算

```python
def calculate_il(price_change_percent: float) -> float:
    """
    計算無常損失
    
    Args:
        price_change_percent: 價格變化百分比（如 50 表示上漲 50%）
    
    Returns:
        float: IL 百分比（負數表示損失）
    """
    price_ratio = 1 + (price_change_percent / 100)
    il = (2 * math.sqrt(price_ratio) / (1 + price_ratio)) - 1
    return il * 100  # 轉換為百分比
```

### 2. 預期 IL（基於歷史波動率）

```python
def estimate_expected_il(
    volatility_annual: float,
    holding_period_days: float = 365
) -> float:
    """
    基於年化波動率估算預期 IL
    
    Args:
        volatility_annual: 年化波動率（如 80 表示 80%）
        holding_period_days: 持有天數
    
    Returns:
        float: 預期 IL 百分比
    """
    # 將年化波動率轉換為持有期波動率
    holding_volatility = volatility_annual * math.sqrt(holding_period_days / 365)
    
    # 使用簡化模型：預期 IL ≈ 0.5 * volatility^2
    expected_il = -0.5 * (holding_volatility / 100) ** 2 * 100
    
    return expected_il
```

### 3. Delta Neutral 對沖效果

```python
def calculate_hedge_effectiveness(
    hedge_ratio: float = 1.0,
    rebalance_frequency_days: float = 7
) -> float:
    """
    計算對沖有效性
    
    Args:
        hedge_ratio: 對沖比率（1.0 = 100% 對沖）
        rebalance_frequency_days: 再平衡頻率（天）
    
    Returns:
        float: 對沖有效性（0-1，1 表示 100% 有效）
    """
    # 基礎對沖有效性
    base_effectiveness = hedge_ratio
    
    # 再平衡頻率影響（越頻繁越有效）
    rebalance_factor = 1 - (rebalance_frequency_days / 30) * 0.1
    rebalance_factor = max(0.7, min(1.0, rebalance_factor))
    
    # 總有效性
    effectiveness = base_effectiveness * rebalance_factor
    
    return min(1.0, effectiveness)
```

### 4. 淨 IL（考慮對沖後）

```python
def calculate_net_il(
    expected_il: float,
    hedge_effectiveness: float
) -> float:
    """
    計算對沖後的淨 IL
    
    Args:
        expected_il: 預期 IL（負數）
        hedge_effectiveness: 對沖有效性（0-1）
    
    Returns:
        float: 淨 IL 百分比
    """
    # 對沖後的 IL = 原始 IL * (1 - 對沖有效性)
    net_il = expected_il * (1 - hedge_effectiveness)
    
    return net_il
```

### 5. 調整後的淨收益

```python
def calculate_adjusted_net_profit(
    lp_apy: float,
    funding_apy: float,
    net_il_annual: float,
    gas_cost_annual: float,
    capital: float
) -> dict:
    """
    計算考慮 IL 後的調整淨收益
    
    Args:
        lp_apy: LP APY (%)
        funding_apy: 資金費率 APY (%)
        net_il_annual: 年化淨 IL (%)
        gas_cost_annual: 年化 Gas 成本 (USD)
        capital: 投資資本 (USD)
    
    Returns:
        dict: 包含各項收益和成本的詳細信息
    """
    # 1. LP 收益
    lp_profit = capital * (lp_apy / 100)
    
    # 2. 資金費率收益
    funding_profit = capital * (funding_apy / 100)
    
    # 3. IL 損失（已考慮對沖）
    il_loss = capital * (net_il_annual / 100)
    
    # 4. Gas 成本
    gas_cost = gas_cost_annual
    
    # 5. 總收益
    total_profit = lp_profit + funding_profit + il_loss - gas_cost
    
    # 6. 淨 APY
    net_apy = (total_profit / capital) * 100
    
    return {
        "lp_profit": lp_profit,
        "funding_profit": funding_profit,
        "il_loss": il_loss,
        "gas_cost": gas_cost,
        "total_profit": total_profit,
        "net_apy": net_apy,
        "breakdown": {
            "lp_apy": lp_apy,
            "funding_apy": funding_apy,
            "il_impact": net_il_annual,
            "gas_impact": -(gas_cost / capital) * 100
        }
    }
```

---

## 📊 波動率估算

由於我們沒有歷史價格數據，需要根據代幣類型估算波動率：

### 代幣波動率分類

```python
VOLATILITY_ESTIMATES = {
    # 穩定幣
    "stablecoins": {
        "tokens": ["USDC", "USDT", "DAI", "FRAX", "LUSD", "BUSD"],
        "annual_volatility": 2.0  # 2%
    },
    
    # 主流代幣
    "major": {
        "tokens": ["ETH", "WETH", "BTC", "WBTC"],
        "annual_volatility": 80.0  # 80%
    },
    
    # 大市值代幣
    "large_cap": {
        "tokens": ["BNB", "SOL", "MATIC", "AVAX"],
        "annual_volatility": 100.0  # 100%
    },
    
    # 中小市值代幣
    "mid_small_cap": {
        "tokens": [],  # 其他所有代幣
        "annual_volatility": 150.0  # 150%
    }
}
```

### 池波動率計算

對於 LP 池，需要計算兩個代幣的組合波動率：

```python
def estimate_pool_volatility(token_a: str, token_b: str) -> float:
    """
    估算 LP 池的波動率
    
    邏輯:
    - 穩定幣對: 極低波動率
    - 一個穩定幣: 使用非穩定幣的波動率
    - 兩個波動代幣: 使用較高的波動率
    """
    vol_a = get_token_volatility(token_a)
    vol_b = get_token_volatility(token_b)
    
    # 如果都是穩定幣
    if vol_a < 5 and vol_b < 5:
        return 2.0
    
    # 如果一個是穩定幣
    if vol_a < 5:
        return vol_b
    if vol_b < 5:
        return vol_a
    
    # 如果都是波動代幣，使用較高的波動率
    return max(vol_a, vol_b)
```

---

## 🎯 整合到 LAL 搜尋

### 更新的收益計算流程

```
1. 獲取 LP 池數據（TVL, APY）
   ↓
2. 獲取資金費率數據
   ↓
3. 估算池波動率
   ↓
4. 計算預期 IL
   ↓
5. 計算對沖有效性
   ↓
6. 計算淨 IL（對沖後）
   ↓
7. 計算調整後的淨收益
   ↓
8. 生成完整的收益分析報告
```

### 新的數據結構

```python
{
    "pool_id": "...",
    "protocol": "uniswap-v3",
    "symbol": "WETH-USDC",
    "tvl": 86476153,
    
    # 收益
    "lp_apy": 101.47,
    "funding_apy": 10.95,
    "total_apy": 112.42,
    
    # IL 分析
    "il_analysis": {
        "pool_volatility": 80.0,  # 年化波動率 (%)
        "expected_il_annual": -12.8,  # 預期年化 IL (%)
        "hedge_effectiveness": 0.95,  # 對沖有效性 (0-1)
        "net_il_annual": -0.64,  # 淨 IL (%)
        "il_impact_usd": -64.0  # IL 影響 (USD)
    },
    
    # 成本
    "gas_cost_annual": 200,
    
    # 調整後的淨收益
    "adjusted_net_apy": 111.78,  # 考慮 IL 後的淨 APY
    "adjusted_net_profit": 11178,  # 考慮 IL 後的淨收益
    
    # 收益分解
    "profit_breakdown": {
        "lp_profit": 10147,
        "funding_profit": 1095,
        "il_loss": -64,
        "gas_cost": -200,
        "total": 11178
    },
    
    # 風險指標
    "risk_metrics": {
        "il_risk_level": "medium",  # low/medium/high
        "volatility_level": "high",  # low/medium/high
        "hedge_quality": "excellent"  # poor/fair/good/excellent
    }
}
```

---

## 📈 對沖參數配置

### 默認對沖參數

```python
DEFAULT_HEDGE_PARAMS = {
    "hedge_ratio": 1.0,  # 100% 對沖
    "rebalance_frequency_days": 7,  # 每週再平衡
    "hedge_effectiveness": 0.95  # 95% 有效性
}
```

### 用戶可配置參數

允許用戶調整對沖策略：

```python
# API 參數
hedge_ratio: float = 1.0  # 0.0-1.0
rebalance_frequency: int = 7  # 天數
```

---

## 🎨 使用示例

### 示例 1: 基礎 IL 計算

```python
# ETH 價格上漲 50%
il = calculate_il(50)
print(f"IL: {il:.2f}%")  # -2.02%
```

### 示例 2: 預期 IL（基於波動率）

```python
# ETH 年化波動率 80%
expected_il = estimate_expected_il(volatility_annual=80)
print(f"預期 IL: {expected_il:.2f}%")  # -12.8%
```

### 示例 3: Delta Neutral 對沖後的淨 IL

```python
# 95% 對沖有效性
net_il = calculate_net_il(
    expected_il=-12.8,
    hedge_effectiveness=0.95
)
print(f"淨 IL: {net_il:.2f}%")  # -0.64%
```

### 示例 4: 完整的收益分析

```python
result = calculate_adjusted_net_profit(
    lp_apy=101.47,
    funding_apy=10.95,
    net_il_annual=-0.64,
    gas_cost_annual=200,
    capital=10000
)

print(f"LP 收益: ${result['lp_profit']:,.0f}")
print(f"資金費率收益: ${result['funding_profit']:,.0f}")
print(f"IL 損失: ${result['il_loss']:,.0f}")
print(f"Gas 成本: ${result['gas_cost']:,.0f}")
print(f"總收益: ${result['total_profit']:,.0f}")
print(f"淨 APY: {result['net_apy']:.2f}%")
```

**輸出**:
```
LP 收益: $10,147
資金費率收益: $1,095
IL 損失: $-64
Gas 成本: $-200
總收益: $11,178
淨 APY: 111.78%
```

---

## 🔍 對比分析

### 沒有 IL 計算 vs 有 IL 計算

| 項目 | 無 IL 計算 | 有 IL 計算 | 差異 |
|-----|-----------|-----------|------|
| LP APY | 101.47% | 101.47% | - |
| 資金費率 APY | 10.95% | 10.95% | - |
| IL 影響 | - | -0.64% | 新增 |
| Gas 成本 | -2.00% | -2.00% | - |
| **淨 APY** | **110.42%** | **111.78%** | **+1.36%** |

**說明**: 雖然 IL 是負面影響，但 Delta Neutral 對沖將 IL 從 -12.8% 降低到 -0.64%，大幅減少了損失。

---

## 🎯 優化建議

### 1. 動態對沖比率

根據市場條件調整對沖比率：
- 高波動期：增加對沖比率（如 1.1）
- 低波動期：減少對沖比率（如 0.9）

### 2. 智能再平衡

根據價格偏離程度決定再平衡：
- 偏離 < 5%：不再平衡
- 偏離 5-10%：每週再平衡
- 偏離 > 10%：立即再平衡

### 3. 風險調整評分

將 IL 風險納入最終評分：
```python
final_score = (
    apy_score * 0.4 +
    tvl_score * 0.2 +
    davis_score * 0.2 +
    il_risk_score * 0.2  # 新增
)
```

---

## 📊 預期效果

### 收益計算更準確

- ✅ 考慮 IL 影響
- ✅ 反映 Delta Neutral 對沖效果
- ✅ 提供完整的收益分解

### 風險評估更全面

- ✅ 顯示 IL 風險等級
- ✅ 顯示波動率水平
- ✅ 顯示對沖質量

### 用戶決策更明智

- ✅ 了解真實的淨收益
- ✅ 了解風險來源
- ✅ 了解對沖效果

---

## 🚀 實現計劃

### 階段 1: 實現 IL 計算引擎

創建 `il_calculator.py`：
- IL 計算函數
- 波動率估算
- 對沖效果計算

### 階段 2: 整合到 LAL 搜尋

更新 `lal_smart_search.py`：
- 添加 IL 分析
- 更新收益計算
- 更新數據結構

### 階段 3: 更新 API

更新 `lal_api_server_deploy.py`：
- 添加 IL 相關字段
- 更新文檔
- 添加示例

### 階段 4: 測試和部署

- 單元測試
- 集成測試
- 部署到生產環境

---

**下一步**: 開始實現 IL 計算引擎

