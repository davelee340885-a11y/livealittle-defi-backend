# LAL 智能搜尋前端儀表板設計

## 設計目標

創建一個**專業、直觀、功能豐富**的前端儀表板，展示 LAL 智能搜尋服務的核心功能：
- ✅ Delta Neutral 投資機會搜尋
- ✅ IL（無常損失）分析和對沖效果
- ✅ 多維度篩選器
- ✅ 實時數據展示

---

## 頁面架構

### 1. **主頁 (Home)**
- Hero Section
  - 標題: "LAL 智能搜尋 - 找到最佳 Delta Neutral 投資機會"
  - 副標題: "整合 IL 計算、對沖分析、多維度篩選"
  - CTA 按鈕: "開始搜尋"
- 核心功能展示
  - 戴維斯雙擊分析
  - Delta Neutral 配對
  - IL 計算和對沖
  - 成本效益優化
- 統計數據
  - 已分析池數量
  - 平均 APY
  - 對沖效果提升

### 2. **搜尋頁面 (Search)**

#### 2.1 搜尋表單
```
┌─────────────────────────────────────────────┐
│ 基礎參數                                     │
├─────────────────────────────────────────────┤
│ • 代幣: [ETH ▼]                             │
│ • 投資資本: [$10,000]                        │
│ • 風險偏好: [○ Low ● Medium ○ High]         │
├─────────────────────────────────────────────┤
│ 對沖參數 (新增)                              │
├─────────────────────────────────────────────┤
│ • 對沖比率: [━━━●━━━] 100%                  │
│ • 再平衡頻率: [7] 天                         │
├─────────────────────────────────────────────┤
│ 篩選器 (可展開)                              │
├─────────────────────────────────────────────┤
│ ▼ TVL 範圍                                  │
│   最小: [$5M]  最大: [無限制]               │
│                                             │
│ ▼ APY 範圍                                  │
│   最小: [5%]   最大: [無限制]               │
│                                             │
│ ▼ 協議                                      │
│   ☑ Uniswap V3  ☑ Curve  ☐ Balancer        │
│                                             │
│ ▼ 區塊鏈                                    │
│   ☑ Ethereum  ☑ Arbitrum  ☑ Optimism       │
│                                             │
│ ▼ IL 風險等級                               │
│   ☐ Low  ☑ Medium  ☑ High                  │
└─────────────────────────────────────────────┘
         [🔍 開始搜尋]
```

#### 2.2 結果展示

**卡片視圖**（默認）
```
┌─────────────────────────────────────────────┐
│ 🥇 #1 - Uniswap V3 WETH-USDC (Arbitrum)     │
├─────────────────────────────────────────────┤
│ 綜合評分: ⭐ 93.0/100                        │
│                                             │
│ 📊 收益分析                                  │
│ • 調整後淨 APY: 91.86%                       │
│ • 預期年收益: $9,186                         │
│                                             │
│ 🛡️ IL 分析                                   │
│ • 預期 IL (無對沖): -32.00%                  │
│ • 對沖有效性: 97.67%                         │
│ • 淨 IL (對沖後): -0.75% ✨                  │
│ • 對沖質量: excellent                        │
│                                             │
│ 💰 收益分解                                  │
│ ┌─────────────────────────────────────┐     │
│ │ LP 收益        $8,366 ████████░░░   │     │
│ │ 資金費率收益   $1,095 ██░░░░░░░░░   │     │
│ │ IL 損失        -$75   ░░░░░░░░░░░   │     │
│ │ Gas 成本       -$200  ░░░░░░░░░░░   │     │
│ └─────────────────────────────────────┘     │
│                                             │
│ 📈 戴維斯評分: 100/100 (極佳)                │
│ 💧 TVL: $158.9M                             │
│                                             │
│         [查看詳情] [開始投資]                │
└─────────────────────────────────────────────┘
```

**表格視圖**（可切換）
```
┌─────┬──────────┬─────┬────────┬──────┬─────────┬──────────┬────────┐
│ 排名 │ 池       │ 鏈  │ 淨 APY │ 收益 │ IL 影響 │ 對沖質量 │ 評分   │
├─────┼──────────┼─────┼────────┼──────┼─────────┼──────────┼────────┤
│ 🥇  │ WETH-USDC│ Arb │ 91.86% │$9,186│  -$75   │excellent │ 93.0   │
│ 🥈  │ WETH-USDT│ Eth │ 83.75% │$8,375│  -$75   │excellent │ 92.1   │
│ 🥉  │ WBTC-WETH│ Arb │ 51.80% │$5,180│  -$75   │excellent │ 85.1   │
└─────┴──────────┴─────┴────────┴──────┴─────────┴──────────┴────────┘
```

