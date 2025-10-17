"""
LAL評分引擎 V2
整合流動性、可對沖性、協議安全性的綜合評分系統
"""

from typing import Dict, List, Optional
import math
from liquidity_scorer_optimized import LiquidityScorerOptimized as LiquidityScorer
from hedgeability_scorer import HedgeabilityScorer
from protocol_security_scorer import ProtocolSecurityScorer


class ScoringEngineV2:
    """LAL評分引擎 V2"""
    
    def __init__(self):
        self.liquidity_scorer = LiquidityScorer()
        self.hedgeability_scorer = HedgeabilityScorer()
        self.security_scorer = ProtocolSecurityScorer()
        
        # 風險偏好權重配置
        self.risk_weights = {
            "conservative": {  # 保守型
                "yield": 0.18,  # 20% - 2%
                "growth": 0.08,  # 10% - 2%
                "liquidity": 0.23,
                "hedgeability": 0.22,
                "security": 0.20,  # 15% + 5%（保守型更重視安全）
                "scale": 0.09  # 10% - 1%
            },
            "balanced": {  # 平衡型
                "yield": 0.28,  # 30% - 2%
                "growth": 0.13,  # 15% - 2%
                "liquidity": 0.18,
                "hedgeability": 0.17,
                "security": 0.15,  # 10% + 5%
                "scale": 0.09  # 10% - 1%
            },
            "aggressive": {  # 進取型
                "yield": 0.38,  # 40% - 2%
                "growth": 0.18,  # 20% - 2%
                "liquidity": 0.13,
                "hedgeability": 0.12,
                "security": 0.15,  # 10% + 5%
                "scale": 0.04  # 5% - 1%
            }
        }
    
    def apply_minimum_thresholds(self, opportunity: Dict) -> Dict:
        """
        應用最低准入門檻篩選
        
        Args:
            opportunity: 投資機會數據
        
        Returns:
            包含通過狀態和原因的字典
        """
        failures = []
        
        # 1. 檢查現貨流動性
        liquidity_data = opportunity.get("liquidity_data")
        if not liquidity_data or not liquidity_data.get("meets_minimum", False):
            failures.append("現貨流動性不足（需要24小時交易量 ≥ $5M）")
        
        # 2. 檢查TVL
        tvl = opportunity.get("tvl", 0)
        if tvl < 1_000_000:
            failures.append(f"TVL過低（${tvl:,.0f} < $1M）")
        
        # 3. 檢查可對沖性
        hedgeability_data = opportunity.get("hedgeability_data")
        if not hedgeability_data or not hedgeability_data.get("meets_minimum", False):
            failures.append("無法有效對沖（需要永續合約交易量 ≥ $1M）")
        
        # 4. 檢查協議安全性
        security_score = opportunity.get("security_score", 0)
        if security_score < 50:
            failures.append(f"協議安全性不足（{security_score}/100 < 50）")
        
        # 5. 檢查安全事件歷史
        has_major_incident = opportunity.get("has_major_security_incident", False)
        if has_major_incident:
            failures.append("18個月內有重大安全事件")
        
        return {
            "passed": len(failures) == 0,
            "failures": failures
        }
    
    def calculate_comprehensive_score(
        self,
        opportunity: Dict,
        risk_profile: str = "balanced"
    ) -> Dict:
        """
        計算綜合評分
        
        Args:
            opportunity: 投資機會數據
            risk_profile: 風險偏好 ("conservative", "balanced", "aggressive")
        
        Returns:
            綜合評分結果
        """
        # 獲取權重
        weights = self.risk_weights.get(risk_profile, self.risk_weights["balanced"])
        
        # 1. 淨收益評分 (30%)
        yield_score = self._calculate_yield_score(
            opportunity.get("adjusted_net_apy", 0),
            opportunity.get("roi", 0)
        )
        
        # 2. 增長潛力評分 (15%)
        growth_score = opportunity.get("davis_score", 0)
        
        # 3. 流動性評分 (15%)
        liquidity_score = opportunity.get("liquidity_data", {}).get("total_score", 0)
        
        # 4. 可對沖性評分 (15%)
        hedgeability_score = opportunity.get("hedgeability_data", {}).get("total_score", 0)
        
        # 5. 協議安全評分 (10%)
        security_score = opportunity.get("security_score", 0)
        
        # 6. 規模與信任評分 (10%)
        scale_score = self._calculate_scale_score(opportunity.get("tvl", 0))
        
        # 計算加權總分
        final_score = (
            yield_score * weights["yield"] +
            growth_score * weights["growth"] +
            liquidity_score * weights["liquidity"] +
            hedgeability_score * weights["hedgeability"] +
            security_score * weights["security"] +
            scale_score * weights["scale"]
        )
        
        # 評級
        grade = self._get_overall_grade(final_score)
        
        # 計算各維度的貢獻分數
        contributions = {
            "yield": round(yield_score * weights["yield"], 2),
            "growth": round(growth_score * weights["growth"], 2),
            "liquidity": round(liquidity_score * weights["liquidity"], 2),
            "hedgeability": round(hedgeability_score * weights["hedgeability"], 2),
            "security": round(security_score * weights["security"], 2),
            "scale": round(scale_score * weights["scale"], 2)
        }
        
        # 風險控制維度貢獻
        risk_control_contribution = contributions["liquidity"] + contributions["hedgeability"] + contributions["security"]
        
        # 構建dimensions數組（前端tooltip需要）
        dimensions = [
            {
                "name": "淨收益",
                "icon": "💰",
                "score": round(yield_score, 1),
                "weight": int(weights["yield"] * 100),
                "contribution": contributions["yield"],
                "grade": self._get_component_grade(yield_score)
            },
            {
                "name": "增長潛力",
                "icon": "📈",
                "score": round(growth_score, 1),
                "weight": int(weights["growth"] * 100),
                "contribution": contributions["growth"],
                "grade": self._get_component_grade(growth_score)
            },
            {
                "name": "流動性",
                "icon": "💧",
                "score": round(liquidity_score, 1),
                "weight": int(weights["liquidity"] * 100),
                "contribution": contributions["liquidity"],
                "grade": self._get_component_grade(liquidity_score)
            },
            {
                "name": "可對沖性",
                "icon": "🛡️",
                "score": round(hedgeability_score, 1),
                "weight": int(weights["hedgeability"] * 100),
                "contribution": contributions["hedgeability"],
                "grade": self._get_component_grade(hedgeability_score)
            },
            {
                "name": "協議安全",
                "icon": "🔒",
                "score": round(security_score, 1),
                "weight": int(weights["security"] * 100),
                "contribution": contributions["security"],
                "grade": self._get_component_grade(security_score)
            },
            {
                "name": "規模信任",
                "icon": "📊",
                "score": round(scale_score, 1),
                "weight": int(weights["scale"] * 100),
                "contribution": contributions["scale"],
                "grade": self._get_component_grade(scale_score)
            }
        ]
        
        # 評估亮點
        highlights = []
        if liquidity_score >= 80:
            highlights.append(f"流動性{self._get_component_grade(liquidity_score)}級")
        if hedgeability_score >= 80:
            highlights.append(f"可對沖性{self._get_component_grade(hedgeability_score)}級")
        if security_score >= 80:
            highlights.append(f"協議安全{self._get_component_grade(security_score)}級")
        if yield_score >= 80:
            highlights.append(f"高收益{self._get_component_grade(yield_score)}級")
        if growth_score >= 80:
            highlights.append(f"增長潛力{self._get_component_grade(growth_score)}級")
        
        return {
            "total_score": round(final_score, 2),
            "grade": grade,
            "passed_threshold": True,  # 如果到這裡說明已通過最低門檻
            "dimensions": dimensions,
            "summary": {
                "risk_control_weight": int((weights["liquidity"] + weights["hedgeability"] + weights["security"]) * 100),
                "risk_control_contribution": round(risk_control_contribution, 2)
            },
            "highlights": highlights,
            "risk_profile": risk_profile,
            # 保留舊格式以兼容
            "final_score": round(final_score, 2),
            "component_scores": {
                "yield": round(yield_score, 2),
                "growth": round(growth_score, 2),
                "liquidity": round(liquidity_score, 2),
                "hedgeability": round(hedgeability_score, 2),
                "security": round(security_score, 2),
                "scale": round(scale_score, 2)
            },
            "weights": weights
        }
    
    def _calculate_yield_score(self, net_apy: float, roi: float) -> float:
        """
        計算淨收益評分
        
        組合調整後淨APY和ROI
        """
        # APY歸一化 (80% APY = 100分)
        apy_score = min(100, (net_apy / 80) * 100)
        
        # ROI歸一化 (200% ROI = 100分)
        roi_score = min(100, (roi / 200) * 100)
        
        # 加權組合 (APY 70%, ROI 30%)
        return apy_score * 0.7 + roi_score * 0.3
    
    def _calculate_scale_score(self, tvl: float) -> float:
        """
        計算規模與信任評分
        
        使用對數尺度避免頭部效應過強
        $100M TVL ≈ 100分
        """
        if tvl <= 0:
            return 0
        
        # 對數尺度
        log_tvl = math.log10(tvl)
        score = min(100, (log_tvl / 8) * 100)
        
        return score
    

    
    def _get_component_grade(self, score: float) -> str:
        """
        獲取單個維度的評級
        """
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _get_overall_grade(self, score: float) -> str:
        """獲取總體評級"""
        if score >= 85:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 50:
            return "C"
        elif score >= 30:
            return "D"
        else:
            return "F"
    
    def enrich_opportunity_with_scores(
        self,
        opportunity: Dict,
        token_a_symbol: str,
        token_b_symbol: str,
        protocol: str
    ) -> Dict:
        """
        為投資機會添加所有評分數據
        
        Args:
            opportunity: 基礎投資機會數據
            token_a_symbol: 代幣A符號
            token_b_symbol: 代幣B符號
            protocol: 協議名稱
        
        Returns:
            豐富後的投資機會數據
        """
        # 1. 獲取流動性數據（代幣A和B的平均）
        liquidity_a = self.liquidity_scorer.get_token_liquidity_data(token_a_symbol)
        liquidity_b = self.liquidity_scorer.get_token_liquidity_data(token_b_symbol)
        
        # 計算平均流動性評分
        if liquidity_a and liquidity_b:
            score_a = self.liquidity_scorer.calculate_liquidity_score(liquidity_a)
            score_b = self.liquidity_scorer.calculate_liquidity_score(liquidity_b)
            
            avg_liquidity_score = {
                "total_score": (score_a["total_score"] + score_b["total_score"]) / 2,
                "volume_score": (score_a["volume_score"] + score_b["volume_score"]) / 2,
                "depth_score": (score_a["depth_score"] + score_b["depth_score"]) / 2,
                "spread_score": (score_a["spread_score"] + score_b["spread_score"]) / 2,
                "grade": score_a["grade"] if score_a["total_score"] < score_b["total_score"] else score_b["grade"],
                "meets_minimum": score_a["meets_minimum"] and score_b["meets_minimum"],
                "token_a": score_a,
                "token_b": score_b
            }
        else:
            avg_liquidity_score = {
                "total_score": 0,
                "meets_minimum": False,
                "grade": "F"
            }
        
        opportunity["liquidity_data"] = avg_liquidity_score
        
        # 2. 獲取可對沖性數據（只評估非穩定幣）
        is_stable_a = self.hedgeability_scorer.is_stablecoin(token_a_symbol)
        is_stable_b = self.hedgeability_scorer.is_stablecoin(token_b_symbol)
        
        # 穩定幣不需要對沖，給予滿分
        if is_stable_a:
            score_a = {
                "total_score": 100,
                "availability_score": 100,
                "funding_stability_score": 100,
                "exchange_coverage_score": 100,
                "tier": "穩定幣（不需對沖）",
                "grade": "A",
                "meets_minimum": True
            }
        else:
            hedgeability_a = self.hedgeability_scorer.get_perpetual_data(token_a_symbol)
            score_a = self.hedgeability_scorer.calculate_hedgeability_score(hedgeability_a) if hedgeability_a else {
                "total_score": 0,
                "meets_minimum": False,
                "tier": "不可對沖",
                "grade": "F"
            }
        
        if is_stable_b:
            score_b = {
                "total_score": 100,
                "availability_score": 100,
                "funding_stability_score": 100,
                "exchange_coverage_score": 100,
                "tier": "穩定幣（不需對沖）",
                "grade": "A",
                "meets_minimum": True
            }
        else:
            hedgeability_b = self.hedgeability_scorer.get_perpetual_data(token_b_symbol)
            score_b = self.hedgeability_scorer.calculate_hedgeability_score(hedgeability_b) if hedgeability_b else {
                "total_score": 0,
                "meets_minimum": False,
                "tier": "不可對沖",
                "grade": "F"
            }
        
        # 計算綜合可對沖性評分
        avg_hedgeability_score = {
            "total_score": (score_a["total_score"] + score_b["total_score"]) / 2,
            "availability_score": (score_a.get("availability_score", 100) + score_b.get("availability_score", 100)) / 2,
            "funding_stability_score": (score_a.get("funding_stability_score", 100) + score_b.get("funding_stability_score", 100)) / 2,
            "exchange_coverage_score": (score_a.get("exchange_coverage_score", 100) + score_b.get("exchange_coverage_score", 100)) / 2,
            "tier": score_a["tier"] if score_a["total_score"] < score_b["total_score"] else score_b["tier"],
            "grade": score_a["grade"] if score_a["total_score"] < score_b["total_score"] else score_b["grade"],
            "meets_minimum": score_a["meets_minimum"] and score_b["meets_minimum"],
            "token_a": score_a,
            "token_b": score_b,
            "token_a_is_stable": is_stable_a,
            "token_b_is_stable": is_stable_b
        }
        
        opportunity["hedgeability_data"] = avg_hedgeability_score
        
        # 3. 獲取協議安全評分
        # 獲取協議安全評分（需要額外參數，這裡使用默認值）
        security_result = self.security_scorer.calculate_security_score(
            protocol=protocol,
            tvl=opportunity.get("tvl", 0),
            maturity_days=730,  # 假設2年成熟度
            assets=["ETH", "USDC"]  # 簡化處理
        )
        opportunity["security_score"] = security_result["total_score"]
        opportunity["security_grade"] = security_result["grade"]
        opportunity["security_details"] = security_result
        
        # 4. 檢查安全事件歷史（模擬，實際應查詢數據庫）
        opportunity["has_major_security_incident"] = False  # 實際應查詢
        
        return opportunity


