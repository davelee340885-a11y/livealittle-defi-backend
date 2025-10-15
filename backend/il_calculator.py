"""
無常損失（Impermanent Loss, IL）計算引擎

實現精確的 IL 計算和 Delta Neutral 對沖效果分析
"""

import math
from typing import Dict, List, Tuple
from dataclasses import dataclass


# 代幣波動率估算（年化）
VOLATILITY_ESTIMATES = {
    # 穩定幣 - 極低波動
    "stablecoins": {
        "tokens": ["USDC", "USDT", "DAI", "FRAX", "LUSD", "BUSD", "USDD", "TUSD", "USDP"],
        "annual_volatility": 2.0  # 2%
    },
    
    # 主流代幣 - 中等波動
    "major": {
        "tokens": ["ETH", "WETH", "BTC", "WBTC", "stETH", "wstETH", "rETH"],
        "annual_volatility": 80.0  # 80%
    },
    
    # 大市值代幣 - 高波動
    "large_cap": {
        "tokens": ["BNB", "SOL", "MATIC", "AVAX", "LINK", "UNI", "AAVE"],
        "annual_volatility": 100.0  # 100%
    },
    
    # 中小市值代幣 - 極高波動
    "mid_small_cap": {
        "tokens": [],  # 其他所有代幣
        "annual_volatility": 150.0  # 150%
    }
}


@dataclass
class ILAnalysis:
    """IL 分析結果"""
    pool_volatility: float  # 池波動率 (%)
    expected_il_annual: float  # 預期年化 IL (%)
    hedge_effectiveness: float  # 對沖有效性 (0-1)
    net_il_annual: float  # 淨 IL (%)
    il_impact_usd: float  # IL 影響 (USD)
    il_risk_level: str  # IL 風險等級
    volatility_level: str  # 波動率等級
    hedge_quality: str  # 對沖質量


@dataclass
class HedgeParams:
    """對沖參數"""
    hedge_ratio: float = 1.0  # 對沖比率 (0-1)
    rebalance_frequency_days: float = 7  # 再平衡頻率（天）


