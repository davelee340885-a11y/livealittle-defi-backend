"""
LAL 智能搜尋服務
整合戴維斯雙擊分析、Delta Neutral 配對、成本效益計算
"""

from typing import Dict, List, Optional
from datetime import datetime
import requests

# 導入現有模組
from davis_double_click_analyzer import DavisDoubleClickAnalyzer
from unified_data_aggregator import UnifiedDataAggregator
from delta_neutral_calculator import DeltaNeutralCalculator


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


class LALSmartSearch:
    """LAL 智能搜尋服務"""
    
    def __init__(self):
        self.davis_analyzer = DavisDoubleClickAnalyzer()
        self.data_aggregator = UnifiedDataAggregator()
        self.dn_calculator = DeltaNeutralCalculator()
        self.gas_estimator = GasFeeEstimator()
    
    def search(
        self,
        token: str = "ETH",
        capital: float = 10000,
        risk_tolerance: str = "medium",
        min_tvl: float = 5_000_000,
        min_apy: float = 5.0,
        top_n: int = 5
    ) -> List[Dict]:
        """
        智能搜尋最佳 Delta Neutral 方案
        
        Args:
            token: 目標代幣
            capital: 投資資本
            risk_tolerance: 風險偏好（low/medium/high）
            min_tvl: 最小 TVL
            min_apy: 最小 APY
            top_n: 返回前 N 個方案
        
        Returns:
            最佳方案列表
        """
        print(f"\n{'='*80}")
        print(f"🔍 LAL 智能搜尋服務")
        print(f"{'='*80}")
        print(f"代幣: {token}")
        print(f"資本: ${capital:,.0f}")
        print(f"風險偏好: {risk_tolerance}")
        print(f"{'='*80}\n")
        
        # 步驟 1: 戴維斯雙擊分析
        print("📊 步驟 1/5: 戴維斯雙擊分析...")
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
        print("💰 步驟 2/5: 獲取資金費率...")
        funding_rate_data = self.data_aggregator.get_funding_rate(token)
        
        if not funding_rate_data:
            print("⚠️  無法獲取資金費率，使用默認值")
            funding_apy = 10.0
        else:
            funding_apy = funding_rate_data["annualized_rate_pct"]
            print(f"✅ {token} 資金費率: {funding_apy:.2f}% (年化)\n")
        
        # 步驟 3: Delta Neutral 配對和收益計算
        print("🎯 步驟 3/5: Delta Neutral 配對和收益計算...")
        opportunities = []
        
        for pool in davis_results:
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
            
            # 計算淨收益
            total_revenue = capital * (total_apy / 100)
            net_profit = total_revenue - annual_gas_cost
            net_apy = (net_profit / capital) * 100
            
            # ROI
            roi = (net_profit / annual_gas_cost) * 100 if annual_gas_cost > 0 else 0
            
            opportunities.append({
                "pool_id": pool["pool_id"],
                "protocol": pool["protocol"],
                "chain": pool["chain"],
                "symbol": pool["symbol"],
                "tvl": pool["tvl"],
                "lp_apy": lp_apy,
                "funding_apy": funding_apy,
                "total_apy": total_apy,
                "gas_cost_annual": annual_gas_cost,
                "net_apy": net_apy,
                "net_profit": net_profit,
                "roi": roi,
                "davis_score": pool["davis_score"],
                "davis_category": pool["category"]
            })
        
        print(f"✅ 完成 {len(opportunities)} 個配對方案\n")
        
        # 步驟 4: 智能優化和排序
        print("🧠 步驟 4/5: 智能優化和排序...")
        
        # 風險偏好權重
        risk_weights = {
            "low": {"net_apy": 0.3, "davis": 0.2, "tvl": 0.3, "roi": 0.2},
            "medium": {"net_apy": 0.4, "davis": 0.3, "tvl": 0.2, "roi": 0.1},
            "high": {"net_apy": 0.5, "davis": 0.3, "tvl": 0.1, "roi": 0.1}
        }
        
        weights = risk_weights.get(risk_tolerance, risk_weights["medium"])
        
        # 計算綜合評分
        for opp in opportunities:
            # 歸一化各項指標（0-100）
            norm_net_apy = min(100, opp["net_apy"] * 2)  # 50% APY = 100 分
            norm_davis = opp["davis_score"]
            norm_tvl = min(100, (opp["tvl"] / 100_000_000) * 100)  # $100M = 100 分
            norm_roi = min(100, opp["roi"] / 10)  # 1000% ROI = 100 分
            
            # 綜合評分
            final_score = (
                norm_net_apy * weights["net_apy"] +
                norm_davis * weights["davis"] +
                norm_tvl * weights["tvl"] +
                norm_roi * weights["roi"]
            )
            
            opp["final_score"] = round(final_score, 2)
        
        # 排序
        opportunities.sort(key=lambda x: x["final_score"], reverse=True)
        
        print(f"✅ 評分完成\n")
        
        # 步驟 5: 選出前 N 個方案
        print(f"🏆 步驟 5/5: 選出前 {top_n} 個最佳方案...")
        top_opportunities = opportunities[:top_n]
        
        print(f"✅ 完成！\n")
        
        return top_opportunities
    
    def generate_report(self, opportunities: List[Dict], capital: float) -> str:
        """
        生成詳細報告
        
        Args:
            opportunities: 機會列表
            capital: 投資資本
        
        Returns:
            報告文本
        """
        if not opportunities:
            return "無可用方案"
        
        report = []
        report.append("\n" + "="*80)
        report.append("🎯 LAL 智能搜尋結果報告")
        report.append("="*80 + "\n")
        
        for i, opp in enumerate(opportunities, 1):
            report.append(f"{'='*80}")
            report.append(f"方案 #{i}: {opp['protocol']} - {opp['symbol']}")
            report.append(f"{'='*80}")
            report.append(f"鏈: {opp['chain']}")
            report.append(f"TVL: ${opp['tvl']:,.0f}")
            report.append(f"\n💰 收益分析:")
            report.append(f"  LP APY: {opp['lp_apy']:.2f}%")
            report.append(f"  資金費率 APY: {opp['funding_apy']:.2f}%")
            report.append(f"  總 APY: {opp['total_apy']:.2f}%")
            report.append(f"  年化 Gas 成本: ${opp['gas_cost_annual']:,.0f}")
            report.append(f"  淨 APY: {opp['net_apy']:.2f}%")
            report.append(f"  預期淨收益: ${opp['net_profit']:,.0f}/年")
            report.append(f"\n📊 評分:")
            report.append(f"  戴維斯雙擊評分: {opp['davis_score']:.2f}/100 ({opp['davis_category']})")
            report.append(f"  綜合評分: {opp['final_score']:.2f}/100")
            report.append(f"  ROI: {opp['roi']:.0f}%")
            report.append(f"\n✅ 執行步驟:")
            report.append(f"  1. 在 {opp['protocol']} 添加 ${capital:,.0f} 到 {opp['symbol']} 池")
            report.append(f"  2. 在 Hyperliquid 開設 ${capital/2:,.0f} 空單")
            report.append(f"  3. 每週監控並根據需要調整")
            report.append("")
        
        return "\n".join(report)


# ==================== 測試代碼 ====================

if __name__ == "__main__":
    print("🧪 測試 LAL 智能搜尋服務\n")
    
    lal = LALSmartSearch()
    
    # 測試搜尋
    opportunities = lal.search(
        token="ETH",
        capital=10000,
        risk_tolerance="medium",
        min_tvl=10_000_000,
        min_apy=10.0,
        top_n=5
    )
    
    if opportunities:
        # 生成報告
        report = lal.generate_report(opportunities, 10000)
        print(report)
        
        # 摘要
        print("\n" + "="*80)
        print("📋 方案摘要")
        print("="*80 + "\n")
        
        for i, opp in enumerate(opportunities, 1):
            print(f"{i}. {opp['protocol']} - {opp['symbol']}")
            print(f"   綜合評分: {opp['final_score']:.2f}/100")
            print(f"   淨 APY: {opp['net_apy']:.2f}%")
            print(f"   預期年收益: ${opp['net_profit']:,.0f}")
            print()
    
    print("✅ 測試完成！")

