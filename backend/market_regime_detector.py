import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MarketRegimeDetector:
    """
    市場狀態識別器
    
    識別三種市場狀態：
    1. 牛市 (Bull Market)
    2. 熊市 (Bear Market)  
    3. 橫盤 (Sideways/Range-bound)
    """
    
    def __init__(self):
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        
    def fetch_price_history(self, coin_id='bitcoin', days=30):
        """獲取價格歷史數據"""
        try:
            url = f"{self.coingecko_api}/coins/{coin_id}/market_chart"
            params = {'vs_currency': 'usd', 'days': days}
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            prices = data['prices']
            
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df
        except Exception as e:
            print(f"錯誤：無法獲取價格數據。{e}")
            return None
    
    def calculate_trend_indicators(self, df):
        """計算趨勢指標"""
        # 1. 移動平均線
        df['ma_7'] = df['price'].rolling(window=7).mean()
        df['ma_30'] = df['price'].rolling(window=30).mean()
        
        # 2. 價格變化率
        df['price_change_7d'] = df['price'].pct_change(periods=7) * 100
        df['price_change_30d'] = df['price'].pct_change(periods=30) * 100
        
        # 3. 波動率（標準差）
        df['volatility_7d'] = df['price'].rolling(window=7).std()
        df['volatility_30d'] = df['price'].rolling(window=30).std()
        
        # 4. RSI (相對強弱指標)
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    
    def detect_regime(self, df):
        """
        識別市場狀態
        
        判斷邏輯：
        1. 牛市：價格 > MA30，7日漲幅 > 5%，RSI > 50
        2. 熊市：價格 < MA30，7日跌幅 > 5%，RSI < 50
        3. 橫盤：其他情況，波動率較低
        """
        latest = df.iloc[-1]
        
        price = latest['price']
        ma_30 = latest['ma_30']
        price_change_7d = latest['price_change_7d']
        rsi = latest['rsi']
        volatility = latest['volatility_7d']
        
        # 判斷邏輯
        if pd.isna(ma_30) or pd.isna(rsi):
            return {
                'regime': 'UNKNOWN',
                'confidence': 0,
                'reason': '數據不足'
            }
        
        # 牛市判斷
        bull_signals = 0
        if price > ma_30:
            bull_signals += 1
        if price_change_7d > 5:
            bull_signals += 1
        if rsi > 60:
            bull_signals += 1
        
        # 熊市判斷
        bear_signals = 0
        if price < ma_30:
            bear_signals += 1
        if price_change_7d < -5:
            bear_signals += 1
        if rsi < 40:
            bear_signals += 1
        
        # 決策
        if bull_signals >= 2:
            regime = 'BULL'
            confidence = bull_signals / 3
        elif bear_signals >= 2:
            regime = 'BEAR'
            confidence = bear_signals / 3
        else:
            regime = 'SIDEWAYS'
            confidence = 0.6
        
        return {
            'regime': regime,
            'confidence': confidence,
            'price': price,
            'ma_30': ma_30,
            'price_change_7d': price_change_7d,
            'rsi': rsi,
            'volatility': volatility,
            'bull_signals': bull_signals,
            'bear_signals': bear_signals
        }
    
    def analyze_market(self, coin_id='bitcoin', days=30):
        """完整的市場分析"""
        print(f"正在分析 {coin_id.upper()} 市場狀態...")
        
        # 獲取數據
        df = self.fetch_price_history(coin_id, days)
        if df is None:
            return None
        
        # 計算指標
        df = self.calculate_trend_indicators(df)
        
        # 識別狀態
        regime_info = self.detect_regime(df)
        
        return regime_info

