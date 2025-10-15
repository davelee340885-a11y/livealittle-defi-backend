# LAL 智能搜尋 - Lovable 快速開始指南

## 🎯 目標

將 LAL 智能搜尋功能整合到您的 LiveaLittle DeFi 平台（Strategy 頁面）

---

## ⚡ 快速開始（3 步驟）

### 步驟 1：打開 Lovable 項目

1. 訪問：https://lovable.dev
2. 登入您的帳號
3. 找到並打開 **"LiveaLittle DeFi"** 項目

### 步驟 2：複製並粘貼提示詞

**在 Lovable 聊天框中粘貼以下完整提示詞**：

---

## 📝 完整提示詞（直接複製使用）

```
在 Strategy 頁面添加 "LAL 智能搜尋" 功能標籤。

## 整合位置
在 Strategy 頁面創建標籤導航，添加新標籤 "LAL 智能搜尋"（與現有的 LP 池選擇器並列）。

## LAL 智能搜尋標籤內容

### 搜尋表單區域

**基礎參數卡片**（淺色背景，圓角 12px）
- 標題：基礎參數
- 代幣選擇：下拉菜單，選項：ETH, BTC, SOL, AVAX, MATIC，默認 ETH
- 投資資本：數字輸入框，默認 10000，前綴 $
  - 快捷按鈕（4 個並排）：$1K, $5K, $10K, $50K
  - 點擊快捷按鈕自動填充金額

**對沖參數卡片**（青色淺背景 bg-cyan-50/10，圓角 12px）
- 標題：對沖設置
- 對沖比率：
  - 滑塊組件，範圍 0-100，默認 100
  - 實時顯示當前值：如 "100%（完全對沖）"
  - 提示文字（小字，灰色）：「100% 對沖可將 IL 從 -32% 降低到 -0.75%」
- 再平衡頻率：
  - 數字輸入框，範圍 1-30，默認 7
  - 後綴：天
  - 提示文字：「建議每週再平衡一次」

**篩選條件卡片**（灰色淺背景，圓角 12px）
- 標題：篩選條件（可選）
- 最小 APY：數字輸入框，默認 50，後綴 %
- 區塊鏈篩選：多選下拉菜單
  - 選項：Ethereum, Arbitrum, Base, Optimism, Polygon, Avalanche, Solana
  - 默認：全選
- 協議篩選：多選下拉菜單
  - 選項：Uniswap V3, Curve, Raydium, Trader Joe, Balancer
  - 默認：全選
- 結果數量：滑塊，範圍 1-20，默認 5

**搜尋按鈕**
- 全寬按鈕，高度 48px
- 背景：青色漸變（from-cyan-500 to-cyan-600）
- 文字：白色，16px，粗體
- 圖標 + 文字：「🔍 開始智能搜尋」
- 懸停效果：輕微變暗
- 加載狀態：
  - 顯示旋轉圖標
  - 文字改為「搜尋中...」
  - 禁用按鈕

### 結果展示區域

**加載狀態**（搜尋中）
- 顯示 5 個骨架屏卡片
- 使用 shimmer 動畫效果

**空狀態**（未搜尋或無結果）
- 圖標：🔍
- 文字：「開始搜尋以發現最佳投資機會」
- 或「未找到符合條件的機會，請調整篩選條件」

**結果列表**
- 網格佈局：
  - 桌面（>1024px）：2 列，間距 24px
  - 平板（768-1024px）：1 列
  - 手機（<768px）：1 列
- 淡入動畫（stagger effect）

**每個機會卡片**（深色背景 bg-slate-800，圓角 12px，陰影）

**卡片頭部**
- 左側：
  - 排名徽章（如果是前 3 名）
    - 第 1 名：🥇 金色背景
    - 第 2 名：🥈 銀色背景
    - 第 3 名：🥉 銅色背景
  - 池名稱：大字體 24px，粗體，如「WETH-USDT」
- 右上角：
  - 綜合評分：超大數字 48px，青色，如「93.0」
  - 小字：「/100」

**協議和鏈 Badge**（頭部下方）
- 協議 Badge：如「Uniswap V3」，藍色背景
- 鏈 Badge：如「Ethereum」，綠色背景
- 圓角 6px，padding 4px 8px

**主要指標區域**（淺青色背景 bg-cyan-900/20，padding 16px，圓角 8px）
- 調整後淨 APY：
  - 標籤：「調整後淨 APY」，灰色小字
  - 數值：超大綠色數字 36px，粗體，如「91.86%」
- 預期年收益：
  - 標籤：「預期年收益」，灰色小字
  - 數值：大綠色數字 28px，粗體，如「$9,186」

**IL 對沖分析區域**（淺藍色背景 bg-blue-900/20，padding 16px，圓角 8px，margin-top 16px）
- 標題：「IL 對沖分析」，16px，粗體
- 4 行數據（每行 flex 佈局，space-between）：
  1. 預期 IL（無對沖）：
     - 標籤：「預期 IL（無對沖）」
     - 數值：紅色，如「-32.00%」
  2. 淨 IL（對沖後）：
     - 標籤：「淨 IL（對沖後）」
     - 數值：綠色，如「-0.75%」
  3. 對沖有效性：
     - 標籤：「對沖有效性」
     - 數值：青色，如「97.67%」
  4. 對沖質量：
     - 標籤：「對沖質量」
     - Badge：
       - excellent：綠色背景
       - good：藍色背景
       - fair：黃色背景
       - poor：紅色背景
- IL 影響（USD）：
  - 標籤：「IL 影響」
  - 數值：如「-$74.67」

**收益分解區域**（padding 16px，margin-top 16px）
- 標題：「收益分解」，16px，粗體
- 4 個進度條（每個 margin-bottom 12px）：
  1. LP 收益：
     - 標籤 + 數值：「LP 收益: $8,366」
     - 進度條：綠色，寬度按比例
  2. 資金費率收益：
     - 標籤 + 數值：「資金費率收益: $1,095」
     - 進度條：綠色，寬度按比例
  3. IL 損失：
     - 標籤 + 數值：「IL 損失: -$75」
     - 進度條：紅色，寬度按比例
  4. Gas 成本：
     - 標籤 + 數值：「Gas 成本: -$200」
     - 進度條：紅色，寬度按比例
- 總收益（底部，粗體，大字）：
  - 標籤：「總收益」
  - 數值：綠色 24px，如「$9,186」

**其他指標區域**（2 列網格，gap 16px，margin-top 16px）
- 左列：
  - 戴維斯評分：如「100/100 ⭐⭐⭐⭐⭐」
  - 戴維斯評級：如「極佳」，綠色 Badge
- 右列：
  - TVL：如「$158.9M」
  - 協議：如「Uniswap V3」
  - 鏈：如「Ethereum」

**卡片懸停效果**
- 輕微放大（scale-105）
- 陰影加深
- 平滑過渡（transition-all duration-300）

## API 整合

**創建 API 客戶端文件** `src/lib/lal-api.ts`

```typescript
const API_BASE_URL = 'https://lal-smart-search-api.onrender.com/api/v1';

