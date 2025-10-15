"""
Delta Neutral 策略計算器
"""

from typing import Dict, List, Optional
from datetime import datetime
from unified_data_aggregator import UnifiedDataAggregator


class DeltaNeutralCalculator:
    """Delta Neutral 策略計算器"""
    
    def __init__(self):
        self.aggregator = UnifiedDataAggregator()
    
    def calculate_hedge_ratio(
        self,
        lp_value: float,
        token_price: float,
        pool_composition: float = 0.5
    ) -> Dict:
        """
        計算對沖比率
        
        Args:
            lp_value: LP 倉位總價值 (USD)
            token_price: 代幣價格 (USD)
            pool_composition: 池中目標代幣的比例（默認 0.5 表示 50/50 池）
        
        Returns:
            對沖信息字典
        """
        # LP 中目標代幣的價值
        token_value_in_lp = lp_value * pool_composition
        
        # 需要對沖的代幣數量
        token_amount = token_value_in_lp / token_price
        
        # 對沖倉位大小（USD）
        hedge_position_size = token_value_in_lp
        
        return {
            "lp_value": lp_value,
            "token_value_in_lp": token_value_in_lp,
            "token_amount": token_amount,
            "token_price": token_price,
            "hedge_position_size": hedge_position_size,
            "hedge_leverage": 1.0,  # 1x 槓桿以保持 Delta Neutral
        }
    
    def calculate_total_yield(
        self,
        lp_apy: float,
        funding_rate_apy: float,
        gas_cost_annual: float = 0,
        capital: float = 10000
    ) -> Dict:
        """
        計算總收益
        
        Args:
            lp_apy: LP 池年化收益率 (%)
            funding_rate_apy: 資金費率年化收益率 (%)
            gas_cost_annual: 年化 Gas 成本 (USD)
            capital: 投入資本 (USD)
        
        Returns:
            收益計算結果
        """
        # LP 收益
        lp_yield_annual = capital * (lp_apy / 100)
        
        # 資金費率收益（空單收取正費率）
        funding_yield_annual = capital * (funding_rate_apy / 100)
        
        # Gas 成本 APY
        gas_cost_apy = (gas_cost_annual / capital) * 100 if capital > 0 else 0
        
        # 總收益
        total_yield_annual = lp_yield_annual + funding_yield_annual - gas_cost_annual
        total_apy = (total_yield_annual / capital) * 100 if capital > 0 else 0
        
        return {
            "lp_apy": lp_apy,
            "lp_yield_annual": lp_yield_annual,
            "funding_rate_apy": funding_rate_apy,
            "funding_yield_annual": funding_yield_annual,
            "gas_cost_apy": gas_cost_apy,
            "gas_cost_annual": gas_cost_annual,
            "total_apy": total_apy,
            "total_yield_annual": total_yield_annual,
            "capital": capital,
        }
    
    def calculate_rebalance_decision(
        self,
        current_apy: float,
        new_apy: float,
        rebalance_cost: float,
        capital: float,
        min_apy_improvement: float = 5.0,
        max_payback_days: int = 7
    ) -> Dict:
        """
        計算轉倉決策
        
        Args:
            current_apy: 當前池 APY (%)
            new_apy: 新池 APY (%)
            rebalance_cost: 轉倉成本 (USD)
            capital: 投入資本 (USD)
            min_apy_improvement: 最小 APY 提升要求 (%)
            max_payback_days: 最大回本天數
        
        Returns:
            轉倉決策結果
        """
        # APY 提升
        apy_improvement = new_apy - current_apy
        
        # 年化收益提升
        yield_improvement_annual = capital * (apy_improvement / 100)
        
        # 日收益提升
        yield_improvement_daily = yield_improvement_annual / 365
        
        # 回本天數
        payback_days = rebalance_cost / yield_improvement_daily if yield_improvement_daily > 0 else float('inf')
        
        # ROI
        roi = (yield_improvement_annual / rebalance_cost) * 100 if rebalance_cost > 0 else 0
        
        # 決策
        should_rebalance = (
            apy_improvement >= min_apy_improvement and
            payback_days <= max_payback_days and
            roi >= 200  # ROI 至少 200%
        )
        
        return {
            "current_apy": current_apy,
            "new_apy": new_apy,
            "apy_improvement": apy_improvement,
            "yield_improvement_annual": yield_improvement_annual,
            "yield_improvement_daily": yield_improvement_daily,
            "rebalance_cost": rebalance_cost,
            "payback_days": payback_days,
            "roi": roi,
            "should_rebalance": should_rebalance,
            "reason": self._get_rebalance_reason(
                should_rebalance,
                apy_improvement,
                min_apy_improvement,
                payback_days,
                max_payback_days,
                roi
            )
        }
    
    def _get_rebalance_reason(
        self,
        should_rebalance: bool,
        apy_improvement: float,
        min_apy_improvement: float,
        payback_days: float,
        max_payback_days: int,
        roi: float
    ) -> str:
        """生成轉倉決策原因"""
        if should_rebalance:
            return f"建議轉倉：APY 提升 {apy_improvement:.2f}%，{payback_days:.1f} 天回本，ROI {roi:.0f}%"
        else:
            reasons = []
            if apy_improvement < min_apy_improvement:
                reasons.append(f"APY 提升不足（{apy_improvement:.2f}% < {min_apy_improvement}%）")
            if payback_days > max_payback_days:
                reasons.append(f"回本期過長（{payback_days:.1f} 天 > {max_payback_days} 天）")
            if roi < 200:
                reasons.append(f"ROI 過低（{roi:.0f}% < 200%）")
            return "不建議轉倉：" + "、".join(reasons)
    
    def find_best_opportunities(
        self,
        token: str = "ETH",
        capital: float = 10000,
        min_tvl: float = 1000000,
        top_n: int = 10
    ) -> List[Dict]:
        """
        尋找最佳 Delta Neutral 機會
        
        Args:
            token: 目標代幣
            capital: 投入資本 (USD)
            min_tvl: 最小 TVL 過濾
            top_n: 返回前 N 個機會
        
        Returns:
            機會列表，按總 APY 排序
        """
        print(f"\n🔍 尋找 {token} 的最佳 Delta Neutral 機會...")
        print(f"   資本: ${capital:,.0f}")
        print(f"   最小 TVL: ${min_tvl:,.0f}\n")
        
        # 獲取數據
        data = self.aggregator.get_delta_neutral_data(token)
        
        if not data["lp_pools"] or not data["funding_rate"]:
            print("❌ 無法獲取必要數據")
            return []
        
        # 資金費率 APY
        funding_apy = data["funding_rate"]["annualized_rate_pct"]
        
        opportunities = []
        
        for pool in data["lp_pools"]:
            # 過濾低 TVL 池
            if pool["tvl"] < min_tvl:
                continue
            
            # 計算總收益
            lp_apy = pool["apy"]
            total_apy = lp_apy + funding_apy
            
            # 估算 Gas 成本（簡化版）
            gas_cost_annual = 200  # 假設每年 $200 Gas 成本
            
            yield_calc = self.calculate_total_yield(
                lp_apy=lp_apy,
                funding_rate_apy=funding_apy,
                gas_cost_annual=gas_cost_annual,
                capital=capital
            )
            
            opportunities.append({
                "pool_id": pool["pool_id"],
                "protocol": pool["protocol"],
                "chain": pool["chain"],
                "symbol": pool["symbol"],
                "tvl": pool["tvl"],
                "lp_apy": lp_apy,
                "funding_apy": funding_apy,
                "total_apy": yield_calc["total_apy"],
                "annual_yield": yield_calc["total_yield_annual"],
                "il_risk": pool.get("il_risk", "unknown"),
                "score": self._calculate_opportunity_score(pool, yield_calc),
            })
        
        # 按總 APY 排序
        opportunities.sort(key=lambda x: x["total_apy"], reverse=True)
        
        return opportunities[:top_n]
    
    def _calculate_opportunity_score(self, pool: Dict, yield_calc: Dict) -> float:
        """
        計算機會評分
        
        綜合考慮：
        - 總 APY
        - TVL（流動性）
        - 無常損失風險
        """
        score = 0.0
        
        # APY 得分（最高 50 分）
        apy_score = min(yield_calc["total_apy"] / 2, 50)
        score += apy_score
        
        # TVL 得分（最高 30 分）
        tvl_millions = pool["tvl"] / 1_000_000
        tvl_score = min(tvl_millions / 100 * 30, 30)
        score += tvl_score
        
        # 無常損失風險得分（最高 20 分）
        il_risk = pool.get("il_risk", "unknown").lower()
        if il_risk == "none" or il_risk == "low":
            il_score = 20
        elif il_risk == "medium":
            il_score = 10
        elif il_risk == "high":
            il_score = 5
        else:
            il_score = 10  # unknown
        score += il_score
        
        return score
    
    def generate_strategy_report(
        self,
        token: str = "ETH",
        capital: float = 10000
    ) -> Dict:
        """
        生成完整的策略報告
        
        Args:
            token: 目標代幣
            capital: 投入資本
        
        Returns:
            策略報告
        """
        print(f"\n{'='*60}")
        print(f"📊 生成 {token} Delta Neutral 策略報告")
        print(f"{'='*60}\n")
        
        # 獲取最佳機會
        opportunities = self.find_best_opportunities(
            token=token,
            capital=capital,
            top_n=5
        )
        
        if not opportunities:
            return {
                "error": "無法找到合適的機會",
                "timestamp": datetime.now().isoformat()
            }
        
        # 最佳機會
        best_opportunity = opportunities[0]
        
        # 獲取價格數據
        price_data = self.aggregator.get_token_price(token)
        
        # 計算對沖比率
        hedge_info = self.calculate_hedge_ratio(
            lp_value=capital,
            token_price=price_data["price"] if price_data else 4000
        )
        
        # 獲取市場情緒
        sentiment = self.aggregator.get_fear_greed_index()
        
        report = {
            "token": token,
            "capital": capital,
            "timestamp": datetime.now().isoformat(),
            "market_data": {
                "token_price": price_data["price"] if price_data else None,
                "price_change_24h": price_data["change_24h"] if price_data else None,
                "fear_greed_index": sentiment["value"] if sentiment else None,
                "market_sentiment": sentiment["classification"] if sentiment else None,
            },
            "best_opportunity": best_opportunity,
            "hedge_info": hedge_info,
            "top_opportunities": opportunities,
            "recommendation": self._generate_recommendation(best_opportunity, sentiment),
        }
        
        return report
    
    def _generate_recommendation(
        self,
        opportunity: Dict,
        sentiment: Optional[Dict]
    ) -> str:
        """生成投資建議"""
        apy = opportunity["total_apy"]
        
        if apy > 30:
            risk_level = "中等"
            recommendation = "極佳機會"
        elif apy > 20:
            risk_level = "中低"
            recommendation = "良好機會"
        elif apy > 10:
            risk_level = "低"
            recommendation = "穩健機會"
        else:
            risk_level = "極低"
            recommendation = "保守機會"
        
        market_note = ""
        if sentiment:
            if sentiment["value"] < 30:
                market_note = "市場恐懼，可能是進場好時機"
            elif sentiment["value"] > 70:
                market_note = "市場貪婪，建議謹慎"
        
        return f"{recommendation}（風險等級：{risk_level}）。{market_note}"


