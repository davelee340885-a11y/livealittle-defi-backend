import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

class BearMarketBacktest:
    """
    熊市回測引擎
    
    模擬市場崩盤環境下的策略表現
    """
    
    def __init__(self, initial_capital=10000, start_date='2024-01-01', end_date='2025-01-01'):
        self.initial_capital = initial_capital
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.risk_free_rate = 0.05
        
    def generate_bear_market_data(self):
        """
        生成熊市數據
        
        特點：
        - 價格下跌趨勢
        - 高波動性
        - 負資金費率
        - LP APY 下降
        """
        dates = pd.date_range(self.start_date, self.end_date, freq='D')
        n_days = len(dates)
        
        np.random.seed(100)  # 不同的種子以產生熊市
        
        # BTC: 從 $110k 跌至 $40k（-64%）
        btc_trend = np.linspace(110000, 40000, n_days)
        # 熊市特徵：下跌過程中有劇烈波動
        btc_volatility = np.random.normal(0, 0.05, n_days).cumsum()
        # 添加幾次暴跌
        crash_days = [60, 120, 180, 240, 300]
        for day in crash_days:
            if day < n_days:
                btc_volatility[day:] -= 0.15  # 單日暴跌 15%
        
        btc_price = btc_trend * (1 + btc_volatility * 0.1)
        btc_price = np.maximum(btc_price, 20000)  # 設置底部
        
        # ETH: 從 $4k 跌至 $1.5k
        eth_trend = np.linspace(4000, 1500, n_days)
        eth_volatility = np.random.normal(0, 0.06, n_days).cumsum()
        for day in crash_days:
            if day < n_days:
                eth_volatility[day:] -= 0.18
        eth_price = eth_trend * (1 + eth_volatility * 0.1)
        eth_price = np.maximum(eth_price, 800)
        
        # SOL: 從 $200 跌至 $50
        sol_trend = np.linspace(200, 50, n_days)
        sol_volatility = np.random.normal(0, 0.08, n_days).cumsum()
        for day in crash_days:
            if day < n_days:
                sol_volatility[day:] -= 0.20
        sol_price = sol_trend * (1 + sol_volatility * 0.1)
        sol_price = np.maximum(sol_price, 20)
        
        # LP APY（熊市中下降，因為交易量減少）
        base_apy = np.linspace(150, 50, n_days)  # 從 150% 降至 50%
        apy_volatility = np.abs(np.random.normal(0, 20, n_days))
        lp_apy = base_apy + apy_volatility
        
        # 資金費率（熊市中多為負值，做空者獲利）
        funding_rate = np.random.normal(-0.0002, 0.0001, n_days)  # 平均為負
        
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
        """純 LP 策略（熊市中會虧損）"""
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
            
            # LP 收益
            lp_return = row['lp_apy'] / 100 / 365
            
            # 價格變動（50% 敞口）
            price_change = (row['btc_price'] - market_data.iloc[i-1]['btc_price']) / market_data.iloc[i-1]['btc_price']
            price_return = price_change * 0.5
            
            # 無常損失（熊市中更嚴重）
            il_loss = -abs(price_change) * 0.15  # 熊市中 IL 更高
            
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
        """Delta Neutral 策略（熊市中仍能獲利）"""
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
            
            # LP 收益
            lp_return = row['lp_apy'] / 100 / 365
            
            # 資金費率（熊市中為負，做空者獲利！）
            funding_benefit = -row['funding_rate'] * 0.5  # 負的負 = 正收益
            
            # 總收益（無價格風險）
            daily_return = lp_return + funding_benefit
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
        """動態策略（熊市中應快速切換到完全對沖）"""
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
            
            # 判斷市場狀態
            if i >= 30:
                ma_30 = market_data.iloc[i-30:i]['btc_price'].mean()
                current_price = row['btc_price']
                
                if current_price > ma_30 * 1.05:  # 牛市（熊市中很少）
                    hedge_ratio = 0.3
                elif current_price < ma_30 * 0.95:  # 熊市（大部分時間）
                    hedge_ratio = 1.0
                else:  # 橫盤
                    hedge_ratio = 1.0
            else:
                hedge_ratio = 1.0
            
            # LP 收益
            lp_return = row['lp_apy'] / 100 / 365
            
            # 價格變動
            price_change = (row['btc_price'] - market_data.iloc[i-1]['btc_price']) / market_data.iloc[i-1]['btc_price']
            exposure = 0.5 * (1 - hedge_ratio)
            price_return = price_change * exposure
            
            # 資金費率
            funding_benefit = -row['funding_rate'] * 0.5 * hedge_ratio
            
            # 無常損失
            il_loss = -abs(price_change) * 0.15 * (1 - hedge_ratio * 0.5)
            
            # 總收益
            daily_return = lp_return + price_return + funding_benefit + il_loss
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
        """計算績效指標"""
        total_return = results_df.iloc[-1]['cumulative_return']
        
        days = len(results_df)
        if total_return > -1:  # 避免負數開根號
            annual_return = (1 + total_return) ** (365 / days) - 1
        else:
            annual_return = -1
        
        daily_returns = results_df['daily_return'].dropna()
        volatility = daily_returns.std() * np.sqrt(365)
        
        excess_return = annual_return - self.risk_free_rate
        sharpe_ratio = excess_return / volatility if volatility > 0 else 0
        
        cumulative_returns = results_df['cumulative_return']
        running_max = cumulative_returns.cummax()
        drawdown = cumulative_returns - running_max
        max_drawdown = drawdown.min()
        
        win_rate = (daily_returns > 0).sum() / len(daily_returns)
        
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
        """運行熊市回測"""
        print("="*80)
        print("🐻 熊市回測引擎")
        print("="*80)
        print(f"\n回測期間：{self.start_date.date()} 至 {self.end_date.date()}")
        print(f"初始資金：${self.initial_capital:,.2f}")
        print(f"市場環境：熊市（BTC 從 $110k 跌至 $40k，-64%）")
        
        # 生成熊市數據
        print("\n正在生成熊市市場數據...")
        market_data = self.generate_bear_market_data()
        
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
        self.display_results(metrics, market_data)
        
        # 生成圖表
        print("\n正在生成可視化報告...")
        self.plot_results(pure_lp, delta_neutral, dynamic, market_data)
        
        # 保存結果
        self.save_results(metrics, pure_lp, delta_neutral, dynamic, market_data)
        
        return metrics, pure_lp, delta_neutral, dynamic
    
    def display_results(self, metrics, market_data):
        """顯示回測結果"""
        print(f"\n{'='*80}")
        print("📊 熊市回測結果總結")
        print("="*80)
        
        # 市場統計
        btc_start = market_data.iloc[0]['btc_price']
        btc_end = market_data.iloc[-1]['btc_price']
        btc_change = (btc_end - btc_start) / btc_start
        
        print(f"\n📉 市場表現：")
        print(f"  BTC: ${btc_start:,.0f} → ${btc_end:,.0f} ({btc_change*100:.1f}%)")
        print(f"  平均 LP APY: {market_data['lp_apy'].mean():.1f}%")
        print(f"  平均資金費率: {market_data['funding_rate'].mean()*365*100:.2f}% (年化)")
        
        strategies = {
            'pure_lp': '純 LP 策略',
            'delta_neutral': 'Delta Neutral 策略',
            'dynamic': '動態策略'
        }
        
        print(f"\n{'策略':<20} | {'總收益':>10} | {'年化收益':>10} | {'夏普比率':>10} | {'最大回撤':>10} | {'最終資金':>12}")
        print("-" * 100)
        
        for key, name in strategies.items():
            m = metrics[key]
            print(f"{name:<20} | {m['total_return']*100:>9.2f}% | {m['annual_return']*100:>9.2f}% | {m['sharpe_ratio']:>10.2f} | {m['max_drawdown']*100:>9.2f}% | ${m['final_capital']:>11,.2f}")
        
        print("\n" + "="*80)
        print("💡 熊市關鍵發現：")
        
        # 分析
        pure_lp_loss = metrics['pure_lp']['total_return'] < 0
        delta_profit = metrics['delta_neutral']['total_return'] > 0
        
        if pure_lp_loss:
            print(f"  ⚠️  純 LP 策略虧損 {abs(metrics['pure_lp']['total_return'])*100:.1f}%，證明無對沖的風險")
        
        if delta_profit:
            print(f"  ✅ Delta Neutral 策略仍獲利 {metrics['delta_neutral']['total_return']*100:.1f}%，證明對沖的價值")
            print(f"  ✅ 即使市場下跌 {abs(btc_change)*100:.1f}%，Delta Neutral 仍能賺錢")
        
        print(f"  💰 資金費率收益：熊市中做空者獲得資金費率，增強 Delta Neutral 收益")
        
        print("="*80)
    
    def plot_results(self, pure_lp, delta_neutral, dynamic, market_data):
        """生成可視化圖表"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. 收益曲線對比
        ax1 = axes[0, 0]
        ax1.plot(pure_lp['date'], pure_lp['cumulative_return'] * 100, label='純 LP 策略', linewidth=2, color='red')
        ax1.plot(delta_neutral['date'], delta_neutral['cumulative_return'] * 100, label='Delta Neutral 策略', linewidth=2, color='green')
        ax1.plot(dynamic['date'], dynamic['cumulative_return'] * 100, label='動態策略', linewidth=2, color='blue')
        ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax1.set_title('熊市累積收益率對比', fontsize=14, fontweight='bold')
        ax1.set_xlabel('日期')
        ax1.set_ylabel('累積收益率 (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 資本曲線
        ax2 = axes[0, 1]
        ax2.plot(pure_lp['date'], pure_lp['capital'], label='純 LP 策略', linewidth=2, color='red')
        ax2.plot(delta_neutral['date'], delta_neutral['capital'], label='Delta Neutral 策略', linewidth=2, color='green')
        ax2.plot(dynamic['date'], dynamic['capital'], label='動態策略', linewidth=2, color='blue')
        ax2.axhline(y=self.initial_capital, color='gray', linestyle='--', label='初始資金')
        ax2.set_title('熊市資本曲線', fontsize=14, fontweight='bold')
        ax2.set_xlabel('日期')
        ax2.set_ylabel('資本 (USD)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 回撤分析
        ax3 = axes[1, 0]
        for df, label, color in [(pure_lp, '純 LP', 'red'), (delta_neutral, 'Delta Neutral', 'green'), (dynamic, '動態', 'blue')]:
            running_max = df['cumulative_return'].cummax()
            drawdown = (df['cumulative_return'] - running_max) * 100
            ax3.fill_between(df['date'], drawdown, 0, alpha=0.3, label=label, color=color)
        ax3.set_title('熊市回撤分析', fontsize=14, fontweight='bold')
        ax3.set_xlabel('日期')
        ax3.set_ylabel('回撤 (%)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 市場價格（BTC）
        ax4 = axes[1, 1]
        ax4.plot(market_data['date'], market_data['btc_price'], color='orange', linewidth=2)
        ax4.set_title('BTC 價格走勢（熊市）', fontsize=14, fontweight='bold')
        ax4.set_xlabel('日期')
        ax4.set_ylabel('BTC 價格 (USD)')
        ax4.grid(True, alpha=0.3)
        
        # 標記暴跌點
        crash_days = [60, 120, 180, 240, 300]
        for day in crash_days:
            if day < len(market_data):
                ax4.axvline(x=market_data.iloc[day]['date'], color='red', linestyle='--', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('/home/ubuntu/defi_system/backend/backtest_bear_results.png', dpi=300, bbox_inches='tight')
        print("  ✅ 圖表已保存到 backtest_bear_results.png")
        
        plt.close()
    
    def save_results(self, metrics, pure_lp, delta_neutral, dynamic, market_data):
        """保存回測結果"""
        with open('/home/ubuntu/defi_system/backend/backtest_bear_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        
        pure_lp.to_csv('/home/ubuntu/defi_system/backend/backtest_bear_pure_lp.csv', index=False)
        delta_neutral.to_csv('/home/ubuntu/defi_system/backend/backtest_bear_delta_neutral.csv', index=False)
        dynamic.to_csv('/home/ubuntu/defi_system/backend/backtest_bear_dynamic.csv', index=False)
        market_data.to_csv('/home/ubuntu/defi_system/backend/backtest_bear_market_data.csv', index=False)
        
        print("  ✅ 數據已保存到 CSV 和 JSON 文件")

def main():
    # 運行熊市回測
    engine = BearMarketBacktest(
        initial_capital=10000,
        start_date='2024-01-01',
        end_date='2025-01-01'
    )
    
    metrics, pure_lp, delta_neutral, dynamic = engine.run_backtest()

if __name__ == '__main__':
    main()
