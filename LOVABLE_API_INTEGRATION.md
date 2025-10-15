# Lovable 前端 API 集成指南

本指南專門針對在 Lovable.dev 平台上開發 LiveaLittle DeFi 前端時如何集成後端 API。

---

## 第一步：設置 API 客戶端

在 Lovable 項目中創建 API 客戶端文件。

### 提示詞給 Lovable：

```
創建一個新文件 src/lib/api-client.ts，實現以下功能：

1. 使用 axios 創建 API 客戶端
2. 基礎 URL 設置為環境變量 VITE_API_BASE_URL
3. 自動添加 Authorization 頭部（從 localStorage 獲取 token）
4. 實現以下 API 方法：
   - login(email, password)
   - getPortfolioOverview()
   - getPortfolioPerformance(timeframe)
   - getPortfolioPositions()
   - getMarketPools(protocol?, chain?)
   - getMarketRegime()
   - getExecutionOpportunities()
   - executeRebalance(opportunityId)
   - getSubscriptionPlans()

5. 添加錯誤處理和請求攔截器
```

---

## 第二步：創建 React Hooks

### 提示詞給 Lovable：

```
創建文件 src/hooks/useApi.ts，實現以下自定義 Hooks：

1. usePortfolioOverview()
   - 獲取投資組合總覽
   - 返回 { data, loading, error, refetch }
   - 使用 useQuery 或 useState + useEffect

2. usePortfolioPerformance(timeframe)
   - 獲取歷史表現數據
   - 支持時間範圍參數
   - 返回圖表所需的數據格式

3. useMarketPools(filters)
   - 獲取流動性池列表
   - 支持協議和鏈過濾
   - 返回池列表和加載狀態

4. useExecutionOpportunities()
   - 獲取再平衡機會
   - 每 30 秒自動刷新
   - 返回機會列表

所有 Hooks 都應該：
- 處理加載狀態
- 處理錯誤
- 支持手動刷新
- 在組件卸載時清理
```

---

## 第三步：實現儀表板組件

### 提示詞給 Lovable：

```
更新 Dashboard 頁面，集成真實 API 數據：

1. 總覽卡片：
   - 使用 usePortfolioOverview() Hook
   - 顯示 total_value_usd, total_return_percent, apy
   - 添加加載骨架屏
   - 添加錯誤提示

2. 收益曲線圖：
   - 使用 usePortfolioPerformance('30d') Hook
   - 使用 Recharts LineChart 組件
   - X 軸顯示日期，Y 軸顯示美元金額
   - 添加工具提示顯示詳細數據

3. 倉位列表：
   - 使用 usePortfolioPositions() Hook
   - 表格顯示：協議、類型、資產、價值、APY
   - 支持按 APY 排序
   - 添加刷新按鈕

配色使用之前定義的主題：
- 主色: #00D9FF
- 背景: #0A0E27
- 卡片背景: #1A1F3A
```

---

## 第四步：實現策略配置頁面

### 提示詞給 Lovable：

```
創建 Strategy 頁面，包含以下功能：

1. LP 池選擇器：
   - 使用 useMarketPools() Hook 獲取可用池
   - 顯示卡片列表，每個卡片包含：
     * 代幣對（如 ETH/USDC）
     * 協議和鏈
     * TVL 和 APY
     * 選擇按鈕
   - 支持按協議和鏈過濾
   - 支持搜索

2. 風險設置：
   - 滑塊選擇槓桿倍數（1-3x）
   - 滑塊選擇再平衡閾值（1-20%）
   - 實時顯示預計收益和風險

3. 保存按鈕：
   - 調用 API 保存策略配置
   - 顯示成功/失敗提示
   - 成功後跳轉到儀表板
```

---

## 第五步：實現轉倉確認系統

### 提示詞給 Lovable：

