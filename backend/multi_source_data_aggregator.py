"""
多源數據聚合器
從多個數據源獲取加密貨幣價格並進行驗證和共識
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Optional
from datetime import datetime
import statistics
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPoint:
    """單個數據點"""
    def __init__(self, source: str, token: str, price: float, timestamp: int):
        self.source = source
        self.token = token
        self.price = price
        self.timestamp = timestamp
        self.is_valid = True
        self.validation_errors = []


class DataSource:
    """數據源基類"""
    def __init__(self, name: str):
        self.name = name
        self.last_update = 0
        self.is_available = True
        self.error_count = 0
    
    async def fetch_price(self, token: str) -> Optional[DataPoint]:
        """獲取價格數據 - 子類需要實現"""
        raise NotImplementedError


class CoinGeckoSource(DataSource):
    """CoinGecko 數據源"""
    def __init__(self):
        super().__init__("coingecko")
        self.api_url = "https://api.coingecko.com/api/v3"
        # 代幣 ID 映射
        self.token_map = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "USDC": "usd-coin",
            "USDT": "tether",
            "DAI": "dai"
        }
    
    async def fetch_price(self, token: str) -> Optional[DataPoint]:
        """從 CoinGecko 獲取價格"""
        try:
            token_id = self.token_map.get(token)
            if not token_id:
                logger.warning(f"Token {token} not found in CoinGecko mapping")
                return None
            
            url = f"{self.api_url}/simple/price?ids={token_id}&vs_currencies=usd"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        price = data.get(token_id, {}).get("usd")
                        
                        if price:
                            self.last_update = int(time.time())
                            self.is_available = True
                            self.error_count = 0
                            
                            return DataPoint(
                                source=self.name,
                                token=token,
                                price=float(price),
                                timestamp=self.last_update
                            )
        except Exception as e:
            logger.error(f"CoinGecko fetch error for {token}: {e}")
            self.error_count += 1
            if self.error_count >= 3:
                self.is_available = False
        
        return None


class DefiLlamaSource(DataSource):
    """DefiLlama 數據源"""
    def __init__(self):
        super().__init__("defillama")
        self.api_url = "https://coins.llama.fi"
        # 代幣地址映射（以太坊）
        self.token_map = {
            "ETH": "ethereum:0x0000000000000000000000000000000000000000",
            "USDC": "ethereum:0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
            "USDT": "ethereum:0xdac17f958d2ee523a2206206994597c13d831ec7",
            "DAI": "ethereum:0x6b175474e89094c44da98b954eedeac495271d0f"
        }
    
    async def fetch_price(self, token: str) -> Optional[DataPoint]:
        """從 DefiLlama 獲取價格"""
        try:
            token_address = self.token_map.get(token)
            if not token_address:
                logger.warning(f"Token {token} not found in DefiLlama mapping")
                return None
            
            url = f"{self.api_url}/prices/current/{token_address}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        coin_data = data.get("coins", {}).get(token_address, {})
                        price = coin_data.get("price")
                        timestamp = coin_data.get("timestamp")
                        
                        if price and timestamp:
                            self.last_update = int(time.time())
                            self.is_available = True
                            self.error_count = 0
                            
                            return DataPoint(
                                source=self.name,
                                token=token,
                                price=float(price),
                                timestamp=int(timestamp)
                            )
        except Exception as e:
            logger.error(f"DefiLlama fetch error for {token}: {e}")
            self.error_count += 1
            if self.error_count >= 3:
                self.is_available = False
        
        return None


class BinanceSource(DataSource):
    """Binance 數據源（作為備用）"""
    def __init__(self):
        super().__init__("binance")
        self.api_url = "https://api.binance.com/api/v3"
    
    async def fetch_price(self, token: str) -> Optional[DataPoint]:
        """從 Binance 獲取價格"""
        try:
            # 大多數代幣對 USDT
            symbol = f"{token}USDT"
            url = f"{self.api_url}/ticker/price?symbol={symbol}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        price = data.get("price")
                        
                        if price:
                            self.last_update = int(time.time())
                            self.is_available = True
                            self.error_count = 0
                            
                            return DataPoint(
                                source=self.name,
                                token=token,
                                price=float(price),
                                timestamp=self.last_update
                            )
        except Exception as e:
            logger.error(f"Binance fetch error for {token}: {e}")
            self.error_count += 1
            if self.error_count >= 3:
                self.is_available = False
        
        return None


class DataValidator:
    """數據驗證器"""
    @staticmethod
    def validate_datapoint(dp: DataPoint) -> bool:
        """驗證單個數據點"""
        current_time = int(time.time())
        
        # 時間戳驗證（不超過 60 秒延遲）
        if current_time - dp.timestamp > 60:
            dp.is_valid = False
            dp.validation_errors.append("Timestamp too old")
            return False
        
        # 價格範圍驗證
        if dp.price <= 0:
            dp.is_valid = False
            dp.validation_errors.append("Invalid price (<=0)")
            return False
        
        # 價格合理性檢查（簡單範圍）
        if dp.price > 1000000:  # 超過 100 萬美元的價格需要特別檢查
            logger.warning(f"Unusually high price for {dp.token}: ${dp.price}")
        
        return True


class ConsensusEngine:
    """共識引擎"""
    @staticmethod
    def calculate_consensus(datapoints: List[DataPoint]) -> Optional[Dict]:
        """計算共識價格"""
        if not datapoints:
            return None
        
        # 只使用有效的數據點
        valid_points = [dp for dp in datapoints if dp.is_valid]
        
        if len(valid_points) < 2:
            logger.warning(f"Not enough valid data points: {len(valid_points)}")
            return None
        
        prices = [dp.price for dp in valid_points]
        
        # 異常值檢測 (IQR 方法)
        if len(prices) >= 3:
            q1 = statistics.quantiles(prices, n=4)[0]
            q3 = statistics.quantiles(prices, n=4)[2]
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            # 過濾異常值
            filtered_prices = [p for p in prices if lower_bound <= p <= upper_bound]
            
            if len(filtered_prices) < 2:
                # 如果過濾後數據太少，使用原始數據
                filtered_prices = prices
        else:
            filtered_prices = prices
        
        # 計算中位數作為共識價格
        consensus_price = statistics.median(filtered_prices)
        
        # 計算標準差（數據一致性指標）
        std_dev = statistics.stdev(filtered_prices) if len(filtered_prices) > 1 else 0
        
        return {
            "price": consensus_price,
            "std_dev": std_dev,
            "data_points": len(valid_points),
            "filtered_points": len(filtered_prices),
            "sources": [dp.source for dp in valid_points],
            "timestamp": int(time.time())
        }


class MultiSourceAggregator:
    """多源數據聚合器"""
    def __init__(self):
        self.sources = [
            CoinGeckoSource(),
            DefiLlamaSource(),
            BinanceSource()
        ]
        self.validator = DataValidator()
        self.consensus_engine = ConsensusEngine()
    
    async def fetch_all_sources(self, token: str) -> List[DataPoint]:
        """並發從所有數據源獲取數據"""
        tasks = [source.fetch_price(token) for source in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 過濾掉 None 和異常
        datapoints = [r for r in results if isinstance(r, DataPoint)]
        
        return datapoints
    
    async def get_consensus_price(self, token: str) -> Optional[Dict]:
        """獲取共識價格"""
        # 獲取所有數據點
        datapoints = await self.fetch_all_sources(token)
        
        if not datapoints:
            logger.error(f"No data points received for {token}")
            return None
        
        # 驗證數據點
        for dp in datapoints:
            self.validator.validate_datapoint(dp)
        
        # 計算共識
        consensus = self.consensus_engine.calculate_consensus(datapoints)
        
        if consensus:
            logger.info(
                f"Consensus for {token}: ${consensus['price']:.2f} "
                f"(from {consensus['data_points']} sources)"
            )
        
        return consensus
    
    def get_data_quality_metrics(self) -> Dict:
        """獲取數據質量指標"""
        available_sources = sum(1 for s in self.sources if s.is_available)
        total_sources = len(self.sources)
        
        return {
            "source_availability": available_sources / total_sources,
            "available_sources": available_sources,
            "total_sources": total_sources,
            "sources_status": {
                s.name: {
                    "available": s.is_available,
                    "last_update": s.last_update,
                    "error_count": s.error_count
                }
                for s in self.sources
            }
        }


# 使用範例
async def main():
    """測試函數"""
    aggregator = MultiSourceAggregator()
    
    tokens = ["BTC", "ETH", "USDC"]
    
    for token in tokens:
        print(f"\n{'='*50}")
        print(f"Fetching consensus price for {token}...")
        print(f"{'='*50}")
        
        consensus = await aggregator.get_consensus_price(token)
        
        if consensus:
            print(f"✅ Consensus Price: ${consensus['price']:.2f}")
            print(f"   Standard Deviation: ${consensus['std_dev']:.4f}")
            print(f"   Data Points: {consensus['data_points']}")
            print(f"   Sources: {', '.join(consensus['sources'])}")
        else:
            print(f"❌ Failed to get consensus price for {token}")
    
    # 顯示數據質量指標
    print(f"\n{'='*50}")
    print("Data Quality Metrics")
    print(f"{'='*50}")
    metrics = aggregator.get_data_quality_metrics()
    print(f"Source Availability: {metrics['source_availability']*100:.1f}%")
    print(f"Available Sources: {metrics['available_sources']}/{metrics['total_sources']}")
    
    for source_name, status in metrics['sources_status'].items():
        status_icon = "✅" if status['available'] else "❌"
        print(f"{status_icon} {source_name}: Errors={status['error_count']}")


if __name__ == "__main__":
    asyncio.run(main())

