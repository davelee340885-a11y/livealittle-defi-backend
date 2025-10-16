# Delta Neutral 計算器 V2 整合文檔

## 概述

Delta Neutral 計算器 V2 是對原有計算邏輯的重大升級,解決了以下關鍵問題:

1. **支持任意池權重** - 不再限於 50/50,支持 80/20, 60/40 等任意配置
2. **支持雙波動資產池** - 正確處理 ETH-BTC, SOL-ETH 等雙波動資產對
3. **精確 Delta 計算** - 使用 Uniswap V3 公式計算精確的 Delta
4. **多資產對沖策略** - 根據池類型自動決定對沖哪些資產
5. **相關性風險評估** - 評估雙波動資產池的額外風險

## 核心改進

### 1. 池類型識別

V2 計算器自動識別三種池類型:

```python
class PoolType(Enum):
    STABLE_STABLE = "stable-stable"          # USDC-USDT
    VOLATILE_STABLE = "volatile-stable"      # ETH-USDC
    VOLATILE_VOLATILE = "volatile-volatile"  # ETH-BTC
```

### 2. 精確 Delta 計算

#### 單波動資產池 (ETH-USDC)
- **Delta 計算**: 使用 Uniswap V3 公式
  ```
  Delta = (√P_upper - √P) / (√P_upper - √P_lower)
  ```
- **對沖策略**: 只對沖波動資產
- **對沖金額**: `capital × weight × Delta × hedge_ratio`

#### 雙波動資產池 (ETH-BTC)
- **Delta A**: 使用 Uniswap V3 公式計算
- **Delta B**: `1 - Delta A`
- **對沖策略**: **兩個資產都對沖**
- **對沖金額 A**: `capital × weight_a × Delta_a × hedge_ratio`
- **對沖金額 B**: `capital × weight_b × Delta_b × hedge_ratio`

### 3. 收益計算公式

#### 標準公式
```
淨收益 = LP 手續費 - 資金費率成本 A - 資金費率成本 B - Gas 成本
```

#### 詳細分解
```python
lp_profit = capital × (lp_apy / 100)
funding_cost_a = hedge_amount_a × (funding_rate_a_apy / 100)
funding_cost_b = hedge_amount_b × (funding_rate_b_apy / 100)
total_profit = lp_profit - funding_cost_a - funding_cost_b - gas_cost
```

### 4. 風險評估

#### 波動率敞口
```python
volatility_exposure = max(
    delta_a × (1 - hedge_ratio_a) × volatility_a,
    delta_b × (1 - hedge_ratio_b) × volatility_b
)
```

#### 相關性風險 (僅雙波動資產池)
```python
correlation_risk = min(volatility_a, volatility_b) / 100
```

#### 對沖有效性
```python
hedge_effectiveness = 1.0 - (volatility_exposure / 100)
```

## 使用方法

### 方法 1: 直接使用 V2 計算器

```python
from delta_neutral_calculator_v2 import DeltaNeutralCalculatorV2

calc = DeltaNeutralCalculatorV2()

# 創建池配置
pool_config = calc.create_pool_config(
    token_a="ETH",
    token_b="USDC",
    weight_a=0.8,  # 80% ETH
    weight_b=0.2,  # 20% USDC
    current_price=2000.0,
    price_lower=1800.0,
    price_upper=2200.0
)

# 計算 Delta Neutral 策略
result = calc.calculate_delta_neutral_strategy(
    pool_config=pool_config,
    capital=10000,
    lp_apy=50.0,
    funding_rate_a_apy=10.0,
    funding_rate_b_apy=0.0,
    hedge_ratio=1.0,
    gas_cost_annual=200
)

print(f"淨 APY: {result.net_apy:.2f}%")
print(f"對沖金額 A: ${result.hedge_amount_a_usd:,.2f}")
print(f"對沖金額 B: ${result.hedge_amount_b_usd:,.2f}")
```

### 方法 2: 使用兼容層 (推薦用於整合)

```python
from il_calculator_v2 import ILCalculatorV2, HedgeParamsV2

calc = ILCalculatorV2()

# 創建對沖參數
hedge_params = HedgeParamsV2(
    hedge_ratio=1.0,
    weight_a=0.8,
    weight_b=0.2,
    current_price=2000.0,
    price_lower=1800.0,
    price_upper=2200.0
)

# 計算淨收益
result = calc.calculate_adjusted_net_profit(
    token_a="ETH",
    token_b="USDC",
    lp_apy=50.0,
    funding_rate_a_apy=10.0,
    funding_rate_b_apy=0.0,
    gas_cost_annual=200,
    capital=10000,
    hedge_params=hedge_params
)

print(f"淨 APY: {result['net_apy']:.2f}%")
print(f"池類型: {result['pool_type']}")
print(f"Delta A: {result['delta_a']:.4f}")
print(f"Delta B: {result['delta_b']:.4f}")
```

### 方法 3: 使用池解析器 (自動解析)

