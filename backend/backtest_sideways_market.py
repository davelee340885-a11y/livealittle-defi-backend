import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

class SidewaysMarketBacktest:
    """
    橫盤市場回測引擎
    
    模擬震盪、無明確趨勢的市場環境
    """
    
    def __init__(self, initial_capital=10000, start_date='2024-01-01', end_date='2025-01-01'):
        self.initial_capital = initial_capital
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.risk_free_rate = 0.05
        
    def generate_sideways_market_data(self):
        """
        生成橫盤市場數據
        
        特點：
        - 價格在區間內震盪
        - 高波動但無趨勢
        - 資金費率接近 0
        - LP APY 中等水平
        """
        dates = pd.date_range(self.start_date, self.end_date, freq='D')
        n_days = len(dates)
        
        np.random.seed(200)
        
        # BTC: 在 $60k-$70k 之間震盪
        center_price = 65000
        amplitude = 5000
        
        # 使用正弦波 + 隨機噪聲模擬震盪
        time_points = np.linspace(0, 4*np.pi, n_days)  # 4 個完整週期
        sine_wave = np.sin(time_points) * amplitude
        random_noise = np.random.normal(0, 2000, n_days)
        btc_price = center_price + sine_wave + random_noise
        
        # ETH: 在 $2.8k-$3.5k 之間震盪
        eth_center = 3150
        eth_amplitude = 350
        eth_sine = np.sin(time_points + 0.5) * eth_amplitude  # 相位偏移
        eth_noise = np.random.normal(0, 150, n_days)
        eth_price = eth_center + eth_sine + eth_noise
        
        # SOL: 在 $120-$160 之間震盪
        sol_center = 140
        sol_amplitude = 20
        sol_sine = np.sin(time_points + 1.0) * sol_amplitude
        sol_noise = np.random.normal(0, 8, n_days)
        sol_price = sol_center + sol_sine + sol_noise
        
        # LP APY（橫盤市場中等水平，因為波動仍然存在）
        base_apy = 120
        apy_volatility = np.abs(np.random.normal(0, 30, n_days))
        lp_apy = base_apy + apy_volatility
        
        # 資金費率（橫盤中接近 0，正負交替）
        funding_rate = np.random.normal(0, 0.00015, n_days)
        
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
        """純 LP 策略（橫盤中受 IL 影響）"""
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
            
            # 無常損失（橫盤中累積，因為價格反覆波動）
            il_loss = -abs(price_change) * 0.12
            
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
        """Delta Neutral 策略（橫盤中表現穩定）"""
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
            
            # 資金費率（橫盤中接近 0，影響很小）
            funding_cost = row['funding_rate'] * 0.5
            
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
        """動態策略（橫盤中應保持完全對沖）"""
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
                
                if current_price > ma_30 * 1.05:  # 牛市
                    hedge_ratio = 0.3
                elif current_price < ma_30 * 0.95:  # 熊市
                    hedge_ratio = 1.0
                else:  # 橫盤（大部分時間）
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
            funding_cost = row['funding_rate'] * 0.5 * hedge_ratio
            
            # 無常損失
            il_loss = -abs(price_change) * 0.12 * (1 - hedge_ratio * 0.5)
            
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
        """計算績效指標"""
        total_return = results_df.iloc[-1]['cumulative_return']
        
        days = len(results_df)
        if total_return > -1:
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
        """運行橫盤市場回測"""
        print("="*80)
        print("↔️  橫盤市場回測引擎")
        print("="*80)
        print(f"\n回測期間：{self.start_date.date()} 至 {self.end_date.date()}")
        print(f"初始資金：${self.initial_capital:,.2f}")
        print(f"市場環境：橫盤震盪（BTC 在 $60k-$70k 之間）")
        
        # 生成橫盤數據
        print("\n正在生成橫盤市場數據...")
        market_data = self.generate_sideways_market_data()
        
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
        print("📊 橫盤市場回測結果總結")
        print("="*80)
        
        # 市場統計
        btc_start = market_data.iloc[0]['btc_price']
        btc_end = market_data.iloc[-1]['btc_price']
        btc_change = (btc_end - btc_start) / btc_start
        btc_max = market_data['btc_price'].max()
        btc_min = market_data['btc_price'].min()
        
        print(f"\n↔️  市場表現：")
        print(f"  BTC: ${btc_start:,.0f} → ${btc_end:,.0f} ({btc_change*100:+.1f}%)")
        print(f"  價格區間: ${btc_min:,.0f} - ${btc_max:,.0f}")
        print(f"  平均 LP APY: {market_data['lp_apy'].mean():.1f}%")
        print(f"  平均資金費率: {market_data['funding_rate'].mean()*365*100:+.2f}% (年化)")
        
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
        print("💡 橫盤市場關鍵發現：")
        
        # 分析
        pure_lp_return = metrics['pure_lp']['annual_return']
        delta_return = metrics['delta_neutral']['annual_return']
        
        print(f"  ✅ Delta Neutral 年化收益：{delta_return*100:.1f}%")
        print(f"  ⚠️  純 LP 受無常損失影響，收益降至：{pure_lp_return*100:.1f}%")
        print(f"  💡 橫盤市場是 Delta Neutral 策略的優勢場景")
        print(f"  📊 價格震盪但無趨勢，對沖完全消除風險")
        
        print("="*80)
    
    def plot_results(self, pure_lp, delta_neutral, dynamic, market_data):
        """生成可視化圖表"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. 收益曲線對比
        ax1 = axes[0, 0]
        ax1.plot(pure_lp['date'], pure_lp['cumulative_return'] * 100, label='純 LP 策略', linewidth=2, color='orange')
        ax1.plot(delta_neutral['date'], delta_neutral['cumulative_return'] * 100, label='Delta Neutral 策略', linewidth=2, color='green')
        ax1.plot(dynamic['date'], dynamic['cumulative_return'] * 100, label='動態策略', linewidth=2, color='blue')
        ax1.set_title('橫盤市場累積收益率對比', fontsize=14, fontweight='bold')
        ax1.set_xlabel('日期')
        ax1.set_ylabel('累積收益率 (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 資本曲線
        ax2 = axes[0, 1]
        ax2.plot(pure_lp['date'], pure_lp['capital'], label='純 LP 策略', linewidth=2, color='orange')
        ax2.plot(delta_neutral['date'], delta_neutral['capital'], label='Delta Neutral 策略', linewidth=2, color='green')
        ax2.plot(dynamic['date'], dynamic['capital'], label='動態策略', linewidth=2, color='blue')
        ax2.axhline(y=self.initial_capital, color='gray', linestyle='--', label='初始資金')
        ax2.set_title('橫盤市場資本曲線', fontsize=14, fontweight='bold')
        ax2.set_xlabel('日期')
        ax2.set_ylabel('資本 (USD)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 回撤分析
        ax3 = axes[1, 0]
        for df, label, color in [(pure_lp, '純 LP', 'orange'), (delta_neutral, 'Delta Neutral', 'green'), (dynamic, '動態', 'blue')]:
            running_max = df['cumulative_return'].cummax()
            drawdown = (df['cumulative_return'] - running_max) * 100
            ax3.fill_between(df['date'], drawdown, 0, alpha=0.3, label=label, color=color)
        ax3.set_title('橫盤市場回撤分析', fontsize=14, fontweight='bold')
        ax3.set_xlabel('日期')
        ax3.set_ylabel('回撤 (%)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 市場價格（BTC）
        ax4 = axes[1, 1]
        ax4.plot(market_data['date'], market_data['btc_price'], color='purple', linewidth=2)
        ax4.axhline(y=market_data['btc_price'].mean(), color='gray', linestyle='--', alpha=0.5, label='平均價格')
        ax4.set_title('BTC 價格走勢（橫盤震盪）', fontsize=14, fontweight='bold')
        ax4.set_xlabel('日期')
        ax4.set_ylabel('BTC 價格 (USD)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('/home/ubuntu/defi_system/backend/backtest_sideways_results.png', dpi=300, bbox_inches='tight')
        print("  ✅ 圖表已保存到 backtest_sideways_results.png")
        
        plt.close()
    
    def save_results(self, metrics, pure_lp, delta_neutral, dynamic, market_data):
        """保存回測結果"""
        with open('/home/ubuntu/defi_system/backend/backtest_sideways_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        
        pure_lp.to_csv('/home/ubuntu/defi_system/backend/backtest_sideways_pure_lp.csv', index=False)
        delta_neutral.to_csv('/home/ubuntu/defi_system/backend/backtest_sideways_delta_neutral.csv', index=False)
        dynamic.to_csv('/home/ubuntu/defi_system/backend/backtest_sideways_dynamic.csv', index=False)
        market_data.to_csv('/home/ubuntu/defi_system/backend/backtest_sideways_market_data.csv', index=False)
        
        print("  ✅ 數據已保存到 CSV 和 JSON 文件")

def main():
    # 運行橫盤市場回測
    engine = SidewaysMarketBacktest(
        initial_capital=10000,
        start_date='2024-01-01',
        end_date='2025-01-01'
    )
    
    metrics, pure_lp, delta_neutral, dynamic = engine.run_backtest()

if __name__ == '__main__':
    main()
