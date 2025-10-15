"""
LP 篩選器
提供多維度的 LP 池篩選功能
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class FilterCriteria:
    """篩選條件"""
    # TVL 範圍
    min_tvl: Optional[float] = None
    max_tvl: Optional[float] = None
    
    # APY 範圍
    min_apy: Optional[float] = None
    max_apy: Optional[float] = None
    
    # 協議列表
    protocols: Optional[List[str]] = None
    
    # 鏈列表
    chains: Optional[List[str]] = None
    
    # 代幣篩選
    include_tokens: Optional[List[str]] = None
    exclude_tokens: Optional[List[str]] = None
    
    # 戴維斯評分範圍
    min_davis_score: Optional[float] = None
    max_davis_score: Optional[float] = None
    davis_categories: Optional[List[str]] = None
    
    # 穩定性
    min_base_apy_ratio: Optional[float] = None
    
    # 風險等級
    il_risk: Optional[str] = None  # low/medium/high
    
    # Gas 成本
    max_gas_cost: Optional[float] = None
    
    # 排序
    sort_by: str = "final_score"
    sort_order: str = "desc"
    
    # 分頁
    limit: int = 5
    offset: int = 0


class LPFilter:
    """LP 池篩選器"""
    
    # 支持的協議列表
    SUPPORTED_PROTOCOLS = [
        "uniswap-v3", "uniswap-v2", "curve-dex", "balancer-v2",
        "pancakeswap", "sushiswap", "aerodrome", "velodrome",
        "trader-joe", "quickswap", "spookyswap", "spiritswap"
    ]
    
    # 支持的鏈列表
    SUPPORTED_CHAINS = [
        "Ethereum", "Arbitrum", "Optimism", "Base", "Polygon",
        "BSC", "Avalanche", "Fantom", "Gnosis", "Celo"
    ]
    
    # 戴維斯評級
    DAVIS_CATEGORIES = ["極佳", "優質", "良好", "一般", "不推薦"]
    
    # 風險等級
    IL_RISK_LEVELS = ["low", "medium", "high"]
    
    # 排序字段
    SORT_FIELDS = [
        "final_score", "net_apy", "tvl", "davis_score",
        "roi", "net_profit", "lp_apy", "total_apy"
    ]
    
    def __init__(self):
        """初始化篩選器"""
        pass
    
    def validate_criteria(self, criteria: FilterCriteria) -> Dict[str, Any]:
        """
        驗證篩選條件
        
        Returns:
            dict: 驗證結果 {"valid": bool, "errors": list}
        """
        errors = []
        
        # 驗證 TVL 範圍
        if criteria.min_tvl is not None and criteria.min_tvl < 0:
            errors.append("min_tvl 必須 >= 0")
        
        if criteria.max_tvl is not None and criteria.max_tvl < 0:
            errors.append("max_tvl 必須 >= 0")
        
        if (criteria.min_tvl is not None and criteria.max_tvl is not None and 
            criteria.min_tvl > criteria.max_tvl):
            errors.append("min_tvl 不能大於 max_tvl")
        
        # 驗證 APY 範圍
        if criteria.min_apy is not None and criteria.min_apy < 0:
            errors.append("min_apy 必須 >= 0")
        
        if criteria.max_apy is not None and criteria.max_apy < 0:
            errors.append("max_apy 必須 >= 0")
        
        if (criteria.min_apy is not None and criteria.max_apy is not None and 
            criteria.min_apy > criteria.max_apy):
            errors.append("min_apy 不能大於 max_apy")
        
        # 驗證協議
        if criteria.protocols:
            invalid_protocols = [p for p in criteria.protocols 
                               if p not in self.SUPPORTED_PROTOCOLS]
            if invalid_protocols:
                errors.append(f"不支持的協議: {', '.join(invalid_protocols)}")
        
        # 驗證鏈
        if criteria.chains:
            invalid_chains = [c for c in criteria.chains 
                            if c not in self.SUPPORTED_CHAINS]
            if invalid_chains:
                errors.append(f"不支持的鏈: {', '.join(invalid_chains)}")
        
        # 驗證戴維斯評分
        if criteria.min_davis_score is not None and (
            criteria.min_davis_score < 0 or criteria.min_davis_score > 100
        ):
            errors.append("min_davis_score 必須在 0-100 之間")
        
        if criteria.max_davis_score is not None and (
            criteria.max_davis_score < 0 or criteria.max_davis_score > 100
        ):
            errors.append("max_davis_score 必須在 0-100 之間")
        
        # 驗證戴維斯評級
        if criteria.davis_categories:
            invalid_categories = [c for c in criteria.davis_categories 
                                if c not in self.DAVIS_CATEGORIES]
            if invalid_categories:
                errors.append(f"不支持的評級: {', '.join(invalid_categories)}")
        
        # 驗證基礎 APY 比例
        if criteria.min_base_apy_ratio is not None and (
            criteria.min_base_apy_ratio < 0 or criteria.min_base_apy_ratio > 100
        ):
            errors.append("min_base_apy_ratio 必須在 0-100 之間")
        
        # 驗證風險等級
        if criteria.il_risk and criteria.il_risk not in self.IL_RISK_LEVELS:
            errors.append(f"il_risk 必須是: {', '.join(self.IL_RISK_LEVELS)}")
        
        # 驗證 Gas 成本
        if criteria.max_gas_cost is not None and criteria.max_gas_cost < 0:
            errors.append("max_gas_cost 必須 >= 0")
        
        # 驗證排序字段
        if criteria.sort_by not in self.SORT_FIELDS:
            errors.append(f"sort_by 必須是: {', '.join(self.SORT_FIELDS)}")
        
        # 驗證排序方向
        if criteria.sort_order not in ["asc", "desc"]:
            errors.append("sort_order 必須是 'asc' 或 'desc'")
        
        # 驗證分頁
        if criteria.limit < 1 or criteria.limit > 100:
            errors.append("limit 必須在 1-100 之間")
        
        if criteria.offset < 0:
            errors.append("offset 必須 >= 0")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def filter_pools(
        self,
        pools: List[Dict[str, Any]],
        criteria: FilterCriteria
    ) -> List[Dict[str, Any]]:
        """
        篩選 LP 池
        
        Args:
            pools: LP 池列表
            criteria: 篩選條件
            
        Returns:
            list: 篩選後的池列表
        """
        filtered = pools.copy()
        
        # 1. TVL 篩選
        if criteria.min_tvl is not None:
            filtered = [p for p in filtered if p.get("tvl", 0) >= criteria.min_tvl]
        
        if criteria.max_tvl is not None:
            filtered = [p for p in filtered if p.get("tvl", 0) <= criteria.max_tvl]
        
        # 2. APY 篩選
        if criteria.min_apy is not None:
            filtered = [p for p in filtered 
                       if p.get("net_apy", p.get("lp_apy", 0)) >= criteria.min_apy]
        
        if criteria.max_apy is not None:
            filtered = [p for p in filtered 
                       if p.get("net_apy", p.get("lp_apy", 0)) <= criteria.max_apy]
        
        # 3. 協議篩選
        if criteria.protocols:
            filtered = [p for p in filtered if p.get("protocol") in criteria.protocols]
        
        # 4. 鏈篩選
        if criteria.chains:
            filtered = [p for p in filtered if p.get("chain") in criteria.chains]
        
        # 5. 代幣篩選
        if criteria.include_tokens:
            filtered = [p for p in filtered 
                       if self._pool_includes_tokens(p, criteria.include_tokens)]
        
        if criteria.exclude_tokens:
            filtered = [p for p in filtered 
                       if not self._pool_includes_tokens(p, criteria.exclude_tokens)]
        
        # 6. 戴維斯評分篩選
        if criteria.min_davis_score is not None:
            filtered = [p for p in filtered 
                       if p.get("davis_score", 0) >= criteria.min_davis_score]
        
        if criteria.max_davis_score is not None:
            filtered = [p for p in filtered 
                       if p.get("davis_score", 0) <= criteria.max_davis_score]
        
        # 7. 戴維斯評級篩選
        if criteria.davis_categories:
            filtered = [p for p in filtered 
                       if p.get("davis_category") in criteria.davis_categories]
        
        # 8. 基礎 APY 比例篩選
        if criteria.min_base_apy_ratio is not None:
            filtered = [p for p in filtered 
                       if self._get_base_apy_ratio(p) >= criteria.min_base_apy_ratio]
        
        # 9. 風險等級篩選
        if criteria.il_risk:
            filtered = [p for p in filtered 
                       if self._get_il_risk(p) == criteria.il_risk]
        
        # 10. Gas 成本篩選
        if criteria.max_gas_cost is not None:
            filtered = [p for p in filtered 
                       if p.get("gas_cost_annual", 0) <= criteria.max_gas_cost]
        
        # 11. 排序
        filtered = self._sort_pools(filtered, criteria.sort_by, criteria.sort_order)
        
        # 12. 分頁
        start = criteria.offset
        end = start + criteria.limit
        filtered = filtered[start:end]
        
        return filtered
    
    def _pool_includes_tokens(self, pool: Dict[str, Any], tokens: List[str]) -> bool:
        """檢查池是否包含指定代幣"""
        symbol = pool.get("symbol", "")
        symbol_upper = symbol.upper()
        
        for token in tokens:
            token_upper = token.upper()
            if token_upper in symbol_upper:
                return True
        
        return False
    
    def _get_base_apy_ratio(self, pool: Dict[str, Any]) -> float:
        """計算基礎 APY 比例"""
        lp_apy = pool.get("lp_apy", 0)
        apy_base = pool.get("apy_base", lp_apy)
        
        if lp_apy == 0:
            return 0
        
        return (apy_base / lp_apy) * 100
    
    def _get_il_risk(self, pool: Dict[str, Any]) -> str:
        """
        判斷無常損失風險等級
        
        邏輯:
        - low: 穩定幣對（USDC-USDT, DAI-USDC 等）
        - medium: 一個穩定幣（ETH-USDC, BTC-USDT 等）
        - high: 兩個波動代幣（ETH-BTC, ETH-LINK 等）
        """
        symbol = pool.get("symbol", "").upper()
        
        stablecoins = ["USDC", "USDT", "DAI", "FRAX", "LUSD", "BUSD", "TUSD", "USDP"]
        
        # 計算穩定幣數量
        stable_count = sum(1 for stable in stablecoins if stable in symbol)
        
        if stable_count >= 2:
            return "low"
        elif stable_count == 1:
            return "medium"
        else:
            return "high"
    
    def _sort_pools(
        self,
        pools: List[Dict[str, Any]],
        sort_by: str,
        sort_order: str
    ) -> List[Dict[str, Any]]:
        """排序池列表"""
        if not pools:
            return pools
        
        reverse = (sort_order == "desc")
        
        try:
            sorted_pools = sorted(
                pools,
                key=lambda p: p.get(sort_by, 0),
                reverse=reverse
            )
            return sorted_pools
        except Exception as e:
            print(f"排序錯誤: {e}")
            return pools
    
    def get_filter_summary(
        self,
        criteria: FilterCriteria,
        total_before: int,
        total_after: int
    ) -> Dict[str, Any]:
        """
        生成篩選摘要
        
        Returns:
            dict: 篩選摘要信息
        """
        filters_applied = {}
        
        if criteria.min_tvl is not None or criteria.max_tvl is not None:
            filters_applied["tvl"] = {
                "min": criteria.min_tvl,
                "max": criteria.max_tvl
            }
        
        if criteria.min_apy is not None or criteria.max_apy is not None:
            filters_applied["apy"] = {
                "min": criteria.min_apy,
                "max": criteria.max_apy
            }
        
        if criteria.protocols:
            filters_applied["protocols"] = criteria.protocols
        
        if criteria.chains:
            filters_applied["chains"] = criteria.chains
        
        if criteria.include_tokens:
            filters_applied["include_tokens"] = criteria.include_tokens
        
        if criteria.exclude_tokens:
            filters_applied["exclude_tokens"] = criteria.exclude_tokens
        
        if criteria.min_davis_score is not None or criteria.max_davis_score is not None:
            filters_applied["davis_score"] = {
                "min": criteria.min_davis_score,
                "max": criteria.max_davis_score
            }
        
        if criteria.davis_categories:
            filters_applied["davis_categories"] = criteria.davis_categories
        
        if criteria.min_base_apy_ratio is not None:
            filters_applied["min_base_apy_ratio"] = criteria.min_base_apy_ratio
        
        if criteria.il_risk:
            filters_applied["il_risk"] = criteria.il_risk
        
        if criteria.max_gas_cost is not None:
            filters_applied["max_gas_cost"] = criteria.max_gas_cost
        
        return {
            "total_before_filter": total_before,
            "total_after_filter": total_after,
            "filtered_out": total_before - total_after,
            "filters_applied": filters_applied,
            "sort_by": criteria.sort_by,
            "sort_order": criteria.sort_order
        }


# ==================== 測試 ====================

if __name__ == "__main__":
    print("🧪 測試 LP 篩選器...")
    
    # 創建篩選器
    lp_filter = LPFilter()
    
    # 測試數據
    test_pools = [
        {
            "pool_id": "1",
            "protocol": "uniswap-v3",
            "chain": "Ethereum",
            "symbol": "WETH-USDC",
            "tvl": 100_000_000,
            "lp_apy": 50,
            "net_apy": 45,
            "davis_score": 95,
            "davis_category": "極佳",
            "gas_cost_annual": 500
        },
        {
            "pool_id": "2",
            "protocol": "curve-dex",
            "chain": "Arbitrum",
            "symbol": "USDC-USDT",
            "tvl": 50_000_000,
            "lp_apy": 20,
            "net_apy": 19.5,
            "davis_score": 85,
            "davis_category": "優質",
            "gas_cost_annual": 10
        },
        {
            "pool_id": "3",
            "protocol": "uniswap-v3",
            "chain": "Optimism",
            "symbol": "ETH-BTC",
            "tvl": 30_000_000,
            "lp_apy": 80,
            "net_apy": 75,
            "davis_score": 100,
            "davis_category": "極佳",
            "gas_cost_annual": 20
        }
    ]
    
    # 測試 1: 基本篩選
    print("\n測試 1: TVL > 40M")
    criteria = FilterCriteria(min_tvl=40_000_000)
    validation = lp_filter.validate_criteria(criteria)
    print(f"驗證結果: {validation}")
    
    if validation["valid"]:
        filtered = lp_filter.filter_pools(test_pools, criteria)
        print(f"篩選結果: {len(filtered)} 個池")
        for pool in filtered:
            print(f"  - {pool['symbol']}: TVL ${pool['tvl']:,.0f}")
    
    # 測試 2: 鏈篩選
    print("\n測試 2: 只要 L2 (Arbitrum, Optimism)")
    criteria = FilterCriteria(chains=["Arbitrum", "Optimism"])
    filtered = lp_filter.filter_pools(test_pools, criteria)
    print(f"篩選結果: {len(filtered)} 個池")
    for pool in filtered:
        print(f"  - {pool['symbol']} on {pool['chain']}")
    
    # 測試 3: 風險篩選
    print("\n測試 3: 低風險池（穩定幣對）")
    criteria = FilterCriteria(il_risk="low")
    filtered = lp_filter.filter_pools(test_pools, criteria)
    print(f"篩選結果: {len(filtered)} 個池")
    for pool in filtered:
        risk = lp_filter._get_il_risk(pool)
        print(f"  - {pool['symbol']}: 風險等級 {risk}")
    
    # 測試 4: 組合篩選
    print("\n測試 4: 組合篩選（高 APY + L2 + 低 Gas）")
    criteria = FilterCriteria(
        min_apy=30,
        chains=["Arbitrum", "Optimism"],
        max_gas_cost=50,
        sort_by="net_apy",
        sort_order="desc"
    )
    filtered = lp_filter.filter_pools(test_pools, criteria)
    print(f"篩選結果: {len(filtered)} 個池")
    for pool in filtered:
        print(f"  - {pool['symbol']}: APY {pool['net_apy']:.2f}%, Gas ${pool['gas_cost_annual']}")
    
    # 測試 5: 篩選摘要
    print("\n測試 5: 篩選摘要")
    summary = lp_filter.get_filter_summary(criteria, len(test_pools), len(filtered))
    print(f"篩選摘要:")
    print(f"  - 篩選前: {summary['total_before_filter']} 個池")
    print(f"  - 篩選後: {summary['total_after_filter']} 個池")
    print(f"  - 過濾掉: {summary['filtered_out']} 個池")
    print(f"  - 應用的篩選: {list(summary['filters_applied'].keys())}")
    
    print("\n✅ 測試完成！")