```python
from pool_parser import PoolParser
from il_calculator_v2 import ILCalculatorV2, HedgeParamsV2

parser = PoolParser()
calc = ILCalculatorV2()

# 從池 symbol 解析
pool_info = parser.parse_pool(
    symbol="ETH-USDC-80-20",  # 自動解析為 80/20 權重
    protocol="balancer-v2",
    pool_data={"current_price": 2000.0}
)

# 創建對沖參數
hedge_params = HedgeParamsV2(
    hedge_ratio=1.0,
    weight_a=pool_info.weight_a,
    weight_b=pool_info.weight_b,
    current_price=pool_info.current_price
)

# 如果沒有價格範圍,估算一個
if not hedge_params.price_lower:
    hedge_params.price_lower, hedge_params.price_upper = parser.estimate_price_range(
        pool_info.current_price, 
        range_pct=10.0
    )

# 計算
result = calc.calculate_adjusted_net_profit(
    token_a=pool_info.token_a,
    token_b=pool_info.token_b,
    lp_apy=50.0,
    funding_rate_a_apy=10.0,
    funding_rate_b_apy=0.0,
    gas_cost_annual=200,
    capital=10000,
    hedge_params=hedge_params
)
```

## 測試結果

### 場景 1: 標準 50/50 池 (ETH-USDC)
- **淨 APY**: 45.56%
- **對沖策略**: 只對沖 ETH (48.7%)
- **風險等級**: 低

### 場景 2: 非對稱池 (ETH-USDC 80/20)
- **淨 APY**: 54.10%
- **對沖策略**: 只對沖 ETH (48.7%)
- **對沖金額更大**: $3,899.81 vs $2,437.38

### 場景 3: 雙波動資產池 (ETH-BTC 50/50)
- **淨 APY**: 33.51%
- **對沖策略**: **兩個都對沖** (ETH 48.7%, BTC 51.3%)
- **風險等級**: 高 (相關性風險)

### 場景 4: 雙波動資產池 (SOL-ETH 60/40)
- **淨 APY**: 61.60%
- **對沖策略**: 兩個都對沖 (SOL 47.9%, ETH 52.1%)
- **考慮不同波動率**: SOL 100%, ETH 80%

### 場景 5: 穩定幣池 (USDC-USDT)
- **淨 APY**: 4.00%
- **對沖策略**: 無需對沖
- **風險等級**: 極低

### 場景 6: 部分對沖 (ETH-USDC 50% 對沖)
- **淨 APY**: 46.78%
- **對沖金額減半**: $1,218.69
- **波動率敞口增加**: 29.49%

## 整合到 LAL 智能搜尋

### 步驟 1: 更新 lal_smart_search_v3.py

```python
from il_calculator_v2 import ILCalculatorV2, HedgeParamsV2
from pool_parser import PoolParser

class LALSmartSearchV3:
    def __init__(self):
        self.il_calculator = ILCalculatorV2()  # 使用 V2
        self.pool_parser = PoolParser()
        # ... 其他初始化
    
    def search(self, ...):
        for pool in davis_results:
            # 解析池配置
            pool_info = self.pool_parser.parse_pool(
                symbol=pool["symbol"],
                protocol=pool["protocol"],
                pool_data=pool.get("metadata", {})
            )
            
            # 創建對沖參數
            hedge_params = HedgeParamsV2(
                hedge_ratio=hedge_ratio,
                weight_a=pool_info.weight_a,
                weight_b=pool_info.weight_b,
                current_price=pool_info.current_price,
                price_lower=pool_info.price_lower,
                price_upper=pool_info.price_upper
            )
            
            # 獲取資金費率
            # 注意: 雙波動資產池需要兩個資金費率
            funding_rate_a_apy = self.get_funding_rate(pool_info.token_a)
            funding_rate_b_apy = self.get_funding_rate(pool_info.token_b)
            
            # 計算淨收益
            profit_result = self.il_calculator.calculate_adjusted_net_profit(
                token_a=pool_info.token_a,
                token_b=pool_info.token_b,
                lp_apy=pool["apy"],
                funding_rate_a_apy=funding_rate_a_apy,
                funding_rate_b_apy=funding_rate_b_apy,
                gas_cost_annual=annual_gas_cost,
                capital=capital,
                hedge_params=hedge_params
            )
```

### 步驟 2: 更新 API 響應格式

添加 V2 新增的字段:

```python
{
    "pool_type": "volatile-volatile",
    "delta_a": 0.4875,
    "delta_b": 0.5125,
    "hedge_amount_a_usd": 2437.38,
    "hedge_amount_b_usd": 2562.62,
    "volatility_exposure": 19.99,
    "correlation_risk": 0.8,
    "hedge_effectiveness": 0.8001,
    "risk_level": "高"
}
```

## 向後兼容性

V2 計算器完全向後兼容:

1. **舊版 API 仍然可用** - `il_calculator_compat.py` 提供舊版接口
2. **默認行為不變** - 如果不指定權重,默認 50/50
3. **漸進式升級** - 可以逐步遷移到 V2,不需要一次性修改所有代碼

## 性能考慮

V2 計算器的計算複雜度略高,但仍然非常快:

- **單次計算**: < 1ms
- **批量計算 (100 個池)**: < 100ms
- **無需額外 API 調用**: 所有計算都在本地完成

## 下一步

1. ✅ 完成 V2 計算器開發和測試
2. ⏳ 整合到 lal_smart_search_v3.py
3. ⏳ 更新 API 響應格式
4. ⏳ 部署到 Render
5. ⏳ 更新前端以顯示新字段
6. ⏳ 添加資金費率雙幣種支持

## 文件清單

- `delta_neutral_calculator_v2.py` - V2 核心計算引擎
- `il_calculator_v2.py` - V2 兼容層
- `pool_parser.py` - 池解析工具
- `test_calculator_v2.py` - V2 測試套件
- `DELTA_NEUTRAL_V2_INTEGRATION.md` - 本文檔

