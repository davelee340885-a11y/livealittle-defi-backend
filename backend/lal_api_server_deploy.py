"""
LAL API 服務器（部署版本）
提供 LAL 智能搜尋服務的 RESTful API
支持 Render 和其他雲平台部署
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os

# 導入 LAL 智能搜尋
from lal_smart_search import LALSmartSearch

# 創建 FastAPI 應用
app = FastAPI(
    title="LAL Smart Search API",
    description="LAL 智能搜尋服務 - 尋找最佳 Delta Neutral 投資方案",
    version="1.0.0"
)

# CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 LAL 服務
lal = LALSmartSearch()


# ==================== 數據模型 ====================

class SearchRequest(BaseModel):
    """搜尋請求"""
    token: str = "ETH"
    capital: float = 10000
    risk_tolerance: str = "medium"
    min_tvl: float = 5_000_000
    min_apy: float = 5.0
    top_n: int = 5


# ==================== API 端點 ====================

@app.get("/")
async def root():
    """根端點"""
    return {
        "service": "LAL Smart Search API",
        "version": "1.0.0",
        "status": "running",
        "description": "尋找最佳 Delta Neutral 投資方案",
        "endpoints": {
            "smart_search": "/api/v1/lal/smart-search",
            "davis_analysis": "/api/v1/lal/davis-analysis",
            "health": "/health",
            "docs": "/docs"
        },
        "github": "https://github.com/davelee340885-a11y/livealittle-defi-backend"
    }


@app.get("/health")
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy",
        "service": "LAL Smart Search API",
        "version": "1.0.0"
    }


@app.post("/api/v1/lal/smart-search")
async def smart_search(request: SearchRequest):
    """
    LAL 智能搜尋
    
    尋找最佳 Delta Neutral 投資方案
    """
    try:
        # 執行搜尋
        opportunities = lal.search(
            token=request.token,
            capital=request.capital,
            risk_tolerance=request.risk_tolerance,
            min_tvl=request.min_tvl,
            min_apy=request.min_apy,
            top_n=request.top_n
        )
        
        return {
            "success": True,
            "data": {
                "query": {
                    "token": request.token,
                    "capital": request.capital,
                    "risk_tolerance": request.risk_tolerance
                },
                "opportunities": opportunities,
                "count": len(opportunities)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/lal/smart-search")
async def smart_search_get(
    token: str = Query("ETH", description="目標代幣"),
    capital: float = Query(10000, description="投資資本（USD）"),
    risk_tolerance: str = Query("medium", description="風險偏好（low/medium/high）"),
    min_tvl: float = Query(5_000_000, description="最小 TVL"),
    min_apy: float = Query(5.0, description="最小 APY"),
    top_n: int = Query(5, description="返回前 N 個方案")
):
    """
    LAL 智能搜尋（GET 方法）
    
    尋找最佳 Delta Neutral 投資方案
    """
    request = SearchRequest(
        token=token,
        capital=capital,
        risk_tolerance=risk_tolerance,
        min_tvl=min_tvl,
        min_apy=min_apy,
        top_n=top_n
    )
    
    return await smart_search(request)


@app.get("/api/v1/lal/davis-analysis")
async def davis_analysis(
    token: str = Query("ETH", description="目標代幣"),
    min_tvl: float = Query(5_000_000, description="最小 TVL"),
    min_apy: float = Query(5.0, description="最小 APY"),
    top_n: int = Query(10, description="返回前 N 個池")
):
    """
    戴維斯雙擊分析
    
    識別潛在優質 LP 池
    """
    try:
        results = lal.davis_analyzer.analyze_token_pools(
            token=token,
            min_tvl=min_tvl,
            min_apy=min_apy,
            top_n=top_n
        )
        
        return {
            "success": True,
            "data": {
                "token": token,
                "pools": results,
                "count": len(results)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 主程序 ====================

if __name__ == "__main__":
    # 從環境變量獲取端口，默認 8001
    port = int(os.environ.get("PORT", 8001))
    
    print(f"🚀 啟動 LAL API 服務器...")
    print(f"📖 API 文檔: http://0.0.0.0:{port}/docs")
    print(f"🔍 智能搜尋: http://0.0.0.0:{port}/api/v1/lal/smart-search?token=ETH&capital=10000")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