```
創建 Rebalance 頁面，實現轉倉確認流程：

1. 機會列表：
   - 使用 useExecutionOpportunities() Hook
   - 每個機會顯示為卡片，包含：
     * 描述
     * 預計收益（綠色）
     * 預計成本（紅色）
     * 淨收益（收益 - 成本）
     * 確認按鈕

2. 確認對話框：
   - 點擊確認按鈕彈出對話框
   - 顯示詳細的交易信息
   - 顯示風險警告
   - 最終確認按鈕

3. 執行狀態：
   - 調用 executeRebalance() API
   - 顯示執行進度
   - 輪詢 getExecutionStatus() 獲取狀態
   - 顯示交易哈希和區塊鏈瀏覽器鏈接

4. 自動刷新：
   - 每 30 秒刷新機會列表
   - 顯示上次更新時間
```

---

## 第六步：實現訂閱管理

### 提示詞給 Lovable：

```
創建 Subscription 頁面，集成 Stripe 支付：

1. 定價表格：
   - 使用 getSubscriptionPlans() API
   - 顯示 3 個訂閱層級（基礎版、專業版、機構版）
   - 每個層級顯示：
     * 價格
     * 功能列表
     * 訂閱按鈕

2. Stripe 集成：
   - 安裝 @stripe/stripe-js 和 @stripe/react-stripe-js
   - 創建 Stripe Elements
   - 處理支付流程
   - 調用 subscribe() API

3. 當前訂閱狀態：
   - 使用 getSubscriptionStatus() API
   - 顯示當前計劃
   - 顯示下次計費日期
   - 提供升級/降級選項

配色保持一致，使用卡片佈局和漸變背景。
```

---

## 第七步：添加認證流程

### 提示詞給 Lovable：

```
創建認證相關組件和頁面：

1. Login 頁面：
   - 郵箱和密碼輸入框
   - 登錄按鈕
   - 調用 login() API
   - 保存 token 到 localStorage
   - 成功後跳轉到儀表板

2. Register 頁面：
   - 郵箱、密碼、確認密碼輸入框
   - 註冊按鈕
   - 調用 register() API
   - 自動登錄並跳轉

3. ProtectedRoute 組件：
   - 檢查 localStorage 中的 token
   - 未登錄時重定向到登錄頁
   - 包裝所有需要認證的頁面

4. 錢包連接（RainbowKit）：
   - 集成 RainbowKit
   - 在導航欄顯示連接按鈕
   - 連接後顯示地址和餘額
```

---

## 第八步：錯誤處理和加載狀態

### 提示詞給 Lovable：

```
創建全局錯誤處理和加載組件：

1. ErrorBoundary 組件：
   - 捕獲 React 錯誤
   - 顯示友好的錯誤頁面
   - 提供重試按鈕

2. LoadingSpinner 組件：
   - 全屏加載動畫
   - 使用主題顏色
   - 可選的加載文字

3. Toast 通知：
   - 使用 react-hot-toast 或 sonner
   - 成功、錯誤、警告三種類型
   - 自動消失

4. API 錯誤處理：
   - 在 API 客戶端添加響應攔截器
   - 401 錯誤：清除 token 並跳轉登錄
   - 429 錯誤：顯示速率限制提示
   - 500 錯誤：顯示服務器錯誤提示
```

---

## 第九步：優化和性能

### 提示詞給 Lovable：

```
優化應用性能：

1. 數據緩存：
   - 使用 React Query 或 SWR
   - 設置合理的緩存時間
   - 實現樂觀更新

2. 懶加載：
   - 使用 React.lazy() 和 Suspense
   - 按路由分割代碼
   - 預加載關鍵資源

3. 圖表優化：
   - 限制數據點數量
   - 使用虛擬化處理大列表
   - 防抖搜索和過濾

4. 離線支持：
   - 使用 Service Worker
   - 緩存靜態資源
   - 顯示離線狀態
```

---

## 第十步：測試和部署

### 提示詞給 Lovable：

