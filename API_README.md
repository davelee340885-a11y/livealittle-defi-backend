# LiveaLittle DeFi API 文檔總覽

歡迎使用 LiveaLittle DeFi API 文檔！本文檔集合提供了完整的 API 規範、使用指南和部署說明。

---

## 📚 文檔結構

本項目包含以下文檔：

### 1. **API 規範文檔** (`livealittle_defi_api_docs.md`)

完整的 RESTful API 規範，包括：

- **認證機制**：JWT Token 認證
- **市場數據端點**：獲取市場總覽、代幣價格、流動性池、市場狀態
- **投資組合端點**：查看總覽、歷史表現、當前倉位
- **策略端點**：獲取可用策略、創建自定義策略
- **執行端點**：獲取再平衡機會、執行交易、查看狀態
- **用戶管理端點**：註冊、登錄、個人資料管理
- **訂閱端點**：查看計劃、創建訂閱、管理訂閱狀態
- **錯誤處理**：標準錯誤碼和響應格式
- **速率限制**：API 使用限制說明

**適用對象**：前端開發者、API 集成工程師

### 2. **API 使用指南** (`API_USAGE_GUIDE.md`)

詳細的使用說明和代碼範例，包括：

- **快速開始**：啟動服務器、註冊登錄
- **JavaScript/TypeScript 範例**：使用 Fetch API 和 Axios
- **React Hook 範例**：自定義 Hooks 實現
- **Python 範例**：Python 客戶端實現
- **錯誤處理最佳實踐**
- **環境配置**

**適用對象**：前端開發者、全棧開發者

### 3. **Lovable 集成指南** (`LOVABLE_API_INTEGRATION.md`)

專門針對 Lovable.dev 平台的集成指南，包括：

- **10 步完整集成流程**
- **Lovable 提示詞範例**：直接可用的提示詞
- **組件實現範例**：儀表板、策略配置、轉倉確認
- **認證流程**：登錄、註冊、受保護路由
- **錯誤處理和加載狀態**
- **性能優化建議**
- **測試和部署**

**適用對象**：使用 Lovable 進行前端開發的開發者

### 4. **API 部署指南** (`API_DEPLOYMENT_GUIDE.md`)

生產環境部署的完整指南，包括：

- **多種部署選項**：Railway、Render、Docker
- **數據庫設置**：Supabase 配置、表結構、RLS 安全
- **監控和日誌**：Sentry 集成、日誌配置
- **性能優化**：緩存、速率限制、連接池
- **安全最佳實踐**：HTTPS、CORS、密碼哈希
- **CI/CD 設置**：GitHub Actions 自動部署
- **備份策略**

**適用對象**：DevOps 工程師、後端開發者

### 5. **API 實現代碼** (`backend/api_server.py`)

完整的 FastAPI 實現範例，包括：

- 所有端點的實現
- JWT 認證中間件
- 數據模型定義
- 錯誤處理
- CORS 配置

**適用對象**：後端開發者

---

## 🚀 快速開始

### 對於前端開發者

1. 閱讀 **API 規範文檔** 了解可用端點
2. 查看 **API 使用指南** 中的代碼範例
3. 如果使用 Lovable，參考 **Lovable 集成指南**

### 對於後端開發者

1. 查看 **API 實現代碼** 了解實現細節
2. 閱讀 **API 部署指南** 準備生產環境

### 對於 DevOps 工程師

1. 直接查看 **API 部署指南**
2. 選擇合適的部署方式
3. 配置監控和日誌

---

## 🔑 核心功能

LiveaLittle DeFi API 提供以下核心功能：

### 1. 實時市場數據

- 獲取加密貨幣價格和市場總覽
- 查詢流動性池信息（TVL、APY、費率）
- 識別當前市場狀態（牛市/熊市/震盪）

### 2. 投資組合管理

- 實時查看投資組合總價值和收益
- 歷史表現追蹤（支持多個時間範圍）
- 詳細的倉位列表和資產分佈

### 3. 智能策略

- Delta Neutral 策略
- 趨勢跟隨策略
- 自定義策略配置

### 4. 自動再平衡

- 智能識別再平衡機會
- 成本效益分析
- 手動確認執行
- 交易狀態追蹤

### 5. 用戶和訂閱管理

- 安全的用戶認證
- 多層級訂閱計劃
- Stripe 支付集成

---

