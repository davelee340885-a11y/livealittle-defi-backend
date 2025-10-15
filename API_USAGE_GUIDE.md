# LiveaLittle DeFi API 使用指南

本指南提供了如何使用 LiveaLittle DeFi API 的詳細說明和範例代碼。

---

## 快速開始

### 1. 啟動 API 服務器

首先，確保已安裝所需的依賴：

```bash
pip3 install fastapi uvicorn pyjwt python-multipart
```

然後啟動服務器：

```bash
cd /home/ubuntu/defi_system/backend
python3 api_server.py
```

服務器將在 `http://localhost:8000` 上運行。您可以訪問 `http://localhost:8000/docs` 查看自動生成的 API 文檔（Swagger UI）。

### 2. 註冊和登錄

**註冊新用戶**：

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "your_password"}'
```

**登錄**：

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "your_password"}'
```

響應將包含一個 JWT Token，您需要在後續請求中使用它。

### 3. 使用 Token 訪問受保護的端點

將 Token 添加到 `Authorization` 頭部：

```bash
curl -X GET "http://localhost:8000/api/v1/portfolio/overview" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## JavaScript/TypeScript 範例

### 使用 Fetch API

```typescript
// 登錄並獲取 Token
async function login(email: string, password: string): Promise<string> {
  const response = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  
  const data = await response.json();
  return data.token;
}

// 獲取投資組合總覽
async function getPortfolioOverview(token: string) {
  const response = await fetch('http://localhost:8000/api/v1/portfolio/overview', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  return await response.json();
}

// 使用範例
const token = await login('user@example.com', 'your_password');
const portfolio = await getPortfolioOverview(token);
console.log(portfolio);
```

### 使用 Axios

```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// 創建 Axios 實例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 添加請求攔截器以自動添加 Token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API 函數
export const api = {
  // 認證
  login: async (email: string, password: string) => {
    const response = await apiClient.post('/auth/login', { email, password });
    return response.data;
  },
  
  // 市場數據
  getMarketTokens: async (limit?: number) => {
    const response = await apiClient.get('/market/tokens', { params: { limit } });
    return response.data;
  },
  
  getMarketPools: async (protocol?: string, chain?: string) => {
    const response = await apiClient.get('/market/pools', { 
      params: { protocol, chain } 
    });
    return response.data;
  },
  
  getMarketRegime: async () => {
    const response = await apiClient.get('/market/regime');
    return response.data;
  },
  
  // 投資組合
  getPortfolioOverview: async () => {
    const response = await apiClient.get('/portfolio/overview');
    return response.data;
  },
  
  getPortfolioPerformance: async (timeframe: string = '30d') => {
    const response = await apiClient.get('/portfolio/performance', {
      params: { timeframe }
    });
    return response.data;
  },
  
  getPortfolioPositions: async () => {
    const response = await apiClient.get('/portfolio/positions');
    return response.data;
  },
  
  // 策略
  getStrategies: async () => {
    const response = await apiClient.get('/strategies');
    return response.data;
  },
  
  getStrategyDetail: async (strategyId: string) => {
    const response = await apiClient.get(`/strategies/${strategyId}`);
    return response.data;
  },
  
  // 執行
  getExecutionOpportunities: async () => {
    const response = await apiClient.get('/execution/opportunities');
    return response.data;
  },
  
  executeRebalance: async (opportunityId: string) => {
    const response = await apiClient.post('/execution/rebalance', {
      opportunity_id: opportunityId
    });
    return response.data;
  },
  
  getExecutionStatus: async (executionId: string) => {
    const response = await apiClient.get(`/execution/status/${executionId}`);
    return response.data;
  },
  
  // 訂閱
  getSubscriptionPlans: async () => {
    const response = await apiClient.get('/subscriptions/plans');
    return response.data;
  },
  
  subscribe: async (planId: string, paymentToken: string) => {
    const response = await apiClient.post('/subscriptions/subscribe', {
      plan_id: planId,
      payment_token: paymentToken
    });
    return response.data;
  },
};
```

---

## React Hook 範例

創建自定義 Hook 來管理 API 調用：

```typescript
import { useState, useEffect } from 'react';
import { api } from './api-client';

// 獲取投資組合總覽的 Hook
export function usePortfolioOverview() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const result = await api.getPortfolioOverview();
        setData(result);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }
    
    fetchData();
  }, []);
  
  return { data, loading, error };
}

