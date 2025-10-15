import pandas as pd
import numpy as np
from datetime import datetime
import json

class BullBearScoringSystem:
    """
    牛熊綜合評分系統（演示版）
    
    整合多維度指標並給出 0-100 的綜合評分
    """
    
    def __init__(self):
        self.indicators_config = {
            # 技術指標（權重 40%）
            'ma_cross_50_200': {'weight': 0.15, 'category': '技術指標'},
            'ma_200w': {'weight': 0.15, 'category': '技術指標'},
            'pi_cycle': {'weight': 0.10, 'category': '技術指標'},
            
            # 鏈上指標（權重 30%）
            'mvrv_zscore': {'weight': 0.15, 'category': '鏈上指標'},
            'sopr': {'weight': 0.10, 'category': '鏈上指標'},
            'exchange_netflow': {'weight': 0.05, 'category': '鏈上指標'},
            
            # 情緒指標（權重 20%）
            'fear_greed': {'weight': 0.15, 'category': '情緒指標'},
            'funding_rate': {'weight': 0.05, 'category': '情緒指標'},
            
            # 宏觀指標（權重 10%）
            'btc_dominance': {'weight': 0.05, 'category': '宏觀指標'},
            'market_cap_trend': {'weight': 0.05, 'category': '宏觀指標'},
        }
    
    def demo_analysis(self, scenario='bull'):
        """
        演示分析（使用模擬數據）
        
        scenario: 'bull', 'bear', 'sideways'
        """
        print(f"\n{'='*80}")
        print(f"牛熊綜合評分系統 - {scenario.upper()} 市場演示")
        print('='*80)
        
        # 模擬各指標得分
        if scenario == 'bull':
            scores = {
                'ma_cross_50_200': 85,  # 黃金交叉
                'ma_200w': 75,  # 價格高於200週線
                'pi_cycle': 70,  # 距離頂部較遠
                'mvrv_zscore': 65,  # 正常範圍
                'sopr': 70,  # 獲利盤
                'exchange_netflow': 80,  # 資金流出交易所（囤幣）
                'fear_greed': 70,  # 貪婪
                'funding_rate': 60,  # 正資金費率
                'btc_dominance': 55,  # 中性
                'market_cap_trend': 80,  # 上升趨勢
            }
        elif scenario == 'bear':
            scores = {
                'ma_cross_50_200': 15,  # 死亡交叉
                'ma_200w': 25,  # 價格低於200週線
                'pi_cycle': 60,  # 距離頂部遠（不是頂部風險）
                'mvrv_zscore': 85,  # 極低（底部信號）
                'sopr': 30,  # 虧損盤
                'exchange_netflow': 20,  # 資金流入交易所（拋售）
                'fear_greed': 80,  # 極度恐懼（反向指標）
                'funding_rate': 40,  # 負資金費率
                'btc_dominance': 65,  # 上升（避險）
                'market_cap_trend': 20,  # 下降趨勢
            }
        else:  # sideways
            scores = {
                'ma_cross_50_200': 50,
                'ma_200w': 55,
                'pi_cycle': 60,
                'mvrv_zscore': 50,
                'sopr': 50,
                'exchange_netflow': 50,
                'fear_greed': 50,
                'funding_rate': 50,
                'btc_dominance': 50,
                'market_cap_trend': 50,
            }
        
        # 計算加權總分
        total_score = 0
        contributions = {}
        
        print(f"\n📊 各指標得分與權重：")
        print("-" * 80)
        print(f"{'指標':<25} | {'得分':>6} | {'權重':>6} | {'貢獻':>8} | 類別")
        print("-" * 80)
        
        for indicator, config in self.indicators_config.items():
            score = scores[indicator]
            weight = config['weight']
            contribution = score * weight
            total_score += contribution
            contributions[indicator] = contribution
            
            print(f"{indicator:<25} | {score:>6.1f} | {weight*100:>5.0f}% | {contribution:>8.2f} | {config['category']}")
        
        print("-" * 80)
        print(f"{'總分':<25} | {'':<6} | {'100%':>6} | {total_score:>8.2f}")
        
        # 判斷市場狀態
        if total_score >= 80:
            regime = 'STRONG_BULL'
            regime_cn = '強牛市 🚀'
            recommendation = '建議：Long Bias 策略，對沖比例 20-30%，積極捕捉上漲收益'
            risk_level = '中'
        elif total_score >= 60:
            regime = 'BULL'
            regime_cn = '牛市 📈'
            recommendation = '建議：Long Bias 策略，對沖比例 30-50%，平衡收益與風險'
            risk_level = '中低'
        elif total_score >= 40:
            regime = 'SIDEWAYS'
            regime_cn = '橫盤/中性 ↔️'
            recommendation = '建議：Delta Neutral 策略，對沖比例 100%，專注賺取手續費'
            risk_level = '低'
        elif total_score >= 20:
            regime = 'BEAR'
            regime_cn = '熊市 📉'
            recommendation = '建議：Delta Neutral 策略，對沖比例 100%，保護本金'
            risk_level = '中'
        else:
            regime = 'STRONG_BEAR'
            regime_cn = '強熊市 💥'
            recommendation = '建議：退出 LP 或超額對沖，對沖比例 100%+，優先保本'
            risk_level = '高'
        
        # 顯示結果
        print(f"\n{'='*80}")
        print(f"🎯 綜合評分報告")
        print('='*80)
        print(f"\n📈 綜合評分：{total_score:.2f} / 100")
        print(f"📊 市場狀態：{regime_cn} ({regime})")
        print(f"⚠️  風險等級：{risk_level}")
        print(f"\n💡 策略建議：")
        print(f"   {recommendation}")
        
        # 分類統計
        print(f"\n📋 分類得分統計：")
        print("-" * 80)
        categories = {}
        for indicator, config in self.indicators_config.items():
            cat = config['category']
            if cat not in categories:
                categories[cat] = {'total_weight': 0, 'weighted_score': 0}
            categories[cat]['total_weight'] += config['weight']
            categories[cat]['weighted_score'] += contributions[indicator]
        
        for cat, data in categories.items():
            avg_score = data['weighted_score'] / data['total_weight']
            print(f"  {cat:<15} | 平均得分: {avg_score:>6.2f} | 總權重: {data['total_weight']*100:>5.0f}%")
        
        # 保存結果
        result = {
            'timestamp': datetime.now().isoformat(),
            'scenario': scenario,
            'total_score': round(total_score, 2),
            'regime': regime,
            'regime_cn': regime_cn,
            'recommendation': recommendation,
            'risk_level': risk_level,
            'scores': scores,
            'contributions': contributions,
            'categories': categories
        }
        
        with open(f'/home/ubuntu/defi_system/backend/bull_bear_score_{scenario}.json', 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 分析結果已保存到 bull_bear_score_{scenario}.json")
        print("="*80)
        
        return result

def main():
    system = BullBearScoringSystem()
    
    # 演示三種市場狀態
    print("\n" + "🔍 系統將演示三種市場狀態的評分結果...\n")
    
    scenarios = ['bull', 'sideways', 'bear']
    results = {}
    
    for scenario in scenarios:
        results[scenario] = system.demo_analysis(scenario)
        print("\n")
    
    # 對比總結
    print(f"\n{'='*80}")
    print("📊 三種市場狀態對比總結")
    print('='*80)
    print(f"\n{'市場狀態':<15} | {'綜合評分':>10} | {'狀態':>15} | 對沖比例")
    print("-" * 80)
    for scenario in scenarios:
        r = results[scenario]
        hedge_ratio = '20-30%' if r['regime'] == 'STRONG_BULL' else \
                      '30-50%' if r['regime'] == 'BULL' else \
                      '100%' if r['regime'] in ['SIDEWAYS', 'BEAR'] else '100%+'
        print(f"{scenario.upper():<15} | {r['total_score']:>10.2f} | {r['regime_cn']:>15} | {hedge_ratio}")
    
    print("\n" + "="*80)
    print("💡 使用建議：")
    print("   1. 每日運行此腳本，獲取最新的市場評分")
    print("   2. 當評分跨越關鍵閾值（40, 60, 80）時，考慮調整對沖策略")
    print("   3. 結合戴維斯雙擊分析，選擇最優的 LP 池")
    print("   4. 定期回顧歷史評分，驗證系統準確性")
    print("="*80)

if __name__ == '__main__':
    main()
