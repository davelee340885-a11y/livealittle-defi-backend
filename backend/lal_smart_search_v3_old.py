"""
LAL 智能搜尋服務 V3
整合戴維斯雙擊分析、Delta Neutral 配對、IL 計算、成本效益計算
"""

from typing import Dict, List, Optional
from datetime import datetime
import requests

# 導入現有模組
from davis_double_click_analyzer import DavisDoubleClickAnalyzer
from unified_data_aggregator import UnifiedDataAggregator
from delta_neutral_calculator import DeltaNeutralCalculator
from il_calculator import ILCalculator, HedgeParams


class GasFeeEstimator:
    """Gas Fee 估算器"""
    
    def __init__(self):
        self.etherscan_api = "https://api.etherscan.io/api"
    
    def get_gas_price(self, chain: str = "Ethereum") -> float:
        """
        獲取當前 Gas 價格
        
        Args:
            chain: 區塊鏈名稱
        
        Returns:
            Gas 價格（Gwei）
        """
        # 不同鏈的 Gas 價格估算
        gas_prices = {
            "Ethereum": 30.0,    # Gwei
            "Arbitrum": 0.1,
            "Optimism": 0.001,
            "Base": 0.001,
            "Polygon": 50.0,
            "BSC": 3.0,
            "Avalanche": 25.0,
            "Fantom": 50.0,
        }
        
        return gas_prices.get(chain, 30.0)
    
    def estimate_total_gas_cost(
        self,
        chain: str,
        eth_price: float
    ) -> Dict:
        """
        估算總 Gas 成本
        
        Args:
            chain: 區塊鏈名稱
            eth_price: ETH 價格
        
        Returns:
            Gas 成本估算
        """
        # Gas 操作估算（Gas units）
        operations = {
            "approve_tokens": 50000,
            "add_liquidity": 200000,
            "remove_liquidity": 150000,
            "open_short": 100000,
            "close_short": 80000,
        }
        
        # 獲取 Gas 價格
        gas_price_gwei = self.get_gas_price(chain)
        
        # 計算每個操作的成本
        costs = {}
        total_gas_units = 0
        
        for op, units in operations.items():
            total_gas_units += units
            gas_cost_eth = (units * gas_price_gwei) / 1e9
            gas_cost_usd = gas_cost_eth * eth_price
            costs[op] = {
                "gas_units": units,
                "cost_eth": gas_cost_eth,
                "cost_usd": gas_cost_usd
            }
        
        # 總成本
        total_cost_eth = (total_gas_units * gas_price_gwei) / 1e9
        total_cost_usd = total_cost_eth * eth_price
        
        # 年化成本（假設每月轉倉一次）
        annual_cost_usd = total_cost_usd * 12
        
        return {
            "chain": chain,
            "gas_price_gwei": gas_price_gwei,
            "total_gas_units": total_gas_units,
            "total_cost_eth": total_cost_eth,
            "total_cost_usd": total_cost_usd,
            "annual_cost_usd": annual_cost_usd,
            "operations": costs
        }


