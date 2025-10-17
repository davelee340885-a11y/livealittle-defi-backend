"""
流動性評估器 (優化版)
使用預設等級 + 緩存機制，大幅提升響應速度和可靠性
"""

from typing import Dict, Optional
import requests
from datetime import datetime, timedelta


class LiquidityScorerOptimized:
    """優化的流動性評分器"""
    
    def __init__(self):
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        
        # 預設流動性等級
        self.tier1_tokens = {
            "BTC", "ETH", "USDC", "USDT", "DAI"
        }
        
        self.tier2_tokens = {
            "WETH", "WBTC", "BNB", "MATIC", "AVAX", "ARB", "OP", "SOL"
        }
        
        self.tier3_tokens = {
            "UNI", "AAVE", "CRV", "LINK", "MKR", "SNX", "COMP", "SUSHI",
            "LDO", "RPL", "FRAX", "FXS", "CVX", "BAL", "PENDLE", "GMX",
            "GNS", "RDNT", "STG", "FTM"
        }
        
        # 簡單內存緩存
        self.cache = {}
        self.cache_ttl = 3600  # 1小時
        
    def get_token_liquidity_data(self, token_symbol: str) -> Optional[Dict]:
        """
        獲取代幣流動性數據（優化版）
        
        優先使用預設等級，只在必要時調用API
        
        Args:
            token_symbol: 代幣符號 (如 "WETH", "USDC")
        
        Returns:
            流動性數據字典
        """
        # 標準化代幣符號
        normalized_symbol = self._normalize_token_symbol(token_symbol)
        
        # 檢查預設等級
        if normalized_symbol in self.tier1_tokens:
            return self._get_tier1_data(normalized_symbol)
        elif normalized_symbol in self.tier2_tokens:
            return self._get_tier2_data(normalized_symbol)
        elif normalized_symbol in self.tier3_tokens:
            return self._get_tier3_data(normalized_symbol)
        else:
            # 其他代幣：嘗試從緩存或API獲取
            return self._get_data_with_cache(normalized_symbol)
    
    def calculate_liquidity_score(self, liquidity_data: Dict) -> Dict:
        """
        計算流動性評分
        
        Args:
            liquidity_data: 流動性數據
        
        Returns:
            評分結果，包含總分和各項子分數
        """
        if not liquidity_data:
            return {
                "total_score": 0,
                "volume_score": 0,
                "depth_score": 0,
                "spread_score": 0,
                "grade": "F",
                "details": "無流動性數據",
                "meets_minimum": False
            }
        
        # 如果是預設等級，直接返回預設評分
        if liquidity_data.get("preset_tier"):
            return liquidity_data.get("score_result")
        
        # 否則按原邏輯計算
        volume = liquidity_data.get("volume_24h_usd", 0)
        volume_score = self._score_volume(volume)
        
        depth = liquidity_data.get("estimated_depth_usd", 0)
        depth_score = self._score_depth(depth)
        
        spread = liquidity_data.get("avg_spread_percentage")
        spread_score = self._score_spread(spread)
        
        total_score = (
            volume_score * 0.4 +
            depth_score * 0.4 +
            spread_score * 0.2
        )
        
        grade = self._get_grade(total_score)
        
        return {
            "total_score": round(total_score, 2),
            "volume_score": round(volume_score, 2),
            "depth_score": round(depth_score, 2),
            "spread_score": round(spread_score, 2),
            "grade": grade,
            "volume_24h_usd": volume,
            "estimated_depth_usd": depth,
            "avg_spread_percentage": spread,
            "meets_minimum": self._meets_minimum_threshold(liquidity_data)
        }
    
    def _get_tier1_data(self, symbol: str) -> Dict:
        """Tier 1: 超高流動性代幣"""
        return {
            "symbol": symbol,
            "volume_24h_usd": 20_000_000_000,  # $20B
            "avg_spread_percentage": 0.01,
            "estimated_depth_usd": 20_000_000,  # $20M
            "market_cap_usd": 200_000_000_000,  # $200B
            "data_source": "preset_tier1",
            "timestamp": datetime.now().isoformat(),
            "preset_tier": "Tier 1",
            "score_result": {
                "total_score": 100.0,
                "volume_score": 100.0,
                "depth_score": 100.0,
                "spread_score": 100.0,
                "grade": "A",
                "volume_24h_usd": 20_000_000_000,
                "estimated_depth_usd": 20_000_000,
                "avg_spread_percentage": 0.01,
                "meets_minimum": True
            }
        }
    
    def _get_tier2_data(self, symbol: str) -> Dict:
        """Tier 2: 高流動性代幣"""
        return {
            "symbol": symbol,
            "volume_24h_usd": 2_000_000_000,  # $2B
            "avg_spread_percentage": 0.05,
            "estimated_depth_usd": 2_000_000,  # $2M
            "market_cap_usd": 20_000_000_000,  # $20B
            "data_source": "preset_tier2",
            "timestamp": datetime.now().isoformat(),
            "preset_tier": "Tier 2",
            "score_result": {
                "total_score": 90.0,
                "volume_score": 90.0,
                "depth_score": 90.0,
                "spread_score": 90.0,
                "grade": "A",
                "volume_24h_usd": 2_000_000_000,
                "estimated_depth_usd": 2_000_000,
                "avg_spread_percentage": 0.05,
                "meets_minimum": True
            }
        }
    
    def _get_tier3_data(self, symbol: str) -> Dict:
        """Tier 3: 中等流動性代幣"""
        return {
            "symbol": symbol,
            "volume_24h_usd": 200_000_000,  # $200M
            "avg_spread_percentage": 0.1,
            "estimated_depth_usd": 200_000,  # $200K
            "market_cap_usd": 2_000_000_000,  # $2B
            "data_source": "preset_tier3",
            "timestamp": datetime.now().isoformat(),
            "preset_tier": "Tier 3",
            "score_result": {
                "total_score": 75.0,
                "volume_score": 75.0,
                "depth_score": 75.0,
                "spread_score": 75.0,
                "grade": "B",
                "volume_24h_usd": 200_000_000,
                "estimated_depth_usd": 200_000,
                "avg_spread_percentage": 0.1,
                "meets_minimum": True
            }
        }
    
    def _get_data_with_cache(self, symbol: str) -> Optional[Dict]:
        """
        從緩存或API獲取數據
        
        Args:
            symbol: 代幣符號
        
        Returns:
            流動性數據或None
        """
        # 檢查緩存
        cache_key = f"liquidity_{symbol}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                return cached_data
        
        # 嘗試從API獲取（設置短超時）
        try:
            coin_id = self._get_coingecko_id(symbol)
            if not coin_id:
                return None
            
            url = f"{self.coingecko_api}/coins/{coin_id}"
            params = {
                "localization": "false",
                "tickers": "false",  # 不獲取tickers以加快速度
                "market_data": "true"
            }
            
            response = requests.get(url, params=params, timeout=3)  # 3秒超時
            if response.status_code != 200:
                return None
            
            data = response.json()
            market_data = data.get("market_data", {})
            
            volume_24h = market_data.get("total_volume", {}).get("usd", 0)
            market_cap = market_data.get("market_cap", {}).get("usd", 0)
            estimated_depth = market_cap * 0.001
            
            result = {
                "symbol": symbol,
                "volume_24h_usd": volume_24h,
                "avg_spread_percentage": 0.2,  # 默認值
                "estimated_depth_usd": estimated_depth,
                "market_cap_usd": market_cap,
                "data_source": "coingecko",
                "timestamp": datetime.now().isoformat()
            }
            
            # 緩存結果
            self.cache[cache_key] = (result, datetime.now())
            
            return result
            
        except Exception as e:
            print(f"⚠️  獲取流動性數據失敗 ({symbol}): {e}")
            # 返回保守的默認值
            return {
                "symbol": symbol,
                "volume_24h_usd": 1_000_000,  # $1M (不滿足門檻)
                "avg_spread_percentage": 0.5,
                "estimated_depth_usd": 100_000,
                "market_cap_usd": 10_000_000,
                "data_source": "fallback",
                "timestamp": datetime.now().isoformat()
            }
    
    def _score_volume(self, volume_usd: float) -> float:
        """交易量評分"""
        if volume_usd >= 100_000_000:
            return 100.0
        elif volume_usd >= 10_000_000:
            return 80.0 + (volume_usd - 10_000_000) / 90_000_000 * 20
        elif volume_usd >= 5_000_000:
            return 60.0 + (volume_usd - 5_000_000) / 5_000_000 * 20
        else:
            return max(0, volume_usd / 5_000_000 * 60)
    
    def _score_depth(self, depth_usd: float) -> float:
        """訂單簿深度評分"""
        if depth_usd >= 5_000_000:
            return 100.0
        elif depth_usd >= 1_000_000:
            return 80.0 + (depth_usd - 1_000_000) / 4_000_000 * 20
        elif depth_usd >= 500_000:
            return 60.0 + (depth_usd - 500_000) / 500_000 * 20
        else:
            return max(0, depth_usd / 500_000 * 60)
    
    def _score_spread(self, spread_percentage: Optional[float]) -> float:
        """買賣價差評分"""
        if spread_percentage is None:
            return 50.0
        
        if spread_percentage < 0.1:
            return 100.0
        elif spread_percentage < 0.3:
            return 80.0 + (0.3 - spread_percentage) / 0.2 * 20
        elif spread_percentage < 0.5:
            return 60.0 + (0.5 - spread_percentage) / 0.2 * 20
        else:
            return max(0, 60.0 - (spread_percentage - 0.5) * 40)
    
    def _get_grade(self, score: float) -> str:
        """評分等級"""
        if score >= 85:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 50:
            return "C"
        elif score >= 30:
            return "D"
        else:
            return "F"
    
    def _meets_minimum_threshold(self, liquidity_data: Dict) -> bool:
        """
        檢查是否滿足最低流動性門檻
        
        最低要求: 24小時交易量 >= $5M
        """
        volume = liquidity_data.get("volume_24h_usd", 0)
        return volume >= 5_000_000
    
    def _normalize_token_symbol(self, symbol: str) -> str:
        """標準化代幣符號"""
        symbol = symbol.upper()
        if symbol.startswith("W"):
            base = symbol[1:]
            if base in ["ETH", "BTC", "BNB", "MATIC", "AVAX", "FTM"]:
                return base
        return symbol
    
    def _get_coingecko_id(self, symbol: str) -> Optional[str]:
        """獲取CoinGecko的coin_id"""
        symbol_to_id = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "USDC": "usd-coin",
            "USDT": "tether",
            "DAI": "dai",
            "WETH": "weth",
            "WBTC": "wrapped-bitcoin",
            "BNB": "binancecoin",
            "MATIC": "matic-network",
            "AVAX": "avalanche-2",
            "FTM": "fantom",
            "ARB": "arbitrum",
            "OP": "optimism",
            "SOL": "solana",
            "LINK": "chainlink",
            "UNI": "uniswap",
            "AAVE": "aave",
            "CRV": "curve-dao-token",
            "MKR": "maker",
            "SNX": "havven",
            "COMP": "compound-governance-token",
            "SUSHI": "sushi",
            "LDO": "lido-dao",
            "RPL": "rocket-pool",
            "FRAX": "frax",
            "FXS": "frax-share",
            "CVX": "convex-finance",
            "BAL": "balancer",
            "PENDLE": "pendle",
            "GMX": "gmx",
            "GNS": "gains-network",
            "RDNT": "radiant-capital",
            "STG": "stargate-finance"
        }
        
        return symbol_to_id.get(symbol)


