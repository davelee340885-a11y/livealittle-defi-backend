"""
Delta Neutral 策略計算引擎 (重寫版)

基於正確的 Uniswap V3 數學和 Delta Neutral 策略邏輯
"""

import math
from typing import Dict, Tuple
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
class DeltaNeutralAnalysis:
    """Delta Neutral 策略分析結果"""
    # LP 相關
    lp_delta: float  # LP 的 Delta (0-1)
    lp_fee_apy: float  # LP 手續費 APY (%)
    
    # 對沖相關
    hedge_ratio: float  # 對沖比率 (0-1)
    funding_rate_apy: float  # 資金費率 APY (%)
    
    # 收益分析
    net_apy: float  # 淨 APY (%)
    annual_profit: float  # 年化收益 (USD)
    
    # 風險指標
    volatility: float  # 池波動率 (%)
    max_drawdown: float  # 最大回撤 (%)
    risk_level: str  # 風險等級
    
    # 詳細分解
    profit_breakdown: Dict[str, float]  # 收益分解


class DeltaNeutralCalculator:
    """Delta Neutral 策略計算器"""
    
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
        """獲取代幣的年化波動率"""
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
    
    def calculate_lp_delta(
        self,
        current_price: float,
        price_lower: float,
        price_upper: float
    ) -> float:
        """
        計算 LP 倉位的 Delta
        
        Delta = (√P_upper - √P) / (√P_upper - √P_lower)
        
        Args:
            current_price: 當前價格
            price_lower: 價格下限
            price_upper: 價格上限
        
        Returns:
            float: Delta (0-1)
        """
        sqrt_p = math.sqrt(current_price)
        sqrt_p_lower = math.sqrt(price_lower)
        sqrt_p_upper = math.sqrt(price_upper)
        
        delta = (sqrt_p_upper - sqrt_p) / (sqrt_p_upper - sqrt_p_lower)
        
        # 確保 Delta 在 [0, 1] 範圍內
        return max(0.0, min(1.0, delta))
    
    def estimate_gas_cost(
        self,
        chain: str,
        rebalance_frequency_days: float
    ) -> float:
        """
        估算 Gas 成本
        
        Args:
            chain: 鏈名稱
            rebalance_frequency_days: 再平衡頻率（天）
        
        Returns:
            float: 年化 Gas 成本 (USD)
        """
        # 單次操作的 Gas 成本估算
        gas_costs = {
            "ethereum": 50.0,  # 以太坊主網
            "arbitrum": 2.0,   # Arbitrum
            "optimism": 2.0,   # Optimism
            "polygon": 0.5,    # Polygon
            "base": 1.0,       # Base
            "bsc": 1.0,        # BSC
        }
        
        chain_lower = chain.lower()
        single_operation_cost = gas_costs.get(chain_lower, 10.0)
        
        # 年化 Gas 成本 = 單次成本 × (365 / 再平衡頻率)
        annual_gas_cost = single_operation_cost * (365 / rebalance_frequency_days)
        
        return annual_gas_cost
    
    def calculate_delta_neutral_pnl(
        self,
        capital: float,
        lp_apy: float,
        funding_apy: float,
        hedge_ratio: float = 1.0,
        rebalance_frequency_days: float = 7,
        chain: str = "ethereum",
        price_range_pct: float = 10.0  # 價格範圍 ±%
    ) -> DeltaNeutralAnalysis:
        """
        計算 Delta Neutral 策略的損益
        
        核心邏輯:
        1. LP 倉位有一個 Delta (通常 30-70%)
        2. 對沖該 Delta 的資產數量
        3. 淨收益 = LP 手續費 - 資金費率成本 - Gas 成本
        
        Args:
            capital: 投資資本 (USD)
            lp_apy: LP 手續費 APY (%)
            funding_apy: 資金費率 APY (%)
            hedge_ratio: 對沖比率 (0-1)
            rebalance_frequency_days: 再平衡頻率（天）
            chain: 鏈名稱
            price_range_pct: 價格範圍百分比
        
        Returns:
            DeltaNeutralAnalysis: 策略分析結果
        """
        # 1. 計算 LP Delta (假設價格在範圍中間)
        # 簡化模型: 假設價格範圍 ±10%, Delta ≈ 0.5
        # 精確計算需要知道具體的價格範圍
        current_price = 100  # 標準化價格
        price_lower = current_price * (1 - price_range_pct / 100)
        price_upper = current_price * (1 + price_range_pct / 100)
        
        lp_delta = self.calculate_lp_delta(current_price, price_lower, price_upper)
        
        # 2. 實際對沖的資產比例
        effective_hedge = lp_delta * hedge_ratio
        
        # 3. 計算各項收益/成本
        
        # LP 手續費收益 (整個資本都在 LP 中)
        lp_profit = capital * (lp_apy / 100)
        
        # 資金費率成本 (只對沖 Delta 部分)
        # 注意: funding_apy 可能是正數或負數
        # 正數表示做空需要支付, 負數表示做空可以收取
        funding_cost = capital * effective_hedge * (funding_apy / 100)
        
        # Gas 成本
        gas_cost = self.estimate_gas_cost(chain, rebalance_frequency_days)
        
        # 4. 計算淨收益
        # 在完美對沖下, LP 價值變化和對沖損益相抵消
        # 淨收益 = LP 手續費 - 資金費率成本 - Gas 成本
        total_profit = lp_profit - funding_cost - gas_cost
        net_apy = (total_profit / capital) * 100
        
        # 5. 風險評估
        # 風險主要來自不完美對沖和資金費率波動
        risk_score = abs(1.0 - hedge_ratio) * 100  # 未對沖部分的風險
        
        if risk_score < 10:
            risk_level = "極低"
        elif risk_score < 30:
            risk_level = "低"
        elif risk_score < 50:
            risk_level = "中"
        else:
            risk_level = "高"
        
        # 6. 最大回撤估算
        # 主要風險: 資金費率突然飆升
        max_drawdown = abs(funding_cost / capital) * 100 * 2  # 假設最壞情況翻倍
        
        # 7. 收益分解
        profit_breakdown = {
            "lp_profit": lp_profit,
            "funding_cost": -funding_cost,  # 負數表示成本
            "gas_cost": -gas_cost,
            "total": total_profit
        }
        
        return DeltaNeutralAnalysis(
            lp_delta=lp_delta,
            lp_fee_apy=lp_apy,
            hedge_ratio=hedge_ratio,
            funding_rate_apy=funding_apy,
            net_apy=net_apy,
            annual_profit=total_profit,
            volatility=0.0,  # 完美對沖下波動率接近 0
            max_drawdown=max_drawdown,
            risk_level=risk_level,
            profit_breakdown=profit_breakdown
        )
    
    def simulate_price_scenario(
        self,
        capital: float,
        lp_apy: float,
        funding_apy: float,
        price_change_pct: float,
        hedge_ratio: float = 1.0,
        days: int = 1,
        chain: str = "ethereum",
        price_range_pct: float = 10.0
    ) -> Dict[str, float]:
        """
        模擬價格變動情境
        
        計算在特定價格變動下, Delta Neutral 策略的表現
        
        Args:
            capital: 投資資本 (USD)
            lp_apy: LP 手續費 APY (%)
            funding_apy: 資金費率 APY (%)
            price_change_pct: 價格變動百分比 (如 10 表示上漲 10%)
            hedge_ratio: 對沖比率 (0-1)
            days: 持有天數
            chain: 鏈名稱
            price_range_pct: 價格範圍百分比
        
        Returns:
            Dict: 包含各項損益的字典
        """
        # 1. 計算 LP Delta
        current_price = 100
        price_lower = current_price * (1 - price_range_pct / 100)
        price_upper = current_price * (1 + price_range_pct / 100)
        
        lp_delta = self.calculate_lp_delta(current_price, price_lower, price_upper)
        
        # 2. 實際對沖比例
        effective_hedge = lp_delta * hedge_ratio
        
        # 3. LP 價值變化
        # 簡化模型: LP 價值變化 ≈ Delta × 價格變動 × 資本
        price_change_ratio = price_change_pct / 100
        lp_value_change = capital * lp_delta * price_change_ratio
        
        # 4. 對沖倉位損益
        # 做空: 價格上漲虧損, 價格下跌盈利
        hedge_pnl = -capital * effective_hedge * price_change_ratio
        
        # 5. LP 手續費 (按天計算)
        lp_fee = capital * (lp_apy / 100) * (days / 365)
        
        # 6. 資金費率成本 (按天計算)
        funding_cost = capital * effective_hedge * (funding_apy / 100) * (days / 365)
        
        # 7. Gas 成本
        gas_cost = self.estimate_gas_cost(chain, 7) * (days / 365)
        
        # 8. 總淨損益
        # 在完美對沖下: lp_value_change + hedge_pnl ≈ 0
        total_pnl = lp_value_change + hedge_pnl + lp_fee - funding_cost - gas_cost
        
        # 9. 對沖效果評估
        hedge_effectiveness = 1.0 - abs(lp_value_change + hedge_pnl) / abs(lp_value_change) if lp_value_change != 0 else 1.0
        
        return {
            "lp_value_change": lp_value_change,
            "hedge_pnl": hedge_pnl,
            "lp_fee": lp_fee,
            "funding_cost": -funding_cost,  # 負數表示成本
            "gas_cost": -gas_cost,
            "total_pnl": total_pnl,
            "final_value": capital + total_pnl,
            "hedge_effectiveness": hedge_effectiveness,
            "lp_delta": lp_delta,
            "effective_hedge": effective_hedge
        }


# 向後兼容: 保留舊的函數名
def calculate_adjusted_net_profit(
    capital: float,
    lp_apy: float,
    funding_apy: float,
    hedge_ratio: float = 1.0,
    rebalance_frequency: float = 7,
    chain: str = "ethereum"
) -> Tuple[float, Dict[str, float]]:
    """
    向後兼容的函數
    
    Returns:
        Tuple[float, Dict]: (淨 APY, 收益分解字典)
    """
    calculator = DeltaNeutralCalculator()
    
    result = calculator.calculate_delta_neutral_pnl(
        capital=capital,
        lp_apy=lp_apy,
        funding_apy=funding_apy,
        hedge_ratio=hedge_ratio,
        rebalance_frequency_days=rebalance_frequency,
        chain=chain
    )
    
    return result.net_apy, result.profit_breakdown

