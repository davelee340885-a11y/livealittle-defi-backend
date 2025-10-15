"""
LP Pair 數據聚合器
從多個數據源獲取流動性池數據並進行驗證
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


class LPPoolData:
    """LP 池數據點"""
    def __init__(
        self,
        source: str,
        pool_address: str,
        protocol: str,
        chain: str,
        token0: str,
        token1: str,
        fee_tier: float,
        tvl: float,
        volume_24h: float,
        apy: float,
        timestamp: int
    ):
        self.source = source
        self.pool_address = pool_address
        self.protocol = protocol
        self.chain = chain
        self.token0 = token0
        self.token1 = token1
        self.fee_tier = fee_tier
        self.tvl = tvl
        self.volume_24h = volume_24h
        self.apy = apy
        self.timestamp = timestamp
        self.is_valid = True
        self.validation_errors = []


class LPDataSource:
    """LP 數據源基類"""
    def __init__(self, name: str):
        self.name = name
        self.last_update = 0
        self.is_available = True
        self.error_count = 0
    
    async def fetch_pool_data(self, pool_address: str, chain: str) -> Optional[LPPoolData]:
        """獲取池數據 - 子類需要實現"""
        raise NotImplementedError
    
    async def search_pools(
        self, 
        token0: str, 
        token1: str, 
        protocol: str, 
        chain: str
    ) -> List[LPPoolData]:
        """搜索池 - 子類需要實現"""
        raise NotImplementedError


class DefiLlamaPoolSource(LPDataSource):
    """DefiLlama 池數據源"""
    def __init__(self):
        super().__init__("defillama")
        self.api_url = "https://yields.llama.fi"
    
    async def fetch_pool_data(self, pool_id: str, chain: str = None) -> Optional[LPPoolData]:
        """從 DefiLlama 獲取池數據"""
        try:
            url = f"{self.api_url}/chart/{pool_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data and 'data' in data and len(data['data']) > 0:
                            latest = data['data'][-1]  # 最新數據點
                            
                            self.last_update = int(time.time())
                            self.is_available = True
                            self.error_count = 0
                            
                            return LPPoolData(
                                source=self.name,
                                pool_address=pool_id,
                                protocol=latest.get('project', 'unknown'),
                                chain=latest.get('chain', 'unknown'),
                                token0=latest.get('symbol', '').split('-')[0] if '-' in latest.get('symbol', '') else 'unknown',
                                token1=latest.get('symbol', '').split('-')[1] if '-' in latest.get('symbol', '') else 'unknown',
                                fee_tier=0.0,  # DefiLlama 不直接提供
                                tvl=float(latest.get('tvlUsd', 0)),
                                volume_24h=0.0,  # 需要從其他端點獲取
                                apy=float(latest.get('apy', 0)),
                                timestamp=int(time.time())
                            )
        except Exception as e:
            logger.error(f"DefiLlama fetch error for {pool_id}: {e}")
            self.error_count += 1
            if self.error_count >= 3:
                self.is_available = False
        
        return None
    
    async def search_pools(
        self, 
        token0: str = None, 
        token1: str = None, 
        protocol: str = None, 
        chain: str = None
    ) -> List[LPPoolData]:
        """搜索符合條件的池"""
        try:
            url = f"{self.api_url}/pools"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as response:
                    if response.status == 200:
                        pools_data = await response.json()
                        
                        results = []
                        for pool in pools_data.get('data', []):
                            # 過濾條件
                            if protocol and pool.get('project', '').lower() != protocol.lower():
                                continue
                            if chain and pool.get('chain', '').lower() != chain.lower():
                                continue
                            
                            symbol = pool.get('symbol', '')
                            if token0 and token1:
                                if not (token0.upper() in symbol.upper() and token1.upper() in symbol.upper()):
                                    continue
                            
                            pool_data = LPPoolData(
                                source=self.name,
                                pool_address=pool.get('pool', ''),
                                protocol=pool.get('project', 'unknown'),
                                chain=pool.get('chain', 'unknown'),
                                token0=symbol.split('-')[0] if '-' in symbol else 'unknown',
                                token1=symbol.split('-')[1] if '-' in symbol else 'unknown',
                                fee_tier=0.0,
                                tvl=float(pool.get('tvlUsd', 0)),
                                volume_24h=0.0,
                                apy=float(pool.get('apy', 0)),
                                timestamp=int(time.time())
                            )
                            
                            results.append(pool_data)
                        
                        self.last_update = int(time.time())
                        self.is_available = True
                        return results[:20]  # 限制返回數量
                        
        except Exception as e:
            logger.error(f"DefiLlama search error: {e}")
            self.error_count += 1
        
        return []


class UniswapV3Source(LPDataSource):
    """Uniswap V3 數據源（通過 The Graph）"""
    def __init__(self):
        super().__init__("uniswap_v3")
        # The Graph 子圖端點
        self.subgraph_urls = {
            "ethereum": "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3",
            "arbitrum": "https://api.thegraph.com/subgraphs/name/ianlapham/uniswap-arbitrum-one",
            "polygon": "https://api.thegraph.com/subgraphs/name/ianlapham/uniswap-v3-polygon"
        }
    
    async def fetch_pool_data(self, pool_address: str, chain: str = "ethereum") -> Optional[LPPoolData]:
        """從 Uniswap V3 子圖獲取池數據"""
        try:
            subgraph_url = self.subgraph_urls.get(chain.lower())
            if not subgraph_url:
                logger.warning(f"Chain {chain} not supported for Uniswap V3")
                return None
            
            # GraphQL 查詢
            query = """
            query GetPool($poolAddress: String!) {
              pool(id: $poolAddress) {
                id
                token0 {
                  symbol
                }
                token1 {
                  symbol
                }
                feeTier
                totalValueLockedUSD
                volumeUSD
                token0Price
                token1Price
              }
            }
            """
            
            variables = {"poolAddress": pool_address.lower()}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    subgraph_url,
                    json={"query": query, "variables": variables},
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if 'data' in result and result['data'].get('pool'):
                            pool = result['data']['pool']
                            
                            # 計算 APY（簡化版本）
                            tvl = float(pool.get('totalValueLockedUSD', 0))
                            volume_24h = float(pool.get('volumeUSD', 0))
                            fee_tier = float(pool.get('feeTier', 0)) / 10000  # 轉換為百分比
                            
                            # 簡化 APY 計算：(24h 交易量 * 費率 * 365) / TVL
                            apy = (volume_24h * fee_tier * 365 / tvl * 100) if tvl > 0 else 0
                            
                            self.last_update = int(time.time())
                            self.is_available = True
                            self.error_count = 0
                            
                            return LPPoolData(
                                source=self.name,
                                pool_address=pool['id'],
                                protocol="uniswap_v3",
                                chain=chain,
                                token0=pool['token0']['symbol'],
                                token1=pool['token1']['symbol'],
                                fee_tier=fee_tier,
                                tvl=tvl,
                                volume_24h=volume_24h,
                                apy=apy,
                                timestamp=int(time.time())
                            )
        except Exception as e:
            logger.error(f"Uniswap V3 fetch error for {pool_address}: {e}")
            self.error_count += 1
            if self.error_count >= 3:
                self.is_available = False
        
        return None


class GeckoTerminalSource(LPDataSource):
    """GeckoTerminal 數據源"""
    def __init__(self):
        super().__init__("geckoterminal")
        self.api_url = "https://api.geckoterminal.com/api/v2"
    
    async def fetch_pool_data(self, pool_address: str, chain: str = "eth") -> Optional[LPPoolData]:
        """從 GeckoTerminal 獲取池數據"""
        try:
            url = f"{self.api_url}/networks/{chain}/pools/{pool_address}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if 'data' in result:
                            pool = result['data']['attributes']
                            
                            self.last_update = int(time.time())
                            self.is_available = True
                            self.error_count = 0
                            
                            return LPPoolData(
                                source=self.name,
                                pool_address=pool_address,
                                protocol=pool.get('dex_id', 'unknown'),
                                chain=chain,
                                token0=pool.get('base_token_symbol', 'unknown'),
                                token1=pool.get('quote_token_symbol', 'unknown'),
                                fee_tier=0.0,
                                tvl=float(pool.get('reserve_in_usd', 0)),
                                volume_24h=float(pool.get('volume_usd', {}).get('h24', 0)),
                                apy=0.0,  # GeckoTerminal 不直接提供 APY
                                timestamp=int(time.time())
                            )
        except Exception as e:
            logger.error(f"GeckoTerminal fetch error for {pool_address}: {e}")
            self.error_count += 1
            if self.error_count >= 3:
                self.is_available = False
        
        return None


class LPDataValidator:
    """LP 數據驗證器"""
    @staticmethod
    def validate_pool_data(pool: LPPoolData) -> bool:
        """驗證池數據"""
        current_time = int(time.time())
        
        # 時間戳驗證
        if current_time - pool.timestamp > 300:  # 5 分鐘
            pool.is_valid = False
            pool.validation_errors.append("Data too old")
            return False
        
        # TVL 驗證
        if pool.tvl < 0:
            pool.is_valid = False
            pool.validation_errors.append("Invalid TVL (<0)")
            return False
        
        # APY 合理性檢查
        if pool.apy < 0 or pool.apy > 10000:  # APY 不應該是負數或超過 10000%
            logger.warning(f"Unusual APY for {pool.token0}/{pool.token1}: {pool.apy}%")
            # 不標記為無效，但記錄警告
        
        # 交易量驗證
        if pool.volume_24h < 0:
            pool.is_valid = False
            pool.validation_errors.append("Invalid volume (<0)")
            return False
        
        return True


class LPConsensusEngine:
    """LP 數據共識引擎"""
    @staticmethod
    def calculate_consensus(pool_datapoints: List[LPPoolData]) -> Optional[Dict]:
        """計算 LP 池數據的共識"""
        if not pool_datapoints:
            return None
        
        # 只使用有效的數據點
        valid_points = [p for p in pool_datapoints if p.is_valid]
        
        if len(valid_points) < 1:
            logger.warning("No valid pool data points")
            return None
        
        # 提取數值
        tvls = [p.tvl for p in valid_points if p.tvl > 0]
        apys = [p.apy for p in valid_points if p.apy > 0]
        volumes = [p.volume_24h for p in valid_points if p.volume_24h > 0]
        
        # 計算共識值（使用中位數）
        consensus_tvl = statistics.median(tvls) if tvls else 0
        consensus_apy = statistics.median(apys) if apys else 0
        consensus_volume = statistics.median(volumes) if volumes else 0
        
        # 使用第一個有效數據點的基本信息
        first_valid = valid_points[0]
        
        return {
            "pool_address": first_valid.pool_address,
            "protocol": first_valid.protocol,
            "chain": first_valid.chain,
            "token0": first_valid.token0,
            "token1": first_valid.token1,
            "fee_tier": first_valid.fee_tier,
            "tvl": consensus_tvl,
            "apy": consensus_apy,
            "volume_24h": consensus_volume,
            "data_points": len(valid_points),
            "sources": [p.source for p in valid_points],
            "tvl_std_dev": statistics.stdev(tvls) if len(tvls) > 1 else 0,
            "apy_std_dev": statistics.stdev(apys) if len(apys) > 1 else 0,
            "timestamp": int(time.time())
        }


class LPPairDataAggregator:
    """LP Pair 數據聚合器"""
    def __init__(self):
        self.sources = [
            DefiLlamaPoolSource(),
            # UniswapV3Source(),  # 需要特定池地址
            # GeckoTerminalSource()  # 需要特定池地址
        ]
        self.validator = LPDataValidator()
        self.consensus_engine = LPConsensusEngine()
    
    async def fetch_all_sources(
        self, 
        pool_id: str = None,
        pool_address: str = None,
        chain: str = "ethereum"
    ) -> List[LPPoolData]:
        """從所有數據源獲取池數據"""
        tasks = []
        
        for source in self.sources:
            if pool_id and isinstance(source, DefiLlamaPoolSource):
                tasks.append(source.fetch_pool_data(pool_id, chain))
            elif pool_address and isinstance(source, (UniswapV3Source, GeckoTerminalSource)):
                tasks.append(source.fetch_pool_data(pool_address, chain))
        
        if not tasks:
            logger.warning("No tasks created for fetching pool data")
            return []
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 過濾掉 None 和異常
        datapoints = [r for r in results if isinstance(r, LPPoolData)]
        
        return datapoints
    
    async def search_best_pools(
        self,
        token0: str = None,
        token1: str = None,
        protocol: str = None,
        chain: str = None,
        min_tvl: float = 1000000,  # 最小 TVL 100 萬美元
        min_apy: float = 5.0,  # 最小 APY 5%
        limit: int = 10
    ) -> List[Dict]:
        """搜索最佳池"""
        all_pools = []
        
        for source in self.sources:
            if hasattr(source, 'search_pools'):
                pools = await source.search_pools(token0, token1, protocol, chain)
                all_pools.extend(pools)
        
        # 驗證
        for pool in all_pools:
            self.validator.validate_pool_data(pool)
        
        # 過濾
        filtered_pools = [
            pool for pool in all_pools
            if pool.is_valid and pool.tvl >= min_tvl and pool.apy >= min_apy
        ]
        
        # 按 APY 排序
        filtered_pools.sort(key=lambda x: x.apy, reverse=True)
        
        # 轉換為字典
        results = []
        for pool in filtered_pools[:limit]:
            results.append({
                "pool_address": pool.pool_address,
                "protocol": pool.protocol,
                "chain": pool.chain,
                "pair": f"{pool.token0}/{pool.token1}",
                "tvl": pool.tvl,
                "apy": pool.apy,
                "volume_24h": pool.volume_24h,
                "source": pool.source
            })
        
        return results
    
    async def get_consensus_pool_data(
        self,
        pool_id: str = None,
        pool_address: str = None,
        chain: str = "ethereum"
    ) -> Optional[Dict]:
        """獲取池的共識數據"""
        # 獲取所有數據點
        datapoints = await self.fetch_all_sources(pool_id, pool_address, chain)
        
        if not datapoints:
            logger.error(f"No data points received for pool")
            return None
        
        # 驗證數據點
        for dp in datapoints:
            self.validator.validate_pool_data(dp)
        
        # 計算共識
        consensus = self.consensus_engine.calculate_consensus(datapoints)
        
        if consensus:
            logger.info(
                f"Consensus for {consensus['token0']}/{consensus['token1']}: "
                f"TVL=${consensus['tvl']:,.0f}, APY={consensus['apy']:.2f}% "
                f"(from {consensus['data_points']} sources)"
            )
        
        return consensus


# 測試函數
async def main():
    """測試函數"""
    aggregator = LPPairDataAggregator()
    
    print("\n" + "="*70)
    print("SEARCHING FOR BEST LP POOLS")
    print("="*70)
    
    # 搜索 Uniswap V3 上的 ETH/USDC 池
    pools = await aggregator.search_best_pools(
        token0="ETH",
        token1="USDC",
        protocol="uniswap-v3",
        chain="ethereum",
        min_tvl=10000000,  # 1000 萬美元
        min_apy=5.0,
        limit=5
    )
    
    if pools:
        print(f"\nFound {len(pools)} pools:\n")
        for i, pool in enumerate(pools, 1):
            print(f"{i}. {pool['pair']} on {pool['protocol']}")
            print(f"   TVL: ${pool['tvl']:,.0f}")
            print(f"   APY: {pool['apy']:.2f}%")
            print(f"   24h Volume: ${pool['volume_24h']:,.0f}")
            print(f"   Source: {pool['source']}")
            print()
    else:
        print("❌ No pools found matching criteria")


if __name__ == "__main__":
    asyncio.run(main())

