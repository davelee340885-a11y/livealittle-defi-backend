import pandas as pd
import numpy as np
from datetime import datetime

class DeltaNeutralEngine:
    """
    Delta Neutral 對沖引擎
    
    核心功能：
    1. 計算 LP 池的 Delta 敞口
    2. 生成對沖建議（做空合約）
    3. 實時監控總 Delta
    """
    
    def __init__(self):
        self.positions = []  # 持倉列表
        self.target_delta = 0  # 目標 Delta（完全中性）
        self.delta_tolerance = 0.05  # Delta 容忍度（5%）
    
    def calculate_lp_delta(self, pool_info, position_value_usd):
        """
        計算 LP 池的 Delta
        
        假設：
        - 50/50 LP 池（如 ETH-USDC）
        - Delta = 池中風險資產的價值
        
        參數：
        - pool_info: 池信息（包含代幣對）
        - position_value_usd: LP 倉位總價值（美元）
        
        返回：
        - delta: Delta 值（美元）
        - risk_asset: 風險資產名稱
        """
        symbol = pool_info.get('symbol', '')
        
        # 識別風險資產（非穩定幣）
        stablecoins = ['USDC', 'USDT', 'DAI', 'BUSD', 'FRAX', 'USD1']
        tokens = symbol.split('-')
        
        risk_asset = None
        for token in tokens:
            if token not in stablecoins:
                risk_asset = token
                break
        
        if risk_asset is None:
            # 如果是穩定幣對穩定幣，Delta = 0
            return {
                'delta_usd': 0,
                'risk_asset': 'None (Stablecoin Pool)',
                'pool_type': 'Stable-Stable',
                'hedge_needed': False
            }
        
        # 對於 50/50 池，風險資產佔 50%
        delta_usd = position_value_usd * 0.5
        
        return {
            'delta_usd': delta_usd,
            'risk_asset': risk_asset,
            'pool_type': '50/50 LP',
            'hedge_needed': True
        }
    
    def calculate_hedge_amount(self, lp_delta_usd, current_price=None):
        """
        計算需要對沖的數量
        
        參數：
        - lp_delta_usd: LP 池的 Delta（美元）
        - current_price: 風險資產當前價格（可選）
        
        返回：
        - hedge_amount_usd: 需要做空的美元價值
        - hedge_amount_tokens: 需要做空的代幣數量（如果提供價格）
        """
        # 為了達到 Delta Neutral，需要做空等額的風險資產
        hedge_amount_usd = lp_delta_usd
        
        result = {
            'hedge_amount_usd': hedge_amount_usd,
            'action': 'OPEN_SHORT',
            'reason': f'LP Delta = ${lp_delta_usd:,.2f}, 需要做空等額以達到中性'
        }
        
        if current_price:
            hedge_amount_tokens = hedge_amount_usd / current_price
            result['hedge_amount_tokens'] = hedge_amount_tokens
        
        return result
    
    def add_position(self, position):
        """
        添加持倉
        
        position 格式：
        {
            'type': 'LP' | 'SHORT' | 'LONG',
            'pool_info': {...},  # 僅 LP 需要
            'value_usd': float,
            'asset': str,
            'timestamp': datetime
        }
        """
        self.positions.append(position)
    
    def calculate_portfolio_delta(self):
        """
        計算投資組合總 Delta
        
        返回：
        - total_delta_usd: 總 Delta（美元）
        - breakdown: 各部位的 Delta 明細
        """
        total_delta = 0
        breakdown = []
        
        for pos in self.positions:
            if pos['type'] == 'LP':
                delta_info = self.calculate_lp_delta(pos['pool_info'], pos['value_usd'])
                delta = delta_info['delta_usd']
                breakdown.append({
                    'type': 'LP',
                    'asset': delta_info['risk_asset'],
                    'value_usd': pos['value_usd'],
                    'delta_usd': delta,
                    'pool': pos['pool_info'].get('symbol', 'Unknown')
                })
            elif pos['type'] == 'SHORT':
                delta = -pos['value_usd']  # 做空的 Delta 為負
                breakdown.append({
                    'type': 'SHORT',
                    'asset': pos['asset'],
                    'value_usd': pos['value_usd'],
                    'delta_usd': delta,
                    'pool': 'Perpetual Contract'
                })
            elif pos['type'] == 'LONG':
                delta = pos['value_usd']  # 做多的 Delta 為正
                breakdown.append({
                    'type': 'LONG',
                    'asset': pos['asset'],
                    'value_usd': pos['value_usd'],
                    'delta_usd': delta,
                    'pool': 'Perpetual Contract'
                })
            
            total_delta += delta
        
        return {
            'total_delta_usd': total_delta,
            'breakdown': breakdown,
            'is_neutral': abs(total_delta) < (sum([p['value_usd'] for p in self.positions]) * self.delta_tolerance)
        }
    
    def generate_rebalance_suggestion(self):
        """
        生成再平衡建議
        
        返回：
        - action: 'HOLD' | 'OPEN_SHORT' | 'CLOSE_SHORT' | 'ADJUST_SHORT'
        - amount_usd: 需要調整的金額
        - reason: 原因說明
        """
        portfolio = self.calculate_portfolio_delta()
        total_delta = portfolio['total_delta_usd']
        
        if portfolio['is_neutral']:
            return {
                'action': 'HOLD',
                'amount_usd': 0,
                'reason': f'投資組合已達到 Delta Neutral（Delta = ${total_delta:,.2f}）'
            }
        
        if total_delta > 0:
            # Delta 為正，需要做空
            return {
                'action': 'OPEN_SHORT' if total_delta > 1000 else 'ADJUST_SHORT',
                'amount_usd': abs(total_delta),
                'reason': f'投資組合 Delta 為正（${total_delta:,.2f}），需要增加空頭倉位'
            }
        else:
            # Delta 為負，需要減少空頭或做多
            return {
                'action': 'CLOSE_SHORT',
                'amount_usd': abs(total_delta),
                'reason': f'投資組合 Delta 為負（${total_delta:,.2f}），需要減少空頭倉位'
            }
    
    def simulate_strategy(self, lp_pools, initial_capital=10000):
        """
        模擬 Delta Neutral 策略
        
        參數：
        - lp_pools: LP 池列表（從戴維斯雙擊分析中選出）
        - initial_capital: 初始資金
        
        返回：
        - strategy_plan: 完整的策略計劃
        """
        # 清空現有持倉
        self.positions = []
        
        # 分配資金到各個池
        capital_per_pool = initial_capital / len(lp_pools)
        
        strategy_plan = {
            'initial_capital': initial_capital,
            'lp_positions': [],
            'hedge_positions': [],
            'total_delta': 0,
            'is_neutral': False
        }
        
        for pool in lp_pools:
            # 1. 添加 LP 倉位
            lp_position = {
                'type': 'LP',
                'pool_info': pool,
                'value_usd': capital_per_pool,
                'asset': pool.get('symbol', 'Unknown'),
                'timestamp': datetime.now()
            }
            self.add_position(lp_position)
            strategy_plan['lp_positions'].append(lp_position)
            
            # 2. 計算對沖需求
            delta_info = self.calculate_lp_delta(pool, capital_per_pool)
            
            if delta_info['hedge_needed']:
                hedge_info = self.calculate_hedge_amount(delta_info['delta_usd'])
                
                # 添加對沖倉位
                hedge_position = {
                    'type': 'SHORT',
                    'asset': delta_info['risk_asset'],
                    'value_usd': hedge_info['hedge_amount_usd'],
                    'timestamp': datetime.now()
                }
                self.add_position(hedge_position)
                strategy_plan['hedge_positions'].append(hedge_position)
        
        # 3. 計算最終 Delta
        portfolio = self.calculate_portfolio_delta()
        strategy_plan['total_delta'] = portfolio['total_delta_usd']
        strategy_plan['is_neutral'] = portfolio['is_neutral']
        strategy_plan['breakdown'] = portfolio['breakdown']
        
        return strategy_plan

