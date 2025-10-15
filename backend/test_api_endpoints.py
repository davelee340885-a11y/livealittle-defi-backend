"""
API 端點快速測試腳本
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """打印分隔線"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}\n")

def test_health():
    """測試健康檢查"""
    print_section("測試 1: 健康檢查")
    
    response = requests.get(f"{BASE_URL}/")
    data = response.json()
    
    print(f"狀態: {data['status']}")
    print(f"版本: {data['version']}")
    print(f"時間: {data['timestamp']}")
    print(f"✅ 健康檢查通過")

def test_token_prices():
    """測試代幣價格"""
    print_section("測試 2: 代幣價格")
    
    response = requests.get(f"{BASE_URL}/api/v1/market/tokens?symbols=ETH,BTC,USDC")
    prices = response.json()
    
    for price in prices:
        print(f"{price['symbol']}:")
        print(f"  價格: ${price['price']:,.2f}")
        print(f"  24h 變化: {price['change_24h']:+.2f}%")
        print(f"  24h 交易量: ${price['volume_24h']:,.0f}")
        print()
    
    print(f"✅ 獲取 {len(prices)} 個代幣價格")

def test_lp_pools():
    """測試 LP 池"""
    print_section("測試 3: LP 池列表")
    
    response = requests.get(f"{BASE_URL}/api/v1/market/pools?min_tvl=5000000&limit=5")
    pools = response.json()
    
    for i, pool in enumerate(pools, 1):
        print(f"{i}. {pool['protocol']} - {pool['symbol']}")
        print(f"   Chain: {pool['chain']}")
        print(f"   TVL: ${pool['tvl']:,.0f}")
        print(f"   APY: {pool['apy']:.2f}%")
        print()
    
    print(f"✅ 獲取 {len(pools)} 個 LP 池")

def test_funding_rates():
    """測試資金費率"""
    print_section("測試 4: 資金費率")
    
    response = requests.get(f"{BASE_URL}/api/v1/market/funding-rates?coins=ETH,BTC")
    rates = response.json()
    
    for rate in rates:
        print(f"{rate['coin']}:")
        print(f"  當前費率: {rate['current_rate_pct']:.4f}%")
        print(f"  平均費率: {rate['avg_rate_pct']:.4f}%")
        print(f"  年化費率: {rate['annualized_rate_pct']:.2f}%")
        print(f"  數據源: {rate['source']}")
        print()
    
    print(f"✅ 獲取 {len(rates)} 個資金費率")

def test_market_sentiment():
    """測試市場情緒"""
    print_section("測試 5: 市場情緒")
    
    response = requests.get(f"{BASE_URL}/api/v1/market/sentiment")
    sentiment = response.json()
    
    print(f"恐懼與貪婪指數: {sentiment['value']}")
    print(f"分類: {sentiment['classification']}")
    print(f"時間: {sentiment['timestamp']}")
    
    # 情緒解讀
    value = sentiment['value']
    if value < 25:
        interpretation = "極度恐懼 - 可能是買入機會"
    elif value < 50:
        interpretation = "恐懼 - 市場謹慎"
    elif value < 75:
        interpretation = "貪婪 - 市場樂觀"
    else:
        interpretation = "極度貪婪 - 注意風險"
    
    print(f"解讀: {interpretation}")
    print(f"✅ 市場情緒獲取成功")

def test_delta_neutral_opportunities():
    """測試 Delta Neutral 機會"""
    print_section("測試 6: Delta Neutral 機會")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/delta-neutral/opportunities",
        params={"token": "ETH", "capital": 10000, "top_n": 3}
    )
    opportunities = response.json()
    
    for i, opp in enumerate(opportunities, 1):
        print(f"{i}. {opp['protocol']} - {opp['symbol']}")
        print(f"   Chain: {opp['chain']}")
        print(f"   TVL: ${opp['tvl']:,.0f}")
        print(f"   LP APY: {opp['lp_apy']:.2f}%")
        print(f"   資金費率 APY: {opp['funding_apy']:.2f}%")
        print(f"   總 APY: {opp['total_apy']:.2f}%")
        print(f"   預期年收益: ${opp['annual_yield']:,.0f}")
        print(f"   評分: {opp['score']:.1f}/100")
        print()
    
    print(f"✅ 找到 {len(opportunities)} 個機會")