class ILCalculator:
    """無常損失計算器"""
    
    def __init__(self):
        self.volatility_map = self._build_volatility_map()
    
    def _build_volatility_map(self) -> Dict[str, float]:
        """構建代幣波動率映射"""
        vol_map = {}
        
        for category, data in VOLATILITY_ESTIMATES.items():
            for token in data["tokens"]:
                vol_map[token.upper()] = data["annual_volatility"]
        
        return vol_map
    
    def get_token_volatility(self, token: str) -> float:
        """
        獲取代幣的年化波動率
        
        Args:
            token: 代幣符號（如 "ETH", "USDC"）
        
        Returns:
            float: 年化波動率 (%)
        """
        token = token.upper()
        
        # 移除常見前綴
        for prefix in ["W", "ST", "R"]:
            if token.startswith(prefix) and token[len(prefix):] in self.volatility_map:
                return self.volatility_map[token[len(prefix):]]
        
        # 直接查找
        if token in self.volatility_map:
            return self.volatility_map[token]
        
        # 默認為中小市值代幣
        return VOLATILITY_ESTIMATES["mid_small_cap"]["annual_volatility"]
    
    def estimate_pool_volatility(self, token_a: str, token_b: str) -> float:
        """
        估算 LP 池的波動率
        
        邏輯:
        - 穩定幣對: 極低波動率
        - 一個穩定幣: 使用非穩定幣的波動率
        - 兩個波動代幣: 使用較高的波動率
        
        Args:
            token_a: 代幣 A
            token_b: 代幣 B
        
        Returns:
            float: 池波動率 (%)
        """
        vol_a = self.get_token_volatility(token_a)
        vol_b = self.get_token_volatility(token_b)
        
        # 如果都是穩定幣（波動率 < 5%）
        if vol_a < 5 and vol_b < 5:
            return 2.0
        
        # 如果一個是穩定幣
        if vol_a < 5:
            return vol_b
        if vol_b < 5:
            return vol_a
        
        # 如果都是波動代幣，使用較高的波動率
        return max(vol_a, vol_b)
    
    def calculate_il(self, price_change_percent: float) -> float:
        """
        計算無常損失
        
        公式: IL = (2 * sqrt(price_ratio) / (1 + price_ratio)) - 1
        
        Args:
            price_change_percent: 價格變化百分比（如 50 表示上漲 50%）
        
        Returns:
            float: IL 百分比（負數表示損失）
        """
        price_ratio = 1 + (price_change_percent / 100)
        il = (2 * math.sqrt(price_ratio) / (1 + price_ratio)) - 1
        return il * 100  # 轉換為百分比
    
    def estimate_expected_il(
        self,
        volatility_annual: float,
        holding_period_days: float = 365
    ) -> float:
        """
        基於年化波動率估算預期 IL
        
        使用簡化模型: 預期 IL ≈ -0.5 * volatility^2
        
        Args:
            volatility_annual: 年化波動率 (%)
            holding_period_days: 持有天數
        
        Returns:
            float: 預期 IL 百分比（負數）
        """
        # 將年化波動率轉換為持有期波動率
        holding_volatility = volatility_annual * math.sqrt(holding_period_days / 365)
        
        # 使用簡化模型
        expected_il = -0.5 * (holding_volatility / 100) ** 2 * 100
        
        return expected_il
    
    def calculate_hedge_effectiveness(
        self,
        hedge_params: HedgeParams = None
    ) -> float:
        """
        計算對沖有效性
        
        Args:
            hedge_params: 對沖參數
        
        Returns:
            float: 對沖有效性 (0-1，1 表示 100% 有效)
        """
        if hedge_params is None:
            hedge_params = HedgeParams()
        
        # 基礎對沖有效性
        base_effectiveness = hedge_params.hedge_ratio
        
        # 再平衡頻率影響（越頻繁越有效）
        # 每週再平衡: 1.0, 每月再平衡: 0.9, 更少: 更低
        rebalance_factor = 1 - (hedge_params.rebalance_frequency_days / 30) * 0.1
        rebalance_factor = max(0.7, min(1.0, rebalance_factor))
        
        # 總有效性
        effectiveness = base_effectiveness * rebalance_factor
        
        return min(1.0, effectiveness)
    
    def calculate_net_il(
        self,
        expected_il: float,
        hedge_effectiveness: float
    ) -> float:
        """
        計算對沖後的淨 IL
        
        Args:
            expected_il: 預期 IL（負數）
            hedge_effectiveness: 對沖有效性 (0-1)
        
        Returns:
            float: 淨 IL 百分比
        """
        # 對沖後的 IL = 原始 IL * (1 - 對沖有效性)
        net_il = expected_il * (1 - hedge_effectiveness)
        
        return net_il
    
    def get_il_risk_level(self, pool_volatility: float) -> str:
        """
        獲取 IL 風險等級
        
        Args:
            pool_volatility: 池波動率 (%)
        
        Returns:
            str: 風險等級（low/medium/high）
        """
        if pool_volatility < 10:
            return "low"
        elif pool_volatility < 80:
            return "medium"
        else:
            return "high"
    
    def get_volatility_level(self, pool_volatility: float) -> str:
        """
        獲取波動率等級
        
        Args:
            pool_volatility: 池波動率 (%)
        
        Returns:
            str: 波動率等級（low/medium/high/extreme）
        """
        if pool_volatility < 10:
            return "low"
        elif pool_volatility < 50:
            return "medium"
        elif pool_volatility < 100:
            return "high"
        else:
            return "extreme"
    
    def get_hedge_quality(self, hedge_effectiveness: float) -> str:
        """
        獲取對沖質量
        
        Args:
            hedge_effectiveness: 對沖有效性 (0-1)
        
        Returns:
            str: 對沖質量（poor/fair/good/excellent）
        """
        if hedge_effectiveness < 0.7:
            return "poor"
        elif hedge_effectiveness < 0.85:
            return "fair"
        elif hedge_effectiveness < 0.95:
            return "good"
        else:
            return "excellent"
    
    def analyze_il(
        self,
        token_a: str,
        token_b: str,
        capital: float,
        hedge_params: HedgeParams = None,
        holding_period_days: float = 365
    ) -> ILAnalysis:
        """
        完整的 IL 分析
        
        Args:
            token_a: 代幣 A
            token_b: 代幣 B
            capital: 投資資本 (USD)
            hedge_params: 對沖參數
            holding_period_days: 持有天數
        
        Returns:
            ILAnalysis: IL 分析結果
        """
        if hedge_params is None:
            hedge_params = HedgeParams()
        
        # 1. 估算池波動率
        pool_volatility = self.estimate_pool_volatility(token_a, token_b)
        
        # 2. 計算預期 IL
        expected_il_annual = self.estimate_expected_il(
            pool_volatility,
            holding_period_days
        )
        
        # 3. 計算對沖有效性
        hedge_effectiveness = self.calculate_hedge_effectiveness(hedge_params)
        
        # 4. 計算淨 IL
        net_il_annual = self.calculate_net_il(expected_il_annual, hedge_effectiveness)
        
        # 5. 計算 IL 影響（USD）
        il_impact_usd = capital * (net_il_annual / 100)
        
        # 6. 獲取風險等級
        il_risk_level = self.get_il_risk_level(pool_volatility)
        volatility_level = self.get_volatility_level(pool_volatility)
        hedge_quality = self.get_hedge_quality(hedge_effectiveness)
        
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
        net_il_annual: float,
        gas_cost_annual: float,
        capital: float
    ) -> Dict:
        """
        計算考慮 IL 後的調整淨收益
        
        Args:
            lp_apy: LP APY (%)
            funding_apy: 資金費率 APY (%)
            net_il_annual: 年化淨 IL (%)
            gas_cost_annual: 年化 Gas 成本 (USD)
            capital: 投資資本 (USD)
        
        Returns:
            dict: 包含各項收益和成本的詳細信息
        """
        # 1. LP 收益
        lp_profit = capital * (lp_apy / 100)
        
        # 2. 資金費率收益
        funding_profit = capital * (funding_apy / 100)
        
        # 3. IL 損失（已考慮對沖）
        il_loss = capital * (net_il_annual / 100)
        
        # 4. Gas 成本
        gas_cost = gas_cost_annual
        
        # 5. 總收益
        total_profit = lp_profit + funding_profit + il_loss - gas_cost
        
        # 6. 淨 APY
        net_apy = (total_profit / capital) * 100
        
        return {
            "lp_profit": lp_profit,
            "funding_profit": funding_profit,
            "il_loss": il_loss,
            "gas_cost": gas_cost,
            "total_profit": total_profit,
            "net_apy": net_apy,
            "breakdown": {
                "lp_apy": lp_apy,
                "funding_apy": funding_apy,
                "il_impact": net_il_annual,
                "gas_impact": -(gas_cost / capital) * 100
            }
        }


