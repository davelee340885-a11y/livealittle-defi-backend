# LiveaLittle DeFi - Lovable 開發完整指南

## 🎯 項目概述

**項目名稱**: LiveaLittle DeFi  
**技術棧**: React + TypeScript + Tailwind CSS + Supabase + Stripe  
**開發平台**: Lovable.dev  
**預計時間**: 1-2 週

---

## 📋 功能模塊清單

### Phase 1: 核心基礎（第1-3天）

#### 1.1 項目初始化
- [x] 在 Lovable 創建新項目
- [x] 配置 TypeScript + Tailwind
- [x] 設置路由結構
- [x] 創建基礎佈局組件

#### 1.2 用戶認證系統
- [ ] Supabase 認證集成
- [ ] 註冊/登入頁面
- [ ] MetaMask 錢包連接
- [ ] 用戶資料管理

#### 1.3 數據庫設計
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

-- Rebalance_History 表
CREATE TABLE rebalance_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  strategy_id UUID REFERENCES strategies(id),
  from_pool TEXT,
  to_pool TEXT,
  amount DECIMAL,
  cost DECIMAL,
  profit DECIMAL,
  status TEXT,
  executed_at TIMESTAMP DEFAULT NOW()
);
```

### Phase 2: 核心功能開發（第4-7天）

#### 2.1 儀表板頁面

**組件結構**:
```
Dashboard/
├── Overview.tsx          # 總覽卡片
├── PerformanceChart.tsx  # 收益曲線圖
├── PositionsList.tsx     # 當前倉位列表
├── RiskMetrics.tsx       # 風險指標
└── AlertsPanel.tsx       # 警報中心
```

**核心功能**:
- 實時顯示總資產、總收益、年化收益率
- 收益曲線圖（使用 Chart.js 或 Recharts）
- LP 倉位和對沖倉位列表
- Delta 分析和風險指標
- 智能警報（轉倉機會、風險提示）

#### 2.2 策略配置頁面

**組件結構**:
```
StrategyConfig/
├── PoolSelector.tsx      # LP 池選擇器
├── RiskSettings.tsx      # 風險偏好設置
├── AutoRebalance.tsx     # 自動轉倉設置
└── ConfirmDialog.tsx     # 確認對話框
```

**核心功能**:
- 可視化選擇 LP 池（基於戴維斯雙擊評分）
- 風險偏好配置（回撤容忍度、對沖比例）
- 自動轉倉開關和閾值設置
- 策略預覽和模擬收益

#### 2.3 回測展示頁面

**組件結構**:
```
Backtest/
├── ResultsChart.tsx      # 回測結果圖表
├── MetricsTable.tsx      # 績效指標表格
├── ComparisonView.tsx    # 策略對比
└── DownloadReport.tsx    # 下載報告
```

**核心功能**:
- 展示真實歷史數據回測結果
- 年化收益、夏普比率、最大回撤等指標
- Delta Neutral vs 純 LP 策略對比
- 下載 PDF 報告功能

### Phase 3: 自動化與執行（第8-10天）

#### 3.1 轉倉確認系統

**組件結構**:
```
Rebalance/
├── OpportunityCard.tsx   # 轉倉機會卡片
├── CostAnalysis.tsx      # 成本效益分析
├── ExecutionPlan.tsx     # 執行計劃
└── ConfirmButton.tsx     # 確認按鈕
```

**核心功能**:
- 顯示轉倉機會詳情
- 成本效益分析（Gas、滑點、回本天數）
- 4步執行計劃展示
- 手動確認按鈕（✅ 確認 / ❌ 拒絕 / ⏰ 稍後）

#### 3.2 錢包集成

**技術選擇**: RainbowKit + Wagmi

```typescript
// 支持的錢包
- MetaMask
- WalletConnect
- Coinbase Wallet

