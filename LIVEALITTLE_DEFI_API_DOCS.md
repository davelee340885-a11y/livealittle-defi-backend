# LiveaLittle DeFi API 文檔

**版本**: 1.0
**基礎 URL**: `/api/v1`

---

## 總覽

本文檔定義了 LiveaLittle DeFi 系統的 RESTful API。該 API 旨在為前端應用程序提供實時數據，包括市場數據、投資組合表現、策略執行和用戶管理。

## 認證

所有 API 請求都需要通過 `Authorization` 頭部傳遞 JWT Token 進行認證。

```
Authorization: Bearer <YOUR_JWT_TOKEN>
```

---



## 數據端點

### `GET /market/overview`

獲取市場總覽數據，包括總市值、交易量等。

**響應範例**:

```json
{
  "total_market_cap": 2500000000000,
  "total_volume_24h": 120000000000,
  "btc_dominance": 45.5
}
```

### `GET /market/tokens`

獲取支持的代幣列表及其當前價格。

**查詢參數**:

- `limit` (可選): 返回的代幣數量，默認為 100。

**響應範例**:

```json
[
  {
    "symbol": "BTC",
    "name": "Bitcoin",
    "price": 68000.00,
    "change_24h": 2.5
  },
  {
    "symbol": "ETH",
    "name": "Ethereum",
    "price": 3500.00,
    "change_24h": 1.8
  }
]
```

### `GET /market/pools`

獲取可用的流動性池列表。

**查詢參數**:

- `protocol` (可選): 按協議過濾 (例如 `uniswap_v3`)。
- `chain` (可選): 按鏈過濾 (例如 `ethereum`)。

**響應範例**:

```json
[
  {
    "pool_id": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
    "protocol": "uniswap_v3",
    "chain": "ethereum",
    "token0": "USDC",
    "token1": "ETH",
    "fee": 0.05,
    "tvl": 500000000,
    "apy": 15.5
  }
]
```

### `GET /market/regime`

獲取當前的市場狀態。

**響應範例**:

```json
{
  "regime": "bull",
  "confidence_score": 0.85
}
```

---

## 投資組合端點

### `GET /portfolio/overview`

獲取用戶投資組合的總覽。

**響應範例**:

```json
{
  "total_value_usd": 150000.00,
  "total_return_usd": 25000.00,
  "total_return_percent": 20.0,
  "apy": 25.5
}
```

### `GET /portfolio/performance`

獲取投資組合的歷史表現數據。

**查詢參數**:

- `timeframe` (可選): 時間範圍 (`24h`, `7d`, `30d`, `90d`, `all`)，默認為 `30d`。

**響應範例**:

```json
{
  "timestamps": [1672531200, 1672617600, ...],
  "values_usd": [125000.00, 125500.00, ...]
}
```

### `GET /portfolio/positions`

獲取用戶當前的所有倉位。

**響應範例**:

```json
[
  {
    "position_id": "pos_12345",
    "protocol": "uniswap_v3",
    "type": "lp",
    "assets": [
      {
        "symbol": "ETH",
        "amount": 10
      },
      {
        "symbol": "USDC",
        "amount": 35000
      }
    ],
    "value_usd": 70000.00,
    "apy": 18.0
  }
]
```



## 策略端點

### `GET /strategies`

獲取可用的投資策略列表。

**響應範例**:

```json
[
  {
    "strategy_id": "delta_neutral_v1",
    "name": "Delta Neutral Strategy",
    "description": "A strategy that aims to be market-neutral by hedging LP positions."
  },
  {
    "strategy_id": "trend_following_v1",
    "name": "Trend Following Strategy",
    "description": "A strategy that follows the market trend to capture momentum."
  }
]
```

### `GET /strategies/{strategy_id}`

獲取特定策略的詳細信息。

**響應範例**:

```json
{
  "strategy_id": "delta_neutral_v1",
  "name": "Delta Neutral Strategy",
  "description": "A strategy that aims to be market-neutral by hedging LP positions.",
  "parameters": [
    {
      "name": "leverage",
      "type": "number",
      "default": 1,
      "min": 1,
      "max": 3
    },
    {
      "name": "rebalance_threshold",
      "type": "number",
      "default": 0.05,
      "min": 0.01,
      "max": 0.2
    }
  ]
}
```

### `POST /strategies`

創建一個新的用戶自定義策略。

**請求體**:

```json
{
  "name": "My Custom Strategy",
  "base_strategy_id": "delta_neutral_v1",
  "parameters": {
    "leverage": 1.5,
    "rebalance_threshold": 0.1
  }
}
```

**響應範例**:

```json
{
  "user_strategy_id": "usr_strat_abcde",
  "name": "My Custom Strategy",
  "status": "active"
}
```

---

## 執行端點

### `GET /execution/opportunities`

獲取當前的再平衡機會。

**響應範例**:

```json
[
  {
    "opportunity_id": "opp_67890",
    "type": "rebalance",
    "description": "Rebalance ETH/USDC LP to capture higher yield.",
    "estimated_profit_usd": 150.00,
    "estimated_cost_usd": 15.00
  }
]
```

### `POST /execution/rebalance`

執行一個再平衡計劃。這個請求需要用戶手動確認。

**請求體**:

```json
{
  "opportunity_id": "opp_67890"
}
```

**響應範例**:

```json
{
  "execution_id": "exec_fghij",
  "status": "pending_confirmation"
}
```

### `GET /execution/status/{execution_id}`

獲取特定執行的狀態。

**響應範例**:

```json
{
  "execution_id": "exec_fghij",
  "status": "completed",
  "timestamp": "2025-10-15T10:00:00Z",
  "transactions": [
    {
      "tx_hash": "0x123...",
      "chain": "ethereum",
      "status": "confirmed"
    }
  ]
}
```



## 用戶管理端點

### `POST /auth/register`

註冊一個新用戶。

**請求體**:

```json
{
  "email": "user@example.com",
  "password": "your_strong_password"
}
```

**響應範例**:

```json
{
  "user_id": "usr_12345",
  "email": "user@example.com",
  "token": "<YOUR_JWT_TOKEN>"
}
```

### `POST /auth/login`

用戶登錄。

**請求體**:

```json
{
  "email": "user@example.com",
  "password": "your_strong_password"
}
```

**響應範例**:

```json
{
  "token": "<YOUR_JWT_TOKEN>"
}
```

### `GET /user/profile`

獲取用戶個人資料。

**響應範例**:

```json
{
  "user_id": "usr_12345",
  "email": "user@example.com",
  "full_name": "Alex Doe",
  "subscription_plan": "professional"
}
```

### `PUT /user/profile`

更新用戶個人資料。

**請求體**:

```json
{
  "full_name": "Alexander Doe"
}
```

**響應範例**:

```json
{
  "user_id": "usr_12345",
  "email": "user@example.com",
  "full_name": "Alexander Doe",
  "subscription_plan": "professional"
}
```

---

## 訂閱端點

### `GET /subscriptions/plans`

獲取可用的訂閱計劃。

**響應範例**:

```json
[
  {
    "plan_id": "basic",
    "name": "基礎版",
    "price_monthly": 29,
    "features": [
      "3個策略池監控",
      "每日自動再平衡",
      "基礎風險保護"
    ]
  },
  {
    "plan_id": "professional",
    "name": "專業版",
    "price_monthly": 99,
    "features": [
      "無限策略池",
      "實時自動優化",
      "高級風險管理",
      "優先支持"
    ]
  }
]
```

### `POST /subscriptions/subscribe`

創建一個新的訂閱。

**請求體**:

```json
{
  "plan_id": "professional",
  "payment_token": "<STRIPE_PAYMENT_TOKEN>"
}
```

**響應範例**:

```json
{
  "subscription_id": "sub_klmno",
  "plan_id": "professional",
  "status": "active",
  "next_billing_date": "2025-11-15"
}
```

### `GET /subscriptions/status`

獲取用戶的訂閱狀態。

**響應範例**:

```json
{
  "plan_id": "professional",
  "status": "active",
  "next_billing_date": "2025-11-15"
}
```



---

## 錯誤處理

API 使用標準的 HTTP 狀態碼來表示請求的成功或失敗。一般來說，`2xx` 範圍內的狀態碼表示成功，`4xx` 範圍表示客戶端錯誤（例如，無效的參數），`5xx` 範圍表示服務器端錯誤。

錯誤響應將包含一個 JSON 對象，其中包含 `error` 和 `message` 字段。

**錯誤響應範例**:

```json
{
  "error": "invalid_request",
  "message": "The 'plan_id' field is required."
}
```

| 狀態碼 | 錯誤碼 | 描述 |
| :--- | :--- | :--- |
| `400` | `invalid_request` | 請求無效，例如缺少必需的參數。 |
| `401` | `unauthorized` | 未經授權，JWT Token 無效或缺失。 |
| `403` | `forbidden` | 禁止訪問，用戶無權執行此操作。 |
| `404` | `not_found` | 找不到請求的資源。 |
| `429` | `rate_limit_exceeded` | 超出速率限制。 |
| `500` | `internal_server_error` | 服務器內部錯誤。 |

---

## 速率限制

為了確保服務的穩定性，API 對請求進行速率限制。默認情況下，每個用戶每分鐘最多可以發出 120 個請求。超出此限制的請求將收到 `429 Too Many Requests` 錯誤。

響應頭部將包含有關當前速率限制狀態的信息：

- `X-RateLimit-Limit`: 每個時間窗口允許的請求總數。
- `X-RateLimit-Remaining`: 當前時間窗口內剩餘的請求數。
- `X-RateLimit-Reset`: 重置速率限制的時間戳（UTC 秒）。