# 測試代碼
if __name__ == "__main__":
    engine = ScoringEngineV2()
    
    # 模擬一個投資機會
    mock_opportunity = {
        "protocol": "Uniswap V3",
        "symbol": "ETH-USDC",
        "chain": "Ethereum",
        "tvl": 50_000_000,
        "adjusted_net_apy": 25.5,
        "roi": 150,
        "davis_score": 75,
        "il_analysis": {
            "il_risk_level": "low"
        }
    }
    
    print("=" * 80)
    print("LAL評分引擎 V2 測試")
    print("=" * 80)
    
    # 豐富數據
    print("\n步驟1: 獲取流動性、可對沖性和安全性數據...")
    enriched = engine.enrich_opportunity_with_scores(
        mock_opportunity,
        "ETH",
        "USDC",
        "Uniswap V3"
    )
    
    print("✅ 數據獲取完成\n")
    
    # 應用最低門檻
    print("步驟2: 應用最低准入門檻...")
    threshold_result = engine.apply_minimum_thresholds(enriched)
    
    if threshold_result["passed"]:
        print("✅ 通過所有最低門檻\n")
    else:
        print("❌ 未通過最低門檻:")
        for failure in threshold_result["failures"]:
            print(f"  - {failure}")
        print()
    
    # 計算綜合評分
    if threshold_result["passed"]:
        print("步驟3: 計算綜合評分...")
        
        for profile in ["conservative", "balanced", "aggressive"]:
            print(f"\n風險偏好: {profile}")
            print("-" * 80)
            
            score_result = engine.calculate_comprehensive_score(enriched, profile)
            
            print(f"最終評分: {score_result['final_score']}/100 (等級: {score_result['grade']})")
            print("\n各維度得分:")
            for component, score in score_result["component_scores"].items():
                weight = score_result["weights"][component]
                print(f"  {component:15s}: {score:6.2f}/100 (權重: {weight*100:4.1f}%)")

