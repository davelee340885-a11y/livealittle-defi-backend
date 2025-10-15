"""
測試 LP 篩選器功能
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_filters():
    """測試所有篩選場景"""
    
    print("🧪 測試 LAL 智能搜尋 - LP 篩選器")
    print("=" * 60)
    
    # 測試 1: 獲取支持的篩選選項
    print("\n測試 1: 獲取支持的篩選選項")
    print("-" * 60)
    response = requests.get(f"{BASE_URL}/api/v1/lal/filters")
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✅ 支持的協議: {len(data['protocols'])} 個")
        print(f"   {', '.join(data['protocols'][:5])}...")
        print(f"✅ 支持的鏈: {len(data['chains'])} 個")
        print(f"   {', '.join(data['chains'][:5])}...")
        print(f"✅ 戴維斯評級: {', '.join(data['davis_categories'])}")
        print(f"✅ 風險等級: {', '.join(data['il_risk_levels'])}")
        print(f"✅ 排序字段: {', '.join(data['sort_fields'])}")
    else:
        print(f"❌ 失敗: {response.status_code}")
    
    # 測試 2: 基礎搜尋（無篩選）
    print("\n測試 2: 基礎搜尋（無篩選）")
    print("-" * 60)
    response = requests.get(
        f"{BASE_URL}/api/v1/lal/smart-search",
        params={"token": "ETH", "capital": 10000, "limit": 3}
    )
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✅ 找到 {data['count']} 個機會")
        for i, opp in enumerate(data['opportunities'], 1):
            print(f"   {i}. {opp['protocol']} - {opp['symbol']} ({opp['chain']})")
            print(f"      淨 APY: {opp['net_apy']:.2f}%, TVL: ${opp['tvl']:,.0f}")
    else:
        print(f"❌ 失敗: {response.status_code}")
    
    # 測試 3: 鏈篩選（只要 L2）
    print("\n測試 3: 鏈篩選（只要 L2: Arbitrum, Optimism, Base）")
    print("-" * 60)
    response = requests.get(
        f"{BASE_URL}/api/v1/lal/smart-search",
        params={
            "token": "ETH",
            "capital": 10000,
            "chains": "Arbitrum,Optimism,Base",
            "limit": 3
        }
    )
    if response.status_code == 200:
        data = response.json()["data"]
        summary = data['filter_summary']
        print(f"✅ 篩選前: {summary['total_before_filter']} 個池")
        print(f"✅ 篩選後: {summary['total_after_filter']} 個池")
        print(f"✅ 過濾掉: {summary['filtered_out']} 個池")
        print(f"\n找到的機會:")
        for i, opp in enumerate(data['opportunities'], 1):
            print(f"   {i}. {opp['symbol']} on {opp['chain']}")
            print(f"      淨 APY: {opp['net_apy']:.2f}%")
    else:
        print(f"❌ 失敗: {response.status_code}")
    
    # 測試 4: APY 篩選（高收益）
    print("\n測試 4: APY 篩選（APY >= 100%）")
    print("-" * 60)
    response = requests.get(
        f"{BASE_URL}/api/v1/lal/smart-search",
        params={
            "token": "ETH",
            "capital": 10000,
            "min_apy": 100,
            "limit": 3
        }
    )
    if response.status_code == 200:
        data = response.json()["data"]
        summary = data['filter_summary']
        print(f"✅ 篩選前: {summary['total_before_filter']} 個池")
        print(f"✅ 篩選後: {summary['total_after_filter']} 個池")
        print(f"\n高收益機會:")
        for i, opp in enumerate(data['opportunities'], 1):
            print(f"   {i}. {opp['symbol']} ({opp['chain']})")
            print(f"      淨 APY: {opp['net_apy']:.2f}%")
            print(f"      預期年收益: ${opp['net_profit']:,.0f}")
    else:
        print(f"❌ 失敗: {response.status_code}")
    
    # 測試 5: 風險篩選（低風險穩定幣對）
    print("\n測試 5: 風險篩選（低風險穩定幣對）")
    print("-" * 60)
    response = requests.get(
        f"{BASE_URL}/api/v1/lal/smart-search",
        params={
            "token": "USDC",
            "capital": 10000,
            "il_risk": "low",
            "limit": 3
        }
    )
    if response.status_code == 200:
        data = response.json()["data"]
        summary = data['filter_summary']
        print(f"✅ 篩選前: {summary['total_before_filter']} 個池")
        print(f"✅ 篩選後: {summary['total_after_filter']} 個池")
        print(f"\n低風險機會:")
        for i, opp in enumerate(data['opportunities'], 1):
            print(f"   {i}. {opp['symbol']} ({opp['chain']})")
            print(f"      淨 APY: {opp['net_apy']:.2f}%")
            print(f"      TVL: ${opp['tvl']:,.0f}")
    else:
        print(f"❌ 失敗: {response.status_code}")
    
    # 測試 6: 組合篩選（L2 + 高 APY + 低 Gas）
    print("\n測試 6: 組合篩選（L2 + APY >= 50% + Gas < $50）")
    print("-" * 60)
    response = requests.get(
        f"{BASE_URL}/api/v1/lal/smart-search",
        params={
            "token": "ETH",
            "capital": 10000,
            "chains": "Arbitrum,Optimism,Base",
            "min_apy": 50,
            "max_gas_cost": 50,
            "limit": 5
        }
    )
    if response.status_code == 200:
        data = response.json()["data"]
        summary = data['filter_summary']
        print(f"✅ 篩選前: {summary['total_before_filter']} 個池")
        print(f"✅ 篩選後: {summary['total_after_filter']} 個池")
        print(f"✅ 應用的篩選: {list(summary['filters_applied'].keys())}")
        print(f"\n最佳組合機會:")
        for i, opp in enumerate(data['opportunities'], 1):
            print(f"   {i}. {opp['symbol']} ({opp['chain']})")
            print(f"      淨 APY: {opp['net_apy']:.2f}%")
            print(f"      Gas 成本: ${opp['gas_cost_annual']:.2f}/年")
            print(f"      預期年收益: ${opp['net_profit']:,.0f}")
    else:
        print(f"❌ 失敗: {response.status_code}")
    
    # 測試 7: 協議篩選
    print("\n測試 7: 協議篩選（只要 Uniswap V3）")
    print("-" * 60)
    response = requests.get(
        f"{BASE_URL}/api/v1/lal/smart-search",
        params={
            "token": "ETH",
            "capital": 10000,
            "protocols": "uniswap-v3",
            "min_apy": 30,
            "limit": 3
        }
    )
    if response.status_code == 200:
        data = response.json()["data"]
        summary = data['filter_summary']
        print(f"✅ 篩選前: {summary['total_before_filter']} 個池")
        print(f"✅ 篩選後: {summary['total_after_filter']} 個池")
        print(f"\nUniswap V3 機會:")
        for i, opp in enumerate(data['opportunities'], 1):
            print(f"   {i}. {opp['symbol']} ({opp['chain']})")
            print(f"      淨 APY: {opp['net_apy']:.2f}%")
            print(f"      協議: {opp['protocol']}")
    else:
        print(f"❌ 失敗: {response.status_code}")
    
    # 測試 8: 排序測試（按 TVL 排序）
    print("\n測試 8: 排序測試（按 TVL 降序）")
    print("-" * 60)
    response = requests.get(
        f"{BASE_URL}/api/v1/lal/smart-search",
        params={
            "token": "ETH",
            "capital": 10000,
            "sort_by": "tvl",
            "sort_order": "desc",
            "limit": 3
        }
    )
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✅ 按 TVL 排序的結果:")
        for i, opp in enumerate(data['opportunities'], 1):
            print(f"   {i}. {opp['symbol']} ({opp['chain']})")
            print(f"      TVL: ${opp['tvl']:,.0f}")
            print(f"      淨 APY: {opp['net_apy']:.2f}%")
    else:
        print(f"❌ 失敗: {response.status_code}")
    
    # 測試 9: 分頁測試
    print("\n測試 9: 分頁測試（第 2 頁，每頁 2 個）")
    print("-" * 60)
    response = requests.get(
        f"{BASE_URL}/api/v1/lal/smart-search",
        params={
            "token": "ETH",
            "capital": 10000,
            "limit": 2,
            "offset": 2
        }
    )
    if response.status_code == 200:
        data = response.json()["data"]
        pagination = data['pagination']
        print(f"✅ 分頁信息:")
        print(f"   limit: {pagination['limit']}")
        print(f"   offset: {pagination['offset']}")
        print(f"   total: {pagination['total']}")
        print(f"\n第 2 頁結果:")
        for i, opp in enumerate(data['opportunities'], 1):
            print(f"   {i}. {opp['symbol']} ({opp['chain']})")
    else:
        print(f"❌ 失敗: {response.status_code}")
    
    # 測試 10: 錯誤處理（無效的鏈）
    print("\n測試 10: 錯誤處理（無效的鏈名稱）")
    print("-" * 60)
    response = requests.get(
        f"{BASE_URL}/api/v1/lal/smart-search",
        params={
            "token": "ETH",
            "capital": 10000,
            "chains": "InvalidChain"
        }
    )
    if response.status_code == 400:
        error = response.json()["detail"]
        print(f"✅ 正確返回錯誤:")
        print(f"   {error}")
    else:
        print(f"❌ 應該返回 400 錯誤，但返回了: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ 所有測試完成！")


if __name__ == "__main__":
    test_filters()