class StrategySelector:
    """
    策略選擇器
    
    根據市場狀態選擇最優策略
    """
    
    def __init__(self):
        self.strategies = {
            'BULL': {
                'name': 'Long Bias Strategy',
                'description': '牛市策略：減少對沖，增加多頭敞口',
                'hedge_ratio': 0.3,  # 只對沖 30%
                'target_delta': 0.2,  # 保持 20% 正 Delta
                'reason': '牛市中，允許部分多頭敞口以捕捉上漲收益'
            },
            'BEAR': {
                'name': 'Delta Neutral Strategy',
                'description': '熊市策略：完全對沖，保護本金',
                'hedge_ratio': 1.0,  # 完全對沖
                'target_delta': 0.0,  # Delta = 0
                'reason': '熊市中，優先保護本金，避免價格下跌損失'
            },
            'SIDEWAYS': {
                'name': 'Delta Neutral Strategy',
                'description': '橫盤策略：完全對沖，賺取手續費',
                'hedge_ratio': 1.0,  # 完全對沖
                'target_delta': 0.0,  # Delta = 0
                'reason': '橫盤市場中，專注於賺取 LP 手續費和獎勵'
            },
            'UNKNOWN': {
                'name': 'Conservative Strategy',
                'description': '保守策略：完全對沖',
                'hedge_ratio': 1.0,
                'target_delta': 0.0,
                'reason': '市場不明朗時，採取保守策略'
            }
        }
    
    def select_strategy(self, market_regime):
        """根據市場狀態選擇策略"""
        regime = market_regime['regime']
        strategy = self.strategies.get(regime, self.strategies['UNKNOWN'])
        
        return {
            'regime': regime,
            'confidence': market_regime.get('confidence', 0),
            'strategy': strategy,
            'market_data': market_regime
        }
    
    def calculate_position_adjustments(self, current_positions, new_strategy):
        """
        計算倉位調整建議
        
        參數：
        - current_positions: 當前持倉（包含 LP 和對沖）
        - new_strategy: 新策略
        
        返回：
        - adjustments: 調整建議列表
        """
        adjustments = []
        
        # 計算當前總 LP 價值
        total_lp_value = sum([p['value_usd'] for p in current_positions if p['type'] == 'LP'])
        
        # 計算當前對沖價值
        total_hedge_value = sum([p['value_usd'] for p in current_positions if p['type'] == 'SHORT'])
        
        # 新策略的目標對沖比例
        target_hedge_ratio = new_strategy['strategy']['hedge_ratio']
        target_hedge_value = total_lp_value * 0.5 * target_hedge_ratio  # LP 的 50% * 對沖比例
        
        # 計算調整金額
        adjustment_needed = target_hedge_value - total_hedge_value
        
        if abs(adjustment_needed) > total_lp_value * 0.05:  # 超過 5% 才調整
            if adjustment_needed > 0:
                adjustments.append({
                    'action': 'INCREASE_HEDGE',
                    'amount_usd': adjustment_needed,
                    'reason': f"市場進入 {new_strategy['regime']}，需增加對沖至 {target_hedge_ratio*100}%"
                })
            else:
                adjustments.append({
                    'action': 'DECREASE_HEDGE',
                    'amount_usd': abs(adjustment_needed),
                    'reason': f"市場進入 {new_strategy['regime']}，可減少對沖至 {target_hedge_ratio*100}%"
                })
        else:
            adjustments.append({
                'action': 'HOLD',
                'amount_usd': 0,
                'reason': '當前倉位已符合策略要求'
            })
        
        return adjustments

def demo_market_analysis():
    """演示市場分析和策略選擇"""
    
    print("="*80)
    print("市場狀態識別與策略選擇系統")
    print("="*80)
    
    # 創建檢測器
    detector = MarketRegimeDetector()
    selector = StrategySelector()
    
    # 分析主要資產
    assets = ['bitcoin', 'ethereum', 'solana']
    
    for asset in assets:
        print(f"\n{'='*80}")
        print(f"分析 {asset.upper()}")
        print('='*80)
        
        # 市場分析
        regime_info = detector.analyze_market(asset, days=30)
        
        if regime_info:
            # 選擇策略
            strategy_decision = selector.select_strategy(regime_info)
            
            # 顯示結果
            print(f"\n📊 市場狀態：{regime_info['regime']}")
            print(f"信心度：{regime_info['confidence']*100:.1f}%")
            print(f"\n當前價格：${regime_info['price']:,.2f}")
            print(f"30日均線：${regime_info['ma_30']:,.2f}")
            print(f"7日漲跌：{regime_info['price_change_7d']:+.2f}%")
            print(f"RSI：{regime_info['rsi']:.1f}")
            
            print(f"\n🎯 推薦策略：{strategy_decision['strategy']['name']}")
            print(f"說明：{strategy_decision['strategy']['description']}")
            print(f"對沖比例：{strategy_decision['strategy']['hedge_ratio']*100:.0f}%")
            print(f"目標 Delta：{strategy_decision['strategy']['target_delta']*100:.0f}%")
            print(f"原因：{strategy_decision['strategy']['reason']}")
    
    # 模擬倉位調整
    print(f"\n{'='*80}")
    print("倉位調整建議（假設當前持有 Delta Neutral 倉位）")
    print('='*80)
    
    # 假設當前持倉
    current_positions = [
        {'type': 'LP', 'value_usd': 10000},
        {'type': 'SHORT', 'value_usd': 5000}  # 完全對沖（50%）
    ]
    
    # 假設 BTC 進入牛市
    btc_regime = detector.analyze_market('bitcoin', days=30)
    if btc_regime:
        btc_strategy = selector.select_strategy(btc_regime)
        adjustments = selector.calculate_position_adjustments(current_positions, btc_strategy)
        
        print(f"\n當前市場：{btc_strategy['regime']}")
        print(f"當前 LP 倉位：$10,000")
        print(f"當前對沖倉位：$5,000 (50%)")
        
        print(f"\n調整建議：")
        for adj in adjustments:
            print(f"  操作：{adj['action']}")
            print(f"  金額：${adj['amount_usd']:,.2f}")
            print(f"  原因：{adj['reason']}")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    demo_market_analysis()
