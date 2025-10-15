"""
LAL API 服務器 V2（帶篩選器）
提供 LAL 智能搜尋服務的 RESTful API，支持多維度篩選
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os

# 導入 LAL 智能搜尋和篩選器
from lal_smart_search import LALSmartSearch
from lp_filter import LPFilter, FilterCriteria

# 創建 FastAPI 應用
app = FastAPI(
    title="LAL Smart Search API V2",
    description="LAL 智能搜尋服務 - 尋找最佳 Delta Neutral 投資方案（支持多維度篩選）",
    version="2.0.0"
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
lal = LALSmartSearch()
lp_filter = LPFilter()


# ==================== 數據模型 ====================

class SearchRequest(BaseModel):
    """搜尋請求"""
    # 基礎參數
    token: str = "ETH"
    capital: float = 10000
    risk_tolerance: str = "medium"
    
    # TVL 篩選
    min_tvl: Optional[float] = 5_000_000
    max_tvl: Optional[float] = None
    
    # APY 篩選
    min_apy: Optional[float] = 5.0
    max_apy: Optional[float] = None
    
    # 協議篩選
    protocols: Optional[List[str]] = None
    
    # 鏈篩選
    chains: Optional[List[str]] = None
    
    # 代幣篩選
    include_tokens: Optional[List[str]] = None
    exclude_tokens: Optional[List[str]] = None
    
    # 戴維斯篩選
    min_davis_score: Optional[float] = None
    max_davis_score: Optional[float] = None
    davis_categories: Optional[List[str]] = None
    
    # 穩定性篩選
    min_base_apy_ratio: Optional[float] = None
    
    # 風險篩選
    il_risk: Optional[str] = None
    
    # Gas 篩選
    max_gas_cost: Optional[float] = None
    
    # 排序
    sort_by: str = "final_score"
    sort_order: str = "desc"
    
    # 分頁
    limit: int = 5
    offset: int = 0


# ==================== API 端點 ====================

@app.get("/")
async def root():
    """根端點"""
    return {
        "service": "LAL Smart Search API",
        "version": "2.0.0",
        "status": "running",
        "description": "尋找最佳 Delta Neutral 投資方案（支持多維度篩選）",
        "features": [
            "戴維斯雙擊分析",
            "Delta Neutral 配對",
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
        "service": "LAL Smart Search API",
        "version": "2.0.0"
    }


@app.get("/api/v1/lal/filters")
async def get_supported_filters():
    """獲取支持的篩選選項"""
    return {
        "success": True,
        "data": {
            "protocols": lp_filter.SUPPORTED_PROTOCOLS,
            "chains": lp_filter.SUPPORTED_CHAINS,
            "davis_categories": lp_filter.DAVIS_CATEGORIES,
            "il_risk_levels": lp_filter.IL_RISK_LEVELS,
            "sort_fields": lp_filter.SORT_FIELDS
        }
    }


@app.get("/api/v1/lal/smart-search")
async def smart_search_get(
    # 基礎參數
    token: str = Query("ETH", description="目標代幣"),
    capital: float = Query(10000, description="投資資本（USD）"),
    risk_tolerance: str = Query("medium", description="風險偏好（low/medium/high）"),
    
    # TVL 篩選
    min_tvl: Optional[float] = Query(5_000_000, description="最小 TVL"),
    max_tvl: Optional[float] = Query(None, description="最大 TVL"),
    
    # APY 篩選
    min_apy: Optional[float] = Query(5.0, description="最小 APY"),
    max_apy: Optional[float] = Query(None, description="最大 APY"),
    
    # 協議篩選
    protocols: Optional[str] = Query(None, description="協議列表（逗號分隔）"),
    
    # 鏈篩選
    chains: Optional[str] = Query(None, description="鏈列表（逗號分隔）"),
    
    # 代幣篩選
    include_tokens: Optional[str] = Query(None, description="必須包含的代幣（逗號分隔）"),
    exclude_tokens: Optional[str] = Query(None, description="必須排除的代幣（逗號分隔）"),
    
    # 戴維斯篩選
    min_davis_score: Optional[float] = Query(None, description="最小戴維斯評分"),
    max_davis_score: Optional[float] = Query(None, description="最大戴維斯評分"),
    davis_categories: Optional[str] = Query(None, description="戴維斯評級（逗號分隔）"),
    
    # 穩定性篩選
    min_base_apy_ratio: Optional[float] = Query(None, description="最小基礎 APY 比例"),
    
    # 風險篩選
    il_risk: Optional[str] = Query(None, description="無常損失風險（low/medium/high）"),
    
    # Gas 篩選
    max_gas_cost: Optional[float] = Query(None, description="最大年化 Gas 成本"),
    
    # 排序
    sort_by: str = Query("final_score", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向（asc/desc）"),
    
    # 分頁
    limit: int = Query(5, description="返回數量", ge=1, le=100),
    offset: int = Query(0, description="偏移量", ge=0)
):
    """
    LAL 智能搜尋（GET 方法）
    
    尋找最佳 Delta Neutral 投資方案，支持多維度篩選
    """
    try:
        # 解析逗號分隔的列表
        protocols_list = protocols.split(",") if protocols else None
        chains_list = chains.split(",") if chains else None
        include_tokens_list = include_tokens.split(",") if include_tokens else None
        exclude_tokens_list = exclude_tokens.split(",") if exclude_tokens else None
        davis_categories_list = davis_categories.split(",") if davis_categories else None
        
        # 創建篩選條件
        criteria = FilterCriteria(
            min_tvl=min_tvl,
            max_tvl=max_tvl,
            min_apy=min_apy,
            max_apy=max_apy,
            protocols=protocols_list,
            chains=chains_list,
            include_tokens=include_tokens_list,
            exclude_tokens=exclude_tokens_list,
            min_davis_score=min_davis_score,
            max_davis_score=max_davis_score,
            davis_categories=davis_categories_list,
            min_base_apy_ratio=min_base_apy_ratio,
            il_risk=il_risk,
            max_gas_cost=max_gas_cost,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )
        
        # 驗證篩選條件
        validation = lp_filter.validate_criteria(criteria)
        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid filter criteria",
                    "errors": validation["errors"]
                }
            )
        
        # 執行搜尋（獲取所有結果，不限制數量）
        all_opportunities = lal.search(
            token=token,
            capital=capital,
            risk_tolerance=risk_tolerance,
            min_tvl=0,  # 先不過濾，讓篩選器處理
            min_apy=0,
            top_n=1000  # 獲取更多結果
        )
        
        # 應用篩選器
        total_before = len(all_opportunities)
        filtered_opportunities = lp_filter.filter_pools(all_opportunities, criteria)
        total_after = len(filtered_opportunities)
        
        # 生成篩選摘要
        filter_summary = lp_filter.get_filter_summary(criteria, total_before, total_after)
        
        return {
            "success": True,
            "data": {
                "query": {
                    "token": token,
                    "capital": capital,
                    "risk_tolerance": risk_tolerance
                },
                "opportunities": filtered_opportunities,
                "count": len(filtered_opportunities),
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": total_after
                },
                "filter_summary": filter_summary
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/lal/smart-search")
async def smart_search_post(request: SearchRequest):
    """
    LAL 智能搜尋（POST 方法）
    
    尋找最佳 Delta Neutral 投資方案，支持多維度篩選
    """
    try:
        # 創建篩選條件
        criteria = FilterCriteria(
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
        
        # 驗證篩選條件
        validation = lp_filter.validate_criteria(criteria)
        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid filter criteria",
                    "errors": validation["errors"]
                }
            )
        
        # 執行搜尋
        all_opportunities = lal.search(
            token=request.token,
            capital=request.capital,
            risk_tolerance=request.risk_tolerance,
            min_tvl=0,
            min_apy=0,
            top_n=1000
        )
        
        # 應用篩選器
        total_before = len(all_opportunities)
        filtered_opportunities = lp_filter.filter_pools(all_opportunities, criteria)
        total_after = len(filtered_opportunities)
        
        # 生成篩選摘要
        filter_summary = lp_filter.get_filter_summary(criteria, total_before, total_after)
        
        return {
            "success": True,
            "data": {
                "query": {
                    "token": request.token,
                    "capital": request.capital,
                    "risk_tolerance": request.risk_tolerance
                },
                "opportunities": filtered_opportunities,
                "count": len(filtered_opportunities),
                "pagination": {
                    "limit": request.limit,
                    "offset": request.offset,
                    "total": total_after
                },
                "filter_summary": filter_summary
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    
    print(f"🚀 啟動 LAL API 服務器 V2...")
    print(f"📖 API 文檔: http://0.0.0.0:{port}/docs")
    print(f"🔍 智能搜尋: http://0.0.0.0:{port}/api/v1/lal/smart-search")
    print(f"🎯 支持的篩選: http://0.0.0.0:{port}/api/v1/lal/filters")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

