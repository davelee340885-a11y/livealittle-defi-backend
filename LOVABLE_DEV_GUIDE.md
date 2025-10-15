# LiveaLittle DeFi - Lovable 開發完整指南

## 🎯 項目概述

**項目名稱**: LiveaLittle DeFi  
**技術棧**: React + TypeScript + Tailwind CSS + Supabase + Stripe  
**開發平台**: Lovable.dev  
**預計時間**: 1-2 週

---

## 📋 完整開發計劃

### Week 1: 核心功能開發

**Day 1-2: 項目初始化與認證**
- 在 Lovable 創建項目
- 設置 Supabase 認證
- 實現錢包連接（RainbowKit）

**Day 3-4: 儀表板開發**
- 總覽卡片（總資產、收益、APY）
- 收益曲線圖（Recharts）
- 倉位列表

**Day 5-7: 策略配置**
- LP 池選擇器
- 風險設置
- 自動轉倉配置

### Week 2: 高級功能與商業化

**Day 8-10: 轉倉確認系統**
- 機會卡片
- 成本分析
- 手動確認按鈕

**Day 11-12: 回測展示**
- 回測結果圖表
- 績效指標表格
- 策略對比

**Day 13-14: 訂閱與支付**
- Stripe 集成
- 定價表格
- 訂閱管理

---

## 🎨 Lovable 開發提示詞

### 提示詞 1: 項目初始化

```
創建一個名為 "LiveaLittle DeFi" 的 Web 應用。

技術要求:
- React + TypeScript + Tailwind CSS
- 使用 Supabase 作為後端
- 使用 RainbowKit 進行錢包連接

配色方案:
- 主色: #00D9FF (青色)
- 輔色: #00FF88 (綠色)  
- 背景: #0A0E27 (深藍)
- 文字: #E0E6ED (淺灰)

創建以下頁面:
1. Landing Page (首頁)
2. Dashboard (儀表板)
3. Strategy (策略配置)
4. Backtest (回測展示)
5. Subscription (訂閱管理)

請先創建基礎的路由和導航欄。
```

### 提示詞 2: 儀表板

```
在 Dashboard 頁面添加以下組件:

1. 總覽卡片 (3個並排):
   - 總資產: 顯示美元金額，大字體
   - 總收益: 顯示百分比，綠色表示正收益
   - 年化收益率: 顯示 APY%

2. 收益曲線圖:
   - 使用 Recharts LineChart
   - 顯示過去 30 天的收益曲線
   - 對比 Delta Neutral 和純 LP 策略

3. 倉位列表:
   - 表格顯示: 協議、鏈、代幣對、金額、APY
   - 支持排序

使用之前定義的配色方案，卡片使用圓角和陰影。
```

### 提示詞 3: 策略配置

```
創建策略配置頁面:

1. LP 池選擇器:
   - 顯示高評分 LP 池列表
   - 每個池顯示: 協議名稱、鏈、代幣對、TVL、APY、戴維斯評分
   - 支持多選
   - 顯示預期收益計算

2. 風險設置:
   - 滑塊: 回撤容忍度 (0-30%)
   - 滑塊: 對沖比例 (0-100%)
   - 開關: 自動轉倉
   - 數字輸入: 轉倉閾值 (APY 提升%)

3. 確認按鈕:
   - 大按鈕，青色背景
   - 點擊後顯示確認對話框

使用卡片佈局，確保移動端響應式。
```

### 提示詞 4: 轉倉確認

```
創建轉倉確認對話框:

1. 機會摘要卡片:
   - 從 XXX 池 → YYY 池
   - APY 提升: +100% (綠色大字)
   - 預期 30 天收益: $XXX
   - 總成本: $XXX
   - 淨收益: $XXX (綠色)
   - 回本天數: X 天

2. 執行計劃 (4 步驟):
   - Step 1: 平倉舊資產空頭 (1-2分鐘)
   - Step 2: 退出舊 LP 池 (2-3分鐘)
   - Step 3: 進入新 LP 池 (2-3分鐘)
   - Step 4: 開設新資產空頭 (1-2分鐘)

3. 三個按鈕:
   - ✅ 確認執行 (綠色，主要)
   - ❌ 拒絕 (紅色，次要)
   - ⏰ 稍後決定 (灰色，次要)

4. 風險提示:
   - 列出 3-4 個風險點
   - 需要勾選確認

使用模態對話框，居中顯示。
```

