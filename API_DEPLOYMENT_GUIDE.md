# LiveaLittle DeFi API 部署指南

本指南詳細說明如何將 LiveaLittle DeFi API 部署到生產環境。

---

## 部署選項

我們推薦以下幾種部署方式：

1. **Railway**（推薦）：簡單快速，自動化部署
2. **Render**：免費層級可用，適合初期測試
3. **AWS EC2**：完全控制，適合大規模部署
4. **DigitalOcean App Platform**：平衡的選擇

---

## 選項 1：部署到 Railway（推薦）

Railway 提供了簡單的部署流程和自動擴展功能。

### 步驟 1：準備項目

創建 `requirements.txt` 文件：

```bash
cd /home/ubuntu/defi_system/backend
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
pyjwt==2.8.0
python-multipart==0.0.6
pydantic==2.5.0
requests==2.31.0
pandas==2.1.3
numpy==1.26.2
python-dotenv==1.0.0
supabase==2.0.3
stripe==7.4.0
EOF
```

創建 `Procfile`：

```bash
cat > Procfile << EOF
web: uvicorn api_server:app --host 0.0.0.0 --port \$PORT
EOF
```

創建 `railway.json`：

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn api_server:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 步驟 2：部署到 Railway

1. 訪問 [railway.app](https://railway.app) 並登錄
2. 點擊 "New Project"
3. 選擇 "Deploy from GitHub repo"
4. 選擇您的倉庫
5. Railway 會自動檢測 Python 項目並開始部署

### 步驟 3：配置環境變量

在 Railway 項目設置中添加以下環境變量：

```bash
JWT_SECRET=your-production-secret-key-change-this
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
STRIPE_SECRET_KEY=sk_live_...
DATABASE_URL=postgresql://...
```

### 步驟 4：獲取部署 URL

部署完成後，Railway 會提供一個 URL，例如：
```
https://livealittle-defi-api-production.up.railway.app
```

---

## 選項 2：部署到 Render

Render 提供免費層級，適合初期測試。

### 步驟 1：創建 `render.yaml`

```yaml
services:
  - type: web
    name: livealittle-defi-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api_server:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: JWT_SECRET
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: STRIPE_SECRET_KEY
        sync: false
```

### 步驟 2：部署

1. 訪問 [render.com](https://render.com)
2. 連接 GitHub 倉庫
3. 選擇 "Web Service"
4. 配置環境變量
5. 點擊 "Create Web Service"

---

## 選項 3：使用 Docker 部署

### 步驟 1：創建 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 步驟 2：創建 docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - JWT_SECRET=${JWT_SECRET}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped
```

### 步驟 3：配置 Nginx

創建 `nginx.conf`：

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    server {
        listen 80;
        server_name api.livealittle-defi.com;

        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    server {
        listen 443 ssl;
        server_name api.livealittle-defi.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 步驟 4：部署

```bash
# 構建並啟動
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 停止
docker-compose down
```

---

## 數據庫設置（Supabase）

### 步驟 1：創建 Supabase 項目

1. 訪問 [supabase.com](https://supabase.com)
2. 創建新項目
3. 記錄 URL 和 anon key

### 步驟 2：創建數據表

在 Supabase SQL 編輯器中執行：

```sql
-- 用戶表
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  full_name TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 訂閱表
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  plan_id TEXT NOT NULL,
  status TEXT NOT NULL,
  stripe_subscription_id TEXT,
  next_billing_date DATE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 倉位表
CREATE TABLE positions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  position_id TEXT UNIQUE NOT NULL,
  protocol TEXT NOT NULL,
  type TEXT NOT NULL,
  assets JSONB NOT NULL,
  value_usd DECIMAL NOT NULL,
  apy DECIMAL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 執行記錄表
CREATE TABLE executions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  execution_id TEXT UNIQUE NOT NULL,
  opportunity_id TEXT NOT NULL,
  status TEXT NOT NULL,
  transactions JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 投資組合歷史表
CREATE TABLE portfolio_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  timestamp TIMESTAMP NOT NULL,
  total_value_usd DECIMAL NOT NULL,
  total_return_usd DECIMAL,
  total_return_percent DECIMAL,
  apy DECIMAL
);

-- 創建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_positions_user_id ON positions(user_id);
CREATE INDEX idx_executions_user_id ON executions(user_id);
CREATE INDEX idx_portfolio_history_user_id ON portfolio_history(user_id);
CREATE INDEX idx_portfolio_history_timestamp ON portfolio_history(timestamp);
```

### 步驟 3：設置 Row Level Security (RLS)

```sql
-- 啟用 RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_history ENABLE ROW LEVEL SECURITY;

-- 用戶只能訪問自己的數據
CREATE POLICY "Users can view own data" ON users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can view own subscriptions" ON subscriptions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own positions" ON positions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own executions" ON executions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own portfolio history" ON portfolio_history
  FOR SELECT USING (auth.uid() = user_id);
```

---

## 監控和日誌

### 使用 Sentry 進行錯誤監控

```bash
pip install sentry-sdk[fastapi]
```

在 `api_server.py` 中添加：

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

### 配置日誌

```python
import logging

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 在端點中使用
@app.get("/api/v1/portfolio/overview")
async def get_portfolio_overview(user_id: str = Depends(verify_token)):
    logger.info(f"Fetching portfolio overview for user {user_id}")
    # ...
```

---

## 性能優化

### 1. 添加緩存

使用 Redis 進行緩存：

```bash
pip install redis
```

```python
import redis
import json

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=6379,
    decode_responses=True
)

