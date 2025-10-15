from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
import asyncio
from typing import Optional, Dict
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO )
logger = logging.getLogger(__name__)

app = FastAPI(title="LiveaLittle DeFi API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 價格緩存
price_cache: Dict[str, dict] = {}
CACHE_DURATION = 60

@app.get("/")
async def root():
    return {
        "name": "LiveaLittle DeFi API",
        "version": "1.0",
        "status": "運行中 ✅",
        "endpoints": {
            "健康檢查": "/health",
            "獲取代幣價格": "/api/v1/price/{token}",
            "Delta Neutral 計算": "/api/v1/calculate/delta-neutral",
            "搜索 LP 池": "/api/v1/lp/search"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/price/{token}")
async def get_token_price(token: str):
    """獲取代幣價格（帶緩存）"""
    token = token.upper()
    
    if token in price_cache:
        cached_data = price_cache[token]
        cache_time = datetime.fromtimestamp(cached_data["timestamp"])
        if datetime.now() - cache_time < timedelta(seconds=CACHE_DURATION):
            logger.info(f"📦 使用緩存價格: {token}")
            return cached_data
    
    token_map = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "USDC": "usd-coin",
        "USDT": "tether"
    }
    
    token_id = token_map.get(token)
    if not token_id:
        raise HTTPException(status_code=404, detail=f"不支持的代幣: {token}")
    
    all_token_ids = ",".join(token_map.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={all_token_ids}&vs_currencies=usd"
    
    try:
        async with aiohttp.ClientSession( ) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30 )) as response:
                if response.status == 200:
                    data = await response.json()
                    current_timestamp = int(datetime.now().timestamp())
                    
                    for symbol, coin_id in token_map.items():
                        if coin_id in data and "usd" in data[coin_id]:
                            price_cache[symbol] = {
                                "token": symbol,
                                "price": data[coin_id]["usd"],
                                "source": "CoinGecko",
                                "timestamp": current_timestamp
                            }
                    
                    if token in price_cache:
                        logger.info(f"✅ 成功獲取 {token} 價格: ${price_cache[token]['price']}")
                        return price_cache[token]
                    else:
                        raise HTTPException(status_code=500, detail="價格數據為空")
                        
                elif response.status == 429:
                    logger.error("⚠️ CoinGecko API 速率限制")
                    mock_prices = {
                        "BTC": 111666,
                        "ETH": 4085.45,
                        "SOL": 202.53,
                        "USDC": 1.0,
                        "USDT": 1.0
                    }
                    return {
                        "token": token,
                        "price": mock_prices.get(token, 0),
                        "source": "Mock Data (Rate Limited)",
                        "timestamp": int(datetime.now().timestamp())
                    }
                else:
                    raise HTTPException(status_code=500, detail=f"API 錯誤: {response.status}")
                    
    except Exception as e:
        logger.error(f"❌ 獲取價格失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/calculate/delta-neutral")
async def calculate_delta_neutral(
    investment_amount: float,
    token_symbol: str,
    lp_apy: float,
    token_price: Optional[float] = None
):
    """計算 Delta Neutral 策略收益"""
    try:
        if not token_price:
            price_data = await get_token_price(token_symbol)
            token_price = price_data["price"]
        
        lp_allocation = investment_amount * 0.5
        short_position = investment_amount * 0.5
        
        lp_annual_return = lp_allocation * (lp_apy / 100)
        lp_daily_return = lp_annual_return / 365
        lp_monthly_return = lp_annual_return / 12
        
        funding_rate_annual = 0.05
        short_cost_annual = short_position * funding_rate_annual
        short_cost_daily = short_cost_annual / 365
        short_cost_monthly = short_cost_annual / 12
        
        net_annual_return = lp_annual_return - short_cost_annual
        net_daily_return = lp_daily_return - short_cost_daily
        net_monthly_return = lp_monthly_return - short_cost_monthly
        net_apy = (net_annual_return / investment_amount) * 100
        
        logger.info(f"✅ Delta Neutral 計算: ${investment_amount}, APY {net_apy:.2f}%")
        
        return {
            "strategy": "Delta Neutral",
            "investment_amount": investment_amount,
            "token": token_symbol,
            "token_price": token_price,
            "allocation": {
                "lp_position": lp_allocation,
                "short_position": short_position
            },
            "returns": {
                "lp_annual": round(lp_annual_return, 2),
                "lp_monthly": round(lp_monthly_return, 2),
                "lp_daily": round(lp_daily_return, 2),
                "short_cost_annual": round(short_cost_annual, 2),
                "short_cost_monthly": round(short_cost_monthly, 2),
                "short_cost_daily": round(short_cost_daily, 2),
                "net_annual": round(net_annual_return, 2),
                "net_monthly": round(net_monthly_return, 2),
                "net_daily": round(net_daily_return, 2)
            },
            "apy": {
                "lp_apy": lp_apy,
                "net_apy": round(net_apy, 2),
                "funding_rate": funding_rate_annual * 100
            },
            "risk": {
                "impermanent_loss_protected": True,
                "price_exposure": "Neutral",
                "risk_level": "Low"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Delta Neutral 計算失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

MOCK_LP_POOLS = [
    {
        "pool_address": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
        "protocol": "Uniswap V3",
        "chain": "Ethereum",
        "pair": "USDC/ETH",
        "tvl": 75000000,
        "apy": 15.5,
        "volume_24h": 50000000
    }
]

@app.get("/api/v1/lp/search")
async def search_lp_pools(min_tvl: float = 1000000, min_apy: float = 5.0, limit: int = 10):
    try:
        filtered_pools = [
            pool for pool in MOCK_LP_POOLS
            if pool["tvl"] >= min_tvl and pool["apy"] >= min_apy
        ]
        return {"total": len(filtered_pools[:limit]), "pools": filtered_pools[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 LiveaLittle DeFi API started!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
