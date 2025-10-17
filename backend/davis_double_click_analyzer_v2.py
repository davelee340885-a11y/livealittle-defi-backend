"""
Davis Double Click Analyzer V2 - 真正的戴維斯雙擊分析器
基於 APY 和 TVL 的動態變化趨勢評估投資時機

戴維斯雙擊理論：
- 當業績（APY）和估值（TVL）同步增長時，投資回報呈指數級提升
- 當業績和估值同步下降時（戴維斯雙殺），應立即退出避免損失
"""

import requests
from typing import Dict, List
from pool_history_fetcher import PoolHistoryFetcher


class DavisDoubleClickAnalyzerV2:
    """真正的戴維斯雙擊分析器 - 基於歷史數據的動態評分"""
    
    def __init__(self):
        self.history_fetcher = PoolHistoryFetcher()
    
    def calculate_davis_score(self, pool: Dict) -> Dict:
        """
        計算真正的戴維斯雙擊評分
        
        Args:
            pool: 池數據，包含 pool (ID), apy, tvlUsd 等欄位
            
        Returns:
            {
                'davis_score': int,              # 0-100 的評分
                'category': str,                 # 極佳/優良/良好/一般
                'signal': str,                   # 雙擊/雙殺/混合/穩定
                'signal_strength': str,          # 強烈/溫和/弱/中性
                'recommendation': str,           # 投資建議
                'growth_rates': Dict,            # 增長率數據
                'breakdown': Dict,               # 評分細節
                'has_history': bool              # 是否有歷史數據
            }
        """
        pool_id = pool.get('pool')
        
        # 獲取增長率數據
        growth_rates = self.history_fetcher.get_growth_rates(pool_id)
        
        # 計算戴維斯雙擊評分
        davis_score = self._calculate_double_click_score(pool, growth_rates)
        
        # 判斷信號類型
        signal_info = self._determine_signal(growth_rates)
        
        # 生成投資建議
        recommendation = self._generate_recommendation(davis_score, signal_info)
        
        # 評分細節
        breakdown = self._calculate_breakdown(pool, growth_rates)
        
        return {
            'davis_score': davis_score,
            'category': self._get_category(davis_score),
            'signal': signal_info['signal'],
            'signal_strength': signal_info['strength'],
            'recommendation': recommendation,
            'growth_rates': growth_rates,
            'breakdown': breakdown,
            'has_history': growth_rates['has_history']
        }
    
    def _calculate_double_click_score(self, pool: Dict, growth_rates: Dict) -> int:
        """
        計算戴維斯雙擊評分（0-100）
        
        評分邏輯：
        1. 基礎質量分（40分）：當前 APY 和 TVL 的質量
        2. 增長分數（40分）：7天和30天的增長率
        3. 雙擊加成（20分）：APY 和 TVL 同步增長的乘數效應
        """
        # 1. 基礎質量分（40分）
        quality_score = self._calculate_quality_score(pool)
        
        # 2. 增長分數（40分）
        growth_score = self._calculate_growth_score(growth_rates)
        
        # 3. 雙擊加成（20分）
        double_click_bonus = self._calculate_double_click_bonus(growth_rates)
        
        total_score = quality_score + growth_score + double_click_bonus
        
        return min(100, max(0, int(total_score)))
    
    def _calculate_quality_score(self, pool: Dict) -> float:
        """
        計算基礎質量分（40分）
        評估當前 APY 和 TVL 的質量
        """
        apy = pool.get('apy', 0)
        tvl = pool.get('tvlUsd', 0)
        
        # APY 分數（20分）
        # 5% = 10分，20% = 17.5分，50%+ = 20分
        if apy < 5:
            apy_score = apy * 2  # 0-10
        elif apy < 20:
            apy_score = 10 + (apy - 5) * 0.5  # 10-17.5
        else:
            apy_score = min(20, 17.5 + (apy - 20) * 0.1)  # 17.5-20
        
        # TVL 分數（20分）
        # $1M = 5分，$10M = 14分，$100M = 18.5分，$1B+ = 20分
        tvl_millions = tvl / 1_000_000
        if tvl_millions < 1:
            tvl_score = tvl_millions * 5  # 0-5
        elif tvl_millions < 10:
            tvl_score = 5 + (tvl_millions - 1) * 1  # 5-14
        elif tvl_millions < 100:
            tvl_score = 14 + (tvl_millions - 10) * 0.05  # 14-18.5
        else:
            tvl_score = min(20, 18.5 + (tvl_millions - 100) * 0.001)  # 18.5-20
        
        return apy_score + tvl_score
    
    def _calculate_growth_score(self, growth_rates: Dict) -> float:
        """
        計算增長分數（40分）
        評估 APY 和 TVL 的增長趨勢
        """
        if not growth_rates['has_history']:
            # 沒有歷史數據，返回中性分數
            return 20.0
        
        apy_7d = growth_rates['apy_7d_change']
        tvl_7d = growth_rates['tvl_7d_change']
        apy_30d = growth_rates['apy_30d_change']
        tvl_30d = growth_rates['tvl_30d_change']
        
        # 7天增長分數（20分）
        apy_7d_score = self._score_growth(apy_7d, max_score=10)
        tvl_7d_score = self._score_growth(tvl_7d, max_score=10)
        
        # 30天增長分數（20分）
        apy_30d_score = self._score_growth(apy_30d, max_score=10)
        tvl_30d_score = self._score_growth(tvl_30d, max_score=10)
        
        return apy_7d_score + tvl_7d_score + apy_30d_score + tvl_30d_score
    
    def _score_growth(self, growth_rate: float, max_score: float) -> float:
        """
        評分增長率
        
        增長率評分曲線：
        +50% 以上 = 100% 分數（滿分）
        +20% = 80% 分數
        0% = 50% 分數（中性）
        -20% = 20% 分數
        -50% 以下 = 0% 分數
        """
        if growth_rate >= 50:
            return max_score
        elif growth_rate >= 20:
            # 線性插值：20% 到 50% 之間
            ratio = 0.8 + (growth_rate - 20) / 30 * 0.2
            return max_score * ratio
        elif growth_rate >= 0:
            # 線性插值：0% 到 20% 之間
            ratio = 0.5 + growth_rate / 20 * 0.3
            return max_score * ratio
        elif growth_rate >= -20:
            # 線性插值：-20% 到 0% 之間
            ratio = 0.2 + (growth_rate + 20) / 20 * 0.3
            return max_score * ratio
        elif growth_rate >= -50:
            # 線性插值：-50% 到 -20% 之間
            ratio = (growth_rate + 50) / 30 * 0.2
            return max_score * ratio
        else:
            return 0
    
    def _calculate_double_click_bonus(self, growth_rates: Dict) -> float:
        """
        計算雙擊加成（-20 到 +20分）
        
        當 APY 和 TVL 同步增長時，給予正加成（戴維斯雙擊）
        當 APY 和 TVL 同步下降時，給予負加成（戴維斯雙殺）
        """
        if not growth_rates['has_history']:
            return 5.0  # 沒有歷史數據，給予小幅加分
        
        apy_7d = growth_rates['apy_7d_change']
        tvl_7d = growth_rates['tvl_7d_change']
        
        # 戴維斯雙擊：APY 和 TVL 都增長
        if apy_7d > 0 and tvl_7d > 0:
            # 強烈雙擊：都 > 20%
            if apy_7d > 20 and tvl_7d > 20:
                return 20
            # 溫和雙擊：都 > 10%
            elif apy_7d > 10 and tvl_7d > 10:
                return 15
            # 弱雙擊：都 > 5%
            elif apy_7d > 5 and tvl_7d > 5:
                return 12
            # 微弱雙擊：都 > 0%
            else:
                return 8
        
        # 戴維斯雙殺：APY 和 TVL 都下降
        elif apy_7d < 0 and tvl_7d < 0:
            # 強烈雙殺：都 < -20%
            if apy_7d < -20 and tvl_7d < -20:
                return -20
            # 溫和雙殺：都 < -10%
            elif apy_7d < -10 and tvl_7d < -10:
                return -15
            # 弱雙殺：都 < -5%
            elif apy_7d < -5 and tvl_7d < -5:
                return -10
            # 微弱雙殺：都 < 0%
            else:
                return -5
        
        # 混合信號：方向不一致
        else:
            # 至少有一個在增長，給予小幅加分
            return 5
    
    def _determine_signal(self, growth_rates: Dict) -> Dict:
        """
        判斷戴維斯信號類型
        
        Returns:
            {
                'signal': str,      # 雙擊/雙殺/混合/穩定
                'strength': str     # 強烈/溫和/弱/中性
            }
        """
        if not growth_rates['has_history']:
            return {'signal': '未知', 'strength': '中性'}
        
        apy_7d = growth_rates['apy_7d_change']
        tvl_7d = growth_rates['tvl_7d_change']
        
        # 戴維斯雙擊
        if apy_7d > 0 and tvl_7d > 0:
            if apy_7d > 20 and tvl_7d > 20:
                return {'signal': '雙擊', 'strength': '強烈'}
            elif apy_7d > 10 and tvl_7d > 10:
                return {'signal': '雙擊', 'strength': '溫和'}
            elif apy_7d > 5 and tvl_7d > 5:
                return {'signal': '雙擊', 'strength': '弱'}
            else:
                return {'signal': '雙擊', 'strength': '微弱'}
        
        # 戴維斯雙殺
        elif apy_7d < 0 and tvl_7d < 0:
            if apy_7d < -20 and tvl_7d < -20:
                return {'signal': '雙殺', 'strength': '強烈'}
            elif apy_7d < -10 and tvl_7d < -10:
                return {'signal': '雙殺', 'strength': '溫和'}
            elif apy_7d < -5 and tvl_7d < -5:
                return {'signal': '雙殺', 'strength': '弱'}
            else:
                return {'signal': '雙殺', 'strength': '微弱'}
        
        # 穩定
        elif abs(apy_7d) < 5 and abs(tvl_7d) < 5:
            return {'signal': '穩定', 'strength': '中性'}
        
        # 混合信號
        else:
            return {'signal': '混合', 'strength': '中性'}
    
    def _generate_recommendation(self, davis_score: int, signal_info: Dict) -> str:
        """
        生成投資建議
        
        Args:
            davis_score: 戴維斯評分（0-100）
            signal_info: 信號信息
            
        Returns:
            投資建議文字
        """
        signal = signal_info['signal']
        strength = signal_info['strength']
        
        # 戴維斯雙擊 - 買入信號
        if signal == '雙擊':
            if strength == '強烈':
                return '💰 強烈買入'
            elif strength == '溫和':
                return '✅ 買入'
            elif strength == '弱':
                return '👀 可以考慮'
            else:
                return '👀 謹慎樂觀'
        
        # 戴維斯雙殺 - 賣出信號
        elif signal == '雙殺':
            if strength == '強烈':
                return '🚨 立即退出'
            elif strength == '溫和':
                return '⚠️ 建議退出'
            elif strength == '弱':
                return '⚠️ 謹慎觀察'
            else:
                return '⚠️ 密切關注'
        
        # 穩定 - 根據評分決定
        elif signal == '穩定':
            if davis_score >= 80:
                return '✅ 持有'
            elif davis_score >= 60:
                return '👀 觀察'
            else:
                return '⚠️ 謹慎'
        
        # 混合信號 - 需要分析
        elif signal == '混合':
            if davis_score >= 80:
                return '👀 謹慎樂觀'
            elif davis_score >= 60:
                return '⚠️ 需要分析'
            else:
                return '⚠️ 謹慎觀察'
        
        # 未知 - 無歷史數據
        else:
            if davis_score >= 80:
                return '✅ 質量優秀'
            elif davis_score >= 60:
                return '👀 質量良好'
            else:
                return '⚠️ 謹慎評估'
    
    def _calculate_breakdown(self, pool: Dict, growth_rates: Dict) -> Dict:
        """
        計算評分細節
        
        Returns:
            {
                'quality_score': float,          # 基礎質量分
                'growth_score': float,           # 增長分數
                'double_click_bonus': float,     # 雙擊加成
                'apy_7d_change': float,          # 7天 APY 變化
                'tvl_7d_change': float,          # 7天 TVL 變化
                'apy_30d_change': float,         # 30天 APY 變化
                'tvl_30d_change': float          # 30天 TVL 變化
            }
        """
        quality_score = self._calculate_quality_score(pool)
        growth_score = self._calculate_growth_score(growth_rates)
        bonus = self._calculate_double_click_bonus(growth_rates)
        
        return {
            'quality_score': round(quality_score, 1),
            'growth_score': round(growth_score, 1),
            'double_click_bonus': round(bonus, 1),
            'apy_7d_change': growth_rates['apy_7d_change'],
            'tvl_7d_change': growth_rates['tvl_7d_change'],
            'apy_30d_change': growth_rates['apy_30d_change'],
            'tvl_30d_change': growth_rates['tvl_30d_change']
        }
    
    def _get_category(self, score: int) -> str:
        """根據分數返回評級"""
        if score >= 80:
            return "極佳"
        elif score >= 60:
            return "優良"
        elif score >= 40:
            return "良好"
        else:
            return "一般"


    
    # ========== 批量分析方法 ==========
    
    def get_all_pools(self) -> List[Dict]:
        """
        獲取所有 LP 池數據
        
        Returns:
            池列表
        """
        try:
            url = "https://yields.llama.fi/pools"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            pools = data.get("data", [])
            return pools
            
        except Exception as e:
            print(f"❌ 獲取池數據失敗: {str(e)}")
            return []
    
    def analyze_token_pools(
        self,
        token: str,
        min_tvl: float = 1_000_000,
        min_apy: float = 5.0,
        top_n: int = 20
    ) -> List[Dict]:
        """
        分析特定代幣的 LP 池（整合歷史數據分析）
        
        Args:
            token: 目標代幣（如 "ETH"）
            min_tvl: 最小 TVL 過濾
            min_apy: 最小 APY 過濾
            top_n: 返回前 N 個
        
        Returns:
            分析結果列表，包含戴維斯雙擊評分和增長率數據
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
        
        # 計算戴維斯雙擊評分（包含歷史數據分析）
        print(f"📊 正在分析 {len(token_pools)} 個池的歷史趨勢...")
        
        results = []
        for i, pool in enumerate(token_pools, 1):
            # 顯示進度
            if i % 5 == 0 or i == len(token_pools):
                print(f"   進度: {i}/{len(token_pools)}")
            
            # 計算戴維斯雙擊評分
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
                "signal": davis_analysis["signal"],
                "signal_strength": davis_analysis["signal_strength"],
                "recommendation": davis_analysis["recommendation"],
                "growth_rates": davis_analysis["growth_rates"],
                "has_history": davis_analysis["has_history"],
                "analysis": davis_analysis
            })
        
        # 按戴維斯評分排序
        results.sort(key=lambda x: x["davis_score"], reverse=True)
        
        print(f"✅ 分析完成！返回前 {top_n} 個最佳機會\n")
        
        return results[:top_n]


# 添加 requests 導入


# 測試代碼
if __name__ == "__main__":
    print("=" * 60)
    print("測試 DavisDoubleClickAnalyzerV2")
    print("=" * 60 + "\n")
    
    analyzer = DavisDoubleClickAnalyzerV2()
    
    # 測試池數據
    test_pool = {
        'pool': 'fc9f488e-8183-416f-a61e-4e5c571d4395',  # Uniswap V3 WETH-USDT
        'apy': 55.64,
        'tvlUsd': 155872710
    }
    
    print(f"正在分析池: {test_pool['pool']}")
    print(f"當前 APY: {test_pool['apy']}%")
    print(f"當前 TVL: ${test_pool['tvlUsd']:,.0f}\n")
    
    result = analyzer.calculate_davis_score(test_pool)
    
    print("分析結果：")
    print(f"  戴維斯評分: {result['davis_score']}/100 ({result['category']})")
    print(f"  信號類型: {result['signal_strength']} {result['signal']}")
    print(f"  投資建議: {result['recommendation']}")
    print(f"  有歷史數據: {'是' if result['has_history'] else '否'}\n")
    
    if result['has_history']:
        print("評分細節：")
        breakdown = result['breakdown']
        print(f"  基礎質量分: {breakdown['quality_score']}/40")
        print(f"  增長分數: {breakdown['growth_score']}/40")
        print(f"  雙擊加成: {breakdown['double_click_bonus']:+.1f}/20\n")
        
        print("增長率：")
        print(f"  7天 APY 變化: {breakdown['apy_7d_change']:+.2f}%")
        print(f"  7天 TVL 變化: {breakdown['tvl_7d_change']:+.2f}%")
        print(f"  30天 APY 變化: {breakdown['apy_30d_change']:+.2f}%")
        print(f"  30天 TVL 變化: {breakdown['tvl_30d_change']:+.2f}%")


