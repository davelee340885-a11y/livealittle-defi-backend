import requests
import pandas as pd
import numpy as np

class DavisDoublePlayAnalyzer:
    """
    戴維斯雙擊分析器：識別費用增長快於 TVL 增長的高質量機會
    """
    def __init__(self):
        self.api_url = "https://yields.llama.fi/pools"

    def fetch_pools_data(self):
        """從 DeFiLlama API 獲取完整的池數據"""
        print("正在從 DeFiLlama API 獲取數據...")
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            data = response.json()["data"]
            print(f"成功獲取 {len(data)} 個池的數據。")
            return pd.DataFrame(data)
        except requests.exceptions.RequestException as e:
            print(f"錯誤：無法從 DeFiLlama API 獲取數據。 {e}")
            return None

    def calculate_davis_metrics(self, df):
        """
        計算戴維斯雙擊相關指標
        
        核心邏輯：
        - 費用增長率 = (當前費用 - 7天前費用) / 7天前費用
        - TVL 增長率 = (當前 TVL - 7天前 TVL) / 7天前 TVL
        - 戴維斯比值 = 費用增長率 / TVL 增長率
        - 當比值 > 1 時，表示費用增長快於 TVL 增長，這是好機會
        """
        print("\n正在計算戴維斯雙擊指標...")
        
        # 確保必要的列存在
        required_cols = ['tvlUsd', 'apyBase', 'apyReward', 'apy']
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0
        
        # 計算 7 天 TVL 變化率（使用 DeFiLlama 提供的 tvlPct1D 推算）
        # 注意：DeFiLlama 沒有直接提供 7 天歷史數據，我們使用可用的變化率指標
        df['tvl_change_7d'] = df.get('tvlPct7D', 0)  # 7天 TVL 變化百分比
        
        # 計算費用變化率（基於 APY 變化推算）
        # APY 變化可以反映費用變化，因為 APY = 費用 / TVL
        df['apy_change_7d'] = df.get('apyPct7D', 0)  # 7天 APY 變化百分比
        
        # 計算戴維斯比值
        # 當 TVL 增長率為 0 或負數時，需要特殊處理
        def calculate_davis_ratio(row):
            tvl_change = row['tvl_change_7d']
            apy_change = row['apy_change_7d']
            
            # 如果數據不可用，返回 NaN
            if pd.isna(tvl_change) or pd.isna(apy_change):
                return np.nan
            
            # 費用增長率 ≈ APY 增長率 + TVL 增長率
            # 因為 Fee = APY * TVL
            fee_growth = apy_change + tvl_change
            
            # 戴維斯比值 = 費用增長 / TVL 增長
            if tvl_change > 0:
                return fee_growth / tvl_change
            elif fee_growth > 0 and tvl_change <= 0:
                # TVL 下降但費用增長，這是極好的信號
                return 999  # 設置一個很高的值表示極佳機會
            else:
                return np.nan
        
        df['davis_ratio'] = df.apply(calculate_davis_ratio, axis=1)
        
        # 計算綜合評分（0-100）
        def calculate_opportunity_score(row):
            score = 0
            
            # 1. 戴維斯比值貢獻（40分）
            davis = row['davis_ratio']
            if pd.notna(davis):
                if davis > 2:
                    score += 40
                elif davis > 1.5:
                    score += 30
                elif davis > 1:
                    score += 20
                elif davis > 0.5:
                    score += 10
            
            # 2. APY 水平貢獻（30分）
            apy = row['apy']
            if apy > 100:
                score += 30
            elif apy > 50:
                score += 20
            elif apy > 20:
                score += 10
            
            # 3. TVL 規模貢獻（20分）
            tvl = row['tvlUsd']
            if tvl > 10_000_000:  # > $10M
                score += 20
            elif tvl > 5_000_000:  # > $5M
                score += 15
            elif tvl > 1_000_000:  # > $1M
                score += 10
            
            # 4. 費用增長貢獻（10分）
            apy_change = row['apy_change_7d']
            if pd.notna(apy_change) and apy_change > 50:
                score += 10
            elif pd.notna(apy_change) and apy_change > 20:
                score += 5
            
            return score
        
        df['opportunity_score'] = df.apply(calculate_opportunity_score, axis=1)
        
        # 標記戴維斯雙擊機會
        df['is_davis_opportunity'] = (df['davis_ratio'] > 1) & (df['davis_ratio'].notna())
        
        print(f"計算完成。發現 {df['is_davis_opportunity'].sum()} 個戴維斯雙擊機會。")
        
        return df

    def filter_and_rank_opportunities(self, df, min_tvl=1_000_000, min_score=50, top_n=20):
        """篩選並排名戴維斯雙擊機會"""
        print(f"\n正在篩選機會 (TVL >= ${min_tvl/1e6:.1f}M, 評分 >= {min_score})...")
        
        # 基礎篩選
        filtered = df[
            (df['tvlUsd'] >= min_tvl) &
            (df['opportunity_score'] >= min_score) &
            (df['davis_ratio'].notna())
        ].copy()
        
        print(f"篩選後剩下 {len(filtered)} 個機會。")
        
        # 按機會評分排序
        ranked = filtered.sort_values('opportunity_score', ascending=False).head(top_n)
        
        # 選擇並格式化輸出列
        output = ranked[[
            'chain', 'project', 'symbol', 'tvlUsd', 'apy', 
            'tvl_change_7d', 'apy_change_7d', 'davis_ratio', 
            'opportunity_score', 'is_davis_opportunity'
        ]].copy()
        
        output.rename(columns={
            'chain': '鏈',
            'project': '協議',
            'symbol': '代幣',
            'tvlUsd': 'TVL (USD)',
            'apy': 'APY (%)',
            'tvl_change_7d': 'TVL 7天變化 (%)',
            'apy_change_7d': 'APY 7天變化 (%)',
            'davis_ratio': '戴維斯比值',
            'opportunity_score': '機會評分',
            'is_davis_opportunity': '戴維斯雙擊'
        }, inplace=True)
        
        # 格式化數字
        output['TVL (USD)'] = output['TVL (USD)'].apply(lambda x: f"${x/1e6:,.2f}M")
        output['APY (%)'] = output['APY (%)'].apply(lambda x: f"{x:.2f}%")
        output['TVL 7天變化 (%)'] = output['TVL 7天變化 (%)'].apply(
            lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A"
        )
        output['APY 7天變化 (%)'] = output['APY 7天變化 (%)'].apply(
            lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A"
        )
        output['戴維斯比值'] = output['戴維斯比值'].apply(
            lambda x: f"{x:.2f}x" if pd.notna(x) and x < 999 else "極佳" if x >= 999 else "N/A"
        )
        output['戴維斯雙擊'] = output['戴維斯雙擊'].apply(lambda x: "✅" if x else "❌")
        
        return output

    def run_analysis(self, min_tvl=1_000_000, min_score=50, top_n=20):
        """運行完整的戴維斯雙擊分析"""
        # 1. 獲取數據
        df = self.fetch_pools_data()
        if df is None:
            return None
        
        # 2. 計算戴維斯指標
        df = self.calculate_davis_metrics(df)
        
        # 3. 篩選並排名
        opportunities = self.filter_and_rank_opportunities(df, min_tvl, min_score, top_n)
        
        return opportunities

if __name__ == '__main__':
    analyzer = DavisDoublePlayAnalyzer()
    
    print("="*80)
    print("戴維斯雙擊機會分析器")
    print("="*80)
    
    # 運行分析
    top_opportunities = analyzer.run_analysis(
        min_tvl=1_000_000,  # TVL >= $1M
        min_score=50,        # 機會評分 >= 50
        top_n=20             # Top 20
    )
    
    if top_opportunities is not None:
        print("\n" + "="*80)
        print("🎯 Top 20 戴維斯雙擊機會")
        print("="*80)
        print(top_opportunities.to_markdown(index=False))
        
        # 保存結果
        top_opportunities.to_csv(
            '/home/ubuntu/defi_system/backend/davis_opportunities.csv', 
            index=False
        )
        print("\n✅ 結果已保存到: davis_opportunities.csv")