# 測試代碼
if __name__ == "__main__":
    import time
    
    scorer = LiquidityScorerOptimized()
    
    # 測試不同等級的代幣
    test_tokens = [
        ("ETH", "Tier 1"),
        ("USDC", "Tier 1"),
        ("ARB", "Tier 2"),
        ("PENDLE", "Tier 3")
    ]
    
    print("=" * 80)
    print("優化的流動性評分測試")
    print("=" * 80)
    
    total_time = 0
    
    for token, expected_tier in test_tokens:
        print(f"\n測試代幣: {token} (預期: {expected_tier})")
        print("-" * 80)
        
        start_time = time.time()
        
        # 獲取流動性數據
        data = scorer.get_token_liquidity_data(token)
        
        elapsed = time.time() - start_time
        total_time += elapsed
        
        if data:
            print(f"✅ 數據獲取成功 (耗時: {elapsed:.3f}秒)")
            print(f"  數據來源: {data.get('data_source', 'N/A')}")
            print(f"  24小時交易量: ${data['volume_24h_usd']:,.0f}")
            
            # 計算評分
            score_result = scorer.calculate_liquidity_score(data)
            print(f"\n評分結果:")
            print(f"  總分: {score_result['total_score']}/100 (等級: {score_result['grade']})")
            print(f"  滿足最低門檻: {'✅ 是' if score_result['meets_minimum'] else '❌ 否'}")
        else:
            print(f"❌ 數據獲取失敗")
    
    print(f"\n{'=' * 80}")
    print(f"總耗時: {total_time:.3f}秒 (平均: {total_time/len(test_tokens):.3f}秒/代幣)")
    print(f"{'=' * 80}")