// 支持的鏈
- Ethereum
- Arbitrum
- Base
- Solana (via Phantom)
```

#### 3.3 交易執行監控

**組件結構**:
```
Execution/
├── TransactionStatus.tsx # 交易狀態
├── ProgressBar.tsx       # 進度條
├── ErrorHandler.tsx      # 錯誤處理
└── SuccessView.tsx       # 成功頁面
```

### Phase 4: 訂閱與支付（第11-14天）

#### 4.1 訂閱管理

**Stripe 集成**:
```typescript
// 訂閱層級
const PRICING_PLANS = {
  basic: {
    price: 29,
    priceId: 'price_xxx',
    features: [
      '3個策略池監控',
      '每日自動再平衡',
      '基礎風險保護'
    ]
  },
  pro: {
    price: 99,
    priceId: 'price_xxx',
    features: [
      '無限策略池',
      '實時自動優化',
      '高級風險管理',
      '優先支持'
    ]
  },
  enterprise: {
    price: 499,
    priceId: 'price_xxx',
    features: [
      '定制策略開發',
      'API訪問權限',
      '專屬客戶經理',
      'SLA服務保障'
    ]
  }
};
```

**組件結構**:
```
Subscription/
├── PricingTable.tsx      # 定價表格
├── CheckoutForm.tsx      # 結帳表單
├── ManageSubscription.tsx # 訂閱管理
└── BillingHistory.tsx    # 帳單歷史
```

#### 4.2 支付流程

```
1. 用戶選擇訂閱層級
2. Stripe Checkout 頁面
3. 支付成功後更新數據庫
4. 發送確認郵件
5. 解鎖對應功能
```

---

## 🎨 UI/UX 設計規範

### 配色方案
```css
/* 主色調 */
--primary: #00D9FF;      /* 青色 */
--secondary: #00FF88;    /* 綠色 */
--background: #0A0E27;   /* 深藍 */
--surface: #1a1f3a;      /* 淺藍 */
--text: #E0E6ED;         /* 淺灰 */

/* 狀態色 */
--success: #00FF88;
--warning: #FFB800;
--error: #FF6B6B;
--info: #00D9FF;
```

### 字體
```css
font-family: 'Inter', sans-serif;

/* 標題 */
h1: 48px, 700
h2: 36px, 700
h3: 28px, 600

/* 正文 */
body: 16px, 400
small: 14px, 400
```

### 組件風格
- 圓角: 12px
- 陰影: 0 4px 20px rgba(0, 217, 255, 0.1)
- 間距: 8px 的倍數（8, 16, 24, 32...）

---

## 🔌 API 集成

### 後端 API 端點

```typescript
// 基礎 URL
const API_BASE_URL = 'https://api.livealittle.defi';

// 端點列表
const API_ENDPOINTS = {
  // 用戶
  auth: {
    register: '/auth/register',
    login: '/auth/login',
    logout: '/auth/logout'
  },
  
  // 策略
  strategies: {
    list: '/strategies',
    create: '/strategies',
    update: '/strategies/:id',
    delete: '/strategies/:id'
  },
  
  // 數據
  data: {
    pools: '/data/pools',
    prices: '/data/prices',
    fundingRates: '/data/funding-rates',
    marketScore: '/data/market-score'
  },
  
  // 執行
  execution: {
    rebalance: '/execution/rebalance',
    confirm: '/execution/confirm',
    status: '/execution/status/:id'
  },
  
  // 訂閱
  subscription: {
    checkout: '/subscription/checkout',
    manage: '/subscription/manage',
    cancel: '/subscription/cancel'
  }
};
```

### Python 後端（FastAPI）

將現有的 Python 腳本轉換為 API：

```python
# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 設置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://livealittle.defi"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 導入現有模塊
from backend.davis_double_play_analyzer import DavisAnalyzer
from backend.delta_neutral_engine import DeltaNeutralEngine
from backend.bull_bear_scoring_demo import MarketScorer

@app.get("/data/pools")
async def get_top_pools(min_tvl: float = 1000000, min_apy: float = 10):
    analyzer = DavisAnalyzer()
    pools = analyzer.analyze(min_tvl=min_tvl, min_apy=min_apy)
    return {"pools": pools}

@app.post("/execution/rebalance")
async def create_rebalance_plan(strategy_id: str):
    # 調用智能轉倉系統
    plan = generate_rebalance_plan(strategy_id)
    return {"plan": plan}

# ... 更多端點
```

---

## 📦 Lovable 開發提示詞

### 第1步：項目初始化

```
創建一個名為 "LiveaLittle DeFi" 的 Web 應用，使用 React + TypeScript + Tailwind CSS。

技術要求：
- 使用 Supabase 作為後端
- 使用 RainbowKit 進行錢包連接
- 使用 Recharts 進行數據可視化
- 使用 Stripe 進行支付

配色方案：
- 主色: #00D9FF (青色)
- 輔色: #00FF88 (綠色)
- 背景: #0A0E27 (深藍)

頁面結構：
1. 首頁 (Landing Page)
2. 儀表板 (Dashboard)
3. 策略配置 (Strategy Config)
4. 回測展示 (Backtest)
5. 訂閱管理 (Subscription)

請先創建基礎的路由和佈局組件。
```

### 第2步：儀表板開發

```
在儀表板頁面添加以下組件：

1. 總覽卡片：
   - 顯示總資產、總收益、年化收益率
   - 使用大數字和百分比顯示
   - 綠色表示正收益，紅色表示負收益

2. 收益曲線圖：
   - 使用 Recharts 的 LineChart
   - X軸：時間（日期）
   - Y軸：資產價值（美元）
   - 顯示 Delta Neutral 策略和純 LP 策略的對比