# 測試代碼
if __name__ == "__main__":
    calculator = ILCalculator()
    
    print("=" * 60)
    print("無常損失（IL）計算引擎測試")
    print("=" * 60)
    
    # 測試 1: 基礎 IL 計算
    print("\n測試 1: 基礎 IL 計算")
    print("-" * 60)
    for price_change in [25, 50, 100, 200, 300]:
        il = calculator.calculate_il(price_change)
        print(f"價格變化 {price_change:3d}% → IL: {il:6.2f}%")
    
    # 測試 2: 代幣波動率
    print("\n測試 2: 代幣波動率")
    print("-" * 60)
    test_tokens = ["USDC", "ETH", "BTC", "SOL", "LINK", "RANDOM"]
    for token in test_tokens:
        vol = calculator.get_token_volatility(token)
        print(f"{token:10s} → 年化波動率: {vol:6.1f}%")
    
    # 測試 3: 池波動率
    print("\n測試 3: 池波動率")
    print("-" * 60)
    test_pairs = [
        ("USDC", "USDT"),
        ("ETH", "USDC"),
        ("ETH", "BTC"),
        ("SOL", "LINK")
    ]
    for token_a, token_b in test_pairs:
        pool_vol = calculator.estimate_pool_volatility(token_a, token_b)
        print(f"{token_a}-{token_b:4s} → 池波動率: {pool_vol:6.1f}%")
    
    # 測試 4: 完整的 IL 分析（ETH-USDC 池）
    print("\n測試 4: 完整的 IL 分析（ETH-USDC 池，$10,000 投資）")
    print("-" * 60)
    
    il_analysis = calculator.analyze_il(
        token_a="ETH",
        token_b="USDC",
        capital=10000,
        hedge_params=HedgeParams(hedge_ratio=1.0, rebalance_frequency_days=7)
    )
    
    print(f"池波動率: {il_analysis.pool_volatility:.1f}%")
    print(f"預期年化 IL: {il_analysis.expected_il_annual:.2f}%")
    print(f"對沖有效性: {il_analysis.hedge_effectiveness * 100:.1f}%")
    print(f"淨年化 IL: {il_analysis.net_il_annual:.2f}%")
    print(f"IL 影響: ${il_analysis.il_impact_usd:,.2f}")
    print(f"IL 風險等級: {il_analysis.il_risk_level}")
    print(f"波動率等級: {il_analysis.volatility_level}")
    print(f"對沖質量: {il_analysis.hedge_quality}")
    
    # 測試 5: 調整後的淨收益（考慮 IL）
    print("\n測試 5: 調整後的淨收益（考慮 IL）")
    print("-" * 60)
    
    result = calculator.calculate_adjusted_net_profit(
        lp_apy=101.47,
        funding_apy=10.95,
        net_il_annual=il_analysis.net_il_annual,
        gas_cost_annual=200,
        capital=10000
    )
    
    print(f"LP 收益: ${result['lp_profit']:,.2f}")
    print(f"資金費率收益: ${result['funding_profit']:,.2f}")
    print(f"IL 損失: ${result['il_loss']:,.2f}")
    print(f"Gas 成本: ${result['gas_cost']:,.2f}")
    print(f"總收益: ${result['total_profit']:,.2f}")
    print(f"淨 APY: {result['net_apy']:.2f}%")
    
    print("\n收益分解:")
    print(f"  LP APY: {result['breakdown']['lp_apy']:.2f}%")
    print(f"  資金費率 APY: {result['breakdown']['funding_apy']:.2f}%")
    print(f"  IL 影響: {result['breakdown']['il_impact']:.2f}%")
    print(f"  Gas 影響: {result['breakdown']['gas_impact']:.2f}%")
    
    # 測試 6: 不同對沖策略的比較
    print("\n測試 6: 不同對沖策略的比較")
    print("-" * 60)
    
    hedge_strategies = [
        ("無對沖", HedgeParams(hedge_ratio=0.0, rebalance_frequency_days=30)),
        ("50% 對沖", HedgeParams(hedge_ratio=0.5, rebalance_frequency_days=7)),
        ("100% 對沖（每週）", HedgeParams(hedge_ratio=1.0, rebalance_frequency_days=7)),
        ("100% 對沖（每月）", HedgeParams(hedge_ratio=1.0, rebalance_frequency_days=30)),
    ]
    
    for strategy_name, hedge_params in hedge_strategies:
        il_analysis = calculator.analyze_il(
            token_a="ETH",
            token_b="USDC",
            capital=10000,
            hedge_params=hedge_params
        )
        
        result = calculator.calculate_adjusted_net_profit(
            lp_apy=101.47,
            funding_apy=10.95,
            net_il_annual=il_analysis.net_il_annual,
            gas_cost_annual=200,
            capital=10000
        )
        
        print(f"\n{strategy_name}:")
        print(f"  對沖有效性: {il_analysis.hedge_effectiveness * 100:.1f}%")
        print(f"  淨 IL: {il_analysis.net_il_annual:.2f}%")
        print(f"  淨 APY: {result['net_apy']:.2f}%")
        print(f"  總收益: ${result['total_profit']:,.2f}")
    
    print("\n" + "=" * 60)
    print("✅ 所有測試完成！")
    print("=" * 60)

