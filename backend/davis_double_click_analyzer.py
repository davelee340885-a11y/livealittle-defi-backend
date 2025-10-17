"""
池質量評分引擎（原戴維斯雙擊分析器）
基於當前 APY、TVL 和穩定性評估 LP 池的質量

注意：這是靜態質量評分，不是真正的戴維斯雙擊策略。
真正的戴維斯雙擊需要追蹤 APY 和 TVL 的動態變化趨勢。
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time


class DavisDoubleClickAnalyzer:
    """池質量評分引擎（基於靜態指標）"""
    
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
        計算池質量評分（基於當前靜態指標）
        
        評分維度：
        1. APY 水平（40%）- 收益潛力
        2. TVL 規模（30%）- 流動性和安全性
        3. 穩定性（30%）- 基礎 APY 佔比
        
        注意：這是靜態評分，不追蹤動態變化。
        未來版本將實現真正的戴維斯雙擊（APY增長 × TVL增長）。
        
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
        
        # 1. APY 評分（0-100）- 修正版：線性評分，不懲罰高 APY
        if apy <= 0:
            apy_score = 0
        elif apy < 5:
            apy_score = apy * 10  # 0-50
        elif apy < 20:
            apy_score = 50 + (apy - 5) * 2.67  # 50-90
        elif apy < 100:
            apy_score = 90 + (apy - 20) * 0.125  # 90-100
        else:
            # 超高 APY 保持滿分，不扣分
            apy_score = 100
        
        # 2. TVL 評分（0-100）- 修正版：對數評分，不懲罰大 TVL
        tvl_millions = tvl / 1_000_000
        if tvl_millions <= 0:
            tvl_score = 0
        elif tvl_millions < 1:
            tvl_score = 30  # 小池風險較高
        elif tvl_millions < 10:
            tvl_score = 30 + (tvl_millions - 1) * 5  # 30-75
        elif tvl_millions < 100:
            tvl_score = 75 + (tvl_millions - 10) * 0.22  # 75-95
        else:
            # 大 TVL 保持高分，不扣分
            tvl_score = min(100, 95 + (tvl_millions - 100) * 0.001)
        
        # 3. 穩定性評分（0-100）
        # 基礎 APY 佔比高 = 更穩定（費用收入而非代幣獎勵）
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
        
        # 高 APY + 大 TVL = 優質池
        if apy > 15 and tvl_millions > 10:
            bonus += 5
        
        # 超高基礎 APY = 費用收入極好
        if apy_base > 20:
            bonus += 10
        elif apy_base > 10:
            bonus += 5
        
        # 穩定幣池 = 無常損失低
        symbol = pool.get("symbol", "").upper()
        if any(stable in symbol for stable in ["USDC", "USDT", "DAI", "FRAX", "USDE"]):
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
            },
            "note": "這是基於當前狀態的靜態評分。未來版本將追蹤 APY 和 TVL 的動態變化，實現真正的戴維斯雙擊策略。"
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
        print(f"\n🔍 池質量分析 - {token}")
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
        
        # 計算質量評分
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
        
        # 按質量評分排序
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
        report.append("池質量分析報告")
        report.append("="*80 + "\n")
        
        for i, result in enumerate(analysis_results, 1):
            report.append(f"{i}. {result['protocol']} - {result['symbol']}")
            report.append(f"   Chain: {result['chain']}")
            report.append(f"   TVL: ${result['tvl']:,.0f}")
            report.append(f"   APY: {result['apy']:.2f}% (基礎: {result['apy_base']:.2f}%, 獎勵: {result['apy_reward']:.2f}%)")
            report.append(f"   質量評分: {result['davis_score']:.2f}/100 - {result['category']}")
            report.append(f"   建議: {result['recommendation']}")
            
            # 評分細節
            breakdown = result['analysis']['breakdown']
            report.append(f"   評分細節:")
            report.append(f"     - APY 評分: {breakdown['apy_score']:.2f}/100")
            report.append(f"     - TVL 評分: {breakdown['tvl_score']:.2f}/100")
            report.append(f"     - 穩定性評分: {breakdown['stability_score']:.2f}/100")
            if breakdown['bonus'] > 0:
                report.append(f"     - 額外加分: +{breakdown['bonus']}")
            
            report.append("")
        
        return "\n".join(report)


# ==================== 測試代碼 ====================

if __name__ == "__main__":
    print("🧪 測試池質量評分引擎\n")
    
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
        print("🏆 前 3 個最高質量池")
        print("="*80 + "\n")
        
        for i, result in enumerate(results[:3], 1):
            print(f"{i}. {result['protocol']} - {result['symbol']}")
            print(f"   質量評分: {result['davis_score']:.2f}/100")
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