def test_strategy_report():
    """測試策略報告"""
    print_section("測試 7: 完整策略報告")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/delta-neutral/report",
        params={"token": "ETH", "capital": 10000}
    )
    report = response.json()
    
    print(f"代幣: {report['token']}")
    print(f"資本: ${report['capital']:,.0f}")
    print(f"時間: {report['timestamp']}")
    
    print(f"\n📊 市場數據:")
    market = report['market_data']
    print(f"  當前價格: ${market['token_price']:,.2f}")
    print(f"  24h 變化: {market['price_change_24h']:+.2f}%")
    print(f"  恐懼與貪婪指數: {market['fear_greed_index']}")
    print(f"  市場情緒: {market['market_sentiment']}")
    
    print(f"\n🏆 最佳機會:")
    best = report['best_opportunity']
    print(f"  協議: {best['protocol']}")
    print(f"  池: {best['symbol']}")
    print(f"  總 APY: {best['total_apy']:.2f}%")
    print(f"  預期年收益: ${best['annual_yield']:,.0f}")
    
    print(f"\n🛡️ 對沖信息:")
    hedge = report['hedge_info']
    print(f"  需對沖代幣數量: {hedge['token_amount']:.4f} ETH")
    print(f"  對沖倉位大小: ${hedge['hedge_position_size']:,.0f}")
    
    print(f"\n💡 建議:")
    print(f"  {report['recommendation']}")
    
    print(f"\n✅ 策略報告生成成功")

def test_calculate_hedge():
    """測試對沖計算"""
    print_section("測試 8: 對沖比率計算")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/delta-neutral/calculate-hedge",
        params={
            "lp_value": 10000,
            "token_price": 4000,
            "pool_composition": 0.5
        }
    )
    hedge = response.json()
    
    print(f"LP 價值: ${hedge['lp_value']:,.0f}")
    print(f"LP 中代幣價值: ${hedge['token_value_in_lp']:,.0f}")
    print(f"需對沖代幣數量: {hedge['token_amount']:.4f}")
    print(f"代幣價格: ${hedge['token_price']:,.2f}")
    print(f"對沖倉位大小: ${hedge['hedge_position_size']:,.0f}")
    print(f"槓桿: {hedge['hedge_leverage']}x")
    
    print(f"\n✅ 對沖計算成功")

def test_calculate_yield():
    """測試收益計算"""
    print_section("測試 9: 總收益計算")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/delta-neutral/calculate-yield",
        params={
            "lp_apy": 15.5,
            "funding_rate_apy": 10.95,
            "capital": 10000,
            "gas_cost_annual": 200
        }
    )
    yield_calc = response.json()
    
    print(f"LP APY: {yield_calc['lp_apy']:.2f}%")
    print(f"LP 年收益: ${yield_calc['lp_yield_annual']:,.0f}")
    print(f"資金費率 APY: {yield_calc['funding_rate_apy']:.2f}%")
    print(f"資金費率年收益: ${yield_calc['funding_yield_annual']:,.0f}")
    print(f"Gas 成本 APY: {yield_calc['gas_cost_apy']:.2f}%")
    print(f"Gas 年成本: ${yield_calc['gas_cost_annual']:,.0f}")
    print(f"\n總 APY: {yield_calc['total_apy']:.2f}%")
    print(f"總年收益: ${yield_calc['total_yield_annual']:,.0f}")
    
    print(f"\n✅ 收益計算成功")

def test_rebalance_decision():
    """測試轉倉決策"""
    print_section("測試 10: 轉倉決策")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/delta-neutral/rebalance-decision",
        params={
            "current_apy": 20,
            "new_apy": 28,
            "rebalance_cost": 50,
            "capital": 10000
        }
    )
    decision = response.json()
    
    print(f"當前 APY: {decision['current_apy']:.2f}%")
    print(f"新池 APY: {decision['new_apy']:.2f}%")
    print(f"APY 提升: {decision['apy_improvement']:.2f}%")
    print(f"年收益提升: ${decision['yield_improvement_annual']:,.0f}")
    print(f"日收益提升: ${decision['yield_improvement_daily']:.2f}")
    print(f"轉倉成本: ${decision['rebalance_cost']:.2f}")
    print(f"回本天數: {decision['payback_days']:.1f} 天")
    print(f"ROI: {decision['roi']:.0f}%")
    print(f"\n決策: {'✅ 建議轉倉' if decision['should_rebalance'] else '❌ 不建議轉倉'}")
    print(f"原因: {decision['reason']}")
    
    print(f"\n✅ 轉倉決策計算成功")

def run_all_tests():
    """運行所有測試"""
    print(f"\n{'#'*60}")
    print(f"# Delta Neutral API 端點測試")
    print(f"# 時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}")
    
    try:
        test_health()
        test_token_prices()
        test_lp_pools()
        test_funding_rates()
        test_market_sentiment()
        test_delta_neutral_opportunities()
        test_strategy_report()
        test_calculate_hedge()
        test_calculate_yield()
        test_rebalance_decision()
        
        print_section("🎉 所有測試通過！")
        print("API 服務器運行正常，所有端點都可以正常訪問。")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 錯誤: 無法連接到 API 服務器")
        print("請確保 API 服務器正在運行：")
        print("  cd /home/ubuntu/defi_system/backend")
        print("  python3.11 api_server_v2.py")
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()