class LALSmartSearchV3:
    """LAL 智能搜尋服務 V3（整合 IL 計算）"""
    
    def __init__(self):
        self.davis_analyzer = DavisDoubleClickAnalyzer()
        self.data_aggregator = UnifiedDataAggregator()
        self.dn_calculator = DeltaNeutralCalculator()
        self.gas_estimator = GasFeeEstimator()
        self.il_calculator = ILCalculator()  # 新增
    
    def search(
        self,
        token: str = "ETH",
        capital: float = 10000,
        risk_tolerance: str = "medium",
        min_tvl: float = 5_000_000,
        min_apy: float = 5.0,
        top_n: int = 5,
        hedge_params: HedgeParams = None  # 新增
    ) -> List[Dict]:
        """
        智能搜尋最佳 Delta Neutral 方案（考慮 IL）
        
        Args:
            token: 目標代幣
            capital: 投資資本
            risk_tolerance: 風險偏好（low/medium/high）
            min_tvl: 最小 TVL
            min_apy: 最小 APY
            top_n: 返回前 N 個方案
            hedge_params: 對沖參數
        
        Returns:
            最佳方案列表
        """
        if hedge_params is None:
            hedge_params = HedgeParams(hedge_ratio=1.0, rebalance_frequency_days=7)
        
        print(f"\n{'='*80}")
        print(f"🔍 LAL 智能搜尋服務 V3（整合 IL 計算）")
        print(f"{'='*80}")
        print(f"代幣: {token}")
        print(f"資本: ${capital:,.0f}")
        print(f"風險偏好: {risk_tolerance}")
        print(f"對沖比率: {hedge_params.hedge_ratio * 100:.0f}%")
        print(f"再平衡頻率: {hedge_params.rebalance_frequency_days} 天")
        print(f"{'='*80}\n")
        
        # 步驟 1: 戴維斯雙擊分析
        print("📊 步驟 1/6: 戴維斯雙擊分析...")
        davis_results = self.davis_analyzer.analyze_token_pools(
            token=token,
            min_tvl=min_tvl,
            min_apy=min_apy,
            top_n=20  # 取前 20 個進行後續分析
        )
        
        if not davis_results:
            print("❌ 未找到符合條件的池")
            return []
        
        print(f"✅ 找到 {len(davis_results)} 個優質池\n")
        
        # 步驟 2: 獲取資金費率
        print("💰 步驟 2/6: 獲取資金費率...")
        funding_rate_data = self.data_aggregator.get_funding_rate(token)
        
        if not funding_rate_data:
            print("⚠️  無法獲取資金費率，使用默認值")
            funding_apy = 10.0
            funding_rate_stats = None
        else:
            funding_apy = funding_rate_data["annualized_rate_pct"]
            funding_rate_stats = funding_rate_data  # 保存完整的統計數據
            print(f"✅ {token} 資金費率: {funding_apy:.2f}% (年化)\n")
        
        # 步驟 3: IL 分析（新增）
        print("🛡️  步驟 3/6: 無常損失（IL）分析...")
        opportunities = []
        
        for pool in davis_results:
            # 解析池中的代幣
            tokens = pool["symbol"].split("-")
            if len(tokens) != 2:
                continue
            
            token_a, token_b = tokens[0], tokens[1]
            
            # IL 分析
            il_analysis = self.il_calculator.analyze_il(
                token_a=token_a,
                token_b=token_b,
                capital=capital,
                hedge_params=hedge_params
            )
            
            # 計算總收益
            lp_apy = pool["apy"]
            total_apy = lp_apy + funding_apy
            
            # 估算 Gas 成本
            eth_price = self.data_aggregator.get_token_price(token)
            if eth_price:
                gas_cost = self.gas_estimator.estimate_total_gas_cost(
                    chain=pool["chain"],
                    eth_price=eth_price["price"]
                )
                annual_gas_cost = gas_cost["annual_cost_usd"]
            else:
                annual_gas_cost = 200  # 默認值
            
            # 計算調整後的淨收益（考慮 IL）
            profit_result = self.il_calculator.calculate_adjusted_net_profit(
                lp_apy=lp_apy,
                funding_apy=funding_apy,
                net_il_annual=il_analysis.net_il_annual,
                gas_cost_annual=annual_gas_cost,
                capital=capital
            )
            
            # ROI
            total_cost = annual_gas_cost + abs(il_analysis.il_impact_usd)
            roi = (profit_result["total_profit"] / total_cost) * 100 if total_cost > 0 else 0
            
            opportunities.append({
                "pool_id": pool["pool_id"],
                "protocol": pool["protocol"],
                "chain": pool["chain"],
                "symbol": pool["symbol"],
                "tvl": pool["tvl"],
                "lp_apy": lp_apy,
                "funding_apy": funding_apy,
                "total_apy": total_apy,
                
                # 資金費率統計（新增）
                "funding_rate_stats": funding_rate_stats if funding_rate_stats else None,
                
                # IL 分析（新增）
                "il_analysis": {
                    "pool_volatility": il_analysis.pool_volatility,
                    "expected_il_annual": il_analysis.expected_il_annual,
                    "hedge_effectiveness": il_analysis.hedge_effectiveness,
                    "net_il_annual": il_analysis.net_il_annual,
                    "il_impact_usd": il_analysis.il_impact_usd,
                    "il_risk_level": il_analysis.il_risk_level,
                    "volatility_level": il_analysis.volatility_level,
                    "hedge_quality": il_analysis.hedge_quality
                },
                
                # 成本
                "gas_cost_annual": annual_gas_cost,
                
                # 調整後的淨收益（考慮 IL）
                "adjusted_net_apy": profit_result["net_apy"],
                "adjusted_net_profit": profit_result["total_profit"],
                
                # 收益分解
                "profit_breakdown": {
                    "lp_profit": profit_result["lp_profit"],
                    "funding_cost": profit_result["funding_cost"],
                    "il_loss": profit_result["il_loss"],
                    "gas_cost": profit_result["gas_cost"],
                    "total": profit_result["total_profit"]
                },
                
                # 其他指標
                "roi": roi,
                "davis_score": pool["davis_score"],
                "davis_category": pool["category"]
            })
        
        print(f"✅ 完成 {len(opportunities)} 個配對方案（含 IL 分析）\n")
        
        # 步驟 4: 智能優化和排序
        print("🧠 步驟 4/6: 智能優化和排序...")
        
        # 風險偏好權重
        risk_weights = {
            "low": {"net_apy": 0.25, "davis": 0.25, "tvl": 0.3, "roi": 0.1, "il_risk": 0.1},
            "medium": {"net_apy": 0.35, "davis": 0.25, "tvl": 0.2, "roi": 0.1, "il_risk": 0.1},
            "high": {"net_apy": 0.45, "davis": 0.25, "tvl": 0.1, "roi": 0.1, "il_risk": 0.1}
        }
        
        weights = risk_weights.get(risk_tolerance, risk_weights["medium"])
        
        # 計算綜合評分
        for opp in opportunities:
            # 歸一化各項指標（0-100）
            norm_net_apy = min(100, opp["adjusted_net_apy"] * 2)  # 50% APY = 100 分
            norm_davis = opp["davis_score"]
            norm_tvl = min(100, (opp["tvl"] / 100_000_000) * 100)  # $100M = 100 分
            norm_roi = min(100, opp["roi"] / 10)  # 1000% ROI = 100 分
            
            # IL 風險評分（低風險 = 高分）
            il_risk_map = {"low": 100, "medium": 60, "high": 30}
            norm_il_risk = il_risk_map.get(opp["il_analysis"]["il_risk_level"], 60)
            
            # 綜合評分
            final_score = (
                norm_net_apy * weights["net_apy"] +
                norm_davis * weights["davis"] +
                norm_tvl * weights["tvl"] +
                norm_roi * weights["roi"] +
                norm_il_risk * weights["il_risk"]
            )
            
            opp["final_score"] = round(final_score, 2)
        
        # 排序
        opportunities.sort(key=lambda x: x["final_score"], reverse=True)
        
        print(f"✅ 評分完成\n")
        
        # 步驟 5: 選出前 N 個方案
        print(f"🎯 步驟 5/6: 選出前 {top_n} 個最佳方案...")
        top_opportunities = opportunities[:top_n]
        print(f"✅ 已選出 {len(top_opportunities)} 個方案\n")
        
        # 步驟 6: 生成報告
        print("📋 步驟 6/6: 生成報告...")
        self._print_report(top_opportunities, capital)
        
        return top_opportunities
    
    def _print_report(self, opportunities: List[Dict], capital: float):
        """打印報告"""
        print(f"\n{'='*80}")
        print(f"📊 LAL 智能搜尋報告（考慮 IL 影響）")
        print(f"{'='*80}\n")
        
        for i, opp in enumerate(opportunities, 1):
            print(f"方案 #{i}: {opp['protocol']} - {opp['symbol']} ({opp['chain']})")
            print(f"{'─'*80}")
            print(f"綜合評分: {opp['final_score']:.2f}/100")
            print(f"TVL: ${opp['tvl']:,.0f}")
            print(f"戴維斯評分: {opp['davis_score']}/100 ({opp['davis_category']})")
            print()
            
            print("收益分析:")
            print(f"  LP APY: {opp['lp_apy']:.2f}%")
            print(f"  資金費率 APY: {opp['funding_apy']:.2f}%")
            print(f"  總 APY: {opp['total_apy']:.2f}%")
            print(f"  ✅ 調整後淨 APY: {opp['adjusted_net_apy']:.2f}%")
            print()
            
            print("IL 分析:")
            il = opp["il_analysis"]
            print(f"  池波動率: {il['pool_volatility']:.1f}%")
            print(f"  預期 IL（無對沖）: {il['expected_il_annual']:.2f}%")
            print(f"  對沖有效性: {il['hedge_effectiveness'] * 100:.1f}%")
            print(f"  淨 IL（對沖後）: {il['net_il_annual']:.2f}%")
            print(f"  IL 影響: ${il['il_impact_usd']:,.2f}")
            print(f"  IL 風險等級: {il['il_risk_level']}")
            print(f"  對沖質量: {il['hedge_quality']}")
            print()
            
            print("收益分解:")
            breakdown = opp["profit_breakdown"]
            print(f"  LP 收益: ${breakdown['lp_profit']:,.2f}")
            print(f"  資金費率成本: ${breakdown['funding_cost']:,.2f}")
            print(f"  IL 損失: ${breakdown['il_loss']:,.2f}")
            print(f"  Gas 成本: ${breakdown['gas_cost']:,.2f}")
            print(f"  ✅ 總收益: ${breakdown['total']:,.2f}")
            print()
            
            print(f"ROI: {opp['roi']:.2f}%")
            print(f"預期年收益: ${opp['adjusted_net_profit']:,.2f}")
            print(f"{'='*80}\n")
        
        # 總結
        if opportunities:
            best = opportunities[0]
            print(f"💡 最佳方案: {best['protocol']} - {best['symbol']}")
            print(f"   調整後淨 APY: {best['adjusted_net_apy']:.2f}%")
            print(f"   預期年收益: ${best['adjusted_net_profit']:,.2f}")
            print(f"   IL 風險: {best['il_analysis']['il_risk_level']}")
            print(f"   對沖質量: {best['il_analysis']['hedge_quality']}")
            print(f"\n{'='*80}\n")


