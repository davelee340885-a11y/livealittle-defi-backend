"""
可對沖性評估器 (Hedgeability Scorer)
評估加密貨幣的可對沖性，包括永續合約可用性、資金費率穩定性、交易所覆蓋範圍
"""

from typing import Dict, List, Optional
import requests
from datetime import datetime, timedelta
import statistics


class HedgeabilityScorer:
    """可對沖性評分器"""
    
    def __init__(self):
        # 主流交易所列表
        self.major_exchanges = [
            "binance", "okx", "bybit", "deribit", "bitget",
            "gate", "huobi", "kucoin", "mexc"
        ]
        
        # 穩定幣列表（不需要對沖）
        self.stablecoins = [
            "USDC", "USDT", "DAI", "BUSD", "TUSD", "USDD",
            "FRAX", "LUSD", "GUSD", "USDP", "SUSD", "MIM",
            "USDB", "PYUSD", "FDUSD"
        ]
        
        # CoinGlass API (如果可用)
        self.coinglass_api = "https://open-api.coinglass.com/public/v2"
        
    def is_stablecoin(self, token_symbol: str) -> bool:
        """
        判斷代幣是否為穩定幣
        
        Args:
            token_symbol: 代幣符號
        
        Returns:
            是否為穩定幣
        """
        normalized = self._normalize_symbol(token_symbol)
        return normalized in self.stablecoins
    
    def get_perpetual_data(self, token_symbol: str) -> Optional[Dict]:
        """
        獲取永續合約數據
        
        Args:
            token_symbol: 代幣符號 (如 "ETH", "BTC")
        
        Returns:
            永續合約數據字典
        """
        try:
            # 標準化符號
            normalized_symbol = self._normalize_symbol(token_symbol)
            
            # 模擬數據（實際應從CoinGlass或交易所API獲取）
            # 這裡使用已知的主流幣數據作為示例
            perp_data = self._get_mock_perpetual_data(normalized_symbol)
            
            if not perp_data:
                return None
            
            return {
                "symbol": normalized_symbol,
                "exchanges": perp_data["exchanges"],
                "total_volume_24h_usd": perp_data["volume_24h"],
                "open_interest_usd": perp_data["open_interest"],
                "avg_funding_rate": perp_data["avg_funding_rate"],
                "funding_rate_std": perp_data["funding_rate_std"],
                "data_source": "mock",  # 實際應為 "coinglass" 或具體交易所
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 獲取永續合約數據失敗 ({token_symbol}): {e}")
            return None
    
    def calculate_hedgeability_score(self, perp_data: Dict) -> Dict:
        """
        計算可對沖性評分
        
        Args:
            perp_data: 永續合約數據
        
        Returns:
            評分結果，包含總分和各項子分數
        """
        if not perp_data:
            return {
                "total_score": 0,
                "availability_score": 0,
                "funding_stability_score": 0,
                "exchange_coverage_score": 0,
                "tier": "不可對沖",
                "grade": "F",
                "details": "無永續合約數據"
            }
        
        # 1. 永續合約可用性評分 (50%)
        availability_score, tier = self._score_availability(
            perp_data.get("exchanges", []),
            perp_data.get("total_volume_24h_usd", 0),
            perp_data.get("open_interest_usd", 0)
        )
        
        # 2. 資金費率穩定性評分 (30%)
        funding_stability_score = self._score_funding_stability(
            perp_data.get("avg_funding_rate"),
            perp_data.get("funding_rate_std")
        )
        
        # 3. 交易所覆蓋範圍評分 (20%)
        exchange_coverage_score = self._score_exchange_coverage(
            perp_data.get("exchanges", [])
        )
        
        # 計算總分
        total_score = (
            availability_score * 0.5 +
            funding_stability_score * 0.3 +
            exchange_coverage_score * 0.2
        )
        
        # 評級
        grade = self._get_grade(total_score)
        
        return {
            "total_score": round(total_score, 2),
            "availability_score": round(availability_score, 2),
            "funding_stability_score": round(funding_stability_score, 2),
            "exchange_coverage_score": round(exchange_coverage_score, 2),
            "tier": tier,
            "grade": grade,
            "exchanges": perp_data.get("exchanges", []),
            "volume_24h_usd": perp_data.get("total_volume_24h_usd", 0),
            "open_interest_usd": perp_data.get("open_interest_usd", 0),
            "avg_funding_rate": perp_data.get("avg_funding_rate"),
            "meets_minimum": self._meets_minimum_threshold(perp_data)
        }
    
    def _score_availability(
        self,
        exchanges: List[str],
        volume_24h: float,
        open_interest: float
    ) -> tuple:
        """
        永續合約可用性評分
        
        Tier 1 (100分): ≥3個主流交易所, 交易量>$50M, OI>$100M
        Tier 2 (80分): ≥2個主流交易所, 交易量>$10M, OI>$20M
        Tier 3 (60分): ≥1個主流交易所, 交易量>$1M, OI>$5M
        不可對沖 (0分): 不滿足Tier 3條件
        """
        major_exchange_count = sum(
            1 for ex in exchanges if ex.lower() in self.major_exchanges
        )
        
        # Tier 1
        if (major_exchange_count >= 3 and
            volume_24h >= 50_000_000 and
            open_interest >= 100_000_000):
            return 100.0, "Tier 1"
        
        # Tier 2
        elif (major_exchange_count >= 2 and
              volume_24h >= 10_000_000 and
              open_interest >= 20_000_000):
            return 80.0, "Tier 2"
        
        # Tier 3
        elif (major_exchange_count >= 1 and
              volume_24h >= 1_000_000 and
              open_interest >= 5_000_000):
            return 60.0, "Tier 3"
        
        # 不可對沖
        else:
            return 0.0, "不可對沖"
    
    def _score_funding_stability(
        self,
        avg_funding_rate: Optional[float],
        funding_rate_std: Optional[float]
    ) -> float:
        """
        資金費率穩定性評分
        
        優秀 (100分): 平均費率 -0.01% 至 +0.01%, 標準差 < 0.02%
        良好 (80分): 平均費率 -0.03% 至 +0.03%, 標準差 < 0.05%
        一般 (60分): 平均費率 -0.05% 至 +0.05%, 標準差 < 0.10%
        不佳 (30分): 超出上述範圍
        """
        if avg_funding_rate is None or funding_rate_std is None:
            return 50.0  # 無數據時給予中等分數
        
        # 轉換為百分比（假設輸入為小數形式）
        avg_rate_pct = abs(avg_funding_rate * 100)
        std_pct = funding_rate_std * 100
        
        # 優秀
        if avg_rate_pct <= 0.01 and std_pct < 0.02:
            return 100.0
        
        # 良好
        elif avg_rate_pct <= 0.03 and std_pct < 0.05:
            return 80.0
        
        # 一般
        elif avg_rate_pct <= 0.05 and std_pct < 0.10:
            return 60.0
        
        # 不佳
        else:
            return 30.0
    
    def _score_exchange_coverage(self, exchanges: List[str]) -> float:
        """
        交易所覆蓋範圍評分
        
        ≥5個交易所: 100分
        3-4個交易所: 80分
        2個交易所: 60分
        1個交易所: 40分
        """
        count = len(exchanges)
        
        if count >= 5:
            return 100.0
        elif count >= 3:
            return 80.0
        elif count >= 2:
            return 60.0
        elif count >= 1:
            return 40.0
        else:
            return 0.0
    
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
    
    def _meets_minimum_threshold(self, perp_data: Dict) -> bool:
        """
        檢查是否滿足最低可對沖性門檻
        
        最低要求:
        - 至少在1個主流交易所有永續合約
        - 永續合約24小時交易量 >= $1M
        - 未平倉合約量 >= $5M
        """
        exchanges = perp_data.get("exchanges", [])
        volume = perp_data.get("total_volume_24h_usd", 0)
        oi = perp_data.get("open_interest_usd", 0)
        
        has_major_exchange = any(
            ex.lower() in self.major_exchanges for ex in exchanges
        )
        
        return (has_major_exchange and
                volume >= 1_000_000 and
                oi >= 5_000_000)
    
    def _normalize_symbol(self, symbol: str) -> str:
        """標準化代幣符號"""
        symbol = symbol.upper()
        # 移除W前綴
        if symbol.startswith("W") and len(symbol) > 1:
            base = symbol[1:]
            if base in ["ETH", "BTC", "BNB", "MATIC", "AVAX", "FTM"]:
                return base
        return symbol
    
    def _get_mock_perpetual_data(self, symbol: str) -> Optional[Dict]:
        """
        獲取模擬永續合約數據
        
        實際應用中應替換為真實API調用
        """
        # 主流幣數據（模擬）
        mock_data = {
            "BTC": {
                "exchanges": ["binance", "okx", "bybit", "deribit", "bitget"],
                "volume_24h": 25_000_000_000,  # $25B
                "open_interest": 15_000_000_000,  # $15B
                "avg_funding_rate": 0.0001,  # 0.01%
                "funding_rate_std": 0.0002  # 0.02%
            },
            "ETH": {
                "exchanges": ["binance", "okx", "bybit", "deribit", "bitget"],
                "volume_24h": 12_000_000_000,  # $12B
                "open_interest": 8_000_000_000,  # $8B
                "avg_funding_rate": 0.0001,
                "funding_rate_std": 0.0003
            },
            "ARB": {
                "exchanges": ["binance", "okx", "bybit"],
                "volume_24h": 150_000_000,  # $150M
                "open_interest": 100_000_000,  # $100M
                "avg_funding_rate": 0.0002,
                "funding_rate_std": 0.0005
            },
            "PENDLE": {
                "exchanges": ["binance", "bybit"],
                "volume_24h": 30_000_000,  # $30M
                "open_interest": 25_000_000,  # $25M
                "avg_funding_rate": 0.0003,
                "funding_rate_std": 0.0008
            },
            "USDC": {
                "exchanges": [],  # 穩定幣通常沒有永續合約
                "volume_24h": 0,
                "open_interest": 0,
                "avg_funding_rate": 0,
                "funding_rate_std": 0
            },
            "USDT": {
                "exchanges": [],
                "volume_24h": 0,
                "open_interest": 0,
                "avg_funding_rate": 0,
                "funding_rate_std": 0
            },
            "DAI": {
                "exchanges": [],
                "volume_24h": 0,
                "open_interest": 0,
                "avg_funding_rate": 0,
                "funding_rate_std": 0
            }
        }
        
        return mock_data.get(symbol)


# 測試代碼
if __name__ == "__main__":
    scorer = HedgeabilityScorer()
    
    # 測試幾個代幣
    test_tokens = ["ETH", "ARB", "PENDLE", "USDC"]
    
    print("=" * 80)
    print("可對沖性評分測試")
    print("=" * 80)
    
    for token in test_tokens:
        print(f"\n測試代幣: {token}")
        print("-" * 80)
        
        # 獲取永續合約數據
        data = scorer.get_perpetual_data(token)
        
        if data:
            print(f"✅ 數據獲取成功")
            print(f"  支持交易所: {', '.join(data['exchanges'])}")
            print(f"  24小時交易量: ${data['total_volume_24h_usd']:,.0f}")
            print(f"  未平倉合約: ${data['open_interest_usd']:,.0f}")
            print(f"  平均資金費率: {data['avg_funding_rate']:.4%}")
            
            # 計算評分
            score_result = scorer.calculate_hedgeability_score(data)
            print(f"\n評分結果:")
            print(f"  總分: {score_result['total_score']}/100 (等級: {score_result['grade']})")
            print(f"  可用性分數: {score_result['availability_score']}/100 (Tier: {score_result['tier']})")
            print(f"  資金費率穩定性: {score_result['funding_stability_score']}/100")
            print(f"  交易所覆蓋: {score_result['exchange_coverage_score']}/100")
            print(f"  滿足最低門檻: {'✅ 是' if score_result['meets_minimum'] else '❌ 否'}")
        else:
            print(f"❌ 數據獲取失敗")

