import pandas as pd
import numpy as np
from datetime import datetime
import json

class SmartRebalancer:
    """
    智能轉倉系統
    
    核心功能：
    1. 監控現有 LP 池的戴維斯雙擊評分
    2. 尋找更優質的替代池
    3. 計算轉倉成本效益
    4. 生成轉倉計劃並維持 Delta Neutral
    """
    
    def __init__(self):
        self.rebalance_threshold = 20  # 評分差距閾值
        self.min_apy_improvement = 10  # 最小 APY 提升（百分點）
        self.gas_cost_estimate = 50  # 預估 Gas 費用（USD）
        self.slippage_estimate = 0.005  # 預估滑點（0.5%）
        
    def load_current_positions(self):
        """載入當前持倉"""
        # 模擬當前持倉
        return [
            {
                'pool_id': 'raydium-wsol-usdc',
                'chain': 'Solana',
                'protocol': 'raydium-amm',
                'symbol': 'WSOL-USDC',
                'tvl_usd': 16870000,
                'apy': 222.59,
                'davis_score': 100,
                'position_size_usd': 3333.33,
                'entry_date': '2025-10-01',
                'days_held': 14
            },
            {
                'pool_id': 'uniswap-weth-usdc-arb',
                'chain': 'Arbitrum',
                'protocol': 'uniswap-v3',
                'symbol': 'WETH-USDC',
                'tvl_usd': 87130000,
                'apy': 116.94,
                'davis_score': 95,
                'position_size_usd': 3333.33,
                'entry_date': '2025-10-01',
                'days_held': 14
            },
            {
                'pool_id': 'joe-wavax-usdc',
                'chain': 'Avalanche',
                'protocol': 'joe-v2.1',
                'symbol': 'WAVAX-USDC',
                'tvl_usd': 14960000,
                'apy': 317.03,
                'davis_score': 100,
                'position_size_usd': 3333.33,
                'entry_date': '2025-10-01',
                'days_held': 14
            }
        ]
    
    def load_alternative_pools(self):
        """載入替代池選項（從戴維斯雙擊分析器）"""
        # 模擬高評分的替代池
        return [
            {
                'pool_id': 'hyperliquid-hype-usdc',
                'chain': 'Arbitrum',
                'protocol': 'hyperliquid',
                'symbol': 'HYPE-USDC',
                'tvl_usd': 5000000,
                'apy': 450.0,
                'davis_score': 100,
                'apy_7d_change': 25.0,
                'tvl_7d_change': 5.0
            },
            {
                'pool_id': 'jupiter-jup-usdc',
                'chain': 'Solana',
                'protocol': 'jupiter',
                'symbol': 'JUP-USDC',
                'tvl_usd': 8000000,
                'apy': 380.0,
                'davis_score': 100,
                'apy_7d_change': 30.0,
                'tvl_7d_change': 8.0
            },
            {
                'pool_id': 'pancake-cake-usdc',
                'chain': 'BSC',
                'protocol': 'pancakeswap',
                'symbol': 'CAKE-USDC',
                'tvl_usd': 12000000,
                'apy': 280.0,
                'davis_score': 95,
                'apy_7d_change': 15.0,
                'tvl_7d_change': 3.0
            }
        ]
    
    def evaluate_rebalance_opportunity(self, current_pool, alternative_pool):
        """
        評估轉倉機會
        
        考慮因素：
        1. APY 提升
        2. 戴維斯評分提升
        3. 轉倉成本（Gas + 滑點）
        4. 預期收益增量
        """
        # 1. APY 提升
        apy_improvement = alternative_pool['apy'] - current_pool['apy']
        
        # 2. 評分提升
        score_improvement = alternative_pool['davis_score'] - current_pool['davis_score']
        
        # 3. 估算轉倉成本
        position_size = current_pool['position_size_usd']
        gas_cost = self.gas_cost_estimate
        slippage_cost = position_size * self.slippage_estimate * 2  # 進出各一次
        total_cost = gas_cost + slippage_cost
        
        # 4. 預期收益增量（假設持有 30 天）
        days_to_hold = 30
        current_expected_return = position_size * (current_pool['apy'] / 100) * (days_to_hold / 365)
        alternative_expected_return = position_size * (alternative_pool['apy'] / 100) * (days_to_hold / 365)
        net_benefit = alternative_expected_return - current_expected_return - total_cost
        
        # 5. 回本天數
        if apy_improvement > 0:
            daily_extra_return = position_size * (apy_improvement / 100) / 365
            payback_days = total_cost / daily_extra_return if daily_extra_return > 0 else 999
        else:
            payback_days = 999
        
        # 6. 決策
        should_rebalance = (
            apy_improvement >= self.min_apy_improvement and
            score_improvement >= 0 and
            net_benefit > 0 and
            payback_days <= 7  # 7天內回本
        )
        
        return {
            'should_rebalance': should_rebalance,
            'apy_improvement': apy_improvement,
            'score_improvement': score_improvement,
            'total_cost': total_cost,
            'net_benefit_30d': net_benefit,
            'payback_days': payback_days,
            'current_pool': current_pool,
            'alternative_pool': alternative_pool
        }
    
    def generate_rebalance_plan(self, opportunities):
        """生成轉倉計劃"""
        plan = {
            'timestamp': datetime.now().isoformat(),
            'total_positions': len(opportunities),
            'rebalance_actions': [],
            'hold_actions': [],
            'total_expected_benefit': 0,
            'total_cost': 0
        }
        
        for opp in opportunities:
            if opp['should_rebalance']:
                action = {
                    'action': 'REBALANCE',
                    'from_pool': f"{opp['current_pool']['symbol']} ({opp['current_pool']['chain']})",
                    'to_pool': f"{opp['alternative_pool']['symbol']} ({opp['alternative_pool']['chain']})",
                    'position_size': opp['current_pool']['position_size_usd'],
                    'apy_from': opp['current_pool']['apy'],
                    'apy_to': opp['alternative_pool']['apy'],
                    'apy_improvement': opp['apy_improvement'],
                    'cost': opp['total_cost'],
                    'net_benefit_30d': opp['net_benefit_30d'],
                    'payback_days': opp['payback_days'],
                    'priority': 'HIGH' if opp['payback_days'] <= 3 else 'MEDIUM'
                }
                plan['rebalance_actions'].append(action)
                plan['total_expected_benefit'] += opp['net_benefit_30d']
                plan['total_cost'] += opp['total_cost']
            else:
                action = {
                    'action': 'HOLD',
                    'pool': f"{opp['current_pool']['symbol']} ({opp['current_pool']['chain']})",
                    'reason': self._get_hold_reason(opp)
                }
                plan['hold_actions'].append(action)
        
        return plan
    
    def _get_hold_reason(self, opp):
        """獲取持有原因"""
        if opp['apy_improvement'] < self.min_apy_improvement:
            return f"APY 提升不足 ({opp['apy_improvement']:.1f}% < {self.min_apy_improvement}%)"
        elif opp['net_benefit_30d'] <= 0:
            return f"30天淨收益為負 (${opp['net_benefit_30d']:.2f})"
        elif opp['payback_days'] > 7:
            return f"回本天數過長 ({opp['payback_days']:.1f} 天)"
        else:
            return "當前池表現良好"
    
    def generate_delta_adjustment_plan(self, rebalance_actions):
        """
        生成 Delta 調整計劃
        
        確保在轉倉過程中維持 Delta Neutral
        """
        adjustments = []
        
        for action in rebalance_actions:
            from_pool = action['from_pool']
            to_pool = action['to_pool']
            position_size = action['position_size']
            
            # 提取資產名稱（簡化版）
            from_asset = from_pool.split('-')[0]
            to_asset = to_pool.split('-')[0]
            
            # 如果資產不同，需要調整對沖
            if from_asset != to_asset:
                adjustments.append({
                    'step': 1,
                    'action': 'CLOSE_HEDGE',
                    'asset': from_asset,
                    'amount_usd': position_size * 0.5,
                    'reason': f'平倉 {from_asset} 空頭，準備退出 {from_pool}'
                })
                adjustments.append({
                    'step': 2,
                    'action': 'EXIT_LP',
                    'pool': from_pool,
                    'amount_usd': position_size,
                    'reason': '退出舊 LP 池'
                })
                adjustments.append({
                    'step': 3,
                    'action': 'ENTER_LP',
                    'pool': to_pool,
                    'amount_usd': position_size,
                    'reason': '進入新 LP 池'
                })
                adjustments.append({
                    'step': 4,
                    'action': 'OPEN_HEDGE',
                    'asset': to_asset,
                    'amount_usd': position_size * 0.5,
                    'reason': f'開設 {to_asset} 空頭，維持 Delta Neutral'
                })
            else:
                # 資產相同，只需換池
                adjustments.append({
                    'step': 1,
                    'action': 'EXIT_LP',
                    'pool': from_pool,
                    'amount_usd': position_size,
                    'reason': '退出舊 LP 池'
                })
                adjustments.append({
                    'step': 2,
                    'action': 'ENTER_LP',
                    'pool': to_pool,
                    'amount_usd': position_size,
                    'reason': '進入新 LP 池（對沖倉位無需調整）'
                })
        
        return adjustments
    
    def run_rebalance_analysis(self):
        """運行完整的轉倉分析"""
        print("="*80)
        print("智能轉倉系統 - 分析報告")
        print("="*80)
        
        # 載入數據
        current_positions = self.load_current_positions()
        alternative_pools = self.load_alternative_pools()
        
        print(f"\n📊 當前持倉：{len(current_positions)} 個池")
        print(f"🔍 替代池候選：{len(alternative_pools)} 個池")
        
        # 評估每個持倉
        opportunities = []
        
        for current in current_positions:
            print(f"\n{'='*80}")
            print(f"分析持倉：{current['symbol']} ({current['chain']})")
            print(f"  當前 APY：{current['apy']:.2f}%")
            print(f"  戴維斯評分：{current['davis_score']}")
            print(f"  持倉規模：${current['position_size_usd']:,.2f}")
            
            # 尋找最佳替代池
            best_alternative = None
            best_benefit = 0
            
            for alternative in alternative_pools:
                opp = self.evaluate_rebalance_opportunity(current, alternative)
                
                if opp['should_rebalance'] and opp['net_benefit_30d'] > best_benefit:
                    best_alternative = opp
                    best_benefit = opp['net_benefit_30d']
            
            if best_alternative:
                opportunities.append(best_alternative)
                print(f"\n  ✅ 發現轉倉機會：")
                print(f"     目標池：{best_alternative['alternative_pool']['symbol']} ({best_alternative['alternative_pool']['chain']})")
                print(f"     APY 提升：{best_alternative['apy_improvement']:.2f}% ({best_alternative['current_pool']['apy']:.2f}% → {best_alternative['alternative_pool']['apy']:.2f}%)")
                print(f"     轉倉成本：${best_alternative['total_cost']:.2f}")
                print(f"     30天淨收益：${best_alternative['net_benefit_30d']:.2f}")
                print(f"     回本天數：{best_alternative['payback_days']:.1f} 天")
            else:
                # 創建持有記錄
                hold_opp = {
                    'should_rebalance': False,
                    'current_pool': current,
                    'alternative_pool': None,
                    'apy_improvement': 0,
                    'net_benefit_30d': 0
                }
                opportunities.append(hold_opp)
                print(f"\n  ⏸️  建議持有：當前池表現良好")
        
        # 生成轉倉計劃
        plan = self.generate_rebalance_plan(opportunities)
        
        # 顯示計劃
        print(f"\n{'='*80}")
        print("🎯 轉倉計劃總結")
        print("="*80)
        
        if plan['rebalance_actions']:
            print(f"\n📈 建議轉倉：{len(plan['rebalance_actions'])} 個池")
            print("-" * 80)
            
            for i, action in enumerate(plan['rebalance_actions'], 1):
                print(f"\n{i}. {action['from_pool']} → {action['to_pool']}")
                print(f"   優先級：{action['priority']}")
                print(f"   APY：{action['apy_from']:.2f}% → {action['apy_to']:.2f}% (+{action['apy_improvement']:.2f}%)")
                print(f"   成本：${action['cost']:.2f}")
                print(f"   30天淨收益：${action['net_benefit_30d']:.2f}")
                print(f"   回本天數：{action['payback_days']:.1f} 天")
            
            print(f"\n總預期收益（30天）：${plan['total_expected_benefit']:.2f}")
            print(f"總轉倉成本：${plan['total_cost']:.2f}")
            print(f"淨收益：${plan['total_expected_benefit'] - plan['total_cost']:.2f}")
            
            # 生成 Delta 調整計劃
            print(f"\n{'='*80}")
            print("🛡️ Delta Neutral 維護計劃")
            print("="*80)
            
            delta_adjustments = self.generate_delta_adjustment_plan(plan['rebalance_actions'])
            
            for adj in delta_adjustments:
                print(f"\nStep {adj['step']}: {adj['action']}")
                if 'pool' in adj:
                    print(f"  池：{adj['pool']}")
                if 'asset' in adj:
                    print(f"  資產：{adj['asset']}")
                print(f"  金額：${adj['amount_usd']:,.2f}")
                print(f"  原因：{adj['reason']}")
        
        if plan['hold_actions']:
            print(f"\n⏸️  建議持有：{len(plan['hold_actions'])} 個池")
            print("-" * 80)
            
            for action in plan['hold_actions']:
                print(f"  • {action['pool']}")
                print(f"    原因：{action['reason']}")
        
        # 保存計劃
        with open('/home/ubuntu/defi_system/backend/rebalance_plan.json', 'w') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*80}")
        print("✅ 轉倉計劃已保存到 rebalance_plan.json")
        print("="*80)
        
        return plan

def main():
    rebalancer = SmartRebalancer()
    plan = rebalancer.run_rebalance_analysis()

if __name__ == '__main__':
    main()
