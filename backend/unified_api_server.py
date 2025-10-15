from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
import asyncio
from typing import Optional
import logging

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

@app.get("/")
async def root():
    return {
        "name": "LiveaLittle DeFi API",
        "version": "1.0",
        "status": "運行中 ✅",
        "endpoints": {
            "健康檢查": "/health",
            "獲取代幣價格": "/api/v1/price/{token}",
            "搜索 LP 池": "/api/v1/lp/search"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/price/{token}")
async def get_token_price(token: str):
    """獲取代幣價格"""
    token_map = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "USDC": "usd-coin",
        "USDT": "tether"
    }
    
    token_id = token_map.get(token.upper())
    if not token_id:
        raise HTTPException(status_code=404, detail=f"不支持的代幣: {token}")
    
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd"
    
    try:
        async with aiohttp.ClientSession( ) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30 )) as response:
                if response.status == 200:
                    data = await response.json()
                    price = data.get(token_id, {}).get("usd")
                    
                    if price:
                        logger.info(f"✅ 成功獲取 {token} 價格: ${price}")
                        return {
                            "token": token.upper(),
                            "price": price,
                            "source": "CoinGecko",
                            "timestamp": int(asyncio.get_event_loop().time())
                        }
                    else:
                        logger.error(f"❌ 價格數據為空: {token}")
                        raise HTTPException(status_code=500, detail="價格數據為空")
                else:
                    logger.error(f"❌ CoinGecko API 返回狀態碼: {response.status}")
                    raise HTTPException(status_code=500, detail=f"API 錯誤: {response.status}")
                    
    except asyncio.TimeoutError:
        logger.error(f"⏱️ CoinGecko API 超時: {token}")
        raise HTTPException(status_code=504, detail="API 請求超時")
    except Exception as e:
        logger.error(f"❌ 獲取價格失敗: {e}")
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
    },
    {
        "pool_address": "0x123abc",
        "protocol": "Raydium",
        "chain": "Solana",
        "pair": "WSOL/USDC",
        "tvl": 18450000,
        "apy": 222.6,
        "volume_24h": 12000000
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
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 LiveaLittle DeFi API started!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