# ==================== 測試代碼 ====================

if __name__ == "__main__":
    print("🧪 測試 Delta Neutral 計算器\n")
    
    calculator = DeltaNeutralCalculator()
    
    # 測試 1: 計算對沖比率
    print("="*60)
    print("測試 1: 計算對沖比率")
    print("="*60)
    hedge_info = calculator.calculate_hedge_ratio(
        lp_value=10000,
        token_price=4000
    )
    print(f"LP 價值: ${hedge_info['lp_value']:,.0f}")
    print(f"需對沖代幣數量: {hedge_info['token_amount']:.4f} ETH")
    print(f"對沖倉位大小: ${hedge_info['hedge_position_size']:,.0f}")
    
    # 測試 2: 計算總收益
    print("\n" + "="*60)
    print("測試 2: 計算總收益")
    print("="*60)
    yield_calc = calculator.calculate_total_yield(
        lp_apy=15.5,
        funding_rate_apy=10.95,
        gas_cost_annual=200,
        capital=10000
    )
    print(f"LP APY: {yield_calc['lp_apy']:.2f}%")
    print(f"資金費率 APY: {yield_calc['funding_rate_apy']:.2f}%")
    print(f"總 APY: {yield_calc['total_apy']:.2f}%")
    print(f"年收益: ${yield_calc['total_yield_annual']:,.0f}")
    
    # 測試 3: 轉倉決策
    print("\n" + "="*60)
    print("測試 3: 轉倉決策")
    print("="*60)
    rebalance = calculator.calculate_rebalance_decision(
        current_apy=20,
        new_apy=28,
        rebalance_cost=50,
        capital=10000
    )
    print(f"當前 APY: {rebalance['current_apy']:.2f}%")
    print(f"新池 APY: {rebalance['new_apy']:.2f}%")
    print(f"APY 提升: {rebalance['apy_improvement']:.2f}%")
    print(f"回本天數: {rebalance['payback_days']:.1f} 天")
    print(f"ROI: {rebalance['roi']:.0f}%")
    print(f"決策: {'✅ 建議轉倉' if rebalance['should_rebalance'] else '❌ 不建議轉倉'}")
    print(f"原因: {rebalance['reason']}")
    
    # 測試 4: 尋找最佳機會
    print("\n" + "="*60)
    print("測試 4: 尋找最佳機會")
    print("="*60)
    opportunities = calculator.find_best_opportunities(
        token="ETH",
        capital=10000,
        top_n=5
    )
    
    if opportunities:
        print(f"\n找到 {len(opportunities)} 個機會：\n")
        for i, opp in enumerate(opportunities, 1):
            print(f"{i}. {opp['protocol']} - {opp['symbol']}")
            print(f"   Chain: {opp['chain']}")
            print(f"   TVL: ${opp['tvl']:,.0f}")
            print(f"   LP APY: {opp['lp_apy']:.2f}%")
            print(f"   資金費率 APY: {opp['funding_apy']:.2f}%")
            print(f"   總 APY: {opp['total_apy']:.2f}%")
            print(f"   年收益: ${opp['annual_yield']:,.0f}")
            print(f"   評分: {opp['score']:.1f}/100")
            print()
    
    # 測試 5: 生成完整報告
    print("="*60)
    print("測試 5: 生成完整策略報告")
    print("="*60)
    report = calculator.generate_strategy_report(
        token="ETH",
        capital=10000
    )
    
    if "error" not in report:
        print(f"\n📊 策略報告摘要：")
        print(f"  代幣: {report['token']}")
        print(f"  資本: ${report['capital']:,.0f}")
        print(f"  當前價格: ${report['market_data']['token_price']:,.2f}")
        print(f"  市場情緒: {report['market_data']['market_sentiment']}")
        print(f"\n🏆 最佳機會:")
        best = report['best_opportunity']
        print(f"  協議: {best['protocol']}")
        print(f"  總 APY: {best['total_apy']:.2f}%")
        print(f"  預期年收益: ${best['annual_yield']:,.0f}")
        print(f"\n💡 建議: {report['recommendation']}")
    
    print("\n✅ 所有測試完成！")

