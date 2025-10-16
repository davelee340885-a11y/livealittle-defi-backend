"""
LP 池解析工具

從池的 symbol 和 metadata 中解析:
- 代幣對
- 池權重
- 池類型
"""

import re
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class PoolInfo:
    """解析後的池資訊"""
    token_a: str
    token_b: str
    weight_a: float
    weight_b: float
    protocol: str
    
    # Uniswap V3 特定
    price_lower: Optional[float] = None
    price_upper: Optional[float] = None
    current_price: Optional[float] = None
    fee_tier: Optional[float] = None


class PoolParser:
    """LP 池解析器"""
    
    # 常見的池權重配置
    COMMON_WEIGHTS = {
        "80-20": (0.8, 0.2),
        "70-30": (0.7, 0.3),
        "60-40": (0.6, 0.4),
        "50-50": (0.5, 0.5),
        "40-60": (0.4, 0.6),
        "30-70": (0.3, 0.7),
        "20-80": (0.2, 0.8),
    }
    
    def __init__(self):
        pass
    
    def parse_symbol(self, symbol: str) -> Tuple[str, str]:
        """
        從 symbol 解析代幣對
        
        支持格式:
        - "ETH-USDC"
        - "WETH-USDC"
        - "ETH/USDC"
        - "ETH_USDC"
        - "ETH-USDC-80-20" (帶權重)
        
        Returns:
            Tuple[token_a, token_b]
        """
        # 移除空格
        symbol = symbol.strip()
        
        # 先移除權重部分 (如果有)
        # 查找權重模式 (\d+-\d+)
        weight_pattern = r"-(\d+)-(\d+)$"
        symbol_without_weights = re.sub(weight_pattern, "", symbol)
        
        # 嘗試不同的分隔符
        for sep in ["-", "/", "_"]:
            if sep in symbol_without_weights:
                parts = symbol_without_weights.split(sep)
                if len(parts) == 2:
                    return parts[0].strip().upper(), parts[1].strip().upper()
        
        raise ValueError(f"無法解析 symbol: {symbol}")
    
    def parse_weights_from_symbol(self, symbol: str) -> Tuple[float, float]:
        """
        從 symbol 中解析權重
        
        例如:
        - "ETH-USDC-80-20" -> (0.8, 0.2)
        - "ETH-USDC" -> (0.5, 0.5) [默認]
        
        Returns:
            Tuple[weight_a, weight_b]
        """
        # 查找權重模式 (例如 "80-20")
        weight_pattern = r"(\d+)-(\d+)"
        match = re.search(weight_pattern, symbol)
        
        if match:
            w1 = int(match.group(1))
            w2 = int(match.group(2))
            
            # 驗證總和為 100
            if w1 + w2 == 100:
                return w1 / 100, w2 / 100
        
        # 默認 50/50
        return 0.5, 0.5
    
    def infer_weights_from_protocol(self, protocol: str) -> Tuple[float, float]:
        """
        從協議推斷權重
        
        某些協議有特定的默認權重:
        - Balancer: 支持任意權重
        - Uniswap V2/V3: 默認 50/50
        - Curve: 通常是穩定幣池,50/50
        """
        protocol_lower = protocol.lower()
        
        # Balancer 可能有非對稱權重,但需要額外資訊
        if "balancer" in protocol_lower:
            # 默認返回 50/50,實際應從池數據中獲取
            return 0.5, 0.5
        
        # 其他協議默認 50/50
        return 0.5, 0.5
    
    def parse_pool(
        self,
        symbol: str,
        protocol: str,
        pool_data: Optional[dict] = None
    ) -> PoolInfo:
        """
        解析完整的池資訊
        
        Args:
            symbol: 池符號 (如 "ETH-USDC")
            protocol: 協議名稱 (如 "uniswap-v3")
            pool_data: 額外的池數據 (可選)
        
        Returns:
            PoolInfo: 解析後的池資訊
        """
        # 1. 解析代幣對
        token_a, token_b = self.parse_symbol(symbol)
        
        # 2. 解析權重
        # 優先級: symbol中的權重 > pool_data中的權重 > 協議默認權重
        weight_a, weight_b = self.parse_weights_from_symbol(symbol)
        
        if pool_data:
            # 從 pool_data 中獲取權重 (如果有)
            if "weight_a" in pool_data and "weight_b" in pool_data:
                weight_a = pool_data["weight_a"]
                weight_b = pool_data["weight_b"]
            elif "weights" in pool_data:
                weights = pool_data["weights"]
                if len(weights) >= 2:
                    weight_a = weights[0]
                    weight_b = weights[1]
        
        # 3. 獲取 Uniswap V3 特定參數
        price_lower = None
        price_upper = None
        current_price = None
        fee_tier = None
        
        if pool_data:
            price_lower = pool_data.get("price_lower")
            price_upper = pool_data.get("price_upper")
            current_price = pool_data.get("current_price") or pool_data.get("price")
            fee_tier = pool_data.get("fee_tier") or pool_data.get("fee")
        
        return PoolInfo(
            token_a=token_a,
            token_b=token_b,
            weight_a=weight_a,
            weight_b=weight_b,
            protocol=protocol,
            price_lower=price_lower,
            price_upper=price_upper,
            current_price=current_price,
            fee_tier=fee_tier
        )
    
    def estimate_price_range(
        self,
        current_price: float,
        range_pct: float = 10.0
    ) -> Tuple[float, float]:
        """
        估算價格範圍
        
        Args:
            current_price: 當前價格
            range_pct: 範圍百分比 (默認 ±10%)
        
        Returns:
            Tuple[price_lower, price_upper]
        """
        price_lower = current_price * (1 - range_pct / 100)
        price_upper = current_price * (1 + range_pct / 100)
        
        return price_lower, price_upper


# 測試
if __name__ == "__main__":
    parser = PoolParser()
    
    # 測試 1: 標準池
    print("測試 1: ETH-USDC")
    pool1 = parser.parse_pool("ETH-USDC", "uniswap-v3")
    print(f"  Token A: {pool1.token_a}, Token B: {pool1.token_b}")
    print(f"  權重: {pool1.weight_a:.1%} / {pool1.weight_b:.1%}")
    
    # 測試 2: 帶權重的池
    print("\n測試 2: ETH-USDC-80-20")
    pool2 = parser.parse_pool("ETH-USDC-80-20", "balancer-v2")
    print(f"  Token A: {pool2.token_a}, Token B: {pool2.token_b}")
    print(f"  權重: {pool2.weight_a:.1%} / {pool2.weight_b:.1%}")
    
    # 測試 3: 帶額外數據的池
    print("\n測試 3: 帶 pool_data")
    pool_data = {
        "current_price": 2000.0,
        "fee_tier": 0.003
    }
    pool3 = parser.parse_pool("WETH-USDC", "uniswap-v3", pool_data)
    print(f"  Token A: {pool3.token_a}, Token B: {pool3.token_b}")
    print(f"  當前價格: {pool3.current_price}")
    print(f"  手續費層級: {pool3.fee_tier}")
    
    # 測試 4: 估算價格範圍
    print("\n測試 4: 估算價格範圍")
    price_lower, price_upper = parser.estimate_price_range(2000.0, 10.0)
    print(f"  當前價格: 2000.0")
    print(f"  價格範圍: {price_lower:.2f} - {price_upper:.2f}")

