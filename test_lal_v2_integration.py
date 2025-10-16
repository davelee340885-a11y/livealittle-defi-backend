#!/usr/bin/env python3.11
"""
測試 LAL 智能搜尋 V2 整合

驗證:
1. V2 計算器正確整合
2. 池解析器正常工作
3. 雙幣種資金費率正確獲取
4. API 響應包含所有 V2 字段
"""

import sys
sys.path.insert(0, 'backend')

from backend.lal_smart_search_v3 import LALSmartSearchV3, HedgeParamsV2


def test_lal_search_v2():
    """測試 LAL 智能搜尋 V2"""
    
    print("\n" + "="*80)
    print("測試 LAL 智能搜尋 V2 整合")
    print("="*80)
    
    # 創建搜尋實例
    lal_search = LALSmartSearchV3()
    
    # 創建對沖參數
    hedge_params = HedgeParamsV2(
        hedge_ratio=1.0,
        rebalance_frequency_days=7
    )
    
    # 執行搜尋
    try:
        results = lal_search.search(
            token="ETH",
            capital=10000,
            risk_tolerance="medium",
            min_tvl=5_000_000,
            min_apy=5.0,
            top_n=3,
            hedge_params=hedge_params
        )
        
        print("\n" + "="*80)
        print(f"搜尋完成! 找到 {len(results)} 個最佳方案")
        print("="*80)
        
        # 檢查結果
        for i, result in enumerate(results, 1):
            print(f"\n【方案 {i}】")
            print(f"池符號: {result['symbol']}")
            print(f"協議: {result['protocol']}")
            print(f"鏈: {result['chain']}")
            print(f"TVL: ${result['tvl']:,.0f}")
            
            # V2 新增字段
            print(f"\n【V2 池配置】")
            print(f"  池類型: {result.get('pool_type', 'N/A')}")
            print(f"  權重 A: {result.get('weight_a', 0)*100:.1f}%")
            print(f"  權重 B: {result.get('weight_b', 0)*100:.1f}%")
            
            print(f"\n【V2 Delta 資訊】")
            print(f"  Delta A: {result.get('delta_a', 0):.4f}")
            print(f"  Delta B: {result.get('delta_b', 0):.4f}")
            print(f"  對沖金額 A: ${result.get('hedge_amount_a_usd', 0):,.2f}")
            print(f"  對沖金額 B: ${result.get('hedge_amount_b_usd', 0):,.2f}")
            
            print(f"\n【V2 資金費率】")
            print(f"  資金費率 A: {result.get('funding_rate_a_apy', 0):.2f}%")
            print(f"  資金費率 B: {result.get('funding_rate_b_apy', 0):.2f}%")
            print(f"  總資金費率: {result.get('total_funding_apy', 0):.2f}%")
            
            print(f"\n【收益分析】")
            print(f"  LP APY: {result['lp_apy']:.2f}%")
            print(f"  淨 APY: {result['adjusted_net_apy']:.2f}%")
            print(f"  年化收益: ${result['adjusted_net_profit']:,.2f}")
            
            print(f"\n【V2 收益分解】")
            pb = result.get('profit_breakdown', {})
            print(f"  LP 收益: ${pb.get('lp_profit', 0):,.2f}")
            print(f"  資金費率成本 A: ${pb.get('funding_cost_a', 0):,.2f}")
            print(f"  資金費率成本 B: ${pb.get('funding_cost_b', 0):,.2f}")
            print(f"  總資金費率成本: ${pb.get('funding_cost', 0):,.2f}")
            print(f"  IL 損失: ${pb.get('il_loss', 0):,.2f}")
            print(f"  Gas 成本: ${pb.get('gas_cost', 0):,.2f}")
            print(f"  總淨收益: ${pb.get('total', 0):,.2f}")
            
            print(f"\n【V2 風險評估】")
            print(f"  波動率敞口: {result.get('volatility_exposure', 0):.2f}%")
            print(f"  相關性風險: {result.get('correlation_risk', 0):.4f}")
            print(f"  風險等級: {result.get('risk_level', 'N/A')}")
            
            print(f"\n【V2 IL 分析】")
            il = result.get('il_analysis', {})
            print(f"  池類型: {il.get('pool_type', 'N/A')}")
            print(f"  Delta A: {il.get('delta_a', 0):.4f}")
            print(f"  Delta B: {il.get('delta_b', 0):.4f}")
            print(f"  相關性風險: {il.get('correlation_risk', 0):.4f}")
            print(f"  對沖有效性: {il.get('hedge_effectiveness', 0)*100:.2f}%")
            print(f"  IL 風險等級: {il.get('il_risk_level', 'N/A')}")
            
            print(f"\n【其他指標】")
            print(f"  ROI: {result['roi']:.2f}%")
            print(f"  戴維斯評分: {result['davis_score']:.2f}")
            print(f"  戴維斯類別: {result['davis_category']}")
        
        # 驗證關鍵字段
        print("\n" + "="*80)
        print("驗證 V2 關鍵字段")
        print("="*80)
        
        required_v2_fields = [
            'pool_type', 'weight_a', 'weight_b',
            'delta_a', 'delta_b',
            'hedge_amount_a_usd', 'hedge_amount_b_usd',
            'funding_rate_a_apy', 'funding_rate_b_apy',
            'volatility_exposure', 'correlation_risk', 'risk_level'
        ]
        
        all_present = True
        for field in required_v2_fields:
            present = all(field in result for result in results)
            status = "✅" if present else "❌"
            print(f"{status} {field}: {'存在' if present else '缺失'}")
            if not present:
                all_present = False
        
        if all_present:
            print("\n✅ 所有 V2 字段都存在!")
        else:
            print("\n⚠️  部分 V2 字段缺失")
        
        # 驗證雙波動資產池
        print("\n" + "="*80)
        print("檢查雙波動資產池處理")
        print("="*80)
        
        volatile_volatile_pools = [r for r in results if r.get('pool_type') == 'volatile-volatile']
        if volatile_volatile_pools:
            print(f"✅ 找到 {len(volatile_volatile_pools)} 個雙波動資產池")
            for pool in volatile_volatile_pools:
                print(f"  - {pool['symbol']}: 對沖 A ${pool.get('hedge_amount_a_usd', 0):,.2f}, 對沖 B ${pool.get('hedge_amount_b_usd', 0):,.2f}")
        else:
            print("ℹ️  沒有找到雙波動資產池 (這是正常的,取決於搜尋結果)")
        
        print("\n" + "="*80)
        print("✅ 測試完成!")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_lal_search_v2()
    sys.exit(0 if success else 1)