```
添加測試和準備部署：

1. 單元測試：
   - 測試 API 客戶端函數
   - 測試自定義 Hooks
   - 使用 Vitest 和 React Testing Library

2. 集成測試：
   - 測試完整的用戶流程
   - 模擬 API 響應
   - 測試錯誤處理

3. 環境變量：
   - 創建 .env.example 文件
   - 文檔化所有需要的環境變量
   - 設置開發和生產環境

4. 部署到 Vercel：
   - 連接 GitHub 倉庫
   - 配置環境變量
   - 設置自動部署
   - 配置自定義域名
```

---

## 完整的環境變量列表

在 Lovable 項目設置中添加以下環境變量：

```bash
# API 配置
VITE_API_BASE_URL=https://api.livealittle-defi.com/api/v1

# Supabase 配置
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Stripe 配置
VITE_STRIPE_PUBLIC_KEY=pk_live_...

# WalletConnect 配置
VITE_WALLETCONNECT_PROJECT_ID=your-project-id
```

---

## API 調用範例代碼片段

以下是一些可以直接在 Lovable 中使用的代碼片段：

### 儀表板數據獲取

```typescript
import { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';

export function Dashboard() {
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await api.getPortfolioOverview();
        setPortfolio(data);
      } catch (error) {
        console.error('Failed to fetch portfolio:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="grid grid-cols-3 gap-4">
      <Card>
        <h3>總資產</h3>
        <p className="text-3xl font-bold">
          ${portfolio.total_value_usd.toLocaleString()}
        </p>
      </Card>
      <Card>
        <h3>總收益</h3>
        <p className="text-3xl font-bold text-green-500">
          {portfolio.total_return_percent.toFixed(2)}%
        </p>
      </Card>
      <Card>
        <h3>年化收益率</h3>
        <p className="text-3xl font-bold">
          {portfolio.apy.toFixed(2)}%
        </p>
      </Card>
    </div>
  );
}
```

### 市場池選擇器

```typescript
import { useState, useEffect } from 'react';
import { api } from '@/lib/api-client';

export function PoolSelector() {
  const [pools, setPools] = useState([]);
  const [protocol, setProtocol] = useState('');
  const [chain, setChain] = useState('');

  useEffect(() => {
    async function fetchPools() {
      const data = await api.getMarketPools(protocol, chain);
      setPools(data);
    }
    fetchPools();
  }, [protocol, chain]);

  return (
    <div>
      <div className="flex gap-4 mb-4">
        <select 
          value={protocol} 
          onChange={(e) => setProtocol(e.target.value)}
        >
          <option value="">所有協議</option>
          <option value="uniswap_v3">Uniswap V3</option>
          <option value="curve">Curve</option>
        </select>
        
        <select 
          value={chain} 
          onChange={(e) => setChain(e.target.value)}
        >
          <option value="">所有鏈</option>
          <option value="ethereum">Ethereum</option>
          <option value="arbitrum">Arbitrum</option>
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {pools.map((pool) => (
          <PoolCard key={pool.pool_id} pool={pool} />
        ))}
      </div>
    </div>
  );
}
```

---

## 故障排除

### 常見問題

**問題 1：CORS 錯誤**

解決方案：確保後端 API 服務器配置了正確的 CORS 設置，允許來自 Lovable 部署域名的請求。

**問題 2：Token 過期**

解決方案：在 API 客戶端添加響應攔截器，自動檢測 401 錯誤並重定向到登錄頁。

**問題 3：數據不更新**

解決方案：檢查緩存設置，確保在需要時調用 `refetch()` 函數刷新數據。

---

## 總結

本指南提供了在 Lovable 平台上集成 LiveaLittle DeFi API 的完整步驟。按照這些提示詞和代碼範例，您可以快速構建一個功能完整的 DeFi 投資平台前端。

關鍵要點：

1. 使用 Axios 創建統一的 API 客戶端
2. 使用自定義 Hooks 管理數據獲取
3. 實現完善的錯誤處理和加載狀態
4. 集成 Stripe 進行支付處理
5. 使用 RainbowKit 進行錢包連接
6. 優化性能和用戶體驗

如有任何問題，請參考完整的 API 文檔或聯繫開發團隊。

