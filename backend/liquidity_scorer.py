"""
流動性評估器 (Liquidity Scorer)
評估加密貨幣的市場流動性，包括交易量、訂單簿深度、買賣價差
"""

from typing import Dict, Optional
import requests
from datetime import datetime


class LiquidityScorer:
    """流動性評分器"""
    
    def __init__(self):
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        
    def get_token_liquidity_data(self, token_symbol: str) -> Optional[Dict]:
        """
        獲取代幣流動性數據
        
        Args:
            token_symbol: 代幣符號 (如 "WETH", "USDC")
        
        Returns:
            流動性數據字典，包含交易量、價差等信息
        """
        try:
            # 標準化代幣符號
            normalized_symbol = self._normalize_token_symbol(token_symbol)
            
            # 從CoinGecko獲取數據
            coin_id = self._get_coingecko_id(normalized_symbol)
            if not coin_id:
                return None
            
            # 獲取市場數據
            url = f"{self.coingecko_api}/coins/{coin_id}"
            params = {
                "localization": "false",
                "tickers": "true",
                "market_data": "true"
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # 提取流動性相關數據
            market_data = data.get("market_data", {})
            tickers = data.get("tickers", [])
            
            # 計算24小時交易量
            volume_24h = market_data.get("total_volume", {}).get("usd", 0)
            
            # 計算平均買賣價差
            spreads = []
            for ticker in tickers[:10]:  # 取前10個交易所
                bid = ticker.get("bid_ask_spread_percentage")
                if bid and bid > 0:
                    spreads.append(bid)
            
            avg_spread = sum(spreads) / len(spreads) if spreads else None
            
            # 估算訂單簿深度（使用市值作為代理）
            market_cap = market_data.get("market_cap", {}).get("usd", 0)
            estimated_depth = market_cap * 0.001  # 假設深度為市值的0.1%
            
            return {
                "symbol": normalized_symbol,
                "volume_24h_usd": volume_24h,
                "avg_spread_percentage": avg_spread,
                "estimated_depth_usd": estimated_depth,
                "market_cap_usd": market_cap,
                "data_source": "coingecko",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 獲取流動性數據失敗 ({token_symbol}): {e}")
            return None
    
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
                "details": "無流動性數據"
            }
        
        # 1. 交易量評分 (40%)
        volume = liquidity_data.get("volume_24h_usd", 0)
        volume_score = self._score_volume(volume)
        
        # 2. 訂單簿深度評分 (40%)
        depth = liquidity_data.get("estimated_depth_usd", 0)
        depth_score = self._score_depth(depth)
        
        # 3. 買賣價差評分 (20%)
        spread = liquidity_data.get("avg_spread_percentage")
        spread_score = self._score_spread(spread)
        
        # 計算總分
        total_score = (
            volume_score * 0.4 +
            depth_score * 0.4 +
            spread_score * 0.2
        )
        
        # 評級
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
    
    def _score_volume(self, volume_usd: float) -> float:
        """
        交易量評分
        
        評分標準:
        - >$100M: 100分
        - $10M-$100M: 80分
        - $5M-$10M: 60分
        - <$5M: 按比例
        """
        if volume_usd >= 100_000_000:
            return 100.0
        elif volume_usd >= 10_000_000:
            return 80.0 + (volume_usd - 10_000_000) / 90_000_000 * 20
        elif volume_usd >= 5_000_000:
            return 60.0 + (volume_usd - 5_000_000) / 5_000_000 * 20
        else:
            return max(0, volume_usd / 5_000_000 * 60)
    
    def _score_depth(self, depth_usd: float) -> float:
        """
        訂單簿深度評分
        
        評分標準:
        - >$5M: 100分
        - >$1M: 80分
        - >$0.5M: 60分
        - <$0.5M: 按比例
        """
        if depth_usd >= 5_000_000:
            return 100.0
        elif depth_usd >= 1_000_000:
            return 80.0 + (depth_usd - 1_000_000) / 4_000_000 * 20
        elif depth_usd >= 500_000:
            return 60.0 + (depth_usd - 500_000) / 500_000 * 20
        else:
            return max(0, depth_usd / 500_000 * 60)
    
    def _score_spread(self, spread_percentage: Optional[float]) -> float:
        """
        買賣價差評分
        
        評分標準:
        - <0.1%: 100分
        - 0.1-0.3%: 80分
        - 0.3-0.5%: 60分
        - >0.5%: 按比例遞減
        """
        if spread_percentage is None:
            return 50.0  # 無數據時給予中等分數
        
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
        
        最低要求:
        - 24小時交易量 >= $5M
        """
        volume = liquidity_data.get("volume_24h_usd", 0)
        return volume >= 5_000_000
    
    def _normalize_token_symbol(self, symbol: str) -> str:
        """標準化代幣符號"""
        # 移除常見前綴
        symbol = symbol.upper()
        if symbol.startswith("W"):
            # WETH -> ETH, WBTC -> BTC
            base = symbol[1:]
            if base in ["ETH", "BTC", "BNB", "MATIC", "AVAX", "FTM"]:
                return base
        return symbol
    
    def _get_coingecko_id(self, symbol: str) -> Optional[str]:
        """
        獲取CoinGecko的coin_id
        
        Args:
            symbol: 代幣符號
        
        Returns:
            CoinGecko coin_id
        """
        # 常見代幣映射
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
    scorer = LiquidityScorer()
    
    # 測試幾個代幣
    test_tokens = ["ETH", "USDC", "ARB", "PENDLE"]
    
    print("=" * 80)
    print("流動性評分測試")
    print("=" * 80)
    
    for token in test_tokens:
        print(f"\n測試代幣: {token}")
        print("-" * 80)
        
        # 獲取流動性數據
        data = scorer.get_token_liquidity_data(token)
        
        if data:
            print(f"✅ 數據獲取成功")
            print(f"  24小時交易量: ${data['volume_24h_usd']:,.0f}")
            print(f"  平均價差: {data.get('avg_spread_percentage', 'N/A')}")
            print(f"  估算深度: ${data['estimated_depth_usd']:,.0f}")
            
            # 計算評分
            score_result = scorer.calculate_liquidity_score(data)
            print(f"\n評分結果:")
            print(f"  總分: {score_result['total_score']}/100 (等級: {score_result['grade']})")
            print(f"  交易量分數: {score_result['volume_score']}/100")
            print(f"  深度分數: {score_result['depth_score']}/100")
            print(f"  價差分數: {score_result['spread_score']}/100")
            print(f"  滿足最低門檻: {'✅ 是' if score_result['meets_minimum'] else '❌ 否'}")
        else:
            print(f"❌ 數據獲取失敗")

