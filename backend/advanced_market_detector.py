import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class AdvancedMarketDetector:
    """
    高級市場狀態識別器
    
    整合多維度指標：
    1. 鏈上指標（MVRV Z-Score, SOPR等）
    2. 技術指標（均線交叉、Pi Cycle等）
    3. 情緒指標（Fear & Greed, Google Trends等）
    4. 宏觀指標（BTC Dominance等）
    
    輸出：0-100 綜合評分，越高越牛市
    """
    
    def __init__(self):
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        self.fear_greed_api = "https://api.alternative.me/fng/"
        
    def fetch_price_data(self, coin_id='bitcoin', days=365):
        """獲取價格數據（用於技術指標計算）"""
        try:
            url = f"{self.coingecko_api}/coins/{coin_id}/market_chart"
            params = {'vs_currency': 'usd', 'days': days}
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df
        except Exception as e:
            print(f"⚠️ 無法獲取價格數據：{e}")
            return None
    
    def fetch_fear_greed_index(self):
        """獲取 Fear & Greed Index"""
        try:
            response = requests.get(self.fear_greed_api, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current_value = int(data['data'][0]['value'])
            classification = data['data'][0]['value_classification']
            
            return {
                'value': current_value,
                'classification': classification,
                'score': current_value  # 0-100，越高越貪婪（牛市）
            }
        except Exception as e:
            print(f"⚠️ 無法獲取 Fear & Greed Index：{e}")
            return {'value': 50, 'classification': 'Neutral', 'score': 50}
    
    # ========== 技術指標 ==========
    
    def calculate_ma_cross(self, df):
        """計算 50/200 日均線交叉（黃金交叉/死亡交叉）"""
        df['ma_50'] = df['price'].rolling(window=50).mean()
        df['ma_200'] = df['price'].rolling(window=200).mean()
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        ma_50_current = latest['ma_50']
        ma_200_current = latest['ma_200']
        ma_50_prev = prev['ma_50']
        ma_200_prev = prev['ma_200']
        
        # 判斷交叉
        if pd.isna(ma_50_current) or pd.isna(ma_200_current):
            return {'signal': 'UNKNOWN', 'score': 50, 'reason': '數據不足'}
        
        # 當前狀態
        if ma_50_current > ma_200_current:
            current_state = 'GOLDEN'
            base_score = 70
        else:
            current_state = 'DEATH'
            base_score = 30
        
        # 檢測是否剛發生交叉
        if ma_50_prev <= ma_200_prev and ma_50_current > ma_200_current:
            signal = 'GOLDEN_CROSS'
            score = 85
            reason = '黃金交叉剛發生，強烈牛市信號'
        elif ma_50_prev >= ma_200_prev and ma_50_current < ma_200_current:
            signal = 'DEATH_CROSS'
            score = 15
            reason = '死亡交叉剛發生，強烈熊市信號'
        else:
            signal = current_state
            score = base_score
            reason = f'50日線在200日線{"上方" if current_state == "GOLDEN" else "下方"}'
        
        return {
            'signal': signal,
            'score': score,
            'ma_50': ma_50_current,
            'ma_200': ma_200_current,
            'reason': reason
        }
    
    def calculate_200w_ma(self, df):
        """計算 200 週移動平均線（牛熊分界線）"""
        # 將日線數據轉換為週線
        df_weekly = df.set_index('timestamp').resample('W')['price'].mean().reset_index()
        df_weekly['ma_200w'] = df_weekly['price'].rolling(window=200).mean()
        
        latest = df_weekly.iloc[-1]
        
        if pd.isna(latest['ma_200w']):
            return {'score': 50, 'reason': '數據不足'}
        
        price = latest['price']
        ma_200w = latest['ma_200w']
        
        # 價格相對於 200週均線的位置
        deviation = (price - ma_200w) / ma_200w * 100
        
        if price > ma_200w:
            # 牛市
            if deviation > 50:
                score = 90
                reason = f'價格遠高於200週線 (+{deviation:.1f}%)，強牛市'
            elif deviation > 20:
                score = 75
                reason = f'價格高於200週線 (+{deviation:.1f}%)，牛市'
            else:
                score = 60
                reason = f'價格略高於200週線 (+{deviation:.1f}%)，弱牛市'
        else:
            # 熊市
            if deviation < -30:
                score = 10
                reason = f'價格遠低於200週線 ({deviation:.1f}%)，強熊市'
            elif deviation < -10:
                score = 25
                reason = f'價格低於200週線 ({deviation:.1f}%)，熊市'
            else:
                score = 40
                reason = f'價格略低於200週線 ({deviation:.1f}%)，弱熊市'
        
        return {
            'score': score,
            'price': price,
            'ma_200w': ma_200w,
            'deviation': deviation,
            'reason': reason
        }
    
    def calculate_pi_cycle(self, df):
        """計算 Pi Cycle Top Indicator"""
        # Pi Cycle: 111日MA vs 350日MA*2
        df['ma_111'] = df['price'].rolling(window=111).mean()
        df['ma_350x2'] = df['price'].rolling(window=350).mean() * 2
        
        latest = df.iloc[-1]
        
        if pd.isna(latest['ma_111']) or pd.isna(latest['ma_350x2']):
            return {'score': 50, 'reason': '數據不足'}
        
        ma_111 = latest['ma_111']
        ma_350x2 = latest['ma_350x2']
        
        # 當 111日MA 突破 350日MA*2，通常是市場頂部
        if ma_111 > ma_350x2:
            score = 10
            reason = 'Pi Cycle 頂部信號，可能接近市場頂部'
        elif ma_111 > ma_350x2 * 0.95:
            score = 30
            reason = 'Pi Cycle 接近頂部信號'
        else:
            # 距離頂部越遠，越安全（越牛市）
            distance = (ma_350x2 - ma_111) / ma_350x2 * 100
            if distance > 20:
                score = 80
                reason = f'距離 Pi Cycle 頂部較遠 ({distance:.1f}%)，安全'
            else:
                score = 60
                reason = f'距離 Pi Cycle 頂部中等 ({distance:.1f}%)'
        
        return {
            'score': score,
            'ma_111': ma_111,
            'ma_350x2': ma_350x2,
            'reason': reason
        }
    
    # ========== 鏈上指標（模擬） ==========
    
    def estimate_mvrv_zscore(self, df):
        """
        估算 MVRV Z-Score（簡化版）
        
        真實的 MVRV 需要鏈上數據，這裡用價格偏離度模擬
        """
        # 使用價格相對於 365日均線的 Z-Score 作為近似
        df['ma_365'] = df['price'].rolling(window=365).mean()
        df['std_365'] = df['price'].rolling(window=365).std()
        
        latest = df.iloc[-1]
        
        if pd.isna(latest['ma_365']) or pd.isna(latest['std_365']):
            return {'score': 50, 'reason': '數據不足'}
        
        price = latest['price']
        ma = latest['ma_365']
        std = latest['std_365']
        
        zscore = (price - ma) / std if std > 0 else 0
        
        # MVRV Z-Score 解讀
        if zscore > 7:
            score = 5
            reason = f'MVRV Z-Score 極高 ({zscore:.2f})，市場過熱，頂部信號'
        elif zscore > 3:
            score = 20
            reason = f'MVRV Z-Score 高 ({zscore:.2f})，市場過熱'
        elif zscore > 0:
            score = 70
            reason = f'MVRV Z-Score 正常 ({zscore:.2f})，健康牛市'
        elif zscore > -1:
            score = 50
            reason = f'MVRV Z-Score 略低 ({zscore:.2f})，中性'
        else:
            score = 90
            reason = f'MVRV Z-Score 極低 ({zscore:.2f})，底部信號，買入機會'
        
        return {
            'score': score,
            'zscore': zscore,
            'reason': reason
        }
    
    # ========== 情緒指標 ==========
    
    def analyze_fear_greed(self):
        """分析 Fear & Greed Index"""
        fg = self.fetch_fear_greed_index()
        
        value = fg['value']
        
        # 反向指標：極度恐懼時是買入機會（牛市起點）
        # 極度貪婪時是賣出信號（牛市頂部）
        if value >= 75:
            score = 20  # 極度貪婪，可能接近頂部
            reason = f'極度貪婪 ({value})，市場過熱'
        elif value >= 55:
            score = 60  # 貪婪，牛市中
            reason = f'貪婪 ({value})，牛市'
        elif value >= 45:
            score = 50  # 中性
            reason = f'中性 ({value})'
        elif value >= 25:
            score = 70  # 恐懼，買入機會
            reason = f'恐懼 ({value})，潛在買入機會'
        else:
            score = 90  # 極度恐懼，底部信號
            reason = f'極度恐懼 ({value})，底部信號'
        
        return {
            'score': score,
            'value': value,
            'classification': fg['classification'],
            'reason': reason
        }
    
    # ========== 綜合評分系統 ==========
    
    def calculate_bull_bear_score(self, coin_id='bitcoin'):
        """
        計算綜合牛熊評分（0-100）
        
        0-20: 強熊市
        20-40: 熊市
        40-60: 橫盤/中性
        60-80: 牛市
        80-100: 強牛市
        """
        print(f"\n{'='*80}")
        print(f"正在分析 {coin_id.upper()} 的牛熊狀態...")
        print('='*80)
        
        # 獲取數據
        df = self.fetch_price_data(coin_id, days=365)
        if df is None:
            return None
        
        # 計算各項指標
        indicators = {}
        
        # 1. 技術指標（權重 40%）
        print("\n📊 技術指標分析...")
        indicators['ma_cross'] = self.calculate_ma_cross(df)
        print(f"  50/200日均線交叉: {indicators['ma_cross']['signal']} - {indicators['ma_cross']['reason']}")
        
        indicators['ma_200w'] = self.calculate_200w_ma(df)
        print(f"  200週均線: {indicators['ma_200w']['reason']}")
        
        indicators['pi_cycle'] = self.calculate_pi_cycle(df)
        print(f"  Pi Cycle: {indicators['pi_cycle']['reason']}")
        
        # 2. 鏈上指標（權重 30%）
        print("\n⛓️ 鏈上指標分析...")
        indicators['mvrv'] = self.estimate_mvrv_zscore(df)
        print(f"  MVRV Z-Score: {indicators['mvrv']['reason']}")
        
        # 3. 情緒指標（權重 30%）
        print("\n😱 情緒指標分析...")
        indicators['fear_greed'] = self.analyze_fear_greed()
        print(f"  Fear & Greed: {indicators['fear_greed']['reason']}")
        
        # 計算加權綜合評分
        weights = {
            'ma_cross': 0.15,
            'ma_200w': 0.15,
            'pi_cycle': 0.10,
            'mvrv': 0.30,
            'fear_greed': 0.30
        }
        
        total_score = 0
        for key, weight in weights.items():
            total_score += indicators[key]['score'] * weight
        
        # 判斷市場狀態
        if total_score >= 80:
            regime = 'STRONG_BULL'
            regime_cn = '強牛市'
            recommendation = '建議：Long Bias 策略，對沖比例 20-30%'
        elif total_score >= 60:
            regime = 'BULL'
            regime_cn = '牛市'
            recommendation = '建議：Long Bias 策略，對沖比例 30-50%'
        elif total_score >= 40:
            regime = 'SIDEWAYS'
            regime_cn = '橫盤/中性'
            recommendation = '建議：Delta Neutral 策略，對沖比例 100%'
        elif total_score >= 20:
            regime = 'BEAR'
            regime_cn = '熊市'
            recommendation = '建議：Delta Neutral 策略，對沖比例 100%'
        else:
            regime = 'STRONG_BEAR'
            regime_cn = '強熊市'
            recommendation = '建議：退出 LP 或完全對沖，對沖比例 100%+'
        
        result = {
            'coin': coin_id,
            'timestamp': datetime.now(),
            'total_score': round(total_score, 2),
            'regime': regime,
            'regime_cn': regime_cn,
            'recommendation': recommendation,
            'indicators': indicators,
            'weights': weights
        }
        
        return result
    
    def display_result(self, result):
        """顯示分析結果"""
        if result is None:
            print("無法完成分析")
            return
        
        print(f"\n{'='*80}")
        print(f"🎯 {result['coin'].upper()} 牛熊綜合評分報告")
        print('='*80)
        
        print(f"\n📈 綜合評分：{result['total_score']}/100")
        print(f"📊 市場狀態：{result['regime_cn']} ({result['regime']})")
        print(f"💡 {result['recommendation']}")
        
        print(f"\n📋 各指標得分明細：")
        print("-" * 80)
        for key, weight in result['weights'].items():
            indicator = result['indicators'][key]
            score = indicator['score']
            print(f"  {key:15s} | 得分: {score:5.1f} | 權重: {weight*100:4.0f}% | 貢獻: {score*weight:5.2f}")
        
        print("\n" + "="*80)
        
        # 保存結果
        with open('/home/ubuntu/defi_system/backend/bull_bear_analysis.json', 'w') as f:
            # 轉換 datetime 為字符串
            result_copy = result.copy()
            result_copy['timestamp'] = result_copy['timestamp'].isoformat()
            json.dump(result_copy, f, indent=2, ensure_ascii=False)
        
        print("✅ 分析結果已保存到 bull_bear_analysis.json")

def main():
    detector = AdvancedMarketDetector()
    
    # 分析 BTC
    result = detector.calculate_bull_bear_score('bitcoin')
    detector.display_result(result)
    
    # 可選：分析其他資產
    # for coin in ['ethereum', 'solana']:
    #     result = detector.calculate_bull_bear_score(coin)
    #     detector.display_result(result)

if __name__ == '__main__':
    main()