@app.get("/api/v1/market/tokens")
async def get_market_tokens(limit: int = 100):
    # 檢查緩存
    cache_key = f"market_tokens_{limit}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # 獲取數據
    tokens = fetch_tokens_from_source(limit)
    
    # 緩存 5 分鐘
    redis_client.setex(cache_key, 300, json.dumps(tokens))
    
    return tokens
```

### 2. 添加速率限制

```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/portfolio/overview")
@limiter.limit("60/minute")
async def get_portfolio_overview(
    request: Request,
    user_id: str = Depends(verify_token)
):
    # ...
```

### 3. 數據庫連接池

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

---

## 安全最佳實踐

### 1. HTTPS 強制

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if os.getenv('ENVIRONMENT') == 'production':
    app.add_middleware(HTTPSRedirectMiddleware)
```

### 2. CORS 限制

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://livealittle-defi.com",
        "https://www.livealittle-defi.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 3. 密碼哈希

```bash
pip install passlib[bcrypt]
```

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

---

## 健康檢查端點

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/ready")
async def readiness_check():
    # 檢查數據庫連接
    try:
        # 執行簡單查詢
        # db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service not ready")
```

---

## CI/CD 設置

### GitHub Actions 範例

創建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Railway CLI
        run: npm install -g @railway/cli
      
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## 備份策略

### 數據庫備份

在 Supabase 中啟用自動備份，或使用 cron 作業：

```bash
# 每天凌晨 2 點備份
0 2 * * * pg_dump $DATABASE_URL > /backups/db_$(date +\%Y\%m\%d).sql
```

### 配置備份

將所有配置存儲在版本控制中，敏感信息使用環境變量。

---

## 總結

本指南涵蓋了 LiveaLittle DeFi API 的完整部署流程，包括：

1. 多種部署選項（Railway、Render、Docker）
2. 數據庫設置和安全配置
3. 監控和日誌記錄
4. 性能優化
5. 安全最佳實踐
6. CI/CD 自動化

選擇適合您需求的部署方式，並遵循安全最佳實踐，確保 API 在生產環境中穩定運行。

如有任何問題，請參考各平台的官方文檔或聯繫開發團隊。

