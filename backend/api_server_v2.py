"""
LiveaLittle DeFi API Server v2
整合真實數據的 FastAPI 實現
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn

# 導入我們的數據模組
from unified_data_aggregator import UnifiedDataAggregator
from delta_neutral_calculator import DeltaNeutralCalculator

# 初始化 FastAPI 應用
app = FastAPI(
    title="LiveaLittle DeFi API v2",
    description="DeFi Delta Neutral 策略平台 API - 整合真實數據",
    version="2.0.0"
)

# CORS 設置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應限制為特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化數據聚合器和計算器
aggregator = UnifiedDataAggregator()
calculator = DeltaNeutralCalculator()

# ==================== 數據模型 ====================

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

class TokenPrice(BaseModel):
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    updated_at: str

class LPPool(BaseModel):
    pool_id: str
    protocol: str
    chain: str
    symbol: str
    tvl: float
    apy: float
    apy_base: float
    apy_reward: float

class FundingRate(BaseModel):
    coin: str
    current_rate_pct: float
    avg_rate_pct: float
    annualized_rate_pct: float
    source: str
    updated_at: str

class MarketSentiment(BaseModel):
    value: int
    classification: str
    timestamp: str

class DeltaNeutralOpportunity(BaseModel):
    pool_id: str
    protocol: str
    chain: str
    symbol: str
    tvl: float
    lp_apy: float
    funding_apy: float
    total_apy: float
    annual_yield: float
    score: float

class StrategyReport(BaseModel):
    token: str
    capital: float
    timestamp: str
    market_data: Dict[str, Any]
    best_opportunity: Dict[str, Any]
    hedge_info: Dict[str, Any]
    top_opportunities: List[Dict[str, Any]]
    recommendation: str

# ==================== API 端點 ====================

@app.get("/", response_model=HealthResponse)
async def root():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

# ==================== 市場數據端點 ====================

@app.get("/api/v1/market/tokens", response_model=List[TokenPrice])
async def get_token_prices(
    symbols: str = Query("ETH,BTC,USDC", description="逗號分隔的代幣符號")
):
    """
    獲取代幣價格
    
    - **symbols**: 逗號分隔的代幣符號，例如 "ETH,BTC,USDC"
    """
    try:
        symbol_list = [s.strip() for s in symbols.split(",")]
        prices = aggregator.get_multiple_token_prices(symbol_list)
        
        return [
            {
                "symbol": data["symbol"],
                "price": data["price"],
                "change_24h": data["change_24h"],
                "volume_24h": data["volume_24h"],
                "updated_at": data["updated_at"]
            }
            for data in prices.values()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取代幣價格失敗: {str(e)}")

@app.get("/api/v1/market/pools", response_model=List[LPPool])
async def get_lp_pools(
    min_tvl: float = Query(1000000, description="最小 TVL（USD）"),
    limit: int = Query(50, description="返回數量限制")
):
    """
    獲取 LP 池列表
    
    - **min_tvl**: 最小 TVL 過濾（USD）
    - **limit**: 返回數量限制
    """
    try:
        pools = aggregator.get_lp_pools(min_tvl=min_tvl, limit=limit)
        
        return [
            {
                "pool_id": pool["pool_id"],
                "protocol": pool["protocol"],
                "chain": pool["chain"],
                "symbol": pool["symbol"],
                "tvl": pool["tvl"],
                "apy": pool["apy"],
                "apy_base": pool["apy_base"],
                "apy_reward": pool["apy_reward"]
            }
            for pool in pools
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取 LP 池失敗: {str(e)}")

@app.get("/api/v1/market/funding-rates", response_model=List[FundingRate])
async def get_funding_rates(
    coins: str = Query("ETH,BTC", description="逗號分隔的代幣符號")
):
    """
    獲取資金費率
    
    - **coins**: 逗號分隔的代幣符號，例如 "ETH,BTC"
    """
    try:
        coin_list = [c.strip() for c in coins.split(",")]
        rates = aggregator.get_multiple_funding_rates(coin_list)
        
        return [
            {
                "coin": data["coin"],
                "current_rate_pct": data["current_rate_pct"],
                "avg_rate_pct": data["avg_rate_pct"],
                "annualized_rate_pct": data["annualized_rate_pct"],
                "source": data["source"],
                "updated_at": data["updated_at"]
            }
            for data in rates.values()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取資金費率失敗: {str(e)}")

@app.get("/api/v1/market/sentiment", response_model=MarketSentiment)
async def get_market_sentiment():
    """獲取市場情緒（恐懼與貪婪指數）"""
    try:
        sentiment = aggregator.get_fear_greed_index()
        
        if not sentiment:
            raise HTTPException(status_code=404, detail="無法獲取市場情緒數據")
        
        return {
            "value": sentiment["value"],
            "classification": sentiment["classification"],
            "timestamp": sentiment["timestamp"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取市場情緒失敗: {str(e)}")

# ==================== Delta Neutral 策略端點 ====================

@app.get("/api/v1/delta-neutral/opportunities", response_model=List[DeltaNeutralOpportunity])
async def get_delta_neutral_opportunities(
    token: str = Query("ETH", description="目標代幣"),
    capital: float = Query(10000, description="投入資本（USD）"),
    min_tvl: float = Query(1000000, description="最小 TVL（USD）"),
    top_n: int = Query(10, description="返回前 N 個機會")
):
    """
    獲取 Delta Neutral 策略機會
    
    - **token**: 目標代幣（如 ETH, BTC）
    - **capital**: 投入資本（USD）
    - **min_tvl**: 最小 TVL 過濾（USD）
    - **top_n**: 返回前 N 個機會
    """
    try:
        opportunities = calculator.find_best_opportunities(
            token=token,
            capital=capital,
            min_tvl=min_tvl,
            top_n=top_n
        )
        
        return [
            {
                "pool_id": opp["pool_id"],
                "protocol": opp["protocol"],
                "chain": opp["chain"],
                "symbol": opp["symbol"],
                "tvl": opp["tvl"],
                "lp_apy": opp["lp_apy"],
                "funding_apy": opp["funding_apy"],
                "total_apy": opp["total_apy"],
                "annual_yield": opp["annual_yield"],
                "score": opp["score"]
            }
            for opp in opportunities
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取機會失敗: {str(e)}")

@app.get("/api/v1/delta-neutral/report", response_model=StrategyReport)
async def get_strategy_report(
    token: str = Query("ETH", description="目標代幣"),
    capital: float = Query(10000, description="投入資本（USD）")
):
    """
    生成完整的 Delta Neutral 策略報告
    
    - **token**: 目標代幣（如 ETH, BTC）
    - **capital**: 投入資本（USD）
    """
    try:
        report = calculator.generate_strategy_report(
            token=token,
            capital=capital
        )
        
        if "error" in report:
            raise HTTPException(status_code=404, detail=report["error"])
        
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成報告失敗: {str(e)}")

@app.post("/api/v1/delta-neutral/calculate-hedge")
async def calculate_hedge(
    lp_value: float = Query(..., description="LP 倉位價值（USD）"),
    token_price: float = Query(..., description="代幣價格（USD）"),
    pool_composition: float = Query(0.5, description="池中代幣比例")
):
    """
    計算對沖比率
    
    - **lp_value**: LP 倉位總價值（USD）
    - **token_price**: 代幣價格（USD）
    - **pool_composition**: 池中目標代幣的比例（默認 0.5）
    """
    try:
        hedge_info = calculator.calculate_hedge_ratio(
            lp_value=lp_value,
            token_price=token_price,
            pool_composition=pool_composition
        )
        return hedge_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"計算對沖比率失敗: {str(e)}")

@app.post("/api/v1/delta-neutral/calculate-yield")
async def calculate_yield(
    lp_apy: float = Query(..., description="LP 池 APY（%）"),
    funding_rate_apy: float = Query(..., description="資金費率 APY（%）"),
    capital: float = Query(..., description="投入資本（USD）"),
    gas_cost_annual: float = Query(200, description="年化 Gas 成本（USD）")
):
    """
    計算總收益
    
    - **lp_apy**: LP 池年化收益率（%）
    - **funding_rate_apy**: 資金費率年化收益率（%）
    - **capital**: 投入資本（USD）
    - **gas_cost_annual**: 年化 Gas 成本（USD）
    """
    try:
        yield_calc = calculator.calculate_total_yield(
            lp_apy=lp_apy,
            funding_rate_apy=funding_rate_apy,
            gas_cost_annual=gas_cost_annual,
            capital=capital
        )
        return yield_calc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"計算收益失敗: {str(e)}")

@app.post("/api/v1/delta-neutral/rebalance-decision")
async def rebalance_decision(
    current_apy: float = Query(..., description="當前池 APY（%）"),
    new_apy: float = Query(..., description="新池 APY（%）"),
    rebalance_cost: float = Query(..., description="轉倉成本（USD）"),
    capital: float = Query(..., description="投入資本（USD）"),
    min_apy_improvement: float = Query(5.0, description="最小 APY 提升要求（%）"),
    max_payback_days: int = Query(7, description="最大回本天數")
):
    """
    計算轉倉決策
    
    - **current_apy**: 當前池 APY（%）
    - **new_apy**: 新池 APY（%）
    - **rebalance_cost**: 轉倉成本（USD）
    - **capital**: 投入資本（USD）
    - **min_apy_improvement**: 最小 APY 提升要求（%）
    - **max_payback_days**: 最大回本天數
    """
    try:
        decision = calculator.calculate_rebalance_decision(
            current_apy=current_apy,
            new_apy=new_apy,
            rebalance_cost=rebalance_cost,
            capital=capital,
            min_apy_improvement=min_apy_improvement,
            max_payback_days=max_payback_days
        )
        return decision
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"計算轉倉決策失敗: {str(e)}")

# ==================== 啟動服務器 ====================

if __name__ == "__main__":
    print("🚀 啟動 LiveaLittle DeFi API Server v2")
    print("📊 整合真實數據：DeFiLlama + CoinGecko + Hyperliquid")
    print("🌐 API 文檔: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

