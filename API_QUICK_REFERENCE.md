# LiveaLittle DeFi API 快速參考

這是一個快速參考卡片，幫助您快速找到常用的 API 端點和代碼範例。

---

## 🔗 基礎 URL

```
開發環境: http://localhost:8000/api/v1
生產環境: https://api.livealittle-defi.com/api/v1
```

---

## 🔑 認證

所有受保護的端點都需要在請求頭中包含 JWT Token：

```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 📋 常用端點速查

### 認證

```bash
# 註冊
POST /auth/register
Body: { "email": "user@example.com", "password": "password123" }

# 登錄
POST /auth/login
Body: { "email": "user@example.com", "password": "password123" }
Response: { "token": "eyJ..." }
```

### 投資組合

```bash
# 獲取總覽
GET /portfolio/overview
Headers: Authorization: Bearer TOKEN
Response: {
  "total_value_usd": 150000.00,
  "total_return_percent": 20.0,
  "apy": 25.5
}

# 獲取歷史表現
GET /portfolio/performance?timeframe=30d
Headers: Authorization: Bearer TOKEN

# 獲取倉位列表
GET /portfolio/positions
Headers: Authorization: Bearer TOKEN
```

### 市場數據

```bash
# 獲取代幣列表
GET /market/tokens?limit=100

# 獲取流動性池
GET /market/pools?protocol=uniswap_v3&chain=ethereum

# 獲取市場狀態
GET /market/regime
Response: { "regime": "bull", "confidence_score": 0.85 }
```

### 執行

```bash
# 獲取再平衡機會
GET /execution/opportunities
Headers: Authorization: Bearer TOKEN

# 執行再平衡
POST /execution/rebalance
Headers: Authorization: Bearer TOKEN
Body: { "opportunity_id": "opp_67890" }

# 查看執行狀態
GET /execution/status/exec_fghij
Headers: Authorization: Bearer TOKEN
```

---

## 💻 代碼範例

### JavaScript/TypeScript

```typescript
// 登錄
const response = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'password123' })
});
const { token } = await response.json();

// 獲取投資組合
const portfolio = await fetch('http://localhost:8000/api/v1/portfolio/overview', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

console.log(`Total Value: $${portfolio.total_value_usd}`);
```

### Python

```python
import requests

# 登錄
response = requests.post(
    'http://localhost:8000/api/v1/auth/login',
    json={'email': 'user@example.com', 'password': 'password123'}
)
token = response.json()['token']

# 獲取投資組合
headers = {'Authorization': f'Bearer {token}'}
portfolio = requests.get(
    'http://localhost:8000/api/v1/portfolio/overview',
    headers=headers
).json()

print(f"Total Value: ${portfolio['total_value_usd']}")
```

### cURL

```bash
# 登錄
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  | jq -r '.token')

# 獲取投資組合
curl -X GET "http://localhost:8000/api/v1/portfolio/overview" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎯 React Hook 範例

```typescript
import { useState, useEffect } from 'react';

function usePortfolioOverview() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    
    fetch('http://localhost:8000/api/v1/portfolio/overview', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, []);
  
  return { data, loading };
}

// 使用
function Dashboard() {
  const { data, loading } = usePortfolioOverview();
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div>
      <h1>Total Value: ${data.total_value_usd}</h1>
      <p>Return: {data.total_return_percent}%</p>
    </div>
  );
}
```

---

## ⚠️ 錯誤碼

| 狀態碼 | 錯誤碼 | 描述 | 解決方案 |
| :--- | :--- | :--- | :--- |
| 400 | `invalid_request` | 請求參數無效 | 檢查請求參數 |
| 401 | `unauthorized` | 未授權 | 檢查 Token 是否有效 |
| 403 | `forbidden` | 禁止訪問 | 檢查權限 |
| 404 | `not_found` | 資源不存在 | 檢查 URL 和資源 ID |
| 429 | `rate_limit_exceeded` | 超出速率限制 | 等待後重試 |
| 500 | `internal_server_error` | 服務器錯誤 | 聯繫技術支持 |

---

## 🔄 速率限制

- **默認限制**：每分鐘 120 次請求
- **響應頭**：
  - `X-RateLimit-Limit`: 限制總數
  - `X-RateLimit-Remaining`: 剩餘次數
  - `X-RateLimit-Reset`: 重置時間

---

## 📦 響應格式

所有成功的響應都返回 JSON 格式：

```json
{
  "field1": "value1",
  "field2": 123,
  "field3": ["array", "values"]
}
```

錯誤響應格式：

```json
{
  "error": "error_code",
  "message": "Human readable error message"
}
```

---

## 🚀 啟動本地服務器

```bash
# 安裝依賴
pip3 install fastapi uvicorn pyjwt python-multipart

# 啟動服務器
cd /home/ubuntu/defi_system/backend
python3 api_server.py

# 訪問 API 文檔
open http://localhost:8000/docs
```

---

## 📚 完整文檔

- **API 規範**：`LIVEALITTLE_DEFI_API_DOCS.md`
- **使用指南**：`API_USAGE_GUIDE.md`
- **Lovable 集成**：`LOVABLE_API_INTEGRATION.md`
- **部署指南**：`API_DEPLOYMENT_GUIDE.md`
- **總覽**：`API_README.md`

---

## 🔗 相關資源

- **Swagger UI**：http://localhost:8000/docs
- **ReDoc**：http://localhost:8000/redoc
- **Supabase Dashboard**：https://app.supabase.com
- **Stripe Dashboard**：https://dashboard.stripe.com

---

**提示**：將此頁面加入書籤以便快速訪問！

