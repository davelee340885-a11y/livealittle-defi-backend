# LAL 智能搜尋 - Lovable 項目提示詞

## 項目概述

創建一個專業的 **LAL (LiveaLittle) 智能搜尋**前端應用，用於展示 Delta Neutral 投資機會分析。

**核心功能**：
- 搜尋表單（代幣、資本、對沖參數、篩選條件）
- 投資機會列表（卡片視圖）
- IL（無常損失）分析展示
- 對沖效果可視化
- 收益分解圖表

**API 端點**: `https://lal-smart-search-api.onrender.com`

---

## 第一步：創建項目提示詞

複製以下提示詞到 Lovable：

```
創建一個名為 "LAL 智能搜尋" 的 Web 應用，用於 DeFi Delta Neutral 投資機會分析。

### 主要功能

1. **搜尋表單**
   - 代幣選擇（默認 ETH）
   - 投資資本輸入（默認 $10,000）
   - 對沖比率滑塊（0-100%，默認 100%）
   - 再平衡頻率（天數，默認 7）
   - 最小 APY 篩選（默認 50%）
   - 結果數量限制（默認 5）

2. **投資機會卡片**
   每個卡片顯示：
   - 排名徽章（🥇🥈🥉）
   - 協議和鏈（Badge）
   - 綜合評分（大數字）
   - 調整後淨 APY
   - 預期年收益
   - IL 對沖分析（預期 IL、淨 IL、對沖有效性、對沖質量）
   - 收益分解（LP 收益、資金費率收益、IL 損失、Gas 成本）
   - 戴維斯評分
   - TVL

3. **設計要求**
   - 使用 Tailwind CSS
   - 使用 shadcn/ui 組件
   - 響應式設計
   - 專業的配色方案（藍色主題）
   - 卡片式布局
   - 進度條展示收益分解
   - 徽章展示協議和鏈

4. **API 整合**
   - 端點: `https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search`
   - 方法: GET
   - 參數: token, capital, hedge_ratio, rebalance_frequency_days, min_apy, limit

### 頁面結構

**Header**
- 標題: "LAL 智能搜尋"
- 副標題: "找到最佳 Delta Neutral 投資機會"
- API 狀態指示器

**Hero Section**（搜尋前顯示）
- 大標題: "智能分析，精準投資"
- 副標題: "整合戴維斯雙擊分析、Delta Neutral 策略、IL 計算和對沖效果分析"
- 4 個功能卡片:
  1. 戴維斯雙擊（Search 圖標）
  2. Delta Neutral（TrendingUp 圖標）
  3. IL 對沖分析（Shield 圖標）
  4. 成本優化（DollarSign 圖標）

**搜尋表單**
- 卡片式布局
- 分組顯示（基礎參數、對沖參數、篩選條件）
- 提交按鈕（帶加載狀態）

**結果列表**
- 顯示找到的機會數量
- 篩選前後對比
- 卡片列表（垂直排列）

**Footer**
- 版權信息

### 顏色系統

- Primary: 藍色 (#3B82F6)
- Success: 綠色 (#10B981) - 用於正收益
- Warning: 黃色 (#F59E0B) - 用於中等風險
- Danger: 紅色 (#EF4444) - 用於損失和高風險
- Background: 漸變（藍色到紫色）

### 示例 API 響應

```json
{
  "success": true,
  "data": {
    "opportunities": [
      {
        "protocol": "uniswap-v3",
        "chain": "Ethereum",
        "symbol": "WETH-USDT",
        "tvl": 158947142,
        "adjusted_net_apy": 91.86,
        "adjusted_net_profit": 9186,
        "il_analysis": {
          "expected_il_annual": -32.00,
          "net_il_annual": -0.75,
          "hedge_effectiveness": 0.977,
          "hedge_quality": "excellent"
        },
        "profit_breakdown": {
          "lp_profit": 8366,
          "funding_profit": 1095,
          "il_loss": -75,
          "gas_cost": -200
        },
        "davis_score": 100,
        "davis_category": "極佳",
        "final_score": 93.0
      }
    ]
  }
}
```

請創建這個應用，確保 UI 專業、交互流暢、數據展示清晰。
```

---

## 第二步：組件代碼參考

如果 Lovable 需要更詳細的代碼，可以參考以下組件：

### SearchForm 組件要點

