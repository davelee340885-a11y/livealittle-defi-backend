"""
協議安全性評分模塊

為 LAL 智能搜尋平台提供協議安全性評分功能
基於四個維度評估協議安全性: 代碼安全, 成熟度, 治理, 資產質量

作者: LAL Team
版本: V1.0
日期: 2025-10-17
"""

from typing import Dict, Tuple
from datetime import datetime
import math


class ProtocolSecurityScorer:
    """協議安全性評分器"""
    
    # 評級等級定義
    GRADE_THRESHOLDS = {
        'A': 90,
        'B': 75,
        'C': 60,
        'D': 40,
        'F': 0
    }
    
    # 安全性調整係數
    SAFETY_ADJUSTMENT_FACTORS = {
        'A': 1.00,
        'B': 0.95,
        'C': 0.85,
        'D': 0.70,
        'F': 0.50
    }
    
    # 已知協議的審計信息 (示例數據,實際應從數據庫或 API 獲取)
    PROTOCOL_AUDIT_INFO = {
        'uniswap-v3': {
            'audit_count': 4,
            'auditor_quality': 'top',  # top, good, unknown
            'hack_history': 'none'  # none, minor, major, multiple
        },
        'aerodrome': {
            'audit_count': 3,
            'auditor_quality': 'top',
            'hack_history': 'none'
        },
        'aave-v3': {
            'audit_count': 5,
            'auditor_quality': 'top',
            'hack_history': 'none'
        },
        'compound-v3': {
            'audit_count': 4,
            'auditor_quality': 'top',
            'hack_history': 'none'
        },
        'curve': {
            'audit_count': 3,
            'auditor_quality': 'top',
            'hack_history': 'minor'  # 有過小規模攻擊但已修復
        },
        'balancer-v2': {
            'audit_count': 3,
            'auditor_quality': 'top',
            'hack_history': 'none'
        },
        'pancakeswap-v3': {
            'audit_count': 2,
            'auditor_quality': 'good',
            'hack_history': 'none'
        },
        'sushiswap': {
            'audit_count': 2,
            'auditor_quality': 'good',
            'hack_history': 'minor'
        }
    }
    
    # 已知協議的治理信息
    PROTOCOL_GOVERNANCE_INFO = {
        'uniswap-v3': {
            'governance_type': 'multisig',  # decentralized, multisig, centralized
            'timelock': True,
            'governance_issues': 'none'  # none, minor, major
        },
        'aerodrome': {
            'governance_type': 'multisig',
            'timelock': True,
            'governance_issues': 'none'
        },
        'aave-v3': {
            'governance_type': 'decentralized',
            'timelock': True,
            'governance_issues': 'none'
        },
        'compound-v3': {
            'governance_type': 'decentralized',
            'timelock': True,
            'governance_issues': 'none'
        }
    }
    
    def __init__(self):
        """初始化評分器"""
        pass
    
    def calculate_security_score(self, protocol: str, tvl: float, 
                                 maturity_days: int, assets: list) -> Dict:
        """
        計算協議的安全性評分
        
        Args:
            protocol: 協議名稱 (如 'uniswap-v3')
            tvl: 協議 TVL (USD)
            maturity_days: 協議運行天數
            assets: 資產列表 (如 ['WETH', 'USDT'])
        
        Returns:
            Dict: 包含評分詳情的字典
        """
        # 1. 協議代碼安全 (40%)
        code_security_score = self._calculate_code_security(protocol)
        
        # 2. 協議成熟度 (30%)
        maturity_score = self._calculate_maturity(protocol, tvl, maturity_days)
        
        # 3. 治理和去中心化 (20%)
        governance_score = self._calculate_governance(protocol)
        
        # 4. 資產和抵押品質量 (10%)
        asset_score = self._calculate_asset_quality(assets, tvl)
        
        # 計算總分
        total_score = (
            code_security_score['score'] * 0.4 +
            maturity_score['score'] * 0.3 +
            governance_score['score'] * 0.2 +
            asset_score['score'] * 0.1
        )
        
        # 確定評級
        grade = self._get_grade(total_score)
        
        # 獲取調整係數
        adjustment_factor = self.SAFETY_ADJUSTMENT_FACTORS[grade]
        
        return {
            'total_score': round(total_score, 2),
            'grade': grade,
            'adjustment_factor': adjustment_factor,
            'breakdown': {
                'code_security': code_security_score,
                'maturity': maturity_score,
                'governance': governance_score,
                'asset_quality': asset_score
            }
        }
    
    def _calculate_code_security(self, protocol: str) -> Dict:
        """計算協議代碼安全評分 (40%)"""
        audit_info = self.PROTOCOL_AUDIT_INFO.get(protocol, {
            'audit_count': 0,
            'auditor_quality': 'unknown',
            'hack_history': 'unknown'
        })
        
        # 審計數量評分 (15%)
        audit_count = audit_info['audit_count']
        if audit_count >= 4:
            audit_count_score = 100
        elif audit_count == 3:
            audit_count_score = 85
        elif audit_count == 2:
            audit_count_score = 75
        elif audit_count == 1:
            audit_count_score = 60
        else:
            audit_count_score = 30  # 無審計或未知
        
        # 審計師質量評分 (15%)
        auditor_quality = audit_info['auditor_quality']
        if auditor_quality == 'top':
            auditor_score = 100
        elif auditor_quality == 'good':
            auditor_score = 70
        else:
            auditor_score = 40
        
        # 黑客攻擊歷史評分 (10%)
        hack_history = audit_info['hack_history']
        if hack_history == 'none':
            hack_score = 100
        elif hack_history == 'minor':
            hack_score = 70
        elif hack_history == 'major':
            hack_score = 30
        elif hack_history == 'multiple':
            hack_score = 0
        else:
            hack_score = 50  # 未知
        
        # 計算總分 (滿分 100)
        total = audit_count_score * 0.375 + auditor_score * 0.375 + hack_score * 0.25
        
        return {
            'score': round(total, 2),
            'weight': 40,
            'details': {
                'audit_count': audit_count,
                'audit_count_score': audit_count_score,
                'auditor_quality': auditor_quality,
                'auditor_score': auditor_score,
                'hack_history': hack_history,
                'hack_score': hack_score
            }
        }
    
    def _calculate_maturity(self, protocol: str, tvl: float, maturity_days: int) -> Dict:
        """計算協議成熟度評分 (30%)"""
        # TVL 排名評分 (15%) - 基於 TVL 大小估算排名
        if tvl >= 1_000_000_000:  # $1B+
            tvl_score = 100  # Top 10
        elif tvl >= 500_000_000:  # $500M+
            tvl_score = 90   # Top 20
        elif tvl >= 100_000_000:  # $100M+
            tvl_score = 80   # Top 50
        elif tvl >= 50_000_000:   # $50M+
            tvl_score = 70   # Top 100
        elif tvl >= 10_000_000:   # $10M+
            tvl_score = 60   # Top 200
        else:
            tvl_score = 50
        
        # 運行時間評分 (10%)
        maturity_years = maturity_days / 365.25
        if maturity_years >= 3:
            time_score = 100
        elif maturity_years >= 2:
            time_score = 85
        elif maturity_years >= 1:
            time_score = 70
        elif maturity_years >= 0.5:
            time_score = 60
        else:
            time_score = 50
        
        # 版本穩定性評分 (5%) - 簡化處理,假設主流協議都是穩定版
        stability_score = 100 if tvl >= 100_000_000 else 70
        
        # 計算總分 (滿分 100)
        total = tvl_score * 0.5 + time_score * 0.33 + stability_score * 0.17
        
        return {
            'score': round(total, 2),
            'weight': 30,
            'details': {
                'tvl': tvl,
                'tvl_score': tvl_score,
                'maturity_days': maturity_days,
                'maturity_years': round(maturity_years, 2),
                'time_score': time_score,
                'stability_score': stability_score
            }
        }
    
    def _calculate_governance(self, protocol: str) -> Dict:
        """計算治理和去中心化評分 (20%)"""
        gov_info = self.PROTOCOL_GOVERNANCE_INFO.get(protocol, {
            'governance_type': 'unknown',
            'timelock': False,
            'governance_issues': 'unknown'
        })
        
        # 治理集中度評分 (10%)
        governance_type = gov_info['governance_type']
        if governance_type == 'decentralized':
            gov_type_score = 100
        elif governance_type == 'multisig':
            gov_type_score = 75
        elif governance_type == 'centralized':
            gov_type_score = 30
        else:
            gov_type_score = 50  # 未知
        
        # 時間鎖設置評分 (5%)
        timelock_score = 100 if gov_info['timelock'] else 40
        
        # 治理問題歷史評分 (5%)
        governance_issues = gov_info['governance_issues']
        if governance_issues == 'none':
            issues_score = 100
        elif governance_issues == 'minor':
            issues_score = 70
        elif governance_issues == 'major':
            issues_score = 30
        else:
            issues_score = 60  # 未知
        
        # 計算總分 (滿分 100)
        total = gov_type_score * 0.5 + timelock_score * 0.25 + issues_score * 0.25
        
        return {
            'score': round(total, 2),
            'weight': 20,
            'details': {
                'governance_type': governance_type,
                'gov_type_score': gov_type_score,
                'timelock': gov_info['timelock'],
                'timelock_score': timelock_score,
                'governance_issues': governance_issues,
                'issues_score': issues_score
            }
        }
    
    def _calculate_asset_quality(self, assets: list, tvl: float) -> Dict:
        """計算資產和抵押品質量評分 (10%)"""
        # 藍籌資產列表
        BLUE_CHIP_ASSETS = ['ETH', 'WETH', 'BTC', 'WBTC']
        STABLECOINS = ['USDT', 'USDC', 'DAI', 'USDD', 'BUSD', 'FRAX']
        MAJOR_TOKENS = ['BNB', 'AVAX', 'MATIC', 'ARB', 'OP', 'SOL', 'LINK']
        
        # 抵押品類型評分 (5%)
        asset_types = []
        for asset in assets:
            asset_upper = asset.upper()
            if asset_upper in BLUE_CHIP_ASSETS:
                asset_types.append('blue_chip')
            elif asset_upper in STABLECOINS:
                asset_types.append('stablecoin')
            elif asset_upper in MAJOR_TOKENS:
                asset_types.append('major')
            else:
                asset_types.append('minor')
        
        # 計算平均資產質量
        if 'blue_chip' in asset_types:
            collateral_score = 100
        elif 'stablecoin' in asset_types and len(set(asset_types)) == 1:
            collateral_score = 90
        elif 'major' in asset_types:
            collateral_score = 70
        else:
            collateral_score = 50
        
        # 流動性深度評分 (5%) - 基於 TVL
        if tvl >= 100_000_000:  # $100M+
            liquidity_score = 100
        elif tvl >= 50_000_000:  # $50M+
            liquidity_score = 90
        elif tvl >= 10_000_000:  # $10M+
            liquidity_score = 75
        elif tvl >= 1_000_000:   # $1M+
            liquidity_score = 60
        else:
            liquidity_score = 50
        
        # 計算總分 (滿分 100)
        total = collateral_score * 0.5 + liquidity_score * 0.5
        
        return {
            'score': round(total, 2),
            'weight': 10,
            'details': {
                'assets': assets,
                'asset_types': asset_types,
                'collateral_score': collateral_score,
                'tvl': tvl,
                'liquidity_score': liquidity_score
            }
        }
    
    def _get_grade(self, score: float) -> str:
        """根據分數獲取評級"""
        if score >= self.GRADE_THRESHOLDS['A']:
            return 'A'
        elif score >= self.GRADE_THRESHOLDS['B']:
            return 'B'
        elif score >= self.GRADE_THRESHOLDS['C']:
            return 'C'
        elif score >= self.GRADE_THRESHOLDS['D']:
            return 'D'
        else:
            return 'F'
    
    def apply_safety_adjustment(self, davis_score: float, security_grade: str) -> float:
        """
        應用安全性調整係數到戴維斯評分
        
        Args:
            davis_score: 戴維斯評分 (0-100)
            security_grade: 安全性評級 (A-F)
        
        Returns:
            float: 調整後的最終評分
        """
        adjustment_factor = self.SAFETY_ADJUSTMENT_FACTORS.get(security_grade, 0.85)
        adjusted_score = davis_score * adjustment_factor
        return round(adjusted_score, 2)


