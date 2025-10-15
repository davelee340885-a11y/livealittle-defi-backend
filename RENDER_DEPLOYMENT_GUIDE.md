# Render 部署指南 - LAL 智能搜尋服務

## 🎯 部署目標

將 LAL 智能搜尋服務部署到 Render，提供公開的 API 端點。

---

## 📋 準備工作

### 1. 確認 GitHub 倉庫

倉庫地址: https://github.com/davelee340885-a11y/livealittle-defi-backend

確認以下文件已推送：
- ✅ `render.yaml` - Render 配置文件
- ✅ `requirements.txt` - Python 依賴
- ✅ `backend/lal_api_server_deploy.py` - API 服務器
- ✅ `backend/lal_smart_search.py` - 智能搜尋服務
- ✅ `backend/davis_double_click_analyzer.py` - 戴維斯雙擊分析
- ✅ `backend/unified_data_aggregator.py` - 數據聚合器
- ✅ `backend/delta_neutral_calculator.py` - Delta Neutral 計算器

---

## 🚀 部署步驟

### 方法 1: 使用 render.yaml（推薦）

1. **訪問 Render Dashboard**
   - 前往: https://dashboard.render.com/

2. **創建新服務**
   - 點擊 "New +" → "Blueprint"
   - 選擇 GitHub 倉庫: `livealittle-defi-backend`
   - Render 會自動讀取 `render.yaml` 配置

3. **確認配置**
   ```yaml
   服務名稱: lal-smart-search-api
   環境: Python
   區域: Oregon
   計劃: Free
   分支: main
   構建命令: pip install -r requirements.txt
   啟動命令: python backend/lal_api_server_deploy.py
   ```

4. **部署**
   - 點擊 "Apply"
   - 等待部署完成（約 3-5 分鐘）

5. **獲取 URL**
   - 部署完成後，Render 會提供一個 URL
   - 格式: `https://lal-smart-search-api.onrender.com`

---

### 方法 2: 手動創建 Web Service

1. **訪問 Render Dashboard**
   - 前往: https://dashboard.render.com/

2. **創建新 Web Service**
   - 點擊 "New +" → "Web Service"
   - 連接 GitHub 倉庫: `livealittle-defi-backend`

3. **配置服務**

   **基本設置**:
   - Name: `lal-smart-search-api`
   - Region: `Oregon (US West)`
   - Branch: `main`
   - Root Directory: 留空
   - Runtime: `Python 3`

   **構建設置**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python backend/lal_api_server_deploy.py`

   **計劃**:
   - 選擇 `Free`

4. **環境變量（可選）**
   - `PORT`: 自動設置（不需要手動配置）
   - `PYTHON_VERSION`: `3.11.0`

5. **健康檢查**
   - Health Check Path: `/health`

6. **部署**
   - 點擊 "Create Web Service"
   - 等待部署完成

---

## ✅ 驗證部署

### 1. 檢查健康狀態

```bash
curl https://lal-smart-search-api.onrender.com/health
```

**預期響應**:
```json
{
  "status": "healthy",
  "service": "LAL Smart Search API",
  "version": "1.0.0"
}
```

### 2. 測試根端點

```bash
curl https://lal-smart-search-api.onrender.com/
```

**預期響應**:
```json
{
  "service": "LAL Smart Search API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "smart_search": "/api/v1/lal/smart-search",
    "davis_analysis": "/api/v1/lal/davis-analysis",
    "health": "/health",
    "docs": "/docs"
  }
}
```

### 3. 測試智能搜尋 API

```bash
curl "https://lal-smart-search-api.onrender.com/api/v1/lal/smart-search?token=ETH&capital=10000&top_n=3"
```

**預期響應**:
```json
{
  "success": true,
  "data": {
    "opportunities": [
      {
        "protocol": "uniswap-v3",
        "symbol": "WETH-USDT",
        "net_apy": 83.41,
        "net_profit": 8341,
        "final_score": 99.84
      }
    ]
  }
}
```

### 4. 訪問 API 文檔

在瀏覽器中打開:
```
https://lal-smart-search-api.onrender.com/docs
```

---

## 🔧 常見問題

### 問題 1: 部署超時

**原因**: Free 計劃有 15 分鐘的構建時間限制

**解決方案**:
1. 優化 `requirements.txt`，只包含必要的依賴
2. 使用緩存加速構建

### 問題 2: 服務啟動失敗

**檢查日誌**:
1. 在 Render Dashboard 中查看 "Logs"
2. 查找錯誤信息

**常見原因**:
- 缺少依賴包
- 啟動命令錯誤
- 端口配置問題

**解決方案**:
```bash
# 確保啟動命令正確
python backend/lal_api_server_deploy.py