### 3. **詳情頁面 (Details)**

展示單個投資機會的完整信息：

#### 3.1 概覽
- 池名稱、協議、鏈
- 綜合評分（大數字 + 進度條）
- 關鍵指標（TVL、APY、收益）

#### 3.2 收益分析
- **圖表**: 收益分解（餅圖或堆疊柱狀圖）
- **表格**: 詳細數據
  - LP APY
  - 資金費率 APY
  - 總 APY
  - 調整後淨 APY

#### 3.3 IL 分析（重點）
- **對沖效果對比圖**
  ```
  無對沖    50% 對沖   100% 對沖
  ┌───┐     ┌───┐     ┌───┐
  │   │     │   │     │   │
  │ 78│     │ 94│     │110│ APY (%)
  │   │     │   │     │   │
  └───┘     └───┘     └───┘
  IL: -32%  IL: -16%  IL: -0.75%
  ```

- **IL 風險指標**
  - 池波動率
  - 預期 IL（無對沖）
  - 對沖有效性
  - 淨 IL（對沖後）
  - IL 影響（USD）
  - 風險等級
  - 對沖質量

#### 3.4 戴維斯雙擊分析
- 評分: 100/100
- 評級: 極佳
- 分析說明

#### 3.5 成本分析
- Gas 成本估算
- 年化成本
- ROI

#### 3.6 操作建議
- 投資步驟
- 風險提示
- 最佳實踐

### 4. **對比頁面 (Compare)**

並排對比多個投資機會：
```
┌─────────────┬─────────────┬─────────────┐
│  方案 A     │  方案 B     │  方案 C     │
├─────────────┼─────────────┼─────────────┤
│ WETH-USDC   │ WETH-USDT   │ WBTC-WETH   │
│ Arbitrum    │ Ethereum    │ Arbitrum    │
├─────────────┼─────────────┼─────────────┤
│ 淨 APY      │ 淨 APY      │ 淨 APY      │
│ 91.86%      │ 83.75%      │ 51.80%      │
├─────────────┼─────────────┼─────────────┤
│ IL 影響     │ IL 影響     │ IL 影響     │
│ -$75        │ -$75        │ -$75        │
├─────────────┼─────────────┼─────────────┤
│ 對沖質量    │ 對沖質量    │ 對沖質量    │
│ excellent   │ excellent   │ excellent   │
└─────────────┴─────────────┴─────────────┘
```

---

## 技術棧

### 前端框架
- **React 18** - 使用 `manus-create-react-app` 創建
- **TypeScript** - 類型安全
- **Vite** - 快速構建

### UI 組件庫
- **Tailwind CSS** - 樣式框架
- **shadcn/ui** - 預構建組件
- **Lucide Icons** - 圖標庫

### 數據可視化
- **Recharts** - 圖表庫
  - 柱狀圖（收益對比）
  - 餅圖（收益分解）
  - 折線圖（歷史趨勢）
  - 雷達圖（綜合評分）

### 狀態管理
- **React Query** - API 數據管理
- **Zustand** - 全局狀態（可選）

### API 整合
- **Axios** - HTTP 客戶端
- **Base URL**: `https://lal-smart-search-api.onrender.com`

---

## 核心組件設計

### 1. SearchForm 組件
```typescript
interface SearchFormProps {
  onSearch: (params: SearchParams) => void;
  loading: boolean;
}

interface SearchParams {
  token: string;
  capital: number;
  riskTolerance: 'low' | 'medium' | 'high';
  hedgeRatio: number;
  rebalanceFrequencyDays: number;
  filters?: FilterCriteria;
}
```

### 2. OpportunityCard 組件
```typescript
interface OpportunityCardProps {
  opportunity: Opportunity;
  rank: number;
  onViewDetails: (id: string) => void;
}

interface Opportunity {
  pool_id: string;
  protocol: string;
  chain: string;
  symbol: string;
  tvl: number;
  adjusted_net_apy: number;
  adjusted_net_profit: number;
  il_analysis: ILAnalysis;
  profit_breakdown: ProfitBreakdown;
  davis_score: number;
  final_score: number;
}
```