```typescript
// 狀態管理
const [params, setParams] = useState({
  token: 'ETH',
  capital: 10000,
  hedgeRatio: 1.0,
  rebalanceFrequencyDays: 7,
  minApy: 50,
  limit: 5,
})

// API 調用
const handleSubmit = async (e) => {
  e.preventDefault()
  const queryParams = new URLSearchParams({
    token: params.token,
    capital: params.capital,
    hedge_ratio: params.hedgeRatio,
    rebalance_frequency_days: params.rebalanceFrequencyDays,
    min_apy: params.minApy,
    limit: params.limit,
  })
  
  const response = await fetch(
    `https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?${queryParams}`
  )
  const data = await response.json()
  onSearch(data.data)
}
```

### OpportunityCard 組件要點

```typescript
// 格式化函數
const formatCurrency = (value) => 
  new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency: 'USD' 
  }).format(value)

const formatPercent = (value) => `${value.toFixed(2)}%`

// 顏色映射
const getHedgeQualityColor = (quality) => {
  const colors = {
    excellent: 'text-green-600',
    good: 'text-green-500',
    fair: 'text-yellow-600',
    poor: 'text-red-600',
  }
  return colors[quality] || 'text-gray-600'
}

// 排名徽章
const getRankBadge = (rank) => {
  if (rank === 1) return '🥇'
  if (rank === 2) return '🥈'
  if (rank === 3) return '🥉'
  return `#${rank}`
}
```

---

## 第三步：Lovable 操作步驟

### 1. 創建新項目
1. 登入 Lovable (https://lovable.dev)
2. 點擊 "New Project"
3. 輸入項目名稱: "LAL Smart Search"

### 2. 輸入提示詞
1. 複製上面的完整提示詞
2. 粘貼到 Lovable 的聊天框
3. 點擊發送

### 3. 等待生成
- Lovable 會自動生成完整的 React 應用
- 包含所有組件、樣式和 API 整合

### 4. 測試和調整
1. 點擊 "Preview" 查看應用
2. 測試搜尋功能
3. 檢查 API 響應
4. 根據需要調整樣式或功能

### 5. 部署
1. 點擊 "Deploy"
2. 選擇部署平台（Vercel/Netlify）
3. 獲取部署 URL

---

## 第四步：進階功能（可選）

如果基礎功能完成後，可以添加：

### 1. 對沖效果對比圖表
```
創建一個柱狀圖，對比不同對沖比率（0%, 50%, 100%）的收益和 IL 影響。

使用 Recharts 庫，顯示：
- X 軸：對沖策略（無對沖、50% 對沖、100% 對沖）
- Y 軸：APY 和 IL
- 兩組柱狀圖（APY 綠色，IL 紅色）
```

### 2. 詳情頁面
```
為每個投資機會創建詳情頁面，包含：
- 完整的池信息
- 歷史 APY 趨勢圖（模擬數據）
- 詳細的 IL 分析
- 投資步驟指南
- 風險提示
```

### 3. 對比功能
```
允許用戶選擇多個投資機會進行並排對比，顯示：
- 所有關鍵指標的對比表格
- 雷達圖展示綜合評分
- 推薦最佳選擇
```

---

## 常見問題

### Q1: API 調用失敗怎麼辦？
**A**: 檢查：
1. API URL 是否正確
2. 參數格式是否正確
3. 網絡連接是否正常
4. 在瀏覽器控制台查看錯誤信息

### Q2: 如何調整樣式？
**A**: 告訴 Lovable：
```
請將主題色從藍色改為紫色，並增大卡片間距。
```

### Q3: 如何添加加載動畫？
**A**: 告訴 Lovable：
```
在搜尋時顯示骨架屏加載動畫，使用 shadcn/ui 的 Skeleton 組件。
```

### Q4: 如何優化移動端體驗？
**A**: 告訴 Lovable：
```
優化移動端布局：
- 搜尋表單改為單列
- 卡片改為全寬
- 簡化篩選器為可展開的抽屜
```

---

## 完整的 Lovable 提示詞模板

如果您想要更詳細的控制，可以使用這個完整版本：

```
# LAL 智能搜尋 Web 應用

## 項目描述
創建一個專業的 DeFi 投資分析工具，幫助用戶找到最佳的 Delta Neutral 投資機會。

## 技術棧
- React + TypeScript
- Tailwind CSS
- shadcn/ui 組件
- Lucide Icons
- Recharts（圖表）

## 頁面結構

### 1. Header
- Logo 和標題："LAL 智能搜尋"
- 副標題："找到最佳 Delta Neutral 投資機會"
- API 狀態指示器（綠點 + "API 已連接"）

