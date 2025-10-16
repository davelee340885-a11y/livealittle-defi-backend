#!/usr/bin/env python3.11
"""
測試 Delta Neutral 計算器 V2
驗證支持不同池權重和雙波動資產的計算
"""

import sys
sys.path.insert(0, 'backend')

from backend.delta_neutral_calculator_v2 import (
    DeltaNeutralCalculatorV2,
    PoolType
)


def print_result(title: str, result):
    """打印結果"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")
    
    print(f"\n【池配置】")
    print(f"類型: {result.pool_type.value}")
    print(f"Token A: {result.pool_config.token_a.symbol} (權重: {result.pool_config.weight_a*100:.1f}%, 波動率: {result.pool_config.token_a.volatility:.1f}%)")
    print(f"Token B: {result.pool_config.token_b.symbol} (權重: {result.pool_config.weight_b*100:.1f}%, 波動率: {result.pool_config.token_b.volatility:.1f}%)")
    
    print(f"\n【Delta 分析】")
    print(f"Delta A: {result.delta_a:.4f} ({result.delta_a*100:.2f}%)")
    print(f"Delta B: {result.delta_b:.4f} ({result.delta_b*100:.2f}%)")
    print(f"總 Delta (USD): ${result.total_delta_usd:,.2f}")
    
    print(f"\n【對沖策略】")
    print(f"對沖 Token A: {'是' if result.hedge_strategy.hedge_token_a else '否'} (比率: {result.hedge_strategy.hedge_ratio_a*100:.1f}%)")
    print(f"對沖 Token B: {'是' if result.hedge_strategy.hedge_token_b else '否'} (比率: {result.hedge_strategy.hedge_ratio_b*100:.1f}%)")
    print(f"對沖金額 A: ${result.hedge_amount_a_usd:,.2f}")
    print(f"對沖金額 B: ${result.hedge_amount_b_usd:,.2f}")
    
    print(f"\n【收益分析】")
    print(f"LP 手續費 APY: {result.lp_fee_apy:.2f}%")
    print(f"資金費率成本 A: {result.funding_cost_a_apy:.2f}%")
    print(f"資金費率成本 B: {result.funding_cost_b_apy:.2f}%")
    print(f"總資金費率成本: {result.total_funding_cost_apy:.2f}%")
    print(f"淨 APY: {result.net_apy:.2f}%")
    print(f"年化收益: ${result.annual_profit:,.2f}")
    
    print(f"\n【收益分解】")
    for key, value in result.profit_breakdown.items():
        sign = "+" if value >= 0 else ""
        print(f"  {key:20s}: {sign}${value:,.2f}")
    
    print(f"\n【風險指標】")
    print(f"波動率敞口: {result.volatility_exposure:.2f}%")
    print(f"相關性風險: {result.correlation_risk:.4f}")
    print(f"對沖有效性: {result.hedge_effectiveness*100:.2f}%")
    print(f"風險等級: {result.risk_level}")


def test_scenario_1_standard_50_50():
    """場景 1: 標準 50/50 池 - ETH-USDC"""
    print("\n" + "="*80)
    print("場景 1: 標準 50/50 池 - ETH-USDC")
    print("="*80)
    
    calc = DeltaNeutralCalculatorV2()
    
    pool_config = calc.create_pool_config(
        token_a="ETH",
        token_b="USDC",
        weight_a=0.5,
        weight_b=0.5,
        current_price=100,
        price_lower=90,
        price_upper=110
    )
    
    result = calc.calculate_delta_neutral_strategy(
        pool_config=pool_config,
        capital=10000,
        lp_apy=50.0,
        funding_rate_a_apy=10.0,
        funding_rate_b_apy=0.0,
        hedge_ratio=1.0,
        gas_cost_annual=200
    )
    
    print_result("ETH-USDC (50/50)", result)


def test_scenario_2_weighted_pool():
    """場景 2: 非對稱權重池 - ETH-USDC (80/20)"""
    print("\n" + "="*80)
    print("場景 2: 非對稱權重池 - ETH-USDC (80/20)")
    print("="*80)
    
    calc = DeltaNeutralCalculatorV2()
    
    pool_config = calc.create_pool_config(
        token_a="ETH",
        token_b="USDC",
        weight_a=0.8,
        weight_b=0.2,
        current_price=100,
        price_lower=90,
        price_upper=110
    )
    
    result = calc.calculate_delta_neutral_strategy(
        pool_config=pool_config,
        capital=10000,
        lp_apy=60.0,
        funding_rate_a_apy=10.0,
        funding_rate_b_apy=0.0,
        hedge_ratio=1.0,
        gas_cost_annual=200
    )
    
    print_result("ETH-USDC (80/20)", result)


def test_scenario_3_volatile_volatile():
    """場景 3: 雙波動資產池 - ETH-BTC (50/50)"""
    print("\n" + "="*80)
    print("場景 3: 雙波動資產池 - ETH-BTC (50/50)")
    print("="*80)
    
    calc = DeltaNeutralCalculatorV2()
    
    pool_config = calc.create_pool_config(
        token_a="ETH",
        token_b="BTC",
        weight_a=0.5,
        weight_b=0.5,
        current_price=0.05,  # 1 ETH = 0.05 BTC
        price_lower=0.045,
        price_upper=0.055
    )
    
    result = calc.calculate_delta_neutral_strategy(
        pool_config=pool_config,
        capital=10000,
        lp_apy=40.0,
        funding_rate_a_apy=10.0,  # ETH 資金費率
        funding_rate_b_apy=8.0,   # BTC 資金費率
        hedge_ratio=1.0,
        gas_cost_annual=200
    )
    
    print_result("ETH-BTC (50/50)", result)


def test_scenario_4_sol_eth():
    """場景 4: 雙波動資產池 - SOL-ETH (60/40)"""
    print("\n" + "="*80)
    print("場景 4: 雙波動資產池 - SOL-ETH (60/40)")
    print("="*80)
    
    calc = DeltaNeutralCalculatorV2()
    
    pool_config = calc.create_pool_config(
        token_a="SOL",
        token_b="ETH",
        weight_a=0.6,
        weight_b=0.4,
        current_price=0.03,  # 1 SOL = 0.03 ETH
        price_lower=0.025,
        price_upper=0.035
    )
    
    result = calc.calculate_delta_neutral_strategy(
        pool_config=pool_config,
        capital=10000,
        lp_apy=70.0,
        funding_rate_a_apy=15.0,  # SOL 資金費率
        funding_rate_b_apy=10.0,  # ETH 資金費率
        hedge_ratio=1.0,
        gas_cost_annual=200
    )
    
    print_result("SOL-ETH (60/40)", result)


def test_scenario_5_stable_stable():
    """場景 5: 穩定幣池 - USDC-USDT (50/50)"""
    print("\n" + "="*80)
    print("場景 5: 穩定幣池 - USDC-USDT (50/50)")
    print("="*80)
    
    calc = DeltaNeutralCalculatorV2()
    
    pool_config = calc.create_pool_config(
        token_a="USDC",
        token_b="USDT",
        weight_a=0.5,
        weight_b=0.5
    )
    
    result = calc.calculate_delta_neutral_strategy(
        pool_config=pool_config,
        capital=10000,
        lp_apy=5.0,
        funding_rate_a_apy=0.0,
        funding_rate_b_apy=0.0,
        hedge_ratio=1.0,
        gas_cost_annual=100
    )
    
    print_result("USDC-USDT (50/50)", result)


def test_scenario_6_partial_hedge():
    """場景 6: 部分對沖 - ETH-USDC (50% 對沖)"""
    print("\n" + "="*80)
    print("場景 6: 部分對沖 - ETH-USDC (50% 對沖)")
    print("="*80)
    
    calc = DeltaNeutralCalculatorV2()
    
    pool_config = calc.create_pool_config(
        token_a="ETH",
        token_b="USDC",
        weight_a=0.5,
        weight_b=0.5,
        current_price=100,
        price_lower=90,
        price_upper=110
    )
    
    result = calc.calculate_delta_neutral_strategy(
        pool_config=pool_config,
        capital=10000,
        lp_apy=50.0,
        funding_rate_a_apy=10.0,
        funding_rate_b_apy=0.0,
        hedge_ratio=0.5,  # 只對沖 50%
        gas_cost_annual=200
    )
    
    print_result("ETH-USDC (50% 對沖)", result)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("Delta Neutral 計算器 V2 測試套件")
    print("="*80)
    print("\n測試不同場景:")
    print("1. 標準 50/50 池")
    print("2. 非對稱權重池")
    print("3. 雙波動資產池")
    print("4. 不同波動率的雙波動資產")
    print("5. 穩定幣池")
    print("6. 部分對沖策略")
    
    try:
        test_scenario_1_standard_50_50()
        test_scenario_2_weighted_pool()
        test_scenario_3_volatile_volatile()
        test_scenario_4_sol_eth()
        test_scenario_5_stable_stable()
        test_scenario_6_partial_hedge()
        
        print("\n" + "="*80)
        print("✅ 所有測試完成!")
        print("="*80)
        
    except Exception as e:
        print("\n" + "="*80)
        print(f"❌ 測試失敗: {e}")
        print("="*80)
        import traceback
        traceback.print_exc()
        sys.exit(1)