### 3. ILAnalysisPanel 組件
```typescript
interface ILAnalysisPanelProps {
  ilAnalysis: ILAnalysis;
  showComparison?: boolean;
}

interface ILAnalysis {
  pool_volatility: number;
  expected_il_annual: number;
  hedge_effectiveness: number;
  net_il_annual: number;
  il_impact_usd: number;
  il_risk_level: 'low' | 'medium' | 'high';
  hedge_quality: 'poor' | 'fair' | 'good' | 'excellent';
}
```

### 4. ProfitBreakdownChart 組件
```typescript
interface ProfitBreakdownChartProps {
  breakdown: ProfitBreakdown;
  chartType: 'bar' | 'pie';
}

interface ProfitBreakdown {
  lp_profit: number;
  funding_profit: number;
  il_loss: number;
  gas_cost: number;
  total: number;
}
```

### 5. HedgeComparisonChart 組件
```typescript
interface HedgeComparisonChartProps {
  data: HedgeComparisonData[];
}

interface HedgeComparisonData {
  strategy: string;
  apy: number;
  il: number;
  profit: number;
}
```

---

## 顏色系統

### 主題色
- **Primary**: `#3B82F6` (藍色) - CTA、鏈接
- **Success**: `#10B981` (綠色) - 正收益、優質評級
- **Warning**: `#F59E0B` (橙色) - 中等風險
- **Danger**: `#EF4444` (紅色) - 高風險、損失
- **Info**: `#6366F1` (紫色) - 信息提示

### 語義色
- **Profit**: 綠色漸變
- **Loss**: 紅色
- **Neutral**: 灰色
- **Excellent**: 深綠色
- **Good**: 淺綠色
- **Fair**: 黃色
- **Poor**: 紅色

---

## 響應式設計

### 斷點
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

### 適配策略
- Mobile: 單列卡片，簡化篩選器
- Tablet: 雙列卡片，側邊欄篩選器
- Desktop: 三列卡片，完整篩選器

---

## 用戶體驗優化

### 1. 加載狀態
- Skeleton 加載動畫
- 進度指示器
- 優雅的錯誤處理

### 2. 交互反饋
- Hover 效果
- 點擊動畫
- Toast 通知

### 3. 性能優化
- 虛擬滾動（大量結果）
- 圖片懶加載
- API 請求緩存

### 4. 無障礙
- ARIA 標籤
- 鍵盤導航
- 屏幕閱讀器支持

---

## 開發計劃

### Phase 1: 基礎設置 ✅
- [x] 創建 React 應用
- [x] 安裝依賴
- [x] 設置 Tailwind CSS
- [x] 配置 API 客戶端

### Phase 2: 核心組件
- [ ] SearchForm 組件
- [ ] OpportunityCard 組件
- [ ] ILAnalysisPanel 組件
- [ ] ProfitBreakdownChart 組件

### Phase 3: 頁面開發
- [ ] 主頁
- [ ] 搜尋頁面
- [ ] 詳情頁面
- [ ] 對比頁面

### Phase 4: 整合和測試
- [ ] API 整合
- [ ] 端到端測試
- [ ] 性能優化
- [ ] 部署

---

## API 整合示例

```typescript
// api/client.ts
import axios from 'axios';

const API_BASE_URL = 'https://lal-smart-search-api.onrender.com';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 分鐘
});

// api/search.ts
export async function searchOpportunities(params: SearchParams) {
  const response = await api.get('/api/v1/lal/smart-search', {
    params: {
      token: params.token,
      capital: params.capital,
      risk_tolerance: params.riskTolerance,
      hedge_ratio: params.hedgeRatio,
      rebalance_frequency_days: params.rebalanceFrequencyDays,
      min_apy: params.filters?.minApy,
      limit: params.limit || 10,
    },
  });
  
  return response.data.data;
}
```

---

## 部署

### 開發環境
```bash
npm run dev
```

### 生產構建
```bash
npm run build
```

### 部署到 Render
- 連接 GitHub 倉庫
- 設置構建命令: `npm run build`
- 設置發布目錄: `dist`
- 自動部署

---

**設計完成！準備開始開發。** 🚀

