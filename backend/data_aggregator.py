import requests
import pandas as pd

class DefiLlamaService:
    """
    一個簡單的服務，用於從 DeFiLlama API 獲取和篩選 LP 池數據。
    """
    def __init__(self):
        self.api_url = "https://yields.llama.fi/pools"

    def fetch_and_filter_pools(self, min_tvl_usd=1000000, min_apy=0, top_n=50):
        """
        獲取數據並根據 TVL 和 APY 進行篩選。
        """
        print(f"正在從 DeFiLlama API 獲取數據...")
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()  # 如果請求失敗則拋出異常
            data = response.json()["data"]
            print(f"成功獲取 {len(data)} 個池的數據。")

            # 將數據轉換為 pandas DataFrame 以便於處理
            df = pd.DataFrame(data)

            # 篩選 TVL 和 APY
            filtered_df = df[
                (df['tvlUsd'] >= min_tvl_usd) &
                (df['apy'] >= min_apy)
            ]
            print(f"篩選後剩下 {len(filtered_df)} 個池 (TVL >= ${min_tvl_usd/1e6:.1f}M)。")

            # 按 APY 降序排序並選取前 N 個
            top_pools_df = filtered_df.sort_values(by='apy', ascending=False).head(top_n)

            # 選擇並重命名列以提高可讀性
            output_df = top_pools_df[['chain', 'project', 'symbol', 'tvlUsd', 'apy', 'apyBase', 'apyReward']].copy()
            output_df.rename(columns={
                'chain': '鏈',
                'project': '協議',
                'symbol': '代幣',
                'tvlUsd': '總鎖倉量 (USD)',
                'apy': '總年化收益率 (%)',
                'apyBase': '基礎 APY (%)',
                'apyReward': '獎勵 APY (%)'
            }, inplace=True)

            # 格式化數字
            output_df['總鎖倉量 (USD)'] = output_df['總鎖倉量 (USD)'].apply(lambda x: f"${x/1e6:,.2f}M")
            for col in ['總年化收益率 (%)', '基礎 APY (%)', '獎勵 APY (%)']:
                output_df[col] = output_df[col].apply(lambda x: f"{x:.2f}%")

            print(f"已成功處理並格式化 Top {top_n} 高收益池數據。")
            return output_df

        except requests.exceptions.RequestException as e:
            print(f"錯誤：無法從 DeFiLlama API 獲取數據。 {e}")
            return None

if __name__ == '__main__':
    service = DefiLlamaService()
    # 執行核心功能：獲取並篩選 TVL 超過 100 萬美元的池
    top_pools = service.fetch_and_filter_pools(min_tvl_usd=1000000, top_n=20)

    if top_pools is not None:
        print("\n--- 數據監控儀表板 (MVP) --- Top 20 高收益池 ---")
        print(top_pools.to_markdown(index=False))
        # 將結果保存到文件，模擬 API 的輸出
        top_pools.to_csv('/home/ubuntu/defi_system/backend/top_pools_data.csv', index=False)