## 🏗️ 技術架構

### 後端技術棧

- **框架**：FastAPI
- **認證**：JWT (PyJWT)
- **數據庫**：Supabase (PostgreSQL)
- **支付**：Stripe
- **部署**：Railway / Render / Docker

### 前端技術棧（推薦）

- **框架**：React + TypeScript
- **樣式**：Tailwind CSS
- **圖表**：Recharts
- **錢包**：RainbowKit
- **HTTP 客戶端**：Axios
- **部署**：Vercel

### 數據流

```
用戶請求 → API 網關 → 認證中間件 → 業務邏輯 → 數據庫/外部 API → 響應
```

---

## 📊 API 端點總覽

| 類別 | 端點 | 方法 | 描述 |
| :--- | :--- | :--- | :--- |
| **市場數據** | `/market/overview` | GET | 市場總覽 |
| | `/market/tokens` | GET | 代幣列表 |
| | `/market/pools` | GET | 流動性池 |
| | `/market/regime` | GET | 市場狀態 |
| **投資組合** | `/portfolio/overview` | GET | 投資組合總覽 |
| | `/portfolio/performance` | GET | 歷史表現 |
| | `/portfolio/positions` | GET | 當前倉位 |
| **策略** | `/strategies` | GET | 策略列表 |
| | `/strategies/{id}` | GET | 策略詳情 |
| | `/strategies` | POST | 創建策略 |
| **執行** | `/execution/opportunities` | GET | 再平衡機會 |
| | `/execution/rebalance` | POST | 執行再平衡 |
| | `/execution/status/{id}` | GET | 執行狀態 |
| **認證** | `/auth/register` | POST | 用戶註冊 |
| | `/auth/login` | POST | 用戶登錄 |
| **用戶** | `/user/profile` | GET | 獲取資料 |
| | `/user/profile` | PUT | 更新資料 |
| **訂閱** | `/subscriptions/plans` | GET | 訂閱計劃 |
| | `/subscriptions/subscribe` | POST | 創建訂閱 |
| | `/subscriptions/status` | GET | 訂閱狀態 |

---

## 🔐 安全性

API 實現了多層安全措施：

1. **JWT 認證**：所有受保護端點需要有效的 JWT Token
2. **HTTPS 強制**：生產環境強制使用 HTTPS
3. **CORS 限制**：只允許授權的域名訪問
4. **速率限制**：防止 API 濫用（每分鐘 120 次請求）
5. **密碼哈希**：使用 bcrypt 加密存儲密碼
6. **Row Level Security**：Supabase RLS 確保數據隔離

---

## 📈 性能優化

- **Redis 緩存**：緩存頻繁訪問的數據
- **數據庫連接池**：優化數據庫連接
- **異步處理**：使用 FastAPI 的異步特性
- **CDN**：靜態資源通過 CDN 分發
- **壓縮**：響應數據 gzip 壓縮

---

## 🧪 測試

### 本地測試

```bash
# 啟動開發服務器
cd /home/ubuntu/defi_system/backend
python3 api_server.py

# 訪問 Swagger UI
open http://localhost:8000/docs
```

### 單元測試

```bash
# 安裝測試依賴
pip install pytest pytest-asyncio httpx

# 運行測試
pytest tests/
```

---

## 📞 支持和反饋

如果您在使用 API 時遇到任何問題或有任何建議，請：

1. 查看相關文檔
2. 檢查常見問題解答
3. 聯繫開發團隊

---

## 📝 更新日誌

### Version 1.0.0 (2025-10-15)

- ✅ 初始版本發布
- ✅ 完整的 RESTful API 實現
- ✅ JWT 認證
- ✅ Supabase 集成
- ✅ Stripe 支付集成
- ✅ 完整的文檔

---

## 🗺️ 路線圖

### 即將推出的功能

- [ ] WebSocket 實時數據推送
- [ ] GraphQL API 支持
- [ ] 更多 DeFi 協議集成
- [ ] 高級分析和報告
- [ ] 移動 App API
- [ ] API v2 with enhanced features

---

## 📄 許可證

本項目為 LiveaLittle DeFi 專有軟件。未經授權不得複製、分發或修改。

---

## 👥 貢獻者

- **開發團隊**：LiveaLittle DeFi Team
- **文檔**：Manus AI

---

**最後更新**：2025 年 10 月 15 日

**文檔版本**：1.0.0

