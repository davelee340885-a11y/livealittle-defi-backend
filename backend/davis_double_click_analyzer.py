"""
戴維斯雙擊分析引擎
識別費用增長快於 TVL 增長的優質 LP 池
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time


class DavisDoubleClickAnalyzer:
    """戴維斯雙擊分析引擎"""
    
    def __init__(self):
        self.defillama_base = "https://yields.llama.fi"
        self.cache = {}
        self.cache_ttl = 300  # 5 分鐘緩存
    
    def _get_cached(self, key: str):
        """獲取緩存數據"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
        return None
    
    def _set_cache(self, key: str, data):
        """設置緩存"""
        self.cache[key] = (data, time.time())
    
    def get_all_pools(self) -> List[Dict]:
        """
        獲取所有 LP 池數據
        
        Returns:
            池列表
        """
        cache_key = "all_pools"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{self.defillama_base}/pools"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            pools = data.get("data", [])
            self._set_cache(cache_key, pools)
            return pools
            
        except Exception as e:
            print(f"❌ 獲取池數據失敗: {str(e)}")
            return []
    
    def calculate_davis_score(
        self,
        pool: Dict,
        apy_weight: float = 0.4,
        tvl_weight: float = 0.3,
        stability_weight: float = 0.3
    ) -> Dict:
        """
        計算戴維斯雙擊評分
        
        由於無法獲取歷史數據，我們使用以下指標：
        1. APY 高低（高 APY 可能表示費用增長）
        2. TVL 規模（適中的 TVL 可能表示增長空間）
        3. 穩定性指標（APY 基礎部分 vs 獎勵部分）
        
        Args:
            pool: 池數據
            apy_weight: APY 權重
            tvl_weight: TVL 權重
            stability_weight: 穩定性權重
        
        Returns:
            評分結果
        """
        # 提取數據（處理 None 值）
        apy = pool.get("apy") or 0
        tvl = pool.get("tvlUsd") or 0
        apy_base = pool.get("apyBase") or 0
        apy_reward = pool.get("apyReward") or 0
        
        # 1. APY 評分（0-100）
        # 高 APY 得分高，但過高可能不穩定
        if apy < 5:
            apy_score = apy * 10  # 0-50
        elif apy < 20:
            apy_score = 50 + (apy - 5) * 2.67  # 50-90
        elif apy < 50:
            apy_score = 90 + (apy - 20) * 0.33  # 90-100
        else:
            apy_score = max(70, 100 - (apy - 50) * 0.5)  # 過高扣分
        
        # 2. TVL 評分（0-100）
        # 適中的 TVL 得分高（有增長空間但不太小）
        tvl_millions = tvl / 1_000_000
        if tvl_millions < 1:
            tvl_score = 20  # 太小，風險高
        elif tvl_millions < 10:
            tvl_score = 40 + tvl_millions * 4  # 40-80
        elif tvl_millions < 100:
            tvl_score = 80 + (tvl_millions - 10) * 0.22  # 80-100
        elif tvl_millions < 1000:
            tvl_score = 90  # 理想範圍
        else:
            tvl_score = max(60, 90 - (tvl_millions - 1000) / 100)  # 過大增長空間小
        
        # 3. 穩定性評分（0-100）
        # 基礎 APY 佔比高 = 更穩定
        if apy > 0:
            base_ratio = apy_base / apy
            stability_score = base_ratio * 100
        else:
            stability_score = 0
        
        # 綜合評分
        davis_score = (
            apy_score * apy_weight +
            tvl_score * tvl_weight +
            stability_score * stability_weight
        )
        
        # 特殊加分
        bonus = 0
        
        # 高 APY + 中等 TVL = 可能的戴維斯雙擊
        if apy > 15 and 10 < tvl_millions < 500:
            bonus += 10
        
        # 基礎 APY 高 = 費用收入好
        if apy_base > 10:
            bonus += 5
        
        # 穩定幣池 = 無常損失低
        symbol = pool.get("symbol", "").upper()
        if any(stable in symbol for stable in ["USDC", "USDT", "DAI", "FRAX"]):
            bonus += 5
        
        davis_score = min(100, davis_score + bonus)
        
        # 分類
        if davis_score >= 80:
            category = "極佳"
            recommendation = "強烈推薦"
        elif davis_score >= 65:
            category = "優質"
            recommendation = "推薦"
        elif davis_score >= 50:
            category = "良好"
            recommendation = "可考慮"
        elif davis_score >= 35:
            category = "一般"
            recommendation = "謹慎"
        else:
            category = "不推薦"
            recommendation = "避免"
        
        return {
            "davis_score": round(davis_score, 2),
            "category": category,
            "recommendation": recommendation,
            "breakdown": {
                "apy_score": round(apy_score, 2),
                "tvl_score": round(tvl_score, 2),
                "stability_score": round(stability_score, 2),
                "bonus": bonus
            },
            "metrics": {
                "apy": apy,
                "apy_base": apy_base,
                "apy_reward": apy_reward,
                "tvl": tvl,
                "base_ratio": round(apy_base / apy * 100, 2) if apy > 0 else 0
            }
        }
    
    def analyze_token_pools(
        self,
        token: str,
        min_tvl: float = 1_000_000,
        min_apy: float = 5.0,
        top_n: int = 20
    ) -> List[Dict]:
        """
        分析特定代幣的 LP 池
        
        Args:
            token: 目標代幣（如 "ETH"）
            min_tvl: 最小 TVL 過濾
            min_apy: 最小 APY 過濾
            top_n: 返回前 N 個
        
        Returns:
            分析結果列表
        """
        print(f"\n🔍 戴維斯雙擊分析 - {token}")
        print(f"   最小 TVL: ${min_tvl:,.0f}")
        print(f"   最小 APY: {min_apy}%\n")
        
        # 獲取所有池
        all_pools = self.get_all_pools()
        
        if not all_pools:
            print("❌ 無法獲取池數據")
            return []
        
        print(f"✅ 獲取到 {len(all_pools):,} 個池")
        
        # 過濾包含目標代幣的池
        token_pools = []
        for pool in all_pools:
            symbol = pool.get("symbol", "").upper()
            if token.upper() in symbol:
                # 應用過濾條件
                tvl = pool.get("tvlUsd", 0)
                apy = pool.get("apy", 0)
                
                if tvl >= min_tvl and apy >= min_apy:
                    token_pools.append(pool)
        
        print(f"✅ 找到 {len(token_pools)} 個包含 {token} 的池（TVL >= ${min_tvl:,.0f}, APY >= {min_apy}%）")
        
        if not token_pools:
            return []
        
        # 計算戴維斯評分
        results = []
        for pool in token_pools:
            davis_analysis = self.calculate_davis_score(pool)
            
            results.append({
                "pool_id": pool.get("pool"),
                "protocol": pool.get("project", "unknown"),
                "chain": pool.get("chain", "unknown"),
                "symbol": pool.get("symbol", "unknown"),
                "tvl": pool.get("tvlUsd") or 0,
                "apy": pool.get("apy") or 0,
                "apy_base": pool.get("apyBase") or 0,
                "apy_reward": pool.get("apyReward") or 0,
                "davis_score": davis_analysis["davis_score"],
                "category": davis_analysis["category"],
                "recommendation": davis_analysis["recommendation"],
                "analysis": davis_analysis
            })
        
        # 按戴維斯評分排序
        results.sort(key=lambda x: x["davis_score"], reverse=True)
        
        return results[:top_n]
    
    def generate_report(self, analysis_results: List[Dict]) -> str:
        """
        生成分析報告
        
        Args:
            analysis_results: 分析結果
        
        Returns:
            報告文本
        """
        if not analysis_results:
            return "無分析結果"
        
        report = []
        report.append("\n" + "="*80)
        report.append("戴維斯雙擊分析報告")
        report.append("="*80 + "\n")
        
        for i, result in enumerate(analysis_results, 1):
            report.append(f"{i}. {result['protocol']} - {result['symbol']}")
            report.append(f"   Chain: {result['chain']}")
            report.append(f"   TVL: ${result['tvl']:,.0f}")
            report.append(f"   APY: {result['apy']:.2f}% (基礎: {result['apy_base']:.2f}%, 獎勵: {result['apy_reward']:.2f}%)")
            report.append(f"   戴維斯評分: {result['davis_score']:.2f}/100 - {result['category']}")
            report.append(f"   建議: {result['recommendation']}")
            
            # 評分細節
            breakdown = result['analysis']['breakdown']
            report.append(f"   評分細節:")
            report.append(f"     - APY 評分: {breakdown['apy_score']:.2f}")
            report.append(f"     - TVL 評分: {breakdown['tvl_score']:.2f}")
            report.append(f"     - 穩定性評分: {breakdown['stability_score']:.2f}")
            if breakdown['bonus'] > 0:
                report.append(f"     - 額外加分: +{breakdown['bonus']}")
            
            report.append("")
        
        return "\n".join(report)


