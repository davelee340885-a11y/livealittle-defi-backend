#!/usr/bin/env python3.11
"""
測試 Delta Neutral 計算邏輯
驗證新的計算引擎是否正確工作
"""

import sys
sys.path.insert(0, 'backend')

from backend.il_calculator import DeltaNeutralCalculator
from backend.il_calculator_compat import ILCalculator, HedgeParams

def test_delta_neutral_calculator():
    """測試 Delta Neutral 計算器"""
    print("="*80)
    print("測試 Delta Neutral 計算器")
    print("="*80)
    
    calc = DeltaNeutralCalculator()
    
    # 測試場景 1: ETH-USDC LP 池
    print("\n【場景 1】ETH-USDC LP 池")
    print("-" * 80)
    
    capital = 10000  # $10,000
    lp_apy = 50.0    # 50% APY
    funding_apy = 10.0  # 10% 資金費率
    
    result = calc.calculate_delta_neutral_pnl(
        capital=capital,
        lp_apy=lp_apy,
        funding_apy=funding_apy,
        hedge_ratio=1.0,
        rebalance_frequency_days=7,
        chain="arbitrum"
    )
    
    print(f"投資資本: ${capital:,.0f}")
    print(f"LP APY: {lp_apy:.2f}%")
    print(f"資金費率 APY: {funding_apy:.2f}%")
    print(f"對沖比率: {result.hedge_ratio * 100:.0f}%")
    print(f"\n計算的 LP Delta: {result.lp_delta:.4f} ({result.lp_delta * 100:.2f}%)")
    print(f"\n收益分解:")
    print(f"  LP 手續費收益: ${result.profit_breakdown['lp_profit']:,.2f}")
    print(f"  資金費率成本: ${result.profit_breakdown['funding_cost']:,.2f}")
    print(f"  Gas 成本: ${result.profit_breakdown['gas_cost']:,.2f}")
    print(f"  總淨收益: ${result.profit_breakdown['total']:,.2f}")
    print(f"\n淨 APY: {result.net_apy:.2f}%")
    print(f"年化收益: ${result.annual_profit:,.2f}")
    print(f"風險等級: {result.risk_level}")
    print(f"最大回撤估算: {result.max_drawdown:.2f}%")
    
    # 測試場景 2: 價格變動模擬
    print("\n" + "="*80)
    print("【場景 2】價格變動模擬 - 驗證對沖效果")
    print("="*80)
    
    scenarios = [
        ("價格上漲 20%", 20),
        ("價格下跌 20%", -20),
        ("價格上漲 50%", 50),
        ("價格下跌 50%", -50),
    ]
    
    for scenario_name, price_change in scenarios:
        print(f"\n{scenario_name}")
        print("-" * 80)
        
        sim_result = calc.simulate_price_scenario(
            capital=capital,
            lp_apy=lp_apy,
            funding_apy=funding_apy,
            price_change_pct=price_change,
            hedge_ratio=1.0,
            days=30,  # 30 天
            chain="arbitrum"
        )
        
        print(f"LP 價值變化: ${sim_result['lp_value_change']:,.2f}")
        print(f"對沖倉位損益: ${sim_result['hedge_pnl']:,.2f}")
        print(f"對沖效果: {sim_result['hedge_effectiveness'] * 100:.2f}%")
        print(f"LP 手續費: ${sim_result['lp_fee']:,.2f}")
        print(f"資金費率成本: ${sim_result['funding_cost']:,.2f}")
        print(f"Gas 成本: ${sim_result['gas_cost']:,.2f}")
        print(f"總淨損益: ${sim_result['total_pnl']:,.2f}")
        print(f"最終資產價值: ${sim_result['final_value']:,.2f}")
        
        # 驗證對沖效果
        hedge_offset = sim_result['lp_value_change'] + sim_result['hedge_pnl']
        print(f"\n✓ 對沖抵消效果: ${hedge_offset:,.2f} (應接近 0)")


def test_il_calculator_compat():
    """測試兼容層"""
    print("\n" + "="*80)
    print("測試 IL Calculator 兼容層")
    print("="*80)
    
    calc = ILCalculator()
    
    # 測試場景: ETH-USDC
    print("\n【測試】ETH-USDC IL 分析")
    print("-" * 80)
    
    hedge_params = HedgeParams(
        hedge_ratio=1.0,
        rebalance_frequency_days=7
    )
    
    il_analysis = calc.analyze_il_with_hedge(
        token_a="ETH",
        token_b="USDC",
        capital=10000,
        hedge_params=hedge_params
    )
    
    print(f"池波動率: {il_analysis.pool_volatility:.2f}%")
    print(f"預期年化 IL: {il_analysis.expected_il_annual:.2f}%")
    print(f"對沖效果: {il_analysis.hedge_effectiveness * 100:.2f}%")
    print(f"淨 IL (對沖後): {il_analysis.net_il_annual:.2f}%")
    print(f"IL 影響 (USD): ${il_analysis.il_impact_usd:,.2f}")
    print(f"IL 風險等級: {il_analysis.il_risk_level}")
    print(f"波動率等級: {il_analysis.volatility_level}")
    print(f"對沖質量: {il_analysis.hedge_quality}")
    
    # 測試淨收益計算
    print("\n【測試】淨收益計算")
    print("-" * 80)
    
    profit_result = calc.calculate_adjusted_net_profit(
        lp_apy=50.0,
        funding_apy=10.0,
        net_il_annual=0.0,  # 在新邏輯中應該被忽略
        gas_cost_annual=200,
        capital=10000,
        hedge_ratio=1.0
    )
    
    print(f"LP 收益: ${profit_result['lp_profit']:,.2f}")
    print(f"資金費率成本: ${profit_result['funding_cost']:,.2f}")
    print(f"IL 損失: ${profit_result['il_loss']:,.2f} (應為 0)")
    print(f"Gas 成本: ${profit_result['gas_cost']:,.2f}")
    print(f"總淨收益: ${profit_result['total_profit']:,.2f}")
    print(f"淨 APY: {profit_result['net_apy']:.2f}%")


def test_volatility_mapping():
    """測試代幣波動率映射"""
    print("\n" + "="*80)
    print("測試代幣波動率映射")
    print("="*80)
    
    calc = DeltaNeutralCalculator()
    
    test_tokens = [
        "USDC", "USDT", "DAI",  # 穩定幣
        "ETH", "WETH", "BTC", "WBTC",  # 主流代幣
        "SOL", "AVAX", "MATIC",  # 大市值代幣
        "PEPE", "SHIB", "DOGE"  # 中小市值代幣
    ]
    
    print("\n代幣波動率:")
    print("-" * 80)
    for token in test_tokens:
        vol = calc.get_token_volatility(token)
        print(f"{token:10s}: {vol:6.1f}%")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("Delta Neutral 計算邏輯測試套件")
    print("="*80)
    print("\n這個測試驗證:")
    print("1. Delta Neutral 計算器的核心邏輯")
    print("2. 價格變動情境下的對沖效果")
    print("3. 兼容層是否正確工作")
    print("4. 代幣波動率映射")
    print("\n" + "="*80)
    
    try:
        test_delta_neutral_calculator()
        test_il_calculator_compat()
        test_volatility_mapping()
        
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

