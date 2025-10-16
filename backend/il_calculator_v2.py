"""
IL Calculator V2 - 兼容層
整合新的 DeltaNeutralCalculatorV2 到現有 API
"""

from typing import Dict, Optional
from dataclasses import dataclass
from delta_neutral_calculator_v2 import DeltaNeutralCalculatorV2, PoolConfig


@dataclass
class ILAnalysisV2:
    """IL 分析結果 V2 (兼容舊版 API)"""
    pool_volatility: float
    expected_il_annual: float
    hedge_effectiveness: float
    net_il_annual: float
    il_impact_usd: float
    il_risk_level: str
    volatility_level: str
    hedge_quality: str
    
    # V2 新增
    pool_type: str
    delta_a: float
    delta_b: float
    correlation_risk: float


@dataclass
class HedgeParamsV2:
    """對沖參數 V2"""
    hedge_ratio: float = 1.0
    rebalance_frequency_days: float = 7
    
    # V2 新增: 池配置
    weight_a: float = 0.5
    weight_b: float = 0.5
    price_lower: Optional[float] = None
    price_upper: Optional[float] = None
    current_price: Optional[float] = None


class ILCalculatorV2:
    """
    IL 計算器 V2
    
    整合 DeltaNeutralCalculatorV2,支持:
    - 任意池權重
    - 雙波動資產
    - 精確 Delta 計算
    """
    
    def __init__(self):
        self.dn_calc = DeltaNeutralCalculatorV2()
    
    def get_token_info(self, token: str):
        """獲取代幣資訊"""
        return self.dn_calc.get_token_info(token)
    
    def estimate_pool_volatility(self, token_a: str, token_b: str) -> float:
        """估算池波動率"""
        info_a = self.dn_calc.get_token_info(token_a)
        info_b = self.dn_calc.get_token_info(token_b)
        
        # 返回兩個代幣的波動率差異
        return abs(info_a.volatility - info_b.volatility)
    
    def analyze_il_with_hedge(
        self,
        token_a: str,
        token_b: str,
        capital: float,
        hedge_params: HedgeParamsV2
    ) -> ILAnalysisV2:
        """
        分析 IL 和對沖效果 (V2 版本)
        
        使用新的 DeltaNeutralCalculatorV2 進行精確計算
        """
        # 創建池配置
        pool_config = self.dn_calc.create_pool_config(
            token_a=token_a,
            token_b=token_b,
            weight_a=hedge_params.weight_a,
            weight_b=hedge_params.weight_b,
            price_lower=hedge_params.price_lower,
            price_upper=hedge_params.price_upper,
            current_price=hedge_params.current_price
        )
        
        # 計算 Delta Neutral 策略
        # 注意: 這裡只做分析,不計算實際收益
        # 實際收益由 calculate_adjusted_net_profit 計算
        result = self.dn_calc.calculate_delta_neutral_strategy(
            pool_config=pool_config,
            capital=capital,
            lp_apy=0.0,  # 暫時不計算,只分析 Delta
            funding_rate_a_apy=0.0,
            funding_rate_b_apy=0.0,
            hedge_ratio=hedge_params.hedge_ratio,
            gas_cost_annual=0.0
        )
        
        # 池波動率
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
        if result.hedge_effectiveness >= 0.9:
            hedge_quality = "優秀"
        elif result.hedge_effectiveness >= 0.7:
            hedge_quality = "良好"
        else:
            hedge_quality = "一般"
        
        # 在完美對沖下,IL 影響接近 0
        expected_il_annual = 0.0
        net_il_annual = 0.0
        il_impact_usd = 0.0
        
        return ILAnalysisV2(
            pool_volatility=pool_volatility,
            expected_il_annual=expected_il_annual,
            hedge_effectiveness=result.hedge_effectiveness,
            net_il_annual=net_il_annual,
            il_impact_usd=il_impact_usd,
            il_risk_level=il_risk_level,
            volatility_level=volatility_level,
            hedge_quality=hedge_quality,
            # V2 新增
            pool_type=result.pool_type.value,
            delta_a=result.delta_a,
            delta_b=result.delta_b,
            correlation_risk=result.correlation_risk
        )
    
    def calculate_adjusted_net_profit(
        self,
        token_a: str,
        token_b: str,
        lp_apy: float,
        funding_rate_a_apy: float,
        funding_rate_b_apy: float,
        gas_cost_annual: float,
        capital: float,
        hedge_params: HedgeParamsV2
    ) -> Dict[str, float]:
        """
        計算調整後的淨收益 (V2 版本)
        
        使用新的 DeltaNeutralCalculatorV2 進行精確計算
        """
        # 創建池配置
        pool_config = self.dn_calc.create_pool_config(
            token_a=token_a,
            token_b=token_b,
            weight_a=hedge_params.weight_a,
            weight_b=hedge_params.weight_b,
            price_lower=hedge_params.price_lower,
            price_upper=hedge_params.price_upper,
            current_price=hedge_params.current_price
        )
        
        # 計算 Delta Neutral 策略
        result = self.dn_calc.calculate_delta_neutral_strategy(
            pool_config=pool_config,
            capital=capital,
            lp_apy=lp_apy,
            funding_rate_a_apy=funding_rate_a_apy,
            funding_rate_b_apy=funding_rate_b_apy,
            hedge_ratio=hedge_params.hedge_ratio,
            gas_cost_annual=gas_cost_annual
        )
        
        # 轉換為舊版 API 格式 (向後兼容)
        return {
            "lp_profit": result.profit_breakdown["lp_profit"],
            "funding_cost_a": result.profit_breakdown["funding_cost_a"],
            "funding_cost_b": result.profit_breakdown["funding_cost_b"],
            "funding_cost": result.profit_breakdown["total_funding_cost"],
            "il_loss": 0.0,  # 在新邏輯中,IL 已被對沖抵消
            "gas_cost": result.profit_breakdown["gas_cost"],
            "total_profit": result.profit_breakdown["total"],
            "net_apy": result.net_apy,
            
            # V2 新增字段
            "pool_type": result.pool_type.value,
            "delta_a": result.delta_a,
            "delta_b": result.delta_b,
            "hedge_amount_a_usd": result.hedge_amount_a_usd,
            "hedge_amount_b_usd": result.hedge_amount_b_usd,
            "volatility_exposure": result.volatility_exposure,
            "correlation_risk": result.correlation_risk,
            "hedge_effectiveness": result.hedge_effectiveness,
            "risk_level": result.risk_level
        }