# 測試代碼
if __name__ == "__main__":
    search_service = LALSmartSearchV3()
    
    # 測試 1: 基礎搜尋（100% 對沖，每週再平衡）
    print("\n" + "="*80)
    print("測試 1: 基礎搜尋（100% 對沖，每週再平衡）")
    print("="*80)
    
    results = search_service.search(
        token="ETH",
        capital=10000,
        risk_tolerance="medium",
        min_tvl=5_000_000,
        min_apy=20,
        top_n=3,
        hedge_params=HedgeParams(hedge_ratio=1.0, rebalance_frequency_days=7)
    )
    
    # 測試 2: 不同對沖策略比較
    print("\n" + "="*80)
    print("測試 2: 不同對沖策略比較")
    print("="*80)
    
    hedge_strategies = [
        ("無對沖", HedgeParams(hedge_ratio=0.0, rebalance_frequency_days=30)),
        ("50% 對沖", HedgeParams(hedge_ratio=0.5, rebalance_frequency_days=7)),
        ("100% 對沖（每週）", HedgeParams(hedge_ratio=1.0, rebalance_frequency_days=7)),
    ]
    
    for strategy_name, hedge_params in hedge_strategies:
        print(f"\n{strategy_name}:")
        print("-" * 80)
        results = search_service.search(
            token="ETH",
            capital=10000,
            risk_tolerance="medium",
            min_tvl=5_000_000,
            min_apy=20,
            top_n=1,
            hedge_params=hedge_params
        )
        
        if results:
            best = results[0]
            print(f"\n最佳方案: {best['symbol']}")
            print(f"調整後淨 APY: {best['adjusted_net_apy']:.2f}%")
            print(f"預期年收益: ${best['adjusted_net_profit']:,.2f}")
            print(f"IL 影響: ${best['il_analysis']['il_impact_usd']:,.2f}")