// 獲取市場池的 Hook
export function useMarketPools(protocol?: string, chain?: string) {
  const [pools, setPools] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function fetchPools() {
      setLoading(true);
      const data = await api.getMarketPools(protocol, chain);
      setPools(data);
      setLoading(false);
    }
    
    fetchPools();
  }, [protocol, chain]);
  
  return { pools, loading };
}

// 在組件中使用
function Dashboard() {
  const { data: portfolio, loading } = usePortfolioOverview();
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div>
      <h1>Portfolio Overview</h1>
      <p>Total Value: ${portfolio.total_value_usd}</p>
      <p>Total Return: {portfolio.total_return_percent}%</p>
      <p>APY: {portfolio.apy}%</p>
    </div>
  );
}
```

---

## Python 範例

```python
import requests

class LiveaLittleAPI:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.token = None
    
    def login(self, email, password):
        """登錄並保存 Token"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        data = response.json()
        self.token = data["token"]
        return data
    
    def _get_headers(self):
        """獲取包含認證的請求頭"""
        if not self.token:
            raise Exception("Not authenticated. Please login first.")
        return {"Authorization": f"Bearer {self.token}"}
    
    def get_portfolio_overview(self):
        """獲取投資組合總覽"""
        response = requests.get(
            f"{self.base_url}/portfolio/overview",
            headers=self._get_headers()
        )
        return response.json()
    
    def get_market_pools(self, protocol=None, chain=None):
        """獲取市場池"""
        params = {}
        if protocol:
            params["protocol"] = protocol
        if chain:
            params["chain"] = chain
        
        response = requests.get(
            f"{self.base_url}/market/pools",
            params=params
        )
        return response.json()
    
    def get_execution_opportunities(self):
        """獲取再平衡機會"""
        response = requests.get(
            f"{self.base_url}/execution/opportunities",
            headers=self._get_headers()
        )
        return response.json()

# 使用範例
api = LiveaLittleAPI()
api.login("user@example.com", "your_password")

portfolio = api.get_portfolio_overview()
print(f"Total Value: ${portfolio['total_value_usd']}")

pools = api.get_market_pools(protocol="uniswap_v3")
for pool in pools:
    print(f"{pool['token0']}/{pool['token1']}: {pool['apy']}% APY")
```

---

## WebSocket 實時數據（未來功能）

對於需要實時更新的數據（如價格變化、倉位更新），我們計劃添加 WebSocket 支持：

```typescript
// 未來的 WebSocket 實現
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'price_update') {
    console.log('Price updated:', data.payload);
  } else if (data.type === 'position_update') {
    console.log('Position updated:', data.payload);
  }
};

// 訂閱特定事件
ws.send(JSON.stringify({
  action: 'subscribe',
  channels: ['prices', 'positions']
}));
```

---

## 錯誤處理最佳實踐

```typescript
async function safeApiCall<T>(apiFunction: () => Promise<T>): Promise<T | null> {
  try {
    return await apiFunction();
  } catch (error) {
    if (error.response) {
      // 服務器返回錯誤響應
      console.error('API Error:', error.response.data);
      
      if (error.response.status === 401) {
        // Token 過期，重新登錄
        window.location.href = '/login';
      } else if (error.response.status === 429) {
        // 速率限制
        console.error('Rate limit exceeded. Please try again later.');
      }
    } else if (error.request) {
      // 請求已發送但沒有收到響應
      console.error('Network error:', error.request);
    } else {
      // 其他錯誤
      console.error('Error:', error.message);
    }
    
    return null;
  }
}

// 使用範例
const portfolio = await safeApiCall(() => api.getPortfolioOverview());
if (portfolio) {
  console.log('Portfolio loaded successfully');
}
```

---

## 環境配置

創建一個 `.env` 文件來管理環境變量：

```bash
# API 配置
API_BASE_URL=http://localhost:8000/api/v1
JWT_SECRET=your-secret-key-change-in-production

# Supabase 配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Stripe 配置
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

在前端應用中使用環境變量：

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
```

---

## 部署建議

### 生產環境配置

1. **使用 HTTPS**：確保所有 API 請求都通過 HTTPS 進行。
2. **設置 CORS**：限制允許的來源域名。
3. **速率限制**：使用 `slowapi` 或類似庫來實現速率限制。
4. **日誌記錄**：添加詳細的日誌記錄以便調試。
5. **監控**：使用 Sentry 或類似工具進行錯誤監控。

### Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 總結

本指南涵蓋了 LiveaLittle DeFi API 的基本使用方法，包括認證、數據獲取和錯誤處理。對於更詳細的 API 規範，請參考 `livealittle_defi_api_docs.md`。

如有任何問題或建議，請聯繫開發團隊。