# 測試代碼
if __name__ == "__main__":
    scorer = ProtocolSecurityScorer()
    
    # 測試 Uniswap V3
    print("=" * 60)
    print("測試 1: Uniswap V3 (Arbitrum)")
    print("=" * 60)
    
    security_result = scorer.calculate_security_score(
        protocol='uniswap-v3',
        tvl=2_500_000_000,  # $2.5B
        maturity_days=1095,  # 3 years
        assets=['WETH', 'USDT']
    )
    
    print(f"\n總分: {security_result['total_score']}/100")
    print(f"評級: {security_result['grade']}")
    print(f"調整係數: {security_result['adjustment_factor']}")
    
    print("\n評分細節:")
    for category, details in security_result['breakdown'].items():
        print(f"\n{category}:")
        print(f"  分數: {details['score']}/100 (權重: {details['weight']}%)")
        print(f"  詳情: {details['details']}")
    
    # 測試調整後的評分
    davis_score = 86.3
    adjusted_score = scorer.apply_safety_adjustment(davis_score, security_result['grade'])
    print(f"\n戴維斯評分: {davis_score}")
    print(f"調整後評分: {adjusted_score}")
    
    # 測試新興協議
    print("\n" + "=" * 60)
    print("測試 2: 新興協議")
    print("=" * 60)
    
    security_result2 = scorer.calculate_security_score(
        protocol='unknown-protocol',
        tvl=50_000_000,  # $50M
        maturity_days=180,  # 6 months
        assets=['TOKEN1', 'TOKEN2']
    )
    
    print(f"\n總分: {security_result2['total_score']}/100")
    print(f"評級: {security_result2['grade']}")
    print(f"調整係數: {security_result2['adjustment_factor']}")
    
    davis_score2 = 78.5
    adjusted_score2 = scorer.apply_safety_adjustment(davis_score2, security_result2['grade'])
    print(f"\n戴維斯評分: {davis_score2}")
    print(f"調整後評分: {adjusted_score2}")

