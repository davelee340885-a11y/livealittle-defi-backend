"""
IL Calculator 兼容層

提供與舊版 ILCalculator 相同的 API,但使用新的 DeltaNeutralCalculator
"""

from typing import Dict, Tuple
from dataclasses import dataclass
from il_calculator import DeltaNeutralCalculator


@dataclass
class ILAnalysis:
    """IL 分析結果 (兼容舊版)"""
    pool_volatility: float
    expected_il_annual: float
    hedge_effectiveness: float
    net_il_annual: float
    il_impact_usd: float
    il_risk_level: str
    volatility_level: str
    hedge_quality: str


@dataclass
class HedgeParams:
    """對沖參數 (兼容舊版)"""
    hedge_ratio: float = 1.0
    rebalance_frequency_days: float = 7


class ILCalculator:
    """
    IL 計算器 (兼容層)
    
    提供與舊版相同的 API,內部使用新的 DeltaNeutralCalculator
    """
    
    def __init__(self):
        self.dn_calc = DeltaNeutralCalculator()
    
    def get_token_volatility(self, token: str) -> float:
        """獲取代幣波動率"""
        return self.dn_calc.get_token_volatility(token)
    
    def estimate_pool_volatility(self, token_a: str, token_b: str) -> float:
        """估算池波動率"""
        vol_a = self.dn_calc.get_token_volatility(token_a)
        vol_b = self.dn_calc.get_token_volatility(token_b)
        
        # 簡化模型: 兩個代幣的波動率差異
        return abs(vol_a - vol_b)
    
    def analyze_il_with_hedge(
        self,
        token_a: str,
        token_b: str,
        capital: float,
        hedge_params: HedgeParams
    ) -> ILAnalysis:
        """
        分析 IL 和對沖效果 (兼容舊版 API)
        
        注意: 在新的 Delta Neutral 邏輯中,IL 已經被對沖抵消
        這個函數主要用於風險評估,不再用於收益計算
        """
        pool_volatility = self.estimate_pool_volatility(token_a, token_b)
        
        # 風險等級評估
        if pool_volatility < 20:
            il_risk_level = "低"
            volatility_level = "低"
        elif pool_volatility < 50:
            il_risk_level = "中"
            volatility_level = "中"
        else:
            il_risk_level = "高"
            volatility_level = "高"
        
        # 對沖質量評估
        if hedge_params.hedge_ratio >= 0.9:
            hedge_quality = "優秀"
            hedge_effectiveness = 0.95
        elif hedge_params.hedge_ratio >= 0.7:
            hedge_quality = "良好"
            hedge_effectiveness = 0.85
        else:
            hedge_quality = "一般"
            hedge_effectiveness = 0.70
        
        # 在完美對沖下,IL 影響接近 0
        expected_il_annual = 0.0
        net_il_annual = 0.0
        il_impact_usd = 0.0
        
        return ILAnalysis(
            pool_volatility=pool_volatility,
            expected_il_annual=expected_il_annual,
            hedge_effectiveness=hedge_effectiveness,
            net_il_annual=net_il_annual,
            il_impact_usd=il_impact_usd,
            il_risk_level=il_risk_level,
            volatility_level=volatility_level,
            hedge_quality=hedge_quality
        )
    
    def calculate_adjusted_net_profit(
        self,
        lp_apy: float,
        funding_apy: float,
        net_il_annual: float,  # 忽略此參數,保持 API 兼容
        gas_cost_annual: float,
        capital: float,
        hedge_ratio: float = 1.0
    ) -> Dict[str, float]:
        """
        計算調整後的淨收益 (兼容舊版 API)
        
        新邏輯: 淨收益 = LP 手續費 - 資金費率成本 - Gas 成本
        (不再單獨扣除 IL,因為 IL 已經被對沖抵消)
        """
        # 使用新的 Delta Neutral 計算器
        result = self.dn_calc.calculate_delta_neutral_pnl(
            capital=capital,
            lp_apy=lp_apy,
            funding_apy=funding_apy,
            hedge_ratio=hedge_ratio,
            rebalance_frequency_days=7,
            chain="ethereum"
        )
        
        # 轉換為舊版 API 格式
        return {
            "lp_profit": result.profit_breakdown["lp_profit"],
            "funding_cost": result.profit_breakdown["funding_cost"],
            "il_loss": 0.0,  # 在新邏輯中,IL 已被對沖抵消
            "gas_cost": result.profit_breakdown["gas_cost"],
            "total_profit": result.profit_breakdown["total"],
            "net_apy": result.net_apy
        }