### 提示詞 5: 訂閱管理

```
創建訂閱頁面:

1. 定價表格 (3 列):
   
   基礎版 ($29/月):
   - 3個策略池監控
   - 每日自動再平衡
   - 基礎風險保護
   - 社區支持
   
   專業版 ($99/月) - 推薦:
   - 無限策略池
   - 實時自動優化
   - 高級風險管理
   - 優先支持
   - 完整回測報告
   
   機構版 ($499/月):
   - 定制策略開發
   - API訪問權限
   - 專屬客戶經理
   - SLA服務保障
   - 白標解決方案

2. 每列底部有"選擇計劃"按鈕
3. 專業版列高亮顯示（綠色邊框）
4. 點擊按鈕後集成 Stripe Checkout

使用卡片佈局，確保視覺層級清晰。
```

---

## 🔌 後端 API 設計

### 數據庫結構 (Supabase)

```sql
-- Users 表
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  wallet_address TEXT,
  subscription_tier TEXT DEFAULT 'free',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Strategies 表
CREATE TABLE strategies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  name TEXT NOT NULL,
  status TEXT DEFAULT 'active',
  config JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Positions 表
CREATE TABLE positions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  strategy_id UUID REFERENCES strategies(id),
  type TEXT, -- 'lp' or 'hedge'
  protocol TEXT,
  chain TEXT,
  token_pair TEXT,
  amount DECIMAL,
  entry_price DECIMAL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### API 端點

```typescript
// 數據獲取
GET /api/pools - 獲取高評分 LP 池列表
GET /api/market-score - 獲取牛熊評分
GET /api/backtest - 獲取回測結果

// 策略管理
POST /api/strategies - 創建新策略
GET /api/strategies/:id - 獲取策略詳情
PUT /api/strategies/:id - 更新策略
DELETE /api/strategies/:id - 刪除策略

// 轉倉執行
POST /api/rebalance/analyze - 分析轉倉機會
POST /api/rebalance/execute - 執行轉倉
GET /api/rebalance/status/:id - 查詢執行狀態

// 訂閱管理
POST /api/subscription/checkout - 創建 Stripe Checkout
POST /api/subscription/webhook - Stripe Webhook
GET /api/subscription/status - 查詢訂閱狀態
```

---

## 📦 部署清單

### 環境變量

```env
# Supabase
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key

# Stripe
VITE_STRIPE_PUBLISHABLE_KEY=your_stripe_key
STRIPE_SECRET_KEY=your_secret_key

# WalletConnect
VITE_WALLET_CONNECT_PROJECT_ID=your_project_id
```

### 部署平台

- **前端**: Vercel (自動部署)
- **後端**: Railway 或 Render
- **數據庫**: Supabase (PostgreSQL)
- **支付**: Stripe

---

## ✅ 開發檢查清單

### Week 1
- [ ] 項目初始化完成
- [ ] 用戶認證系統
- [ ] 錢包連接功能
- [ ] 儀表板基礎組件
- [ ] 策略配置頁面

### Week 2
- [ ] 轉倉確認系統
- [ ] 回測展示頁面
- [ ] Stripe 支付集成
- [ ] 訂閱管理功能
- [ ] 移動端響應式優化

### 上線前
- [ ] 安全審計
- [ ] 性能優化
- [ ] Beta 測試
- [ ] 文檔完善
- [ ] 正式部署

---

## 🚀 立即開始

1. 訪問 https://lovable.dev
2. 創建新項目
3. 使用提示詞 1 初始化項目
4. 按照 Week 1 計劃逐步開發

**讓我們開始打造這個改變 DeFi 投資的產品！** 🚀

