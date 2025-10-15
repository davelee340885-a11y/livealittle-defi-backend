import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

class BacktestEngine:
    """
    DeFi 策略回測引擎
    
    核心功能：
    1. 模擬歷史策略表現
    2. 計算關鍵績效指標
    3. 對比不同策略
    4. 生成可視化報告
    """
    
    def __init__(self, initial_capital=10000, start_date='2024-01-01', end_date='2025-01-01'):
        self.initial_capital = initial_capital
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.risk_free_rate = 0.05  # 無風險利率 5%
        
    def generate_mock_market_data(self):
        """
        生成模擬市場數據
        
        包含：
        - BTC 價格
        - ETH 價格
        - SOL 價格
        - LP APY 變化
        - 資金費率
        """
        dates = pd.date_range(self.start_date, self.end_date, freq='D')
        n_days = len(dates)
        
        # 模擬價格走勢（帶趨勢和波動）
        np.random.seed(42)
        
        # BTC: 從 $40k 到 $110k（牛市）
        btc_trend = np.linspace(40000, 110000, n_days)
        btc_volatility = np.random.normal(0, 0.03, n_days).cumsum()
        btc_price = btc_trend * (1 + btc_volatility * 0.1)
        
        # ETH: 從 $2.2k 到 $4k
        eth_trend = np.linspace(2200, 4000, n_days)
        eth_volatility = np.random.normal(0, 0.04, n_days).cumsum()
        eth_price = eth_trend * (1 + eth_volatility * 0.1)
        
        # SOL: 從 $60 到 $200
        sol_trend = np.linspace(60, 200, n_days)
        sol_volatility = np.random.normal(0, 0.05, n_days).cumsum()
        sol_price = sol_trend * (1 + sol_volatility * 0.1)
        
        # LP APY（隨市場波動性變化）
        base_apy = 150
        apy_volatility = np.abs(np.random.normal(0, 50, n_days))
        lp_apy = base_apy + apy_volatility
        
        # 資金費率（正負交替，平均為正）
        funding_rate = np.random.normal(0.0001, 0.0002, n_days)  # 日資金費率
        
        df = pd.DataFrame({
            'date': dates,
            'btc_price': btc_price,
            'eth_price': eth_price,
            'sol_price': sol_price,
            'lp_apy': lp_apy,
            'funding_rate': funding_rate
        })
        
        return df
    
    def simulate_pure_lp_strategy(self, market_data):
        """
        模擬純 LP 策略（無對沖）
        
        收益 = LP 手續費 + 價格變動（IL）
        """
        results = []
        capital = self.initial_capital
        
        for i, row in market_data.iterrows():
            if i == 0:
                initial_price = row['btc_price']
                results.append({
                    'date': row['date'],
                    'capital': capital,
                    'daily_return': 0,
                    'cumulative_return': 0
                })
                continue
            
            # LP 收益（日化）
            lp_return = row['lp_apy'] / 100 / 365
            
            # 價格變動（簡化：假設 50% 敞口）
            price_change = (row['btc_price'] - market_data.iloc[i-1]['btc_price']) / market_data.iloc[i-1]['btc_price']
            price_return = price_change * 0.5
            
            # 無常損失（簡化：價格波動越大，IL 越大）
            il_loss = -abs(price_change) * 0.1  # 簡化模型
            
            # 總收益
            daily_return = lp_return + price_return + il_loss
            capital = capital * (1 + daily_return)
            
            cumulative_return = (capital - self.initial_capital) / self.initial_capital
            
            results.append({
                'date': row['date'],
                'capital': capital,
                'daily_return': daily_return,
                'cumulative_return': cumulative_return
            })
        
        return pd.DataFrame(results)
    
    def simulate_delta_neutral_strategy(self, market_data):
        """
        模擬 Delta Neutral 策略
        
        收益 = LP 手續費 - 資金費率
        價格風險 = 0（完全對沖）
        """
        results = []
        capital = self.initial_capital
        
        for i, row in market_data.iterrows():
            if i == 0:
                results.append({
                    'date': row['date'],
                    'capital': capital,
                    'daily_return': 0,
                    'cumulative_return': 0
                })
                continue
            
            # LP 收益（日化）
            lp_return = row['lp_apy'] / 100 / 365
            
            # 資金費率成本（做空需支付）
            funding_cost = row['funding_rate'] * 0.5  # 50% 倉位對沖
            
            # 總收益（無價格風險）
            daily_return = lp_return - funding_cost
            capital = capital * (1 + daily_return)
            
            cumulative_return = (capital - self.initial_capital) / self.initial_capital
            
            results.append({
                'date': row['date'],
                'capital': capital,
                'daily_return': daily_return,
                'cumulative_return': cumulative_return
            })
        
        return pd.DataFrame(results)
    
    def simulate_dynamic_strategy(self, market_data):
        """
        模擬動態策略（根據市場狀態調整對沖比例）
        
        牛市：30% 對沖（保留 70% 多頭敞口）
        熊市/橫盤：100% 對沖
        """
        results = []
        capital = self.initial_capital
        
        for i, row in market_data.iterrows():
            if i == 0:
                results.append({
                    'date': row['date'],
                    'capital': capital,
                    'daily_return': 0,
                    'cumulative_return': 0,
                    'hedge_ratio': 1.0
                })
                continue
            
            # 判斷市場狀態（簡化：30日移動平均）
            if i >= 30:
                ma_30 = market_data.iloc[i-30:i]['btc_price'].mean()
                current_price = row['btc_price']
                
                if current_price > ma_30 * 1.05:  # 牛市
                    hedge_ratio = 0.3
                elif current_price < ma_30 * 0.95:  # 熊市
                    hedge_ratio = 1.0
                else:  # 橫盤
                    hedge_ratio = 1.0
            else:
                hedge_ratio = 1.0
            
            # LP 收益
            lp_return = row['lp_apy'] / 100 / 365
            
            # 價格變動（根據對沖比例）
            price_change = (row['btc_price'] - market_data.iloc[i-1]['btc_price']) / market_data.iloc[i-1]['btc_price']
            exposure = 0.5 * (1 - hedge_ratio)  # 未對沖的敞口
            price_return = price_change * exposure
            
            # 資金費率成本
            funding_cost = row['funding_rate'] * 0.5 * hedge_ratio
            
            # 無常損失（部分對沖可減少 IL）
            il_loss = -abs(price_change) * 0.1 * (1 - hedge_ratio * 0.5)
            
            # 總收益
            daily_return = lp_return + price_return - funding_cost + il_loss
            capital = capital * (1 + daily_return)
            
            cumulative_return = (capital - self.initial_capital) / self.initial_capital
            
            results.append({
                'date': row['date'],
                'capital': capital,
                'daily_return': daily_return,
                'cumulative_return': cumulative_return,
                'hedge_ratio': hedge_ratio
            })
        
        return pd.DataFrame(results)
    
    def calculate_metrics(self, results_df):
        """
        計算關鍵績效指標
        """
        # 總收益率
        total_return = results_df.iloc[-1]['cumulative_return']
        
        # 年化收益率
        days = len(results_df)
        annual_return = (1 + total_return) ** (365 / days) - 1
        
        # 波動率（年化）
        daily_returns = results_df['daily_return'].dropna()
        volatility = daily_returns.std() * np.sqrt(365)
        
        # 夏普比率
        excess_return = annual_return - self.risk_free_rate
        sharpe_ratio = excess_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        cumulative_returns = results_df['cumulative_return']
        running_max = cumulative_returns.cummax()
        drawdown = cumulative_returns - running_max
        max_drawdown = drawdown.min()
        
        # 勝率
        win_rate = (daily_returns > 0).sum() / len(daily_returns)
        
        # 最終資本
        final_capital = results_df.iloc[-1]['capital']
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'final_capital': final_capital,
            'initial_capital': self.initial_capital
        }
    
    def run_backtest(self):
        """
        運行完整回測
        """
        print("="*80)
        print("DeFi 策略回測引擎")
        print("="*80)
        print(f"\n回測期間：{self.start_date.date()} 至 {self.end_date.date()}")
        print(f"初始資金：${self.initial_capital:,.2f}")
        
        # 生成市場數據
        print("\n正在生成模擬市場數據...")
        market_data = self.generate_mock_market_data()
        
        # 模擬三種策略
        print("\n正在模擬策略表現...")
        print("  1. 純 LP 策略（無對沖）")
        pure_lp = self.simulate_pure_lp_strategy(market_data)
        
        print("  2. Delta Neutral 策略（完全對沖）")
        delta_neutral = self.simulate_delta_neutral_strategy(market_data)
        
        print("  3. 動態策略（智能調整對沖比例）")
        dynamic = self.simulate_dynamic_strategy(market_data)
        
        # 計算指標
        print("\n正在計算績效指標...")
        metrics = {
            'pure_lp': self.calculate_metrics(pure_lp),
            'delta_neutral': self.calculate_metrics(delta_neutral),
            'dynamic': self.calculate_metrics(dynamic)
        }
        
        # 顯示結果
        self.display_results(metrics)
        
        # 生成圖表
        print("\n正在生成可視化報告...")
        self.plot_results(pure_lp, delta_neutral, dynamic, market_data)
        
        # 保存結果
        self.save_results(metrics, pure_lp, delta_neutral, dynamic)
        
        return metrics, pure_lp, delta_neutral, dynamic
    
    def display_results(self, metrics):
        """顯示回測結果"""
        print(f"\n{'='*80}")
        print("📊 回測結果總結")
        print("="*80)
        
        strategies = {
            'pure_lp': '純 LP 策略',
            'delta_neutral': 'Delta Neutral 策略',
            'dynamic': '動態策略'
        }
        
        print(f"\n{'策略':<20} | {'總收益':>10} | {'年化收益':>10} | {'夏普比率':>10} | {'最大回撤':>10} | {'勝率':>8}")
        print("-" * 90)
        
        for key, name in strategies.items():
            m = metrics[key]
            print(f"{name:<20} | {m['total_return']*100:>9.2f}% | {m['annual_return']*100:>9.2f}% | {m['sharpe_ratio']:>10.2f} | {m['max_drawdown']*100:>9.2f}% | {m['win_rate']*100:>7.1f}%")
        
        print("\n" + "="*80)
        print("💡 指標說明：")
        print("  • 總收益：整個回測期間的總收益率")
        print("  • 年化收益：換算成年化的收益率")
        print("  • 夏普比率：風險調整後的收益（>1 為優秀，>2 為卓越）")
        print("  • 最大回撤：歷史最大虧損幅度（越小越好）")
        print("  • 勝率：盈利天數佔比")
        print("="*80)
        
        # 推薦策略
        best_sharpe = max(metrics.items(), key=lambda x: x[1]['sharpe_ratio'])
        best_return = max(metrics.items(), key=lambda x: x[1]['annual_return'])
        lowest_drawdown = min(metrics.items(), key=lambda x: abs(x[1]['max_drawdown']))
        
        print(f"\n🏆 最佳策略：")
        print(f"  • 最高夏普比率：{strategies[best_sharpe[0]]} ({best_sharpe[1]['sharpe_ratio']:.2f})")
        print(f"  • 最高年化收益：{strategies[best_return[0]]} ({best_return[1]['annual_return']*100:.2f}%)")
        print(f"  • 最小回撤：{strategies[lowest_drawdown[0]]} ({lowest_drawdown[1]['max_drawdown']*100:.2f}%)")
    
    def plot_results(self, pure_lp, delta_neutral, dynamic, market_data):
        """生成可視化圖表"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. 收益曲線對比
        ax1 = axes[0, 0]
        ax1.plot(pure_lp['date'], pure_lp['cumulative_return'] * 100, label='純 LP 策略', linewidth=2)
        ax1.plot(delta_neutral['date'], delta_neutral['cumulative_return'] * 100, label='Delta Neutral 策略', linewidth=2)
        ax1.plot(dynamic['date'], dynamic['cumulative_return'] * 100, label='動態策略', linewidth=2)
        ax1.set_title('累積收益率對比', fontsize=14, fontweight='bold')
        ax1.set_xlabel('日期')
        ax1.set_ylabel('累積收益率 (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 資本曲線
        ax2 = axes[0, 1]
        ax2.plot(pure_lp['date'], pure_lp['capital'], label='純 LP 策略', linewidth=2)
        ax2.plot(delta_neutral['date'], delta_neutral['capital'], label='Delta Neutral 策略', linewidth=2)
        ax2.plot(dynamic['date'], dynamic['capital'], label='動態策略', linewidth=2)
        ax2.axhline(y=self.initial_capital, color='gray', linestyle='--', label='初始資金')
        ax2.set_title('資本曲線', fontsize=14, fontweight='bold')
        ax2.set_xlabel('日期')
        ax2.set_ylabel('資本 (USD)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 回撤分析
        ax3 = axes[1, 0]
        for df, label in [(pure_lp, '純 LP'), (delta_neutral, 'Delta Neutral'), (dynamic, '動態')]:
            running_max = df['cumulative_return'].cummax()
            drawdown = (df['cumulative_return'] - running_max) * 100
            ax3.fill_between(df['date'], drawdown, 0, alpha=0.3, label=label)
        ax3.set_title('回撤分析', fontsize=14, fontweight='bold')
        ax3.set_xlabel('日期')
        ax3.set_ylabel('回撤 (%)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 市場價格（BTC）
        ax4 = axes[1, 1]
        ax4.plot(market_data['date'], market_data['btc_price'], color='orange', linewidth=2)
        ax4.set_title('BTC 價格走勢', fontsize=14, fontweight='bold')
        ax4.set_xlabel('日期')
        ax4.set_ylabel('BTC 價格 (USD)')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('/home/ubuntu/defi_system/backend/backtest_results.png', dpi=300, bbox_inches='tight')
        print("  ✅ 圖表已保存到 backtest_results.png")
        
        plt.close()
    
    def save_results(self, metrics, pure_lp, delta_neutral, dynamic):
        """保存回測結果"""
        # 保存指標
        with open('/home/ubuntu/defi_system/backend/backtest_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        
        # 保存詳細數據
        pure_lp.to_csv('/home/ubuntu/defi_system/backend/backtest_pure_lp.csv', index=False)
        delta_neutral.to_csv('/home/ubuntu/defi_system/backend/backtest_delta_neutral.csv', index=False)
        dynamic.to_csv('/home/ubuntu/defi_system/backend/backtest_dynamic.csv', index=False)
        
        print("  ✅ 數據已保存到 CSV 和 JSON 文件")

def main():
    # 運行 1 年回測
    engine = BacktestEngine(
        initial_capital=10000,
        start_date='2024-01-01',
        end_date='2025-01-01'
    )
    
    metrics, pure_lp, delta_neutral, dynamic = engine.run_backtest()

if __name__ == '__main__':
    main()