export interface SearchParams {
  token: string;
  capital: number;
  hedge_ratio: number;
  rebalance_frequency_days: number;
  min_apy?: number;
  chains?: string[];
  protocols?: string[];
  limit: number;
}

export interface Opportunity {
  symbol: string;
  protocol: string;
  chain: string;
  adjusted_net_apy: number;
  adjusted_net_profit: number;
  il_analysis: {
    expected_il_annual: number;
    net_il_annual: number;
    hedge_effectiveness: number;
    hedge_quality: string;
    il_impact_usd: number;
  };
  profit_breakdown: {
    lp_profit: number;
    funding_profit: number;
    il_loss: number;
    gas_cost: number;
    total: number;
  };
  davis_score: number;
  davis_category: string;
  final_score: number;
  tvl: number;
}

export interface SearchResponse {
  data: {
    opportunities: Opportunity[];
    count: number;
  };
}

export async function searchOpportunities(params: SearchParams): Promise<SearchResponse> {
  const queryParams = new URLSearchParams({
    token: params.token,
    capital: params.capital.toString(),
    hedge_ratio: params.hedge_ratio.toString(),
    rebalance_frequency_days: params.rebalance_frequency_days.toString(),
    limit: params.limit.toString(),
  });

  if (params.min_apy !== undefined) {
    queryParams.append('min_apy', params.min_apy.toString());
  }

  if (params.chains && params.chains.length > 0) {
    queryParams.append('chains', params.chains.join(','));
  }

  if (params.protocols && params.protocols.length > 0) {
    queryParams.append('protocols', params.protocols.join(','));
  }

  const response = await fetch(`${API_BASE_URL}/lal/smart-search?${queryParams}`);
  
  if (!response.ok) {
    throw new Error('搜尋失敗，請稍後重試');
  }

  return response.json();
}
```

**在搜尋表單中調用 API**

```typescript
const [loading, setLoading] = useState(false);
const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
const [error, setError] = useState<string | null>(null);

