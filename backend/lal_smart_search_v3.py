"""
LAL 智能搜尋服務 V3 (整合 V2 評分系統)
整合戴維斯雙擊分析、Delta Neutral 配對、IL 計算、成本效益計算和V2評分引擎
"""

from typing import Dict, List, Optional
from datetime import datetime
import requests

# 導入現有模組
from davis_double_click_analyzer_v2 import DavisDoubleClickAnalyzerV2
from unified_data_aggregator import UnifiedDataAggregator
from delta_neutral_calculator import DeltaNeutralCalculator
from il_calculator_v2 import ILCalculatorV2, HedgeParamsV2
from pool_parser import PoolParser
from pool_url_generator import generate_pool_url, generate_protocol_direct_link

# 導入 V2 評分引擎
from scoring_engine_v2 import ScoringEngineV2


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
    """LAL 智能搜尋服務 V3（整合 IL 計算和 V2 評分系統）"""
    
    def __init__(self):
        self.davis_analyzer = DavisDoubleClickAnalyzerV2()
        self.data_aggregator = UnifiedDataAggregator()
        self.dn_calculator = DeltaNeutralCalculator()
        self.gas_estimator = GasFeeEstimator()
        self.il_calculator = ILCalculatorV2()  # V2 計算器
        self.pool_parser = PoolParser()  # 池解析器
        self.scoring_engine_v2 = ScoringEngineV2()  # V2 評分引擎
    
    def _build_tooltip_data(
        self,
        opportunity: Dict,
        score_result: Dict,
        token_a: str,
        token_b: str
    ) -> Dict:
        """
        構建tooltip所需的數據結構
        
        Args:
            opportunity: 機會數據
            score_result: V2評分結果
            token_a: 代幣A符號
            token_b: 代幣B符號
        
        Returns:
            Tooltip數據
        """
        liquidity_data = opportunity.get("liquidity_data", {})
        hedgeability_data = opportunity.get("hedgeability_data", {})
        
        return {
            "total_score": score_result["final_score"],
            "grade": score_result["grade"],
            "risk_profile": "平衡型",
            "passed_threshold": True,
            "dimensions": [
                {
                    "id": "yield",
                    "name": "淨收益",
                    "icon": "💰",
                    "score": score_result["component_scores"]["yield"],
                    "weight": int(score_result["weights"]["yield"] * 100),
                    "contribution": score_result["component_scores"]["yield"] * score_result["weights"]["yield"],
                    "description": "調整後淨APY和ROI的綜合評估",
                    "details": [
                        {"label": "當前 APY", "value": f"{opportunity.get('adjusted_net_apy', 0):.2f}%"},
                        {"label": "歷史 ROI", "value": f"{opportunity.get('roi', 0):.0f}%"}
                    ]
                },
                {
                    "id": "growth",
                    "name": "增長潛力",
                    "icon": "📈",
                    "score": score_result["component_scores"]["growth"],
                    "weight": int(score_result["weights"]["growth"] * 100),
                    "contribution": score_result["component_scores"]["growth"] * score_result["weights"]["growth"],
                    "description": "戴維斯雙擊機會評估",
                    "details": [
                        {"label": "戴維斯評分", "value": f"{opportunity.get('davis_score', 0):.1f} 分"}
                    ]
                },
                {
                    "id": "liquidity",
                    "name": "流動性",
                    "icon": "💧",
                    "score": score_result["component_scores"]["liquidity"],
                    "weight": int(score_result["weights"]["liquidity"] * 100),
                    "contribution": score_result["component_scores"]["liquidity"] * score_result["weights"]["liquidity"],
                    "description": "現貨市場的交易量和深度",
                    "grade": liquidity_data.get("grade", "N/A"),
                    "details": [
                        {"label": f"{token_a} 24h交易量", "value": f"${liquidity_data.get('token_a_volume_24h', 0)/1e9:.1f}B"},
                        {"label": f"{token_b} 24h交易量", "value": f"${liquidity_data.get('token_b_volume_24h', 0)/1e9:.1f}B"},
                        {"label": "綜合評級", "value": f"{liquidity_data.get('grade', 'N/A')}級"}
                    ]
                },
                {
                    "id": "hedgeability",
                    "name": "可對沖性",
                    "icon": "🛡️",
                    "score": score_result["component_scores"]["hedgeability"],
                    "weight": int(score_result["weights"]["hedgeability"] * 100),
                    "contribution": score_result["component_scores"]["hedgeability"] * score_result["weights"]["hedgeability"],
                    "description": "永續合約的可用性和成本",
                    "grade": hedgeability_data.get("grade", "N/A"),
                    "details": [
                        {"label": f"{token_a} 永續合約", "value": f"{hedgeability_data.get('token_a_score', 0):.0f}分"},
                        {"label": f"{token_b} 永續合約", "value": f"{hedgeability_data.get('token_b_score', 0):.0f}分"},
                        {"label": "綜合評級", "value": f"{hedgeability_data.get('grade', 'N/A')}級"}
                    ]
                },
                {
                    "id": "security",
                    "name": "協議安全",
                    "icon": "🔒",
                    "score": score_result["component_scores"]["security"],
                    "weight": int(score_result["weights"]["security"] * 100),
                    "contribution": score_result["component_scores"]["security"] * score_result["weights"]["security"],
                    "description": "智能合約和協議層面的安全性",
                    "grade": opportunity.get("security_grade", "N/A"),
                    "details": [
                        {"label": "協議", "value": opportunity.get("protocol", "Unknown")},
                        {"label": "安全評分", "value": f"{opportunity.get('security_score', 0):.2f}/100"},
                        {"label": "評級", "value": f"{opportunity.get('security_grade', 'N/A')}級"}
                    ]
                },
                {
                    "id": "scale",
                    "name": "規模信任",
                    "icon": "📊",
                    "score": score_result["component_scores"]["scale"],
                    "weight": int(score_result["weights"]["scale"] * 100),
                    "contribution": score_result["component_scores"]["scale"] * score_result["weights"]["scale"],
                    "description": "TVL規模和市場信任度",
                    "details": [
                        {"label": "當前 TVL", "value": f"${opportunity.get('tvl', 0)/1e6:.2f}M"},
                        {"label": "規模評分", "value": f"{score_result['component_scores']['scale']:.1f} 分"}
                    ]
                }
            ],
            "summary": {
                "risk_control_weight": 50,
                "risk_control_dimensions": ["流動性", "可對沖性", "協議安全"],
                "risk_control_contribution": (
                    score_result["component_scores"]["liquidity"] * score_result["weights"]["liquidity"] +
                    score_result["component_scores"]["hedgeability"] * score_result["weights"]["hedgeability"] +
                    score_result["component_scores"]["security"] * score_result["weights"]["security"]
                ),
                "highlights": self._generate_highlights(opportunity, liquidity_data, hedgeability_data)
            }
        }
    
    def _generate_highlights(
        self,
        opportunity: Dict,
        liquidity_data: Dict,
        hedgeability_data: Dict
    ) -> List[str]:
        """生成評估亮點"""
        highlights = []
        
        liquidity_grade = liquidity_data.get("grade", "F")
        if liquidity_grade in ["A", "B"]:
            highlights.append(f"✅ 流動性優秀 ({liquidity_grade}級)")
        else:
            highlights.append(f"⚠️ 流動性偏低 ({liquidity_grade}級)")
        
        hedgeability_grade = hedgeability_data.get("grade", "F")
        if hedgeability_grade in ["A", "B"]:
            highlights.append(f"✅ 可對沖性優秀 ({hedgeability_grade}級)")
        else:
            highlights.append(f"⚠️ 可對沖性偏低 ({hedgeability_grade}級)")
        
        security_grade = opportunity.get("security_grade", "F")
        if security_grade in ["A", "B"]:
            highlights.append(f"✅ 協議安全優秀 ({security_grade}級)")
        else:
            highlights.append(f"⚠️ 協議安全偏低 ({security_grade}級)")
        
        return highlights
    
    def search(
        self,
        token: str = "ETH",
        capital: float = 10000,
        risk_tolerance: str = "medium",
        min_tvl: float = 5_000_000,
        min_apy: float = 5.0,
        top_n: int = 5,
        hedge_params: HedgeParamsV2 = None,
        use_v2_scoring: bool = True  # 是否使用V2評分排序
    ) -> List[Dict]:
        """
        智能搜尋最佳 Delta Neutral 方案（考慮 IL 和 V2 評分）
        
        Args:
            token: 目標代幣
            capital: 投資資本
            risk_tolerance: 風險偏好（low/medium/high）
            min_tvl: 最小 TVL
            min_apy: 最小 APY
            top_n: 返回前 N 個方案
            hedge_params: 對沖參數
            use_v2_scoring: 是否使用V2評分排序（默認True）
        
        Returns:
            最佳方案列表
        """
        if hedge_params is None:
            hedge_params = HedgeParamsV2(hedge_ratio=1.0, rebalance_frequency_days=7)
        
        print(f"\n{'='*80}")
        print(f"🔍 LAL 智能搜尋服務 V3（整合 V2 評分系統）")
        print(f"{'='*80}")
        print(f"代幣: {token}")
        print(f"資本: ${capital:,.0f}")
        print(f"風險偏好: {risk_tolerance}")
        print(f"對沖比率: {hedge_params.hedge_ratio * 100:.0f}%")
        print(f"再平衡頻率: {hedge_params.rebalance_frequency_days} 天")
        print(f"使用V2評分: {'是' if use_v2_scoring else '否'}")
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
            try:
                # 使用池解析器解析池配置
                pool_info = self.pool_parser.parse_pool(
                    symbol=pool["symbol"],
                    protocol=pool["protocol"],
                    pool_data=pool.get("metadata", {})
                )
                
                token_a = pool_info.token_a
                token_b = pool_info.token_b
                
                # 如果沒有價格範圍,估算一個
                if not pool_info.price_lower and pool_info.current_price:
                    pool_info.price_lower, pool_info.price_upper = self.pool_parser.estimate_price_range(
                        pool_info.current_price,
                        range_pct=10.0
                    )
                
                # 獲取雙幣種資金費率
                funding_rates = self.data_aggregator.get_multiple_funding_rates([token_a, token_b])
                funding_rate_a_apy = funding_rates.get(token_a, {}).get("annualized_rate_pct", 0.0)
                funding_rate_b_apy = funding_rates.get(token_b, {}).get("annualized_rate_pct", 0.0)
                
                # 計算總收益
                lp_apy = pool["apy"]
                
                # 估算 Gas 成本（根據鏈和再平衡頻率）
                rebalances_per_year = 365 / hedge_params.rebalance_frequency_days
                
                # 不同鏈的單次再平衡成本（USD）
                chain_gas_costs = {
                    "Ethereum": 20.0,
                    "Arbitrum": 0.2,
                    "Optimism": 0.1,
                    "Base": 0.1,
                    "Polygon": 0.5,
                    "BSC": 0.3,
                    "Avalanche": 1.0,
                }
                
                single_rebalance_cost = chain_gas_costs.get(pool["chain"], 1.0)
                initial_setup_cost = single_rebalance_cost * 2  # 初始設置成本較高
                
                # 年化 Gas 成本 = 初始設置 + (單次成本 × 年度次數)
                annual_gas_cost = initial_setup_cost + (single_rebalance_cost * rebalances_per_year)
                
                # 創建 V2 對冲參數
                hedge_params_v2 = HedgeParamsV2(
                    hedge_ratio=hedge_params.hedge_ratio,
                    rebalance_frequency_days=hedge_params.rebalance_frequency_days,
                    weight_a=pool_info.weight_a,
                    weight_b=pool_info.weight_b,
                    current_price=pool_info.current_price,
                    price_lower=pool_info.price_lower,
                    price_upper=pool_info.price_upper
                )
                
                # IL 分析 (V2)
                il_analysis = self.il_calculator.analyze_il_with_hedge(
                    token_a=token_a,
                    token_b=token_b,
                    capital=capital,
                    hedge_params=hedge_params_v2
                )
                
                # 計算調整後的淨收益 (V2)
                profit_result = self.il_calculator.calculate_adjusted_net_profit(
                    token_a=token_a,
                    token_b=token_b,
                    lp_apy=lp_apy,
                    funding_rate_a_apy=funding_rate_a_apy,
                    funding_rate_b_apy=funding_rate_b_apy,
                    gas_cost_annual=annual_gas_cost,
                    capital=capital,
                    hedge_params=hedge_params_v2
                )
                
            except Exception as e:
                print(f"⚠️  處理池 {pool['symbol']} 時發生錯誤: {e}")
                continue
            
            # ROI
            total_cost = annual_gas_cost + abs(il_analysis.il_impact_usd)
            roi = (profit_result["total_profit"] / total_cost) * 100 if total_cost > 0 else 0
            
            # 計算總 APY (雙幣種資金費率)
            total_funding_apy = funding_rate_a_apy + funding_rate_b_apy
            total_apy = lp_apy - total_funding_apy
            
            # 生成外部連結（雙連結策略）
            external_url = generate_pool_url(
                pool_id=pool["pool_id"],
                protocol=pool["protocol"],
                chain=pool["chain"],
                symbol=pool["symbol"],
                pool_address=pool.get("pool_address", "")  # 傳遞實際的池地址
            )
            
            # 生成協議直連（用於前端的「在協議上操作」按鈕）
            protocol_url = generate_protocol_direct_link(
                protocol=pool["protocol"],
                chain=pool["chain"]
            )
            
            opportunities.append({
                "pool_id": pool["pool_id"],
                "protocol": pool["protocol"],
                "chain": pool["chain"],
                "symbol": pool["symbol"],
                "external_url": external_url,  # DefiLlama 池頁面（主要連結）
                "protocol_url": protocol_url,  # 協議直連（備用連結）
                "tvl": pool["tvl"],
                "lp_apy": lp_apy,
                
                # V2: 雙幣種資金費率
                "funding_rate_a_apy": funding_rate_a_apy,
                "funding_rate_b_apy": funding_rate_b_apy,
                "total_funding_apy": total_funding_apy,
                "total_apy": total_apy,
                
                # V2: 池配置
                "pool_type": profit_result.get("pool_type", "unknown"),
                "weight_a": pool_info.weight_a,
                "weight_b": pool_info.weight_b,
                "fee_tier": pool_info.fee_tier if hasattr(pool_info, 'fee_tier') else pool.get('poolMeta', '').split('-')[-1] if '-' in pool.get('poolMeta', '') else None,
                
                # V2: Delta 資訊
                "delta_a": profit_result.get("delta_a", 0),
                "delta_b": profit_result.get("delta_b", 0),
                "hedge_amount_a_usd": profit_result.get("hedge_amount_a_usd", 0),
                "hedge_amount_b_usd": profit_result.get("hedge_amount_b_usd", 0),
                
                # IL 分析（V2 增強）
                "il_analysis": {
                    "pool_volatility": il_analysis.pool_volatility,
                    "expected_il_annual": il_analysis.expected_il_annual,
                    "hedge_effectiveness": il_analysis.hedge_effectiveness,
                    "net_il_annual": il_analysis.net_il_annual,
                    "il_impact_usd": il_analysis.il_impact_usd,
                    "il_risk_level": il_analysis.il_risk_level,
                    "volatility_level": il_analysis.volatility_level,
                    "hedge_quality": il_analysis.hedge_quality,
                    # V2 新增
                    "pool_type": il_analysis.pool_type,
                    "delta_a": il_analysis.delta_a,
                    "delta_b": il_analysis.delta_b,
                    "correlation_risk": il_analysis.correlation_risk
                },
                
                # 成本
                "gas_cost_annual": annual_gas_cost,
                "gas_cost_details": {
                    "rebalances_per_year": int(rebalances_per_year),
                    "single_rebalance_cost": single_rebalance_cost,
                    "initial_setup_cost": initial_setup_cost,
                    "chain": pool["chain"]
                },
                
                # 調整後的淨收益（考慮 IL）
                "adjusted_net_apy": profit_result["net_apy"],
                "adjusted_net_profit": profit_result["total_profit"],
                
                # 收益分解 (V2 增強)
                "profit_breakdown": {
                    "lp_profit": profit_result["lp_profit"],
                    "funding_cost_a": profit_result.get("funding_cost_a", 0),
                    "funding_cost_b": profit_result.get("funding_cost_b", 0),
                    "funding_cost": profit_result["funding_cost"],
                    "il_loss": profit_result["il_loss"],
                    "gas_cost": profit_result["gas_cost"],
                    "total": profit_result["total_profit"]
                },
                
                # V2: 風險評估
                "volatility_exposure": profit_result.get("volatility_exposure", 0),
                "correlation_risk": profit_result.get("correlation_risk", 0),
                "risk_level": profit_result.get("risk_level", "unknown"),
                
                # 其他指標
                "roi": roi,
                "davis_score": pool["davis_score"],
                "davis_category": pool["category"],
                
                # 戴維斯雙擊分析（新增）
                "signal": pool.get("signal", "未知"),
                "signal_strength": pool.get("signal_strength", "未知"),
                "recommendation": pool.get("recommendation", "需要分析"),
                "has_history": pool.get("has_history", False),
                "growth_rates": pool.get("growth_rates", {}),
                "analysis": pool.get("analysis", {})
            })
        
        print(f"✅ 完成 {len(opportunities)} 個配對方案（含 IL 分析）\n")
        
        # 步驟 4: 智能優化和排序（整合V2評分）
        print("🧠 步驟 4/6: 智能優化和排序（V1 + V2 評分）...")
        
        # V1 評分：風險偏好權重
        risk_weights = {
            "low": {"net_apy": 0.25, "davis": 0.25, "tvl": 0.3, "roi": 0.1, "il_risk": 0.1},
            "medium": {"net_apy": 0.35, "davis": 0.25, "tvl": 0.2, "roi": 0.1, "il_risk": 0.1},
            "high": {"net_apy": 0.45, "davis": 0.25, "tvl": 0.1, "roi": 0.1, "il_risk": 0.1}
        }
        
        weights = risk_weights.get(risk_tolerance, risk_weights["medium"])
        
        # 計算 V1 和 V2 評分
        for opp in opportunities:
            # ========== V1 評分 ==========
            # 歸一化各項指標（0-100）
            norm_net_apy = min(100, opp["adjusted_net_apy"] * 2)  # 50% APY = 100 分
            norm_davis = opp["davis_score"]
            norm_tvl = min(100, (opp["tvl"] / 100_000_000) * 100)  # $100M = 100 分
            norm_roi = min(100, opp["roi"] / 10)  # 1000% ROI = 100 分
            
            # IL 風險評分（低風險 = 高分）
            il_risk_map = {"low": 100, "medium": 60, "high": 30}
            norm_il_risk = il_risk_map.get(opp["il_analysis"]["il_risk_level"], 60)
            
            # V1 綜合評分
            final_score_v1 = (
                norm_net_apy * weights["net_apy"] +
                norm_davis * weights["davis"] +
                norm_tvl * weights["tvl"] +
                norm_roi * weights["roi"] +
                norm_il_risk * weights["il_risk"]
            )
            
            opp["final_score_v1"] = round(final_score_v1, 2)
            
            # ========== V2 評分 ==========
            try:
                # 提取代幣符號
                token_a, token_b = opp["symbol"].split("-")
                
                # 豐富機會數據（添加 V2 所需的字段）
                enriched_opp = self.scoring_engine_v2.enrich_opportunity_with_scores(
                    opp,
                    token_a,
                    token_b,
                    opp["protocol"]
                )
                
                # 應用最低門檻
                threshold_result = self.scoring_engine_v2.apply_minimum_thresholds(enriched_opp)
                
                # 無論是否通過門檻，都計算完整的評分數據
                score_result_v2 = self.scoring_engine_v2.calculate_comprehensive_score(
                    enriched_opp,
                    risk_profile="balanced"
                )
                
                # 如果未通過門檻，將passed_threshold設為False並添加失敗原因
                if not threshold_result["passed"]:
                    score_result_v2["passed_threshold"] = False
                    score_result_v2["failed_reasons"] = threshold_result.get("failures", [])
                    # 總分設為0（因為不推薦）
                    opp["final_score_v2"] = 0
                else:
                    opp["final_score_v2"] = score_result_v2["final_score"]
                
                # 構建完整的tooltip數據
                opp["scoring_v2"] = score_result_v2
            except Exception as e:
                print(f"⚠️  計算 V2 評分時發生錯誤 ({opp['symbol']}): {e}")
                opp["final_score_v2"] = 0
                opp["scoring_v2"] = {
                    "passed_threshold": False,
                    "error": str(e),
                    "total_score": 0,
                    "grade": "F"
                }
            
            # 設置默認排序評分
            if use_v2_scoring:
                opp["final_score"] = opp["final_score_v2"]
            else:
                opp["final_score"] = opp["final_score_v1"]
        
        # 排序（根據選擇的評分系統）
        opportunities.sort(key=lambda x: x["final_score"], reverse=True)
        
        print(f"✅ 評分完成（使用{'V2' if use_v2_scoring else 'V1'}評分排序）\n")
        
        # 步驟 5: 選出前 N 個方案
        print(f"🎯 步驟 5/6: 選出前 {top_n} 個最佳方案...")
        top_opportunities = opportunities[:top_n]
        print(f"✅ 已選出 {len(top_opportunities)} 個方案\n")
        
        # 步驟 6: 生成報告
        print("📋 步驟 6/6: 生成報告...")
        self._print_report(top_opportunities, capital, use_v2_scoring)
        
        return top_opportunities
    
    def _print_report(self, opportunities: List[Dict], capital: float, use_v2_scoring: bool):
        """打印報告"""
        print(f"\n{'='*80}")
        print(f"📊 LAL 智能搜尋報告（V2 評分系統）")
        print(f"{'='*80}\n")
        
        for i, opp in enumerate(opportunities, 1):
            print(f"方案 #{i}: {opp['protocol']} - {opp['symbol']} ({opp['chain']})")
            print(f"{'─'*80}")
            print(f"V1 評分: {opp['final_score_v1']:.2f}/100")
            print(f"V2 評分: {opp['final_score_v2']:.2f}/100 ({opp['scoring_v2'].get('grade', 'N/A')}級)")
            print(f"排序依據: {'V2' if use_v2_scoring else 'V1'} 評分")
            print(f"TVL: ${opp['tvl']:,.0f}")
            print(f"戴維斯評分: {opp['davis_score']}/100 ({opp['davis_category']})")
            print()
            
            print("收益分析:")
            print(f"  LP APY: {opp['lp_apy']:.2f}%")
            print(f"  資金費率 A APY: {opp.get('funding_rate_a_apy', 0):.2f}%")
            print(f"  資金費率 B APY: {opp.get('funding_rate_b_apy', 0):.2f}%")
            print(f"  總資金費率 APY: {opp.get('total_funding_apy', 0):.2f}%")
            print(f"  總 APY: {opp['total_apy']:.2f}%")
            print(f"  ✅ 調整後淨 APY: {opp['adjusted_net_apy']:.2f}%")
            print()
            
            if opp['scoring_v2'].get('passed_threshold', False):
                print("V2 評分詳情:")
                for dim in opp['scoring_v2']['dimensions']:
                    print(f"  {dim['icon']} {dim['name']}: {dim['score']:.1f}/100 (權重{dim['weight']}%, 貢獻{dim['contribution']:.2f}分)")
                print()
            else:
                print("V2 評分: 未通過最低門檻")
                if 'failed_reasons' in opp['scoring_v2']:
                    print(f"  失敗原因: {', '.join(opp['scoring_v2']['failed_reasons'])}")
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
            print(f"   V1 評分: {best['final_score_v1']:.2f}/100")
            print(f"   V2 評分: {best['final_score_v2']:.2f}/100 ({best['scoring_v2'].get('grade', 'N/A')}級)")
            print(f"   調整後淨 APY: {best['adjusted_net_apy']:.2f}%")
            print(f"   預期年收益: ${best['adjusted_net_profit']:,.2f}")
            print(f"   IL 風險: {best['il_analysis']['il_risk_level']}")
            print(f"   對沖質量: {best['il_analysis']['hedge_quality']}")
            print(f"\n{'='*80}\n")


# 測試代碼
if __name__ == "__main__":
    search_service = LALSmartSearchV3()
    
    # 測試: V2 評分系統
    print("\n" + "="*80)
    print("測試: V2 評分系統整合")
    print("="*80)
    
    results = search_service.search(
        token="ETH",
        capital=10000,
        risk_tolerance="medium",
        min_tvl=5_000_000,
        min_apy=20,
        top_n=3,
        hedge_params=HedgeParamsV2(hedge_ratio=1.0, rebalance_frequency_days=7),
        use_v2_scoring=True  # 使用 V2 評分排序
    )
    
    # 打印 V2 評分詳情
    if results:
        print("\n" + "="*80)
        print("V2 評分系統詳細報告")
        print("="*80)
        for i, result in enumerate(results, 1):
            print(f"\n方案 #{i}: {result['symbol']}")
            print(f"V2 評分: {result['final_score_v2']:.2f}/100")
            if result['scoring_v2'].get('passed_threshold', False):
                print("Tooltip 數據已生成 ✅")
                print(f"評級: {result['scoring_v2']['grade']}")
                print(f"風險控制貢獻: {result['scoring_v2']['summary']['risk_control_contribution']:.2f}分")
            else:
                print("未通過最低門檻 ❌")