# 確保所有依賴都在 requirements.txt 中
```

### 問題 3: API 響應慢

**原因**: Free 計劃的服務在閒置 15 分鐘後會休眠

**解決方案**:
1. 第一次請求會喚醒服務（約 30-60 秒）
2. 考慮升級到付費計劃以保持服務常駐
3. 使用定時任務定期訪問 `/health` 端點保持活躍

---

## 📊 監控和維護

### 1. 查看日誌

在 Render Dashboard 中:
- 點擊服務名稱
- 選擇 "Logs" 標籤
- 實時查看服務日誌

### 2. 監控性能

在 Render Dashboard 中:
- 選擇 "Metrics" 標籤
- 查看 CPU、內存、請求數等指標

### 3. 自動部署

Render 會自動監控 GitHub 倉庫:
- 當 `main` 分支有新提交時
- 自動觸發重新部署
- 無需手動操作

---

## 🔄 更新部署

### 方法 1: 推送代碼到 GitHub

```bash
cd /path/to/defi_system
git add .
git commit -m "Update LAL service"
git push origin main
```

Render 會自動檢測並重新部署。

### 方法 2: 手動觸發部署

在 Render Dashboard 中:
1. 點擊服務名稱
2. 點擊 "Manual Deploy" → "Deploy latest commit"

---

## 💰 費用說明

### Free 計劃限制

- ✅ 免費
- ✅ 750 小時/月
- ⚠️ 閒置 15 分鐘後休眠
- ⚠️ 喚醒時間 30-60 秒
- ⚠️ 每月 100GB 流量

### 升級選項

如需更好的性能，可考慮升級到:
- **Starter**: $7/月
  - 常駐服務
  - 更快的 CPU
  - 更多內存

---

## 🌐 使用部署的 API

### Python 客戶端

```python
import requests

BASE_URL = "https://lal-smart-search-api.onrender.com"

def get_best_opportunities(token="ETH", capital=10000):
    response = requests.get(
        f"{BASE_URL}/api/v1/lal/smart-search",
        params={
            "token": token,
            "capital": capital,
            "top_n": 5
        }
    )
    return response.json()

# 使用
opportunities = get_best_opportunities("ETH", 10000)
print(f"找到 {opportunities['data']['count']} 個最佳方案")
```

### JavaScript 客戶端

```javascript
const BASE_URL = "https://lal-smart-search-api.onrender.com";

async function getBestOpportunities(token = "ETH", capital = 10000) {
  const response = await fetch(
    `${BASE_URL}/api/v1/lal/smart-search?token=${token}&capital=${capital}&top_n=5`
  );
  return await response.json();
}

// 使用
getBestOpportunities("ETH", 10000).then(data => {
  console.log(`找到 ${data.data.count} 個最佳方案`);
});
```

---

## 🔐 安全建議

1. **API Rate Limiting**
   - 考慮添加請求頻率限制
   - 防止濫用

2. **CORS 配置**
   - 目前允許所有來源
   - 生產環境建議限制特定域名

3. **環境變量**
   - 敏感信息（如 API 密鑰）應使用 Render 的環境變量功能
   - 不要提交到 GitHub

---

## 📞 獲取幫助

如遇到問題:
1. 查看 Render 日誌
2. 檢查 GitHub Issues
3. 聯繫開發者

---

**部署完成！您的 LAL 智能搜尋服務現在可以在全球訪問了！** 🎉

