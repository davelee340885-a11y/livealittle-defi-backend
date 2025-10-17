"""
Delta Neutral 策略計算引擎 V2 (增強版)

支持:
1. 任意 LP 池權重配置 (不限於 50/50)
2. 雙波動資產池 (如 ETH-BTC, SOL-ETH)
3. 精確的 Delta 計算
4. 多資產對沖策略
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class PoolType(Enum):
    """LP 池類型"""
    STABLE_STABLE = "stable-stable"  # 穩定幣-穩定幣 (如 USDC-USDT)
    VOLATILE_STABLE = "volatile-stable"  # 波動資產-穩定幣 (如 ETH-USDC)
    VOLATILE_VOLATILE = "volatile-volatile"  # 波動資產-波動資產 (如 ETH-BTC)


# 代幣分類和波動率數據
TOKEN_CATEGORIES = {
    # 穩定幣 - 極低波動
    "stablecoins": {
        "tokens": ["USDC", "USDT", "DAI", "FRAX", "LUSD", "BUSD", "USDD", "TUSD", "USDP", "USDE"],
        "annual_volatility": 2.0,  # 2%
        "is_stable": True
    },
    
    # 主流代幣 - 中等波動
    "major": {
        "tokens": ["ETH", "WETH", "BTC", "WBTC", "stETH", "wstETH", "rETH", "cbETH"],
        "annual_volatility": 80.0,  # 80%
        "is_stable": False
    },
    
    # 大市值代幣 - 高波動
    "large_cap": {
        "tokens": ["BNB", "SOL", "WSOL", "MATIC", "AVAX", "WAVAX", "LINK", "UNI", "AAVE", "ARB", "OP"],
        "annual_volatility": 100.0,  # 100%
        "is_stable": False
    },
    
    # 中小市值代幣 - 極高波動
    "mid_small_cap": {
        "tokens": [],  # 其他所有代幣
        "annual_volatility": 150.0,  # 150%
        "is_stable": False
    }
}


@dataclass
class TokenInfo:
    """代幣資訊"""
    symbol: str
    volatility: float  # 年化波動率 (%)
    is_stable: bool  # 是否為穩定幣
    
    
@dataclass
class PoolConfig:
    """LP 池配置"""
    token_a: TokenInfo
    token_b: TokenInfo
    weight_a: float  # token_a 的權重 (0-1)
    weight_b: float  # token_b 的權重 (0-1)
    pool_type: PoolType
    
    # Uniswap V3 特定參數
    price_lower: Optional[float] = None  # 價格下限
    price_upper: Optional[float] = None  # 價格上限
    current_price: Optional[float] = None  # 當前價格
    
    def __post_init__(self):
        # 驗證權重總和為 1
        if not math.isclose(self.weight_a + self.weight_b, 1.0, rel_tol=1e-5):
            raise ValueError(f"權重總和必須為 1, 當前為 {self.weight_a + self.weight_b}")


@dataclass
class HedgeStrategy:
    """對沖策略"""
    hedge_token_a: bool  # 是否對沖 token_a
    hedge_token_b: bool  # 是否對沖 token_b
    hedge_ratio_a: float  # token_a 的對沖比率 (0-1)
    hedge_ratio_b: float  # token_b 的對沖比率 (0-1)
    
    
@dataclass
class DeltaNeutralResult:
    """Delta Neutral 策略結果"""
    # 池資訊
    pool_type: PoolType
    pool_config: PoolConfig
    
    # Delta 分析
    delta_a: float  # token_a 的 Delta
    delta_b: float  # token_b 的 Delta
    total_delta_usd: float  # 總 Delta (USD)
    
    # 對沖策略
    hedge_strategy: HedgeStrategy
    hedge_amount_a_usd: float  # token_a 需要對沖的金額
    hedge_amount_b_usd: float  # token_b 需要對沖的金額
    
    # 收益分析
    lp_fee_apy: float  # LP 手續費 APY
    funding_cost_a_apy: float  # token_a 資金費率成本
    funding_cost_b_apy: float  # token_b 資金費率成本
    total_funding_cost_apy: float  # 總資金費率成本
    gas_cost_annual: float  # 年化 Gas 成本
    net_apy: float  # 淨 APY
    annual_profit: float  # 年化收益
    
    # 風險指標
    volatility_exposure: float  # 波動率敞口
    correlation_risk: float  # 相關性風險
    hedge_effectiveness: float  # 對沖有效性
    risk_level: str  # 風險等級
    
    # 詳細分解
    profit_breakdown: Dict[str, float]


class DeltaNeutralCalculatorV2:
    """Delta Neutral 策略計算器 V2 (增強版)"""
    
    def __init__(self):
        self.token_info_map = self._build_token_info_map()
    
    def _build_token_info_map(self) -> Dict[str, TokenInfo]:
        """構建代幣資訊映射"""
        info_map = {}
        
        for category, data in TOKEN_CATEGORIES.items():
            for token in data["tokens"]:
                info_map[token.upper()] = TokenInfo(
                    symbol=token.upper(),
                    volatility=data["annual_volatility"],
                    is_stable=data["is_stable"]
                )
        
        return info_map
    
    def get_token_info(self, token: str) -> TokenInfo:
        """獲取代幣資訊"""
        token = token.upper()
        
        # 移除常見前綴
        for prefix in ["W", "ST", "R", "CB"]:
            if token.startswith(prefix) and len(token) > len(prefix):
                base_token = token[len(prefix):]
                if base_token in self.token_info_map:
                    return self.token_info_map[base_token]
        
        # 直接查找
        if token in self.token_info_map:
            return self.token_info_map[token]
        
        # 默認為中小市值代幣
        return TokenInfo(
            symbol=token,
            volatility=TOKEN_CATEGORIES["mid_small_cap"]["annual_volatility"],
            is_stable=False
        )
    
    def identify_pool_type(self, token_a_info: TokenInfo, token_b_info: TokenInfo) -> PoolType:
        """識別 LP 池類型"""
        if token_a_info.is_stable and token_b_info.is_stable:
            return PoolType.STABLE_STABLE
        elif token_a_info.is_stable or token_b_info.is_stable:
            return PoolType.VOLATILE_STABLE
        else:
            return PoolType.VOLATILE_VOLATILE
    
    def create_pool_config(
        self,
        token_a: str,
        token_b: str,
        weight_a: float = 0.5,
        weight_b: float = 0.5,
        price_lower: Optional[float] = None,
        price_upper: Optional[float] = None,
        current_price: Optional[float] = None
    ) -> PoolConfig:
        """
        創建 LP 池配置
        
        Args:
            token_a: 代幣 A 符號
            token_b: 代幣 B 符號
            weight_a: 代幣 A 權重 (默認 0.5 = 50%)
            weight_b: 代幣 B 權重 (默認 0.5 = 50%)
            price_lower: Uniswap V3 價格下限
            price_upper: Uniswap V3 價格上限
            current_price: 當前價格
        """
        token_a_info = self.get_token_info(token_a)
        token_b_info = self.get_token_info(token_b)
        pool_type = self.identify_pool_type(token_a_info, token_b_info)
        
        return PoolConfig(
            token_a=token_a_info,
            token_b=token_b_info,
            weight_a=weight_a,
            weight_b=weight_b,
            pool_type=pool_type,
            price_lower=price_lower,
            price_upper=price_upper,
            current_price=current_price
        )
    
    def calculate_uniswap_v3_delta(
        self,
        current_price: float,
        price_lower: float,
        price_upper: float
    ) -> float:
        """
        計算 Uniswap V3 LP 倉位的 Delta
        
        使用公式: Delta = (√P_upper - √P) / (√P_upper - √P_lower)
        
        Returns:
            float: Delta (0-1), 表示 token_a 的敞口比例
        """
        sqrt_p = math.sqrt(current_price)
        sqrt_p_lower = math.sqrt(price_lower)
        sqrt_p_upper = math.sqrt(price_upper)
        
        delta = (sqrt_p_upper - sqrt_p) / (sqrt_p_upper - sqrt_p_lower)
        
        # 確保 Delta 在 [0, 1] 範圍內
        return max(0.0, min(1.0, delta))
    
    def calculate_pool_delta(
        self,
        pool_config: PoolConfig,
        capital: float
    ) -> Tuple[float, float, float]:
        """
        計算 LP 池的 Delta 敞口
        
        Returns:
            Tuple[delta_a, delta_b, total_delta_usd]:
                - delta_a: token_a 的 Delta (0-1)
                - delta_b: token_b 的 Delta (0-1)
                - total_delta_usd: 總 Delta (USD)
        """
        if pool_config.pool_type == PoolType.STABLE_STABLE:
            # 穩定幣對穩定幣: 無 Delta 敞口
            return 0.0, 0.0, 0.0
        
        # 計算每個代幣的資本分配
        capital_a = capital * pool_config.weight_a
        capital_b = capital * pool_config.weight_b
        
        if pool_config.pool_type == PoolType.VOLATILE_STABLE:
            # 波動資產-穩定幣: 只有波動資產有 Delta
            if pool_config.token_a.is_stable:
                # token_b 是波動資產
                if pool_config.price_lower and pool_config.price_upper and pool_config.current_price:
                    # Uniswap V3: 使用精確公式
                    delta_b = self.calculate_uniswap_v3_delta(
                        pool_config.current_price,
                        pool_config.price_lower,
                        pool_config.price_upper
                    )
                else:
                    # 簡化模型: Delta ≈ 權重
                    delta_b = pool_config.weight_b
                
                delta_a = 0.0
                total_delta_usd = capital_b * delta_b
            else:
                # token_a 是波動資產
                if pool_config.price_lower and pool_config.price_upper and pool_config.current_price:
                    delta_a = self.calculate_uniswap_v3_delta(
                        pool_config.current_price,
                        pool_config.price_lower,
                        pool_config.price_upper
                    )
                else:
                    delta_a = pool_config.weight_a
                
                delta_b = 0.0
                total_delta_usd = capital_a * delta_a
        
        else:  # PoolType.VOLATILE_VOLATILE
            # 雙波動資產: 兩個都有 Delta
            if pool_config.price_lower and pool_config.price_upper and pool_config.current_price:
                # Uniswap V3: token_a 的 Delta
                delta_a = self.calculate_uniswap_v3_delta(
                    pool_config.current_price,
                    pool_config.price_lower,
                    pool_config.price_upper
                )
                # token_b 的 Delta = 1 - delta_a
                delta_b = 1.0 - delta_a
            else:
                # 簡化模型: Delta ≈ 權重
                delta_a = pool_config.weight_a
                delta_b = pool_config.weight_b
            
            # 總 Delta 需要考慮兩個資產的相對波動
            # 使用波動率加權
            vol_a = pool_config.token_a.volatility
            vol_b = pool_config.token_b.volatility
            
            # 標準化到 USD 基準
            total_delta_usd = capital_a * delta_a + capital_b * delta_b * (vol_b / vol_a)
        
        return delta_a, delta_b, total_delta_usd
    
    def generate_hedge_strategy(
        self,
        pool_config: PoolConfig,
        delta_a: float,
        delta_b: float,
        hedge_ratio: float = 1.0
    ) -> HedgeStrategy:
        """
        生成對沖策略
        
        Args:
            pool_config: LP 池配置
            delta_a: token_a 的 Delta
            delta_b: token_b 的 Delta
            hedge_ratio: 總體對沖比率 (0-1)
        """
        if pool_config.pool_type == PoolType.STABLE_STABLE:
            # 穩定幣池不需要對沖
            return HedgeStrategy(
                hedge_token_a=False,
                hedge_token_b=False,
                hedge_ratio_a=0.0,
                hedge_ratio_b=0.0
            )
        
        elif pool_config.pool_type == PoolType.VOLATILE_STABLE:
            # 只對沖波動資產
            # hedge_ratio 直接表示要對沖多少比例的波動資產持倉
            if pool_config.token_a.is_stable:
                return HedgeStrategy(
                    hedge_token_a=False,
                    hedge_token_b=True,
                    hedge_ratio_a=0.0,
                    hedge_ratio_b=hedge_ratio  # 修正: 直接使用對沖比率
                )
            else:
                return HedgeStrategy(
                    hedge_token_a=True,
                    hedge_token_b=False,
                    hedge_ratio_a=hedge_ratio,  # 修正: 直接使用對沖比率
                    hedge_ratio_b=0.0
                )
        
        else:  # PoolType.VOLATILE_VOLATILE
            # 對沖兩個波動資產
            # hedge_ratio 表示要對沖多少比例的各自持倉
            return HedgeStrategy(
                hedge_token_a=True,
                hedge_token_b=True,
                hedge_ratio_a=hedge_ratio,  # 修正: 直接使用對沖比率
                hedge_ratio_b=hedge_ratio   # 修正: 直接使用對沖比率
            )
    
    def calculate_delta_neutral_strategy(
        self,
        pool_config: PoolConfig,
        capital: float,
        lp_apy: float,
        funding_rate_a_apy: float = 0.0,
        funding_rate_b_apy: float = 0.0,
        hedge_ratio: float = 1.0,
        gas_cost_annual: float = 200.0
    ) -> DeltaNeutralResult:
        """
        計算完整的 Delta Neutral 策略
        
        Args:
            pool_config: LP 池配置
            capital: 投資資本
            lp_apy: LP 手續費 APY
            funding_rate_a_apy: token_a 的資金費率 APY
            funding_rate_b_apy: token_b 的資金費率 APY
            hedge_ratio: 對沖比率
            gas_cost_annual: 年化 Gas 成本
        """
        # 1. 計算 Delta
        delta_a, delta_b, total_delta_usd = self.calculate_pool_delta(pool_config, capital)
        
        # 2. 生成對沖策略
        hedge_strategy = self.generate_hedge_strategy(pool_config, delta_a, delta_b, hedge_ratio)
        
        # 3. 計算對沖金額
        capital_a = capital * pool_config.weight_a
        capital_b = capital * pool_config.weight_b
        
        hedge_amount_a_usd = capital_a * hedge_strategy.hedge_ratio_a
        hedge_amount_b_usd = capital_b * hedge_strategy.hedge_ratio_b
        
        # 4. 計算收益和成本
        # LP 手續費收益
        lp_profit = capital * (lp_apy / 100)
        
        # 資金費率成本
        funding_cost_a = hedge_amount_a_usd * (funding_rate_a_apy / 100)
        funding_cost_b = hedge_amount_b_usd * (funding_rate_b_apy / 100)
        total_funding_cost = funding_cost_a + funding_cost_b
        
        # 淨收益
        total_profit = lp_profit - total_funding_cost - gas_cost_annual
        net_apy = (total_profit / capital) * 100
        
        # 5. 風險評估
        # 波動率敞口 = 未對沖的部分
        volatility_exposure_a = delta_a * (1 - hedge_strategy.hedge_ratio_a) * pool_config.token_a.volatility
        volatility_exposure_b = delta_b * (1 - hedge_strategy.hedge_ratio_b) * pool_config.token_b.volatility
        volatility_exposure = max(volatility_exposure_a, volatility_exposure_b)
        
        # 相關性風險 (雙波動資產池特有)
        if pool_config.pool_type == PoolType.VOLATILE_VOLATILE:
            correlation_risk = min(pool_config.token_a.volatility, pool_config.token_b.volatility) / 100
        else:
            correlation_risk = 0.0
        
        # 對沖有效性
        hedge_effectiveness = 1.0 - (volatility_exposure / 100)
        
        # 風險等級
        total_risk = volatility_exposure + correlation_risk * 50
        if total_risk < 10:
            risk_level = "極低"
        elif total_risk < 30:
            risk_level = "低"
        elif total_risk < 50:
            risk_level = "中"
        else:
            risk_level = "高"
        
        # 6. 收益分解
        profit_breakdown = {
            "lp_profit": lp_profit,
            "funding_cost_a": -funding_cost_a,
            "funding_cost_b": -funding_cost_b,
            "total_funding_cost": -total_funding_cost,
            "gas_cost": -gas_cost_annual,
            "total": total_profit
        }
        
        return DeltaNeutralResult(
            pool_type=pool_config.pool_type,
            pool_config=pool_config,
            delta_a=delta_a,
            delta_b=delta_b,
            total_delta_usd=total_delta_usd,
            hedge_strategy=hedge_strategy,
            hedge_amount_a_usd=hedge_amount_a_usd,
            hedge_amount_b_usd=hedge_amount_b_usd,
            lp_fee_apy=lp_apy,
            funding_cost_a_apy=funding_rate_a_apy,
            funding_cost_b_apy=funding_rate_b_apy,
            total_funding_cost_apy=(total_funding_cost / capital) * 100,
            gas_cost_annual=gas_cost_annual,
            net_apy=net_apy,
            annual_profit=total_profit,
            volatility_exposure=volatility_exposure,
            correlation_risk=correlation_risk,
            hedge_effectiveness=hedge_effectiveness,
            risk_level=risk_level,
            profit_breakdown=profit_breakdown
        )

