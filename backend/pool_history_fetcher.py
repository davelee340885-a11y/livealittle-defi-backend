"""
Pool History Fetcher - 獲取池的歷史數據
從 DefiLlama API 獲取池的歷史 APY 和 TVL 數據，用於計算增長率
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time


class PoolHistoryFetcher:
    """獲取池的歷史數據並計算增長率"""
    
    BASE_URL = "https://yields.llama.fi/chart"
    TIMEOUT = 30  # API 請求超時時間（秒）
    
    def __init__(self):
        self._cache = {}  # 簡單的內存緩存
        self._cache_ttl = 3600  # 緩存有效期 1 小時
    
    def get_pool_history(self, pool_id: str, use_cache: bool = True) -> Optional[List[Dict]]:
        """
        獲取池的完整歷史數據
        
        Args:
            pool_id: DefiLlama 池 ID (UUID 格式)
            use_cache: 是否使用緩存
            
        Returns:
            歷史數據列表，每個元素包含：
            - timestamp: 日期時間
            - tvlUsd: TVL 數值（美元）
            - apy: 總 APY
            - apyBase: 基礎 APY
            - apyReward: 獎勵 APY
            
        Example:
            [
                {
                    "timestamp": "2025-10-17T00:00:00.000Z",
                    "tvlUsd": 155872710,
                    "apy": 55.64,
                    "apyBase": 47.32,
                    "apyReward": 8.32
                },
                ...
            ]
        """
        # 檢查緩存
        if use_cache and pool_id in self._cache:
            cached_data, cached_time = self._cache[pool_id]
            if time.time() - cached_time < self._cache_ttl:
                return cached_data
        
        try:
            url = f"{self.BASE_URL}/{pool_id}"
            response = requests.get(url, timeout=self.TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    history = data.get('data', [])
                    
                    # 更新緩存
                    if use_cache and history:
                        self._cache[pool_id] = (history, time.time())
                    
                    return history
                else:
                    print(f"API 回應狀態不是 success: {data.get('status')}")
                    return None
            else:
                print(f"API 請求失敗，狀態碼: {response.status_code}")
                return None
                
        except requests.Timeout:
            print(f"API 請求超時（{self.TIMEOUT}秒）")
            return None
        except Exception as e:
            print(f"獲取歷史數據失敗: {e}")
            return None
    
    def get_growth_rates(self, pool_id: str) -> Dict:
        """
        計算池的增長率
        
        Args:
            pool_id: DefiLlama 池 ID
            
        Returns:
            {
                # 7天變化
                'apy_7d_change': float,      # 7天 APY 變化百分比
                'tvl_7d_change': float,      # 7天 TVL 變化百分比
                'apy_7d_ago': float,         # 7天前的 APY
                'tvl_7d_ago': float,         # 7天前的 TVL
                
                # 30天變化
                'apy_30d_change': float,     # 30天 APY 變化百分比
                'tvl_30d_change': float,     # 30天 TVL 變化百分比
                'apy_30d_ago': float,        # 30天前的 APY
                'tvl_30d_ago': float,        # 30天前的 TVL
                
                # 當前數據
                'current_apy': float,        # 當前 APY
                'current_tvl': float,        # 當前 TVL
                'current_date': str,         # 當前日期
                
                # 元數據
                'has_history': bool,         # 是否有歷史數據
                'history_days': int          # 歷史數據天數
            }
        """
        history = self.get_pool_history(pool_id)
        
        # 如果無法獲取歷史數據，返回默認值
        if not history or len(history) < 2:
            return self._get_default_growth_rates()
        
        # 獲取當前和歷史數據
        current = history[-1]
        seven_days_ago = history[-8] if len(history) >= 8 else history[0]
        thirty_days_ago = history[-31] if len(history) >= 31 else history[0]
        
        # 計算變化率
        apy_7d_change = self._calculate_change_percent(
            seven_days_ago.get('apy', 0),
            current.get('apy', 0)
        )
        
        tvl_7d_change = self._calculate_change_percent(
            seven_days_ago.get('tvlUsd', 0),
            current.get('tvlUsd', 0)
        )
        
        apy_30d_change = self._calculate_change_percent(
            thirty_days_ago.get('apy', 0),
            current.get('apy', 0)
        )
        
        tvl_30d_change = self._calculate_change_percent(
            thirty_days_ago.get('tvlUsd', 0),
            current.get('tvlUsd', 0)
        )
        
        return {
            # 7天變化
            'apy_7d_change': apy_7d_change,
            'tvl_7d_change': tvl_7d_change,
            'apy_7d_ago': seven_days_ago.get('apy', 0),
            'tvl_7d_ago': seven_days_ago.get('tvlUsd', 0),
            
            # 30天變化
            'apy_30d_change': apy_30d_change,
            'tvl_30d_change': tvl_30d_change,
            'apy_30d_ago': thirty_days_ago.get('apy', 0),
            'tvl_30d_ago': thirty_days_ago.get('tvlUsd', 0),
            
            # 當前數據
            'current_apy': current.get('apy', 0),
            'current_tvl': current.get('tvlUsd', 0),
            'current_date': current.get('timestamp', '')[:10],
            
            # 元數據
            'has_history': True,
            'history_days': len(history)
        }
    
    def _calculate_change_percent(self, old_value: float, new_value: float) -> float:
        """
        計算變化百分比
        
        Args:
            old_value: 舊值
            new_value: 新值
            
        Returns:
            變化百分比（例如：+50.0 表示增長 50%，-25.0 表示下降 25%）
        """
        if old_value == 0:
            return 0.0
        
        change_percent = ((new_value - old_value) / old_value) * 100
        return round(change_percent, 2)
    
    def _get_default_growth_rates(self) -> Dict:
        """
        返回默認的增長率（當無法獲取歷史數據時）
        所有增長率設為 0，表示無變化
        """
        return {
            # 7天變化
            'apy_7d_change': 0.0,
            'tvl_7d_change': 0.0,
            'apy_7d_ago': 0.0,
            'tvl_7d_ago': 0.0,
            
            # 30天變化
            'apy_30d_change': 0.0,
            'tvl_30d_change': 0.0,
            'apy_30d_ago': 0.0,
            'tvl_30d_ago': 0.0,
            
            # 當前數據
            'current_apy': 0.0,
            'current_tvl': 0.0,
            'current_date': '',
            
            # 元數據
            'has_history': False,
            'history_days': 0
        }
    
    def clear_cache(self):
        """清空緩存"""
        self._cache.clear()


# 測試代碼
if __name__ == "__main__":
    print("=" * 60)
    print("測試 PoolHistoryFetcher")
    print("=" * 60 + "\n")
    
    fetcher = PoolHistoryFetcher()
    
    # 測試池 ID（Uniswap V3 WETH-USDT on Ethereum）
    test_pool_id = "fc9f488e-8183-416f-a61e-4e5c571d4395"
    
    print(f"正在獲取池 {test_pool_id} 的增長率...\n")
    
    growth_rates = fetcher.get_growth_rates(test_pool_id)
    
    if growth_rates['has_history']:
        print("✅ 成功獲取歷史數據！\n")
        
        print("當前數據：")
        print(f"  日期: {growth_rates['current_date']}")
        print(f"  APY: {growth_rates['current_apy']:.2f}%")
        print(f"  TVL: ${growth_rates['current_tvl']:,.0f}")
        print(f"  歷史天數: {growth_rates['history_days']} 天\n")
        
        print("7天變化：")
        print(f"  APY: {growth_rates['apy_7d_ago']:.2f}% → {growth_rates['current_apy']:.2f}% ({growth_rates['apy_7d_change']:+.2f}%)")
        print(f"  TVL: ${growth_rates['tvl_7d_ago']:,.0f} → ${growth_rates['current_tvl']:,.0f} ({growth_rates['tvl_7d_change']:+.2f}%)\n")
        
        print("30天變化：")
        print(f"  APY: {growth_rates['apy_30d_ago']:.2f}% → {growth_rates['current_apy']:.2f}% ({growth_rates['apy_30d_change']:+.2f}%)")
        print(f"  TVL: ${growth_rates['tvl_30d_ago']:,.0f} → ${growth_rates['current_tvl']:,.0f} ({growth_rates['tvl_30d_change']:+.2f}%)")
    else:
        print("❌ 無法獲取歷史數據")