### 2. Hero Section（初始狀態）
- 大標題："智能分析，精準投資"
- 副標題："整合戴維斯雙擊分析、Delta Neutral 策略、IL 計算和對沖效果分析"
- 4 個功能卡片（2x2 網格）：
  - 戴維斯雙擊（Search 圖標，藍色）
  - Delta Neutral（TrendingUp 圖標，綠色）
  - IL 對沖分析（Shield 圖標，紫色）
  - 成本優化（DollarSign 圖標，黃色）

### 3. 搜尋表單（Card 組件）
**基礎參數區域**
- 代幣輸入框（默認 "ETH"）
- 投資資本數字輸入框（默認 10000）

**對沖參數區域**（淺藍色背景）
- 對沖比率滑塊（0-100%，默認 100%）
  - 顯示當前值
  - 提示文字："100% 對沖可將 IL 從 -32% 降低到 -0.75%"
- 再平衡頻率數字輸入框（1-30 天，默認 7）
  - 提示文字："建議每週（7天）再平衡以獲得最佳對沖效果"

**篩選條件區域**（淺灰色背景）
- 最小 APY 數字輸入框（默認 50）
- 結果數量數字輸入框（1-20，默認 5）

**提交按鈕**
- 全寬，大尺寸
- 藍色背景
- Search 圖標 + "開始搜尋"
- 加載狀態：Loader2 圖標旋轉 + "搜尋中..."

### 4. 結果列表
**頭部**
- 左側：找到的機會數量
- 右側：篩選前後對比

**投資機會卡片**（垂直排列）
每個卡片包含：

**卡片頭部**
- 左側：
  - 排名徽章（🥇🥈🥉 或 #4）
  - 池名稱（如 "WETH-USDC"）
  - 協議和鏈的 Badge
- 右側：
  - 綜合評分（大數字，顏色根據分數）
  - "綜合評分" 小字

**收益分析區域**
- TrendingUp 圖標 + "收益分析"
- 兩列：
  - 調整後淨 APY（大數字，綠色）
  - 預期年收益（大數字，綠色）

**IL 對沖分析區域**（淺藍色背景）
- Shield 圖標 + "IL 對沖分析"
- 2x2 網格：
  - 預期 IL（無對沖）：紅色
  - 淨 IL（對沖後）：綠色
  - 對沖有效性：百分比
  - 對沖質量：顏色根據質量
- 分隔線
- IL 影響（USD）：紅色

**收益分解區域**
- DollarSign 圖標 + "收益分解"
- 4 行，每行包含：
  - 項目名稱
  - 進度條（根據比例）
  - 金額（綠色為正，紅色為負）
- 分隔線
- 總收益（大字體，綠色）

**其他指標區域**
- 2 列：
  - 戴維斯評分：分數 + 評級
  - TVL：格式化的大數字（M/B）

### 5. Footer
- 居中
- "© 2025 LAL 智能搜尋 - Powered by Manus AI"

## API 整合

**端點**: `https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search`

**參數**:
- token: string
- capital: number
- hedge_ratio: number (0-1)
- rebalance_frequency_days: number
- min_apy: number
- limit: number

**響應格式**: 見上面的示例

## 樣式要求

**顏色**:
- Primary: #3B82F6（藍色）
- Success: #10B981（綠色）
- Warning: #F59E0B（黃色）
- Danger: #EF4444（紅色）
- Background: 藍色到紫色漸變

**排版**:
- 標題：粗體，大字號
- 數字：等寬字體
- 卡片：白色背景，陰影，圓角

**交互**:
- 卡片 hover 效果：陰影加深
- 按鈕 hover 效果：顏色加深
- 平滑過渡動畫

## 響應式設計
- Desktop (>1024px): 最大寬度容器，多列布局
- Tablet (640-1024px): 雙列卡片
- Mobile (<640px): 單列，簡化篩選器

請創建這個應用，確保代碼質量高、UI 專業、用戶體驗流暢。
```

---

## 提示

1. **分步驟進行**：先創建基礎版本，測試通過後再添加高級功能
2. **使用 Lovable 的迭代功能**：隨時調整和優化
3. **保持簡潔**：不要一次性要求太多功能
4. **測試 API**：確保 API 端點可訪問
5. **保存進度**：Lovable 會自動保存，但建議定期導出代碼

---

**準備好了嗎？複製上面的提示詞到 Lovable，開始創建您的 LAL 智能搜尋應用！** 🚀