3. 倉位列表：
   - 表格形式顯示當前的 LP 倉位和對沖倉位
   - 列：協議、鏈、代幣對、金額、APY、狀態
   - 支持排序和篩選

4. 風險指標：
   - 顯示當前 Delta、最大回撤、夏普比率
   - 使用進度條或儀表盤樣式

請使用之前定義的配色方案。
```

### 第3步：策略配置

```
創建策略配置頁面，包含：

1. LP 池選擇器：
   - 從 API 獲取高評分的 LP 池列表
   - 顯示：協議、鏈、代幣對、TVL、APY、戴維斯評分
   - 支持多選
   - 顯示預期收益計算

2. 風險設置：
   - 滑塊：回撤容忍度 (0-30%)
   - 滑塊：對沖比例 (0-100%)
   - 開關：自動轉倉
   - 輸入：轉倉閾值

3. 確認對話框：
   - 顯示策略摘要
   - 顯示預期收益和風險
   - 確認按鈕

請確保所有輸入都有驗證。
```

### 第4步：轉倉確認系統

```
創建轉倉確認頁面，當系統發現轉倉機會時顯示：

1. 機會卡片：
   - 從 XXX 池到 YYY 池
   - APY 提升：+100%
   - 預期收益：$XXX (30天)
   - 總成本：$XXX
   - 淨收益：$XXX
   - 回本天數：X 天

2. 執行計劃：
   - Step 1: 平倉舊資產空頭
   - Step 2: 退出舊 LP 池
   - Step 3: 進入新 LP 池
   - Step 4: 開設新資產空頭
   - 每步顯示預計時間

3. 三個按鈕：
   - ✅ 確認執行 (綠色，主要按鈕)
   - ❌ 拒絕 (紅色，次要按鈕)
   - ⏰ 稍後決定 (灰色，次要按鈕)

4. 風險提示：
   - 列出可能的風險
   - 要求用戶閱讀並勾選確認

請使用卡片佈局，並確保按鈕有明確的視覺層級。
```

### 第5步：訂閱與支付

```
創建訂閱管理頁面：

1. 定價表格：
   - 三列：基礎版 ($29/月)、專業版 ($99/月)、機構版 ($499/月)
   - 每列顯示功能列表
   - 專業版高亮顯示（推薦）
   - 每列底部有"選擇計劃"按鈕

2. Stripe Checkout 集成：
   - 點擊按鈕後跳轉到 Stripe Checkout
   - 支付成功後返回應用
   - 更新用戶訂閱狀態

3. 訂閱管理：
   - 顯示當前訂閱層級
   - 顯示下次帳單日期
   - 提供升級/降級/取消選項

4. 帳單歷史：
   - 表格顯示歷史帳單
   - 支持下載發票

請確保支付流程安全且用戶友好。
```

---

## 🚀 部署計劃

### 開發環境
- Lovable.dev 內建預覽

### 生產環境
- 前端: Vercel (自動部署)
- 後端: Railway 或 Render
- 數據庫: Supabase (PostgreSQL)
- 支付: Stripe

### 環境變量
```env
# Supabase
VITE_SUPABASE_URL=xxx
VITE_SUPABASE_ANON_KEY=xxx

# Stripe
VITE_STRIPE_PUBLISHABLE_KEY=xxx
STRIPE_SECRET_KEY=xxx

# API
VITE_API_BASE_URL=https://api.livealittle.defi

# 錢包
VITE_WALLET_CONNECT_PROJECT_ID=xxx
```

---

## 📊 成功指標

### 技術指標
- [ ] 頁面加載時間 < 2秒
- [ ] API 響應時間 < 500ms
- [ ] 移動端響應式設計
- [ ] 錢包連接成功率 > 95%
- [ ] 支付成功率 > 98%

### 用戶體驗指標
- [ ] 註冊流程 < 2分鐘
- [ ] 策略配置 < 5分鐘
- [ ] 轉倉確認 < 1分鐘

### 商業指標
- [ ] Beta 測試 100 用戶
- [ ] 轉化率 > 10%
- [ ] 用戶留存率 > 80%

---

## 📝 下一步行動

1. **立即開始**：
   - 在 Lovable.dev 創建新項目
   - 使用第1步提示詞初始化項目

2. **第一週目標**：
   - 完成用戶認證和儀表板
   - 集成 DeFiLlama API
   - 實現基礎的策略配置

3. **第二週目標**：
   - 完成轉倉確認系統
   - 集成 Stripe 支付
   - 部署到生產環境

4. **Beta 測試**：
   - 邀請 10-20 個早期用戶
   - 收集反饋並優化
   - 準備正式上線

---

**讓我們開始打造這個改變 DeFi 投資的產品！** 🚀
