"""
LiveaLittle DeFi 簡化版 API 服務器
適合新手學習和測試
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
import asyncio
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LiveaLittle DeFi API", version="1.0")

# 允許所有來源訪問（開發用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """API 首頁"""
    return {
        "name": "LiveaLittle DeFi API",
        "version": "1.0",
        "status": "運行中 ✅",
        "message": "歡迎使用 LiveaLittle DeFi API！",
        "endpoints": {
            "健康檢查": "/health",
            "獲取代幣價格": "/api/v1/price/{token}",
            "搜索 LP 池": "/api/v1/lp/search",
            "數據質量狀態": "/api/v1/quality/status"
        }
    }


@app.get("/health")
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy",
        "message": "API 運行正常！"
    }


# ==================== 價格 API ====================

async def fetch_coingecko_price(token: str) -> Optional[float]:
    """從 CoinGecko 獲取價格"""
    token_map = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "USDC": "usd-coin",
        "USDT": "tether"
    }
    
    token_id = token_map.get(token.upper())
    if not token_id:
        return None
    
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get(token_id, {}).get("usd")
    except Exception as e:
        logger.error(f"CoinGecko 錯誤: {e}")
    
    return None


@app.get("/api/v1/price/{token}")
async def get_token_price(token: str):
    """獲取代幣價格"""
    try:
        price = await fetch_coingecko_price(token)
        
        if price is None:
            raise HTTPException(
                status_code=404, 
                detail=f"找不到代幣 {token} 的價格"
            )
        
        return {
            "token": token.upper(),
            "price": price,
            "source": "CoinGecko",
            "timestamp": int(asyncio.get_event_loop().time())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取價格錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== LP 池 API ====================

# 模擬 LP 池數據（真實 API 需要更複雜的實現）
MOCK_LP_POOLS = [
    {
        "pool_address": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
        "protocol": "Uniswap V3",
        "chain": "Ethereum",
        "pair": "USDC/ETH",
        "tvl": 75000000,
        "apy": 15.5,
        "volume_24h": 50000000,
        "quality_score": 0.88
    },
    {
        "pool_address": "0x123...",
        "protocol": "Raydium",
        "chain": "Solana",
        "pair": "WSOL/USDC",
        "tvl": 18450000,
        "apy": 222.6,
        "volume_24h": 12000000,
        "quality_score": 0.95
    }
]


@app.get("/api/v1/lp/search")
async def search_lp_pools(
    min_tvl: float = 1000000,
    min_apy: float = 5.0,
    limit: int = 10
):
    """搜索 LP 池"""
    try:
        # 過濾池
        filtered_pools = [
            pool for pool in MOCK_LP_POOLS
            if pool["tvl"] >= min_tvl and pool["apy"] >= min_apy
        ]
        
        # 限制數量
        filtered_pools = filtered_pools[:limit]
        
        return {
            "total": len(filtered_pools),
            "pools": filtered_pools
        }
        
    except Exception as e:
        logger.error(f"搜索池錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 數據質量 API ====================

@app.get("/api/v1/quality/status")
async def get_data_quality_status():
    """獲取數據質量狀態"""
    try:
        return {
            "overall_status": "healthy",
            "price_data": {
                "source_availability": 1.0,
                "available_sources": 1,
                "total_sources": 1,
                "alerts": {
                    "total": 0,
                    "critical": 0,
                    "warning": 0
                }
            },
            "lp_data": {
                "recent_alerts": 0,
                "alert_types": []
            },
            "message": "所有系統運行正常 ✅"
        }
        
    except Exception as e:
        logger.error(f"獲取狀態錯誤: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 啟動消息
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 LiveaLittle DeFi API 已啟動！")
    logger.info("📊 API 文檔: http://localhost:8000/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
