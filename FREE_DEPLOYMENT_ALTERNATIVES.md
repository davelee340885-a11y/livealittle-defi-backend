# 免費後端部署替代方案

**問題**：Railway 免費計劃只能部署數據庫，不能部署應用。

**解決方案**：使用其他免費平台！以下是 3 個完全免費的替代方案，按推薦順序排列。

---

## 🥇 方案 1：Render（最推薦）

**優點**：
- ✅ 完全免費（每月 750 小時）
- ✅ 自動從 GitHub 部署
- ✅ 支持 Python/FastAPI
- ✅ 提供免費域名
- ✅ 操作簡單，類似 Railway

**缺點**：
- ⚠️ 免費版會在 15 分鐘無活動後休眠（首次訪問需要等待 30 秒喚醒）

---

### Render 部署步驟（20 分鐘）

#### 步驟 1：註冊 Render

1. 訪問：https://render.com
2. 點擊 **Get Started for Free**
3. 選擇 **Sign up with GitHub**（用 GitHub 登入最方便）
4. 授權 Render 訪問您的 GitHub

---

#### 步驟 2：創建 Web Service

1. 登入後，點擊 **New +** 按鈕
2. 選擇 **Web Service**
3. 選擇您的 `livealittle-defi-backend` 倉庫
4. 點擊 **Connect**

---

#### 步驟 3：配置部署設置

**填寫以下信息**：

| 字段 | 值 |
|------|-----|
| Name | `livealittle-defi-api` |
| Region | `Oregon (US West)` 或最近的區域 |
| Branch | `main` |
| Root Directory | 留空 |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn backend.unified_api_server:app --host 0.0.0.0 --port $PORT` |

**Instance Type**：選擇 **Free**

---

#### 步驟 4：部署

1. 滾動到底部，點擊 **Create Web Service**
2. Render 會自動開始部署
3. 等待 3-5 分鐘（可以看到實時日誌）
4. 部署成功後，頂部會顯示 **Live** 狀態

---

#### 步驟 5：獲取 API URL

部署成功後，您會看到一個 URL，例如：
```
https://livealittle-defi-api.onrender.com
```

**測試 API**：在瀏覽器打開這個 URL，應該看到歡迎信息。

---

#### 步驟 6：保持喚醒（可選）

**問題**：免費版會在 15 分鐘無活動後休眠。

**解決方案**：使用免費的 Cron 服務定期訪問 API。

**方法 1：使用 UptimeRobot**（推薦）

1. 訪問：https://uptimerobot.com
2. 註冊免費賬號
3. 點擊 **Add New Monitor**
4. 設置：
   - Monitor Type: `HTTP(s)`
   - Friendly Name: `LiveaLittle API`
   - URL: `https://您的Render域名.onrender.com/health`
   - Monitoring Interval: `5 minutes`
5. 點擊 **Create Monitor**

**這樣 API 就會保持喚醒狀態！**

---

## 🥈 方案 2：Vercel（簡單但有限制）

**優點**：
- ✅ 完全免費
- ✅ 不會休眠
- ✅ 超快速部署
- ✅ 自動 HTTPS

**缺點**：
- ⚠️ 主要為前端設計，後端功能有限制
- ⚠️ 每個請求最多 10 秒超時
- ⚠️ 需要稍微修改代碼結構

---

### Vercel 部署步驟（15 分鐘）

#### 步驟 1：修改項目結構

**在 GitHub 倉庫中創建 `api/index.py`**：

1. 在倉庫根目錄，點擊 **Add file** → **Create new file**
2. 文件名：`api/index.py`
3. 內容：

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
sys.path.append('..')
from backend.unified_api_server import app

# Vercel 需要這個
handler = app
```

4. 點擊 **Commit new file**

---

#### 步驟 2：創建 `vercel.json`

1. 在倉庫根目錄，點擊 **Add file** → **Create new file**
2. 文件名：`vercel.json`
3. 內容：

```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

4. 點擊 **Commit new file**

---

#### 步驟 3：在 Vercel 部署

1. 訪問：https://vercel.com
2. 點擊 **Sign Up**，選擇 **Continue with GitHub**
3. 點擊 **Import Project**
4. 選擇 `livealittle-defi-backend` 倉庫
5. 點擊 **Deploy**

部署完成後，您會得到一個 URL：
```
https://livealittle-defi-backend.vercel.app
```

---

## 🥉 方案 3：Fly.io（功能最強但稍複雜）

**優點**：
- ✅ 免費額度慷慨（3 個應用）
- ✅ 不會休眠
- ✅ 支持所有 Python 功能
- ✅ 性能好

**缺點**：
- ⚠️ 需要安裝命令行工具
- ⚠️ 配置稍微複雜

**如果您想嘗試，我可以提供詳細步驟。但對於新手，我更推薦 Render。**

---

## 🎯 我的推薦

**對於您的情況（技術水平 1-2 分），我強烈推薦使用 Render**：

1. ✅ 操作最簡單（和 Railway 幾乎一樣）
2. ✅ 完全免費
3. ✅ 支持所有功能
4. ✅ 配合 UptimeRobot 可以保持喚醒

**唯一的小缺點**：首次訪問需要等待 30 秒喚醒（但配置 UptimeRobot 後就不會有這個問題）。

---

## 📋 快速行動計劃

### 現在立即開始（30 分鐘）

**步驟 1**：註冊 Render（5 分鐘）
- 訪問 https://render.com
- 用 GitHub 登入

**步驟 2**：在 Render 部署（10 分鐘）
- 創建 Web Service
- 連接 GitHub 倉庫
- 配置設置
- 部署

**步驟 3**：測試 API（5 分鐘）
- 訪問 Render 提供的 URL
- 測試 `/health` 端點
- 測試 `/api/v1/price/ETH` 端點

**步驟 4**：設置 UptimeRobot（10 分鐘）
- 註冊 UptimeRobot
- 添加監控
- 保持 API 喚醒

---

## 🆘 需要幫助？

**如果您在任何步驟遇到問題**：

1. 告訴我您選擇了哪個方案
2. 您在哪一步遇到問題
3. 錯誤信息是什麼
4. 截圖會很有幫助

我會立即協助您！

---

## 💡 額外建議

**如果您未來需要更強大的功能**，可以考慮付費方案：

- **Railway Pro**: $5/月
- **Render Starter**: $7/月
- **Fly.io**: 免費額度通常足夠

但對於學習和測試，**免費的 Render 完全足夠**！

---

**現在就開始吧！選擇 Render，按照步驟操作，30 分鐘後您就有一個運行的 API 了！** 🚀