# ==================== 測試代碼 ====================

if __name__ == "__main__":
    print("🧪 測試戴維斯雙擊分析引擎\n")
    
    analyzer = DavisDoubleClickAnalyzer()
    
    # 測試 1: 分析 ETH 池
    print("="*80)
    print("測試 1: 分析 ETH LP 池")
    print("="*80)
    
    results = analyzer.analyze_token_pools(
        token="ETH",
        min_tvl=5_000_000,
        min_apy=3.0,
        top_n=10
    )
    
    if results:
        # 生成報告
        report = analyzer.generate_report(results)
        print(report)
        
        # 顯示前 3 個最佳機會
        print("\n" + "="*80)
        print("🏆 前 3 個最佳戴維斯雙擊機會")
        print("="*80 + "\n")
        
        for i, result in enumerate(results[:3], 1):
            print(f"{i}. {result['protocol']} - {result['symbol']}")
            print(f"   戴維斯評分: {result['davis_score']:.2f}/100")
            print(f"   APY: {result['apy']:.2f}%")
            print(f"   TVL: ${result['tvl']:,.0f}")
            print(f"   建議: {result['recommendation']}")
            print()
    
    # 測試 2: 分析 BTC 池
    print("="*80)
    print("測試 2: 分析 BTC LP 池")
    print("="*80)
    
    results_btc = analyzer.analyze_token_pools(
        token="BTC",
        min_tvl=5_000_000,
        min_apy=3.0,
        top_n=5
    )
    
    if results_btc:
        print(f"\n找到 {len(results_btc)} 個 BTC 池")
        for i, result in enumerate(results_btc[:3], 1):
            print(f"{i}. {result['symbol']} - 評分: {result['davis_score']:.2f}")
    
    print("\n✅ 測試完成！")

