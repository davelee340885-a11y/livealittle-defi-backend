# Delta Neutral API 部署指南 v2

## 📋 概述

本指南說明如何將 Delta Neutral API v2 部署到生產環境。

---

## 🚀 部署選項

### 選項 1: Render (推薦)

**優點**:
- 免費方案可用
- 自動 HTTPS
- 簡單易用
- 自動部署

**步驟**:

1. **準備 requirements.txt**

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
requests==2.31.0
pydantic==2.5.0
```

2. **創建 render.yaml**

```yaml
services:
  - type: web
    name: defi-api-v2
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api_server_v2:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

3. **部署到 Render**

- 前往 https://render.com
- 連接 GitHub 倉庫
- 選擇 `backend` 目錄
- 點擊 "Deploy"

---

### 選項 2: Railway

**優點**:
- 更快的冷啟動
- 更好的性能
- 簡單的環境變量管理

**步驟**:

1. **安裝 Railway CLI**

```bash
npm install -g @railway/cli
```

2. **登錄並初始化**

```bash
railway login
railway init
```

3. **部署**

```bash
cd /home/ubuntu/defi_system/backend
railway up
```

---

### 選項 3: Docker + 任意雲平台

**優點**:
- 最大的靈活性
- 可移植性強
- 適合任何雲平台

**步驟**:

1. **創建 Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api_server_v2:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **構建並運行**

```bash
docker build -t defi-api-v2 .
docker run -p 8000:8000 defi-api-v2
```

---

## 🔧 環境變量配置

### 可選環境變量

```bash
# API 配置
API_HOST=0.0.0.0
API_PORT=8000

# 數據源配置（使用默認值即可）
COINGECKO_API_KEY=  # 可選，提高 rate limit
DEFILLAMA_API_KEY=  # 可選

# 緩存配置
CACHE_ENABLED=true
CACHE_TTL_SECONDS=300
```

---

## 📊 監控與日誌

### 健康檢查端點

```bash
curl https://your-api.com/
curl https://your-api.com/api/v1/health
```

### 查看 API 文檔

```
https://your-api.com/docs
```

### 日誌記錄

建議使用日誌聚合服務：
- Render: 內建日誌查看
- Railway: 內建日誌查看
- 自建: 使用 Sentry 或 LogRocket

---

## ⚡ 性能優化

### 1. 啟用緩存

API 已內建緩存機制：
- 代幣價格: 10 秒
- LP 池數據: 5 分鐘
- 資金費率: 5 分鐘
- 市場情緒: 1 小時

### 2. Rate Limiting

建議在 API 前添加 Rate Limiting：

```python
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/market/tokens")
@limiter.limit("60/minute")
async def get_token_prices():
    ...
```

### 3. CDN

對於靜態內容，建議使用 CDN：
- Cloudflare
- AWS CloudFront

---

## 🔒 安全建議

### 1. CORS 配置

生產環境應限制 CORS：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],  # 限制為特定域名
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 2. API 密鑰

如需 API 密鑰認證：

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key
```

### 3. HTTPS

確保使用 HTTPS：
- Render 和 Railway 自動提供
- 自建需配置 SSL 證書（Let's Encrypt）

---

## 📈 擴展建議

### 1. 數據庫

當需要持久化數據時：

```bash
pip install sqlalchemy asyncpg
```

### 2. Redis 緩存

使用 Redis 替代內存緩存：

```bash
pip install redis aioredis
```

### 3. 任務隊列

使用 Celery 處理長時間運行的任務：

```bash
pip install celery redis
```

---

## 🐛 故障排除

### 問題 1: 部署後 API 無響應

**檢查**:
- 端口配置是否正確
- 健康檢查端點是否通過
- 日誌中是否有錯誤

### 問題 2: 第三方 API 調用失敗

**原因**:
- Rate Limit 超限
- 網絡問題
- API 密鑰無效

**解決**:
- 啟用緩存
- 使用 API 密鑰
- 添加重試機制

### 問題 3: 性能問題

**優化**:
- 啟用緩存
- 使用 Redis
- 增加實例數量
- 使用 CDN

---

## 📞 支持

如有問題：
- 查看 API 文檔: `/docs`
- 查看日誌
- 檢查健康狀態: `/api/v1/health`

---

## 🎉 下一步

部署完成後：
1. 測試所有 API 端點
2. 設置監控和告警
3. 配置 CI/CD 自動部署
4. 整合前端應用
5. 添加使用分析

祝您部署順利！🚀