# 向後兼容: 提供舊版函數接口
def calculate_adjusted_net_profit(
    lp_apy: float,
    funding_apy: float,
    net_il_annual: float,  # 忽略此參數
    gas_cost_annual: float,
    capital: float,
    hedge_ratio: float = 1.0,
    token_a: str = "ETH",
    token_b: str = "USDC",
    weight_a: float = 0.5,
    weight_b: float = 0.5
) -> Dict[str, float]:
    """
    向後兼容的函數接口
    
    新增參數:
    - token_a, token_b: 代幣符號
    - weight_a, weight_b: 池權重
    """
    calc = ILCalculatorV2()
    
    hedge_params = HedgeParamsV2(
        hedge_ratio=hedge_ratio,
        weight_a=weight_a,
        weight_b=weight_b
    )
    
    # 根據池類型決定資金費率分配
    token_a_info = calc.get_token_info(token_a)
    token_b_info = calc.get_token_info(token_b)
    
    if token_a_info.is_stable:
        funding_rate_a_apy = 0.0
        funding_rate_b_apy = funding_apy
    elif token_b_info.is_stable:
        funding_rate_a_apy = funding_apy
        funding_rate_b_apy = 0.0
    else:
        # 雙波動資產: 平均分配
        funding_rate_a_apy = funding_apy
        funding_rate_b_apy = funding_apy
    
    return calc.calculate_adjusted_net_profit(
        token_a=token_a,
        token_b=token_b,
        lp_apy=lp_apy,
        funding_rate_a_apy=funding_rate_a_apy,
        funding_rate_b_apy=funding_rate_b_apy,
        gas_cost_annual=gas_cost_annual,
        capital=capital,
        hedge_params=hedge_params
    )

