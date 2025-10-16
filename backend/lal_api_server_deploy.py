"""
LAL API 服務器 V3（整合 IL 計算）
提供 LAL 智能搜尋服務的 RESTful API，支持多維度篩選和 IL 分析
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os

# 導入 LAL 智能搜尋 V3 和篩選器
from lal_smart_search_v3 import LALSmartSearchV3
from lp_filter import LPFilter, FilterCriteria
from il_calculator import HedgeParams

# 創建 FastAPI 應用
app = FastAPI(
    title="LAL Smart Search API V3",
    description="LAL 智能搜尋服務 - 尋找最佳 Delta Neutral 投資方案（整合 IL 計算和多維度篩選）",
    version="3.0.0"
)

# CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服務
lal = LALSmartSearchV3()
lp_filter = LPFilter()


# ==================== 數據模型 ====================

class SearchRequest(BaseModel):
    """搜尋請求"""
    # 基礎參數
    token: str = "ETH"
    capital: float = 10000
    risk_tolerance: str = "medium"
    
    # 對沖參數（新增）
    hedge_ratio: float = 1.0  # 0-1
    rebalance_frequency_days: int = 7
    
    # TVL 篩選
    min_tvl: Optional[float] = 5_000_000
    max_tvl: Optional[float] = None
    
    # APY 篩選
    min_apy: Optional[float] = 5.0
    max_apy: Optional[float] = None
    
    # 協議篩選
    protocols: Optional[List[str]] = None
    
    # 區塊鏈篩選
    chains: Optional[List[str]] = None
    
    # 代幣篩選
    include_tokens: Optional[List[str]] = None
    exclude_tokens: Optional[List[str]] = None
    
    # 戴維斯雙擊篩選
    min_davis_score: Optional[float] = None
    max_davis_score: Optional[float] = None
    davis_categories: Optional[List[str]] = None
    
    # 穩定性篩選
    min_base_apy_ratio: Optional[float] = None
    
    # 風險篩選
    il_risk: Optional[str] = None
    
    # Gas 成本篩選
    max_gas_cost: Optional[float] = None
    
    # 排序和分頁
    sort_by: str = "final_score"
    sort_order: str = "desc"
    limit: int = 5
    offset: int = 0


# ==================== API 端點 ====================

@app.get("/")
async def root():
    """根端點"""
    return {
        "service": "LAL Smart Search API",
        "version": "3.0.0",
        "status": "running",
        "description": "尋找最佳 Delta Neutral 投資方案（整合 IL 計算和多維度篩選）",
        "features": [
            "戴維斯雙擊分析",
            "Delta Neutral 配對",
            "無常損失（IL）計算",
            "對沖效果分析",
            "成本效益計算",
            "多維度篩選",
            "智能排序"
        ],
        "endpoints": {
            "smart_search": "/api/v1/lal/smart-search",
            "davis_analysis": "/api/v1/lal/davis-analysis",
            "supported_filters": "/api/v1/lal/filters",
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
        "version": "3.0.0",
        "features": {
            "il_calculation": True,
            "hedge_analysis": True,
            "multi_filter": True
        }
    }


@app.get("/api/v1/lal/smart-search")
async def smart_search(
    token: str = Query("ETH", description="目標代幣"),
    capital: float = Query(10000, description="投資資本（USD）"),
    risk_tolerance: str = Query("medium", description="風險偏好（low/medium/high）"),
    
    # 對沖參數（新增）
    hedge_ratio: float = Query(1.0, description="對沖比率（0-1）"),
    rebalance_frequency_days: int = Query(7, description="再平衡頻率（天）"),
    
    # TVL 篩選
    min_tvl: Optional[float] = Query(None, description="最小 TVL（USD）"),
    max_tvl: Optional[float] = Query(None, description="最大 TVL（USD）"),
    
    # APY 篩選
    min_apy: Optional[float] = Query(None, description="最小 APY（%）"),
    max_apy: Optional[float] = Query(None, description="最大 APY（%）"),
    
    # 協議篩選
    protocols: Optional[str] = Query(None, description="協議列表（逗號分隔）"),
    
    # 區塊鏈篩選
    chains: Optional[str] = Query(None, description="區塊鏈列表（逗號分隔）"),
    
    # 代幣篩選
    include_tokens: Optional[str] = Query(None, description="必須包含的代幣（逗號分隔）"),
    exclude_tokens: Optional[str] = Query(None, description="排除的代幣（逗號分隔）"),
    
    # 戴維斯雙擊篩選
    min_davis_score: Optional[float] = Query(None, description="最小戴維斯評分"),
    max_davis_score: Optional[float] = Query(None, description="最大戴維斯評分"),
    davis_categories: Optional[str] = Query(None, description="戴維斯評級（逗號分隔）"),
    
    # 穩定性篩選
    min_base_apy_ratio: Optional[float] = Query(None, description="最小基礎 APY 比例（%）"),
    
    # 風險篩選
    il_risk: Optional[str] = Query(None, description="IL 風險等級（low/medium/high）"),
    
    # Gas 成本篩選
    max_gas_cost: Optional[float] = Query(None, description="最大年化 Gas 成本（USD）"),
    
    # 排序和分頁
    sort_by: str = Query("final_score", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向（asc/desc）"),
    limit: int = Query(5, description="返回數量"),
    offset: int = Query(0, description="偏移量")
):
    """
    智能搜尋最佳 Delta Neutral 方案（整合 IL 計算）
    
    **新功能**:
    - 無常損失（IL）計算
    - Delta Neutral 對沖效果分析
    - 調整後的淨收益（考慮 IL）
    - 對沖參數配置
    """
    try:
        # 創建對沖參數
        hedge_params = HedgeParams(
            hedge_ratio=hedge_ratio,
            rebalance_frequency_days=rebalance_frequency_days
        )
        
        # 執行搜尋
        results = lal.search(
            token=token,
            capital=capital,
            risk_tolerance=risk_tolerance,
            min_tvl=min_tvl or 5_000_000,
            min_apy=min_apy or 5.0,
            top_n=100,  # 先獲取更多結果用於篩選
            hedge_params=hedge_params
        )
        
        # 應用篩選器
        filter_criteria = FilterCriteria(
            min_tvl=min_tvl,
            max_tvl=max_tvl,
            min_apy=min_apy,
            max_apy=max_apy,
            protocols=protocols.split(",") if protocols else None,
            chains=chains.split(",") if chains else None,
            include_tokens=include_tokens.split(",") if include_tokens else None,
            exclude_tokens=exclude_tokens.split(",") if exclude_tokens else None,
            min_davis_score=min_davis_score,
            max_davis_score=max_davis_score,
            davis_categories=davis_categories.split(",") if davis_categories else None,
            min_base_apy_ratio=min_base_apy_ratio,
            il_risk=il_risk,
            max_gas_cost=max_gas_cost,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )
        
        filtered_results = lp_filter.filter_pools(results, filter_criteria)
        filter_summary = lp_filter.get_filter_summary(filter_criteria, len(results), len(filtered_results))
        
        return {
            "success": True,
            "data": {
                "query": {
                    "token": token,
                    "capital": capital,
                    "risk_tolerance": risk_tolerance,
                    "hedge_ratio": hedge_ratio,
                    "rebalance_frequency_days": rebalance_frequency_days
                },
                "opportunities": filtered_results,
                "count": len(filtered_results),
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": len(filtered_results)
                },
                "filter_summary": filter_summary
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/lal/smart-search")
async def smart_search_post(request: SearchRequest):
    """
    智能搜尋（POST 方法）
    """
    try:
        # 創建對沖參數
        hedge_params = HedgeParams(
            hedge_ratio=request.hedge_ratio,
            rebalance_frequency_days=request.rebalance_frequency_days
        )
        
        # 執行搜尋
        results = lal.search(
            token=request.token,
            capital=request.capital,
            risk_tolerance=request.risk_tolerance,
            min_tvl=request.min_tvl or 5_000_000,
            min_apy=request.min_apy or 5.0,
            top_n=100,
            hedge_params=hedge_params
        )
        
        # 應用篩選器
        filter_criteria = FilterCriteria(
            min_tvl=request.min_tvl,
            max_tvl=request.max_tvl,
            min_apy=request.min_apy,
            max_apy=request.max_apy,
            protocols=request.protocols,
            chains=request.chains,
            include_tokens=request.include_tokens,
            exclude_tokens=request.exclude_tokens,
            min_davis_score=request.min_davis_score,
            max_davis_score=request.max_davis_score,
            davis_categories=request.davis_categories,
            min_base_apy_ratio=request.min_base_apy_ratio,
            il_risk=request.il_risk,
            max_gas_cost=request.max_gas_cost,
            sort_by=request.sort_by,
            sort_order=request.sort_order,
            limit=request.limit,
            offset=request.offset
        )
        
        filtered_results = lp_filter.filter_pools(results, filter_criteria)
        filter_summary = lp_filter.get_filter_summary(filter_criteria, len(results), len(filtered_results))
        
        return {
            "success": True,
            "data": {
                "query": {
                    "token": request.token,
                    "capital": request.capital,
                    "risk_tolerance": request.risk_tolerance,
                    "hedge_ratio": request.hedge_ratio,
                    "rebalance_frequency_days": request.rebalance_frequency_days
                },
                "opportunities": filtered_results,
                "count": len(filtered_results),
                "pagination": {
                    "limit": request.limit,
                    "offset": request.offset,
                    "total": len(filtered_results)
                },
                "filter_summary": filter_summary
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/lal/filters")
async def get_supported_filters():
    """
    獲取支持的篩選選項
    """
    return {
        "success": True,
        "data": lp_filter.get_supported_options()
    }


# ==================== 啟動服務 ====================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