def demo_delta_neutral_strategy():
    """演示 Delta Neutral 策略"""
    
    print("="*80)
    print("Delta Neutral 對沖引擎演示")
    print("="*80)
    
    # 創建引擎
    engine = DeltaNeutralEngine()
    
    # 模擬從戴維斯雙擊分析中選出的池
    selected_pools = [
        {'symbol': 'WSOL-USDC', 'chain': 'Solana', 'project': 'raydium-amm', 'apy': 222.59},
        {'symbol': 'WETH-USDC', 'chain': 'Arbitrum', 'project': 'uniswap-v3', 'apy': 116.94},
        {'symbol': 'WAVAX-USDC', 'chain': 'Avalanche', 'project': 'joe-v2.1', 'apy': 317.03},
    ]
    
    # 模擬策略（初始資金 $10,000）
    initial_capital = 10000
    print(f"\n📊 模擬策略：初始資金 ${initial_capital:,}")
    print(f"選定池數量：{len(selected_pools)}")
    print(f"每池分配：${initial_capital/len(selected_pools):,.2f}\n")
    
    strategy = engine.simulate_strategy(selected_pools, initial_capital)
    
    # 顯示 LP 倉位
    print("\n💰 LP 倉位：")
    print("-" * 80)
    for i, pos in enumerate(strategy['lp_positions'], 1):
        print(f"{i}. {pos['pool_info']['symbol']} ({pos['pool_info']['chain']})")
        print(f"   投入：${pos['value_usd']:,.2f}")
        print(f"   APY：{pos['pool_info']['apy']:.2f}%")
        print(f"   協議：{pos['pool_info']['project']}")
        print()
    
    # 顯示對沖倉位
    print("\n🛡️ 對沖倉位（永續合約）：")
    print("-" * 80)
    for i, pos in enumerate(strategy['hedge_positions'], 1):
        print(f"{i}. 做空 {pos['asset']}")
        print(f"   金額：${pos['value_usd']:,.2f}")
        print(f"   目的：對沖 LP 池風險敞口")
        print()
    
    # 顯示 Delta 分析
    print("\n📈 Delta 分析：")
    print("-" * 80)
    print(f"總 Delta：${strategy['total_delta']:,.2f}")
    print(f"Delta Neutral 狀態：{'✅ 是' if strategy['is_neutral'] else '❌ 否'}")
    print()
    
    print("明細：")
    for item in strategy['breakdown']:
        sign = "+" if item['delta_usd'] > 0 else ""
        print(f"  {item['type']:6s} | {item['asset']:10s} | {sign}${item['delta_usd']:,.2f}")
    
    # 計算預期收益
    print("\n💵 預期收益（假設 APY 穩定）：")
    print("-" * 80)
    total_apy = sum([p['pool_info']['apy'] for p in strategy['lp_positions']]) / len(strategy['lp_positions'])
    daily_return = (total_apy / 100) * initial_capital / 365
    monthly_return = daily_return * 30
    yearly_return = (total_apy / 100) * initial_capital
    
    print(f"平均 APY：{total_apy:.2f}%")
    print(f"預期日收益：${daily_return:.2f}")
    print(f"預期月收益：${monthly_return:.2f}")
    print(f"預期年收益：${yearly_return:.2f}")
    
    print("\n⚠️ 風險提示：")
    print("-" * 80)
    print("1. 無常損失（IL）：LP 池仍有 IL 風險，Delta Neutral 只對沖價格風險")
    print("2. 資金費率：永續合約有資金費率成本，需定期監控")
    print("3. 滑點風險：大額交易可能產生滑點")
    print("4. 智能合約風險：協議可能存在漏洞")
    
    # 保存策略計劃
    df_lp = pd.DataFrame(strategy['lp_positions'])
    df_hedge = pd.DataFrame(strategy['hedge_positions'])
    
    df_lp.to_csv('/home/ubuntu/defi_system/backend/strategy_lp_positions.csv', index=False)
    df_hedge.to_csv('/home/ubuntu/defi_system/backend/strategy_hedge_positions.csv', index=False)
    
    print("\n✅ 策略計劃已保存到 CSV 文件")
    print("="*80)

if __name__ == '__main__':
    demo_delta_neutral_strategy()