const handleSearch = async () => {
  setLoading(true);
  setError(null);
  
  try {
    const response = await searchOpportunities({
      token: selectedToken,
      capital: capitalAmount,
      hedge_ratio: hedgeRatio / 100, // 轉換為 0-1
      rebalance_frequency_days: rebalanceFrequency,
      min_apy: minApy,
      chains: selectedChains,
      protocols: selectedProtocols,
      limit: resultLimit,
    });
    
    setOpportunities(response.data.opportunities);
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

## 設計要求

- 保持與現有平台一致的深色主題
- 使用相同的青色主題色（#00D9FF 或 Tailwind 的 cyan-500）
- 所有卡片圓角 12px
- 卡片陰影：shadow-lg
- 響應式設計：
  - 桌面：2 列網格
  - 平板：1 列
  - 手機：1 列，簡化顯示
- 添加平滑動畫：
  - 卡片進入：淡入 + 上移
  - 懸停：放大 + 陰影
  - 按鈕：顏色過渡
- 使用 shadcn/ui 組件：
  - Button
  - Input
  - Slider
  - Select
  - Card
  - Badge
  - Progress
- 錯誤處理：
  - 顯示友好的錯誤信息
  - 提供重試按鈕
- 空狀態：
  - 未搜尋時顯示提示
  - 無結果時顯示建議

## 交互效果

- 卡片懸停：輕微放大（scale-105）+ 陰影加深
- 按鈕懸停：背景顏色變深
- 滑塊拖動：實時更新數值顯示
- 搜尋中：
  - 禁用表單所有輸入
  - 按鈕顯示加載動畫
  - 顯示骨架屏
- 結果出現：淡入動畫，每個卡片延遲 100ms（stagger effect）

請實現這個 LAL 智能搜尋功能。
```

---

### 步驟 3：等待生成並測試

1. **等待 Lovable 生成**（2-5 分鐘）
2. **點擊 Preview 預覽**
3. **導航到 Strategy → LAL 智能搜尋**
4. **測試搜尋功能**

---

## ✅ 測試檢查清單

### 基礎功能
- [ ] 搜尋表單顯示正常
- [ ] 所有輸入框可以使用
- [ ] 點擊搜尋按鈕有反應
- [ ] 顯示加載狀態
- [ ] 顯示搜尋結果

### 結果展示
- [ ] 卡片佈局正確（桌面 2 列）
- [ ] 所有數據顯示完整
- [ ] IL 對沖分析顯示
- [ ] 收益分解顯示
- [ ] 排名徽章顯示（前 3 名）

### 響應式
- [ ] 平板顯示正常（1 列）
- [ ] 手機顯示正常（1 列）
- [ ] 所有元素可點擊

### 錯誤處理
- [ ] 無結果時顯示提示
- [ ] API 錯誤時顯示錯誤信息
- [ ] 輸入驗證正常

---

## 🔧 常見問題快速修復

### 問題 1：樣式不對

**解決方法**：告訴 Lovable

```
請調整 LAL 智能搜尋的樣式，確保：
1. 使用深色主題（bg-slate-900）
2. 青色主色調（cyan-500）
3. 卡片圓角 12px
4. 所有數字使用大字體
```

### 問題 2：API 調用失敗

**解決方法**：檢查並告訴 Lovable

```
API 調用失敗，請確保：
1. API 端點正確：https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search
2. hedge_ratio 轉換為 0-1（除以 100）
3. 添加錯誤處理和重試機制
```

### 問題 3：缺少組件

**解決方法**：告訴 Lovable

```
請確保創建了以下文件：
- src/lib/lal-api.ts（API 客戶端）
- src/components/LALSearchForm.tsx（搜尋表單）
- src/components/OpportunityCard.tsx（機會卡片）
並更新了 src/pages/Strategy.tsx
```

---

## 📞 需要幫助？

如果遇到問題：

1. **檢查 API 狀態**：
   ```
   https://lal-smart-search-api.onrender.com/health
   ```
   應該返回：`{"status": "healthy", "version": "3.0.0"}`

2. **查看瀏覽器控制台**：
   - 按 F12 打開開發者工具
   - 查看 Console 標籤的錯誤
   - 查看 Network 標籤的 API 請求

3. **告訴我**：
   - 具體的錯誤信息
   - 您在哪一步遇到問題
   - Lovable 的響應

---

## 🎉 完成後

您將擁有：

✅ 完整的 LAL 智能搜尋功能  
✅ 整合到 Strategy 頁面  
✅ 專業的 UI/UX  
✅ 真實的 API 數據  
✅ 響應式設計  

**開始使用並享受智能搜尋帶來的便利！** 🚀

