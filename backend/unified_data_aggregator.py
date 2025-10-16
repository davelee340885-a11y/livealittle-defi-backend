"""
統一數據聚合器 - 整合所有 Delta Neutral 策略所需的數據源
"""

import requests
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

class DataCache:
    """簡單的內存緩存實現"""
    def __init__(self):
        self.cache = {}
        self.expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        """獲取緩存數據"""
        if key in self.cache:
            if datetime.now() < self.expiry[key]:
                return self.cache[key]
            else:
                # 過期，刪除
                del self.cache[key]
                del self.expiry[key]
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int):
        """設置緩存數據"""
        self.cache[key] = value
        self.expiry[key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def clear(self):
        """清空緩存"""
        self.cache.clear()
        self.expiry.clear()


class UnifiedDataAggregator:
    """統一數據聚合器"""
    
    def __init__(self):
        self.cache = DataCache()
        
        # 緩存時間設置（秒）
        self.CACHE_DURATION = {
            "token_prices": 10,        # 10秒
            "lp_pools": 300,           # 5分鐘
            "funding_rates": 300,      # 5分鐘
            "gas_prices": 60,          # 1分鐘
            "market_sentiment": 3600,  # 1小時
        }
        
        # API 端點
        self.DEFILLAMA_POOLS_URL = "https://yields.llama.fi/pools"
        self.COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
        self.HYPERLIQUID_BASE_URL = "https://api.hyperliquid.xyz/info"
        self.FEAR_GREED_URL = "https://api.alternative.me/fng/"
        
        # Rate Limit 控制
        self.last_request_time = {}
        self.min_request_interval = 1.0  # 最小請求間隔（秒）
    
    def _rate_limit_wait(self, api_name: str):
        """Rate Limit 控制"""
        if api_name in self.last_request_time:
            elapsed = time.time() - self.last_request_time[api_name]
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)
        self.last_request_time[api_name] = time.time()
    
    def _make_request(self, url: str, api_name: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """統一的 HTTP 請求方法，帶錯誤處理和重試"""
        self._rate_limit_wait(api_name)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"❌ API 請求失敗 ({api_name}), 嘗試 {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指數退避
                else:
                    return None
        return None
    
    # ==================== LP 池數據 ====================
    
    def get_lp_pools(self, min_tvl: float = 1000000, limit: int = 100) -> List[Dict]:
        """
        獲取 LP 池數據
        
        Args:
            min_tvl: 最小 TVL 過濾（USD）
            limit: 返回數量限制
        
        Returns:
            LP 池列表
        """
        cache_key = f"lp_pools_{min_tvl}_{limit}"
        cached = self.cache.get(cache_key)
        if cached:
            print(f"✅ 使用緩存的 LP 池數據")
            return cached
        
        print(f"🔄 從 DeFiLlama 獲取 LP 池數據...")
        data = self._make_request(self.DEFILLAMA_POOLS_URL, "defillama")
        
        if not data or "data" not in data:
            print("❌ 無法獲取 LP 池數據")
            return []
        
        # 過濾和處理數據
        pools = []
        for pool in data["data"]:
            try:
                tvl = float(pool.get("tvlUsd", 0))
                apy = float(pool.get("apy", 0))
                
                # 過濾條件
                if tvl < min_tvl:
                    continue
                if apy <= 0 or apy > 10000:  # 過濾異常 APY
                    continue
                
                # 提取池地址 (poolMeta 通常包含實際的池地址)
                pool_meta = pool.get("poolMeta", "")
                pool_address = ""
                if pool_meta and isinstance(pool_meta, str):
                    # poolMeta 可能是地址或其他格式
                    if pool_meta.startswith("0x") and len(pool_meta) == 42:
                        pool_address = pool_meta
                
                pools.append({
                    "pool_id": pool.get("pool", ""),
                    "protocol": pool.get("project", ""),
                    "chain": pool.get("chain", ""),
                    "symbol": pool.get("symbol", ""),
                    "tvl": tvl,
                    "apy": apy,
                    "apy_base": float(pool.get("apyBase", 0)),
                    "apy_reward": float(pool.get("apyReward", 0)),
                    "il_risk": pool.get("ilRisk", "unknown"),
                    "exposure": pool.get("exposure", ""),
                    "pool_meta": pool_meta,
                    "pool_address": pool_address,  # 新增: 實際的池地址
                })
                
                if len(pools) >= limit:
                    break
                    
            except (ValueError, TypeError) as e:
                continue
        
        # 按 APY 排序
        pools.sort(key=lambda x: x["apy"], reverse=True)
        
        # 緩存結果
        self.cache.set(cache_key, pools, self.CACHE_DURATION["lp_pools"])
        
        print(f"✅ 獲取到 {len(pools)} 個 LP 池")
        return pools
    
    def get_pool_by_id(self, pool_id: str) -> Optional[Dict]:
        """根據池 ID 獲取特定池的數據"""
        pools = self.get_lp_pools(min_tvl=0, limit=10000)
        for pool in pools:
            if pool["pool_id"] == pool_id:
                return pool
        return None
    
    # ==================== 代幣價格數據 ====================
    
    def get_token_price(self, token_symbol: str) -> Optional[Dict]:
        """
        獲取代幣價格
        
        Args:
            token_symbol: 代幣符號，如 'ethereum', 'bitcoin'
        
        Returns:
            價格數據字典
        """
        cache_key = f"token_price_{token_symbol.lower()}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # CoinGecko ID 映射
        symbol_to_id = {
            "eth": "ethereum",
            "ethereum": "ethereum",
            "btc": "bitcoin",
            "bitcoin": "bitcoin",
            "usdc": "usd-coin",
            "usdt": "tether",
            "dai": "dai",
            "weth": "ethereum",
            "wbtc": "wrapped-bitcoin",
        }
        
        coin_id = symbol_to_id.get(token_symbol.lower(), token_symbol.lower())
        
        url = f"{self.COINGECKO_BASE_URL}/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
        }
        
        print(f"🔄 從 CoinGecko 獲取 {token_symbol} 價格...")
        data = self._make_request(url, "coingecko", params)
        
        if not data or coin_id not in data:
            print(f"❌ 無法獲取 {token_symbol} 價格")
            return None
        
        price_data = {
            "symbol": token_symbol.upper(),
            "price": data[coin_id].get("usd", 0),
            "change_24h": data[coin_id].get("usd_24h_change", 0),
            "volume_24h": data[coin_id].get("usd_24h_vol", 0),
            "updated_at": datetime.now().isoformat(),
        }
        
        # 緩存結果
        self.cache.set(cache_key, price_data, self.CACHE_DURATION["token_prices"])
        
        print(f"✅ {token_symbol} 價格: ${price_data['price']:.2f}")
        return price_data
    
    def get_multiple_token_prices(self, token_symbols: List[str]) -> Dict[str, Dict]:
        """批量獲取多個代幣價格"""
        prices = {}
        for symbol in token_symbols:
            price_data = self.get_token_price(symbol)
            if price_data:
                prices[symbol.upper()] = price_data
        return prices
    
    # ==================== 資金費率數據 ====================
    
    def get_funding_rate(self, coin: str = "ETH") -> Optional[Dict]:
        """
        獲取資金費率（使用 Hyperliquid API）
        
        Args:
            coin: 代幣符號，如 'ETH', 'BTC'
        
        Returns:
            資金費率數據
        """
        cache_key = f"funding_rate_{coin}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # 從 Hyperliquid 獲取最近的資金費率
        # 獲取最近 30 天的數據用於計算統計值
        start_time = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
        
        payload = {
            "type": "fundingHistory",
            "coin": coin.upper(),
            "startTime": start_time
        }
        
        print(f"🔄 從 Hyperliquid 獲取 {coin} 資金費率...")
        
        try:
            response = requests.post(
                self.HYPERLIQUID_BASE_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Hyperliquid API 請求失敗: {e}")
            return None
        
        if not data or len(data) == 0:
            print(f"❌ 無法獲取 {coin} 資金費率")
            return None
        
        # 提取所有費率數據
        all_rates = [float(item["fundingRate"]) for item in data]
        current_rate = all_rates[-1]  # 最新的費率
        
        # 計算不同時間段的平均值
        # Hyperliquid 每小時結算一次，24小時 = 24筆數據
        rates_7d = all_rates[-168:] if len(all_rates) >= 168 else all_rates  # 7天 = 168小時
        rates_30d = all_rates  # 所有數據（最多30天）
        
        avg_rate_7d = sum(rates_7d) / len(rates_7d) if rates_7d else 0
        avg_rate_30d = sum(rates_30d) / len(rates_30d) if rates_30d else 0
        
        # 計算標準差（波動性）
        import statistics
        std_dev_7d = statistics.stdev(rates_7d) if len(rates_7d) > 1 else 0
        std_dev_30d = statistics.stdev(rates_30d) if len(rates_30d) > 1 else 0
        
        # 計算最高/最低值
        max_rate_7d = max(rates_7d) if rates_7d else 0
        min_rate_7d = min(rates_7d) if rates_7d else 0
        max_rate_30d = max(rates_30d) if rates_30d else 0
        min_rate_30d = min(rates_30d) if rates_30d else 0
        
        # Hyperliquid 每小時結算一次，所以年化公式：每小時費率 * 24 * 365
        annualized_rate_7d = avg_rate_7d * 24 * 365 * 100  # 轉換為百分比
        annualized_rate_30d = avg_rate_30d * 24 * 365 * 100
        
        funding_data = {
            "coin": coin.upper(),
            "current_rate": current_rate,
            "current_rate_pct": current_rate * 100,
            
            # 7 天統計
            "avg_rate_7d": avg_rate_7d,
            "avg_rate_7d_pct": avg_rate_7d * 100,
            "annualized_rate_7d_pct": annualized_rate_7d,
            "std_dev_7d_pct": std_dev_7d * 100,
            "max_rate_7d_pct": max_rate_7d * 100,
            "min_rate_7d_pct": min_rate_7d * 100,
            
            # 30 天統計
            "avg_rate_30d": avg_rate_30d,
            "avg_rate_30d_pct": avg_rate_30d * 100,
            "annualized_rate_30d_pct": annualized_rate_30d,
            "std_dev_30d_pct": std_dev_30d * 100,
            "max_rate_30d_pct": max_rate_30d * 100,
            "min_rate_30d_pct": min_rate_30d * 100,
            
            # 向後兼容（使用 7 天平均作為默認值）
            "avg_rate": avg_rate_7d,
            "avg_rate_pct": avg_rate_7d * 100,
            "annualized_rate_pct": annualized_rate_7d,
            
            "funding_time": datetime.fromtimestamp(data[-1]["time"] / 1000).isoformat(),
            "updated_at": datetime.now().isoformat(),
            "source": "Hyperliquid",
            "data_points": len(data),
        }
        
        # 緩存結果
        self.cache.set(cache_key, funding_data, self.CACHE_DURATION["funding_rates"])
        
        print(f"✅ {coin} 資金費率: {funding_data['current_rate_pct']:.4f}% (7日年化: {annualized_rate_7d:.2f}%, 範圍: {min_rate_7d*100:.4f}%-{max_rate_7d*100:.4f}%)")
        return funding_data
    
    def get_multiple_funding_rates(self, coins: List[str]) -> Dict[str, Dict]:
        """批量獲取多個代幣的資金費率"""
        rates = {}
        for coin in coins:
            rate_data = self.get_funding_rate(coin)
            if rate_data:
                rates[coin.upper()] = rate_data
        return rates
    
    # ==================== 市場情緒數據 ====================
    
    def get_fear_greed_index(self) -> Optional[Dict]:
        """獲取恐懼與貪婪指數"""
        cache_key = "fear_greed_index"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        print(f"🔄 從 Alternative.me 獲取恐懼與貪婪指數...")
        data = self._make_request(self.FEAR_GREED_URL, "alternative")
        
        if not data or "data" not in data or len(data["data"]) == 0:
            print("❌ 無法獲取恐懼與貪婪指數")
            return None
        
        fgi_data = data["data"][0]
        
        sentiment_data = {
            "value": int(fgi_data["value"]),
            "classification": fgi_data["value_classification"],
            "timestamp": datetime.fromtimestamp(int(fgi_data["timestamp"])).isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        # 緩存結果
        self.cache.set(cache_key, sentiment_data, self.CACHE_DURATION["market_sentiment"])
        
        print(f"✅ 恐懼與貪婪指數: {sentiment_data['value']} ({sentiment_data['classification']})")
        return sentiment_data
    
    # ==================== 綜合數據獲取 ====================
    
    def get_delta_neutral_data(self, token_symbol: str = "ETH") -> Dict:
        """
        獲取 Delta Neutral 策略所需的所有數據
        
        Args:
            token_symbol: 主要代幣符號
        
        Returns:
            包含所有必需數據的字典
        """
        print(f"\n{'='*60}")
        print(f"🚀 開始獲取 {token_symbol} Delta Neutral 策略數據")
        print(f"{'='*60}\n")
        
        # 1. 獲取 LP 池數據
        print("📊 步驟 1/4: 獲取 LP 池數據")
        lp_pools = self.get_lp_pools(min_tvl=1000000, limit=50)
        
        # 過濾包含目標代幣的池
        relevant_pools = [
            pool for pool in lp_pools
            if token_symbol.upper() in pool["symbol"].upper()
        ]
        print(f"   找到 {len(relevant_pools)} 個包含 {token_symbol} 的池\n")
        
        # 2. 獲取代幣價格
        print("💰 步驟 2/4: 獲取代幣價格")
        token_price = self.get_token_price(token_symbol)
        print()
        
        # 3. 獲取資金費率
        print("📈 步驟 3/4: 獲取資金費率")
        funding_rate = self.get_funding_rate(token_symbol)
        print()
        
        # 4. 獲取市場情緒
        print("😨 步驟 4/4: 獲取市場情緒")
        fear_greed = self.get_fear_greed_index()
        print()
        
        print(f"{'='*60}")
        print(f"✅ 數據獲取完成！")
        print(f"{'='*60}\n")
        
        return {
            "token": token_symbol.upper(),
            "lp_pools": relevant_pools,
            "token_price": token_price,
            "funding_rate": funding_rate,
            "market_sentiment": fear_greed,
            "timestamp": datetime.now().isoformat(),
        }


# ==================== 測試代碼 ====================

if __name__ == "__main__":
    print("🧪 測試統一數據聚合器\n")
    
    aggregator = UnifiedDataAggregator()
    
    # 測試 1: 獲取 LP 池數據
    print("\n" + "="*60)
    print("測試 1: 獲取 Top LP 池")
    print("="*60)
    pools = aggregator.get_lp_pools(min_tvl=5000000, limit=5)
    for i, pool in enumerate(pools[:5], 1):
        print(f"{i}. {pool['protocol']} - {pool['symbol']}")
        print(f"   TVL: ${pool['tvl']:,.0f} | APY: {pool['apy']:.2f}%")
        print(f"   Chain: {pool['chain']}")
    
    # 測試 2: 獲取代幣價格
    print("\n" + "="*60)
    print("測試 2: 獲取代幣價格")
    print("="*60)
    for token in ["ETH", "BTC", "USDC"]:
        price_data = aggregator.get_token_price(token)
        if price_data:
            print(f"{token}: ${price_data['price']:,.2f} ({price_data['change_24h']:+.2f}%)")
    
    # 測試 3: 獲取資金費率
    print("\n" + "="*60)
    print("測試 3: 獲取資金費率")
    print("="*60)
    for coin in ["ETH", "BTC"]:
        rate_data = aggregator.get_funding_rate(coin)
        if rate_data:
            print(f"{coin}: {rate_data['current_rate_pct']:.4f}% (年化: {rate_data['annualized_rate_pct']:.2f}%)")
    
    # 測試 4: 獲取恐懼與貪婪指數
    print("\n" + "="*60)
    print("測試 4: 獲取市場情緒")
    print("="*60)
    sentiment = aggregator.get_fear_greed_index()
    if sentiment:
        print(f"恐懼與貪婪指數: {sentiment['value']} - {sentiment['classification']}")
    
    # 測試 5: 獲取完整 Delta Neutral 數據
    print("\n" + "="*60)
    print("測試 5: 獲取完整 Delta Neutral 數據")
    print("="*60)
    delta_data = aggregator.get_delta_neutral_data("ETH")
    
    print("\n📊 數據摘要:")
    print(f"  - LP 池數量: {len(delta_data['lp_pools'])}")
    if delta_data['token_price']:
        print(f"  - ETH 價格: ${delta_data['token_price']['price']:,.2f}")
    if delta_data['funding_rate']:
        print(f"  - 資金費率: {delta_data['funding_rate']['annualized_rate_pct']:.2f}% (年化)")
        if delta_data['funding_rate'].get('is_estimated'):
            print(f"    註: {delta_data['funding_rate']['note']}")
    if delta_data['market_sentiment']:
        print(f"  - 市場情緒: {delta_data['market_sentiment']['classification']}")
    
    print("\n✅ 所有測試完成！")

