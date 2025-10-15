"""
LP 數據質量監控系統
專門針對流動性池數據的質量監控和異常檢測
"""

import time
import json
from typing import Dict, List, Optional
from collections import deque
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LPPoolHistory:
    """LP 池歷史記錄"""
    def __init__(self, max_size: int = 100):
        self.tvl_history = deque(maxlen=max_size)
        self.apy_history = deque(maxlen=max_size)
        self.volume_history = deque(maxlen=max_size)
    
    def add(self, tvl: float, apy: float, volume: float, timestamp: int):
        """添加記錄"""
        self.tvl_history.append({"value": tvl, "timestamp": timestamp})
        self.apy_history.append({"value": apy, "timestamp": timestamp})
        self.volume_history.append({"value": volume, "timestamp": timestamp})
    
    def get_last_values(self) -> Dict:
        """獲取最後的值"""
        return {
            "tvl": self.tvl_history[-1]["value"] if self.tvl_history else None,
            "apy": self.apy_history[-1]["value"] if self.apy_history else None,
            "volume": self.volume_history[-1]["value"] if self.volume_history else None
        }


class LPAnomalyDetector:
    """LP 數據異常檢測器"""
    def __init__(self):
        self.pool_histories = {}  # pool_id -> LPPoolHistory
        self.alerts = []
    
    def _get_history(self, pool_id: str) -> LPPoolHistory:
        """獲取或創建池歷史"""
        if pool_id not in self.pool_histories:
            self.pool_histories[pool_id] = LPPoolHistory()
        return self.pool_histories[pool_id]
    
    def check_tvl_drop(
        self, 
        pool_id: str, 
        pool_name: str,
        new_tvl: float, 
        threshold: float = 0.20
    ) -> Optional[Dict]:
        """檢查 TVL 急劇下降（可能是流動性撤出）"""
        history = self._get_history(pool_id)
        last_values = history.get_last_values()
        
        if last_values["tvl"] is None:
            history.add(new_tvl, 0, 0, int(time.time()))
            return None
        
        last_tvl = last_values["tvl"]
        
        # 計算變化百分比
        if last_tvl > 0:
            change_percent = (new_tvl - last_tvl) / last_tvl
            
            # 檢查是否下降超過閾值
            if change_percent < -threshold:
                alert = {
                    "type": "tvl_drop",
                    "pool_id": pool_id,
                    "pool_name": pool_name,
                    "old_tvl": last_tvl,
                    "new_tvl": new_tvl,
                    "change_percent": change_percent * 100,
                    "threshold_percent": -threshold * 100,
                    "timestamp": int(time.time()),
                    "severity": "warning" if change_percent > -0.50 else "critical"
                }
                
                self.alerts.append(alert)
                logger.warning(
                    f"⚠️  TVL drop detected for {pool_name}: "
                    f"{change_percent*100:.2f}% "
                    f"(${last_tvl:,.0f} → ${new_tvl:,.0f})"
                )
                
                return alert
        
        return None
    
    def check_apy_anomaly(
        self,
        pool_id: str,
        pool_name: str,
        new_apy: float,
        min_apy: float = 1.0,
        max_apy: float = 1000.0
    ) -> Optional[Dict]:
        """檢查 APY 異常（過低或過高）"""
        if new_apy < min_apy:
            alert = {
                "type": "apy_too_low",
                "pool_id": pool_id,
                "pool_name": pool_name,
                "apy": new_apy,
                "min_apy": min_apy,
                "timestamp": int(time.time()),
                "severity": "warning"
            }
            
            self.alerts.append(alert)
            logger.warning(
                f"⚠️  APY too low for {pool_name}: {new_apy:.2f}%"
            )
            
            return alert
        
        if new_apy > max_apy:
            alert = {
                "type": "apy_too_high",
                "pool_id": pool_id,
                "pool_name": pool_name,
                "apy": new_apy,
                "max_apy": max_apy,
                "timestamp": int(time.time()),
                "severity": "warning"
            }
            
            self.alerts.append(alert)
            logger.warning(
                f"⚠️  APY suspiciously high for {pool_name}: {new_apy:.2f}%"
            )
            
            return alert
        
        return None
    
    def check_impermanent_loss_risk(
        self,
        pool_id: str,
        pool_name: str,
        token0_price_change: float,
        token1_price_change: float,
        threshold: float = 0.10
    ) -> Optional[Dict]:
        """檢查無常損失風險（價格分歧）"""
        # 計算價格變化的差異
        price_divergence = abs(token0_price_change - token1_price_change)
        
        if price_divergence > threshold:
            # 估算無常損失
            # 簡化公式：IL ≈ 2 * sqrt(price_ratio) / (1 + price_ratio) - 1
            price_ratio = (1 + token0_price_change) / (1 + token1_price_change)
            il_estimate = 2 * (price_ratio ** 0.5) / (1 + price_ratio) - 1
            
            alert = {
                "type": "impermanent_loss_risk",
                "pool_id": pool_id,
                "pool_name": pool_name,
                "price_divergence": price_divergence * 100,
                "estimated_il": il_estimate * 100,
                "timestamp": int(time.time()),
                "severity": "warning" if abs(il_estimate) < 0.05 else "critical"
            }
            
            self.alerts.append(alert)
            logger.warning(
                f"⚠️  Impermanent loss risk for {pool_name}: "
                f"Price divergence {price_divergence*100:.2f}%, "
                f"Estimated IL {il_estimate*100:.2f}%"
            )
            
            return alert
        
        return None
    
    def check_low_liquidity(
        self,
        pool_id: str,
        pool_name: str,
        tvl: float,
        volume_24h: float,
        min_tvl: float = 100000
    ) -> Optional[Dict]:
        """檢查流動性不足"""
        if tvl < min_tvl:
            alert = {
                "type": "low_liquidity",
                "pool_id": pool_id,
                "pool_name": pool_name,
                "tvl": tvl,
                "min_tvl": min_tvl,
                "volume_24h": volume_24h,
                "timestamp": int(time.time()),
                "severity": "warning"
            }
            
            self.alerts.append(alert)
            logger.warning(
                f"⚠️  Low liquidity for {pool_name}: TVL=${tvl:,.0f}"
            )
            
            return alert
        
        return None
    
    def check_volume_tvl_ratio(
        self,
        pool_id: str,
        pool_name: str,
        tvl: float,
        volume_24h: float,
        min_ratio: float = 0.01
    ) -> Optional[Dict]:
        """檢查交易量/TVL 比率（低比率可能表示流動性效率低）"""
        if tvl > 0:
            ratio = volume_24h / tvl
            
            if ratio < min_ratio:
                alert = {
                    "type": "low_volume_tvl_ratio",
                    "pool_id": pool_id,
                    "pool_name": pool_name,
                    "tvl": tvl,
                    "volume_24h": volume_24h,
                    "ratio": ratio,
                    "min_ratio": min_ratio,
                    "timestamp": int(time.time()),
                    "severity": "info"
                }
                
                self.alerts.append(alert)
                logger.info(
                    f"ℹ️  Low volume/TVL ratio for {pool_name}: {ratio:.4f}"
                )
                
                return alert
        
        return None
    
    def get_recent_alerts(self, seconds: int = 300) -> List[Dict]:
        """獲取最近的警報"""
        current_time = int(time.time())
        cutoff_time = current_time - seconds
        return [a for a in self.alerts if a["timestamp"] >= cutoff_time]


class LPDataQualityCalculator:
    """LP 數據質量計算器"""
    @staticmethod
    def calculate_data_completeness(pool_data: Dict) -> float:
        """計算數據完整性 (0-1)"""
        required_fields = ["tvl", "apy", "volume_24h", "token0", "token1"]
        present_fields = sum(1 for field in required_fields if pool_data.get(field) is not None)
        return present_fields / len(required_fields)
    
    @staticmethod
    def calculate_data_consistency(std_dev: float, value: float) -> float:
        """計算數據一致性 (0-1)"""
        if value == 0:
            return 0.0
        
        coefficient_of_variation = std_dev / value
        consistency = max(0, 1.0 - (coefficient_of_variation / 0.1))
        return min(1.0, consistency)
    
    @staticmethod
    def calculate_liquidity_score(tvl: float, volume_24h: float) -> float:
        """計算流動性評分 (0-1)"""
        # TVL 評分（對數尺度）
        if tvl <= 0:
            tvl_score = 0
        elif tvl < 100000:  # 10 萬
            tvl_score = 0.2
        elif tvl < 1000000:  # 100 萬
            tvl_score = 0.4
        elif tvl < 10000000:  # 1000 萬
            tvl_score = 0.6
        elif tvl < 100000000:  # 1 億
            tvl_score = 0.8
        else:
            tvl_score = 1.0
        
        # 交易量評分
        if volume_24h <= 0:
            volume_score = 0
        elif volume_24h < 10000:
            volume_score = 0.2
        elif volume_24h < 100000:
            volume_score = 0.4
        elif volume_24h < 1000000:
            volume_score = 0.6
        elif volume_24h < 10000000:
            volume_score = 0.8
        else:
            volume_score = 1.0
        
        # 加權平均
        return tvl_score * 0.6 + volume_score * 0.4
    
    @staticmethod
    def calculate_risk_score(apy: float, tvl: float) -> float:
        """計算風險評分 (0-1, 越高越安全)"""
        # APY 風險（過高的 APY 可能有風險）
        if apy < 5:
            apy_risk = 0.5  # 太低
        elif apy < 50:
            apy_risk = 1.0  # 正常範圍
        elif apy < 200:
            apy_risk = 0.7  # 較高
        else:
            apy_risk = 0.3  # 非常高，可能有問題
        
        # TVL 風險（TVL 越高越安全）
        if tvl < 100000:
            tvl_risk = 0.2
        elif tvl < 1000000:
            tvl_risk = 0.4
        elif tvl < 10000000:
            tvl_risk = 0.6
        elif tvl < 100000000:
            tvl_risk = 0.8
        else:
            tvl_risk = 1.0
        
        # 加權平均
        return apy_risk * 0.4 + tvl_risk * 0.6


class LPDataQualityMonitor:
    """LP 數據質量監控器"""
    def __init__(self):
        self.anomaly_detector = LPAnomalyDetector()
        self.quality_calculator = LPDataQualityCalculator()
    
    def monitor_pool(self, pool_data: Dict) -> Dict:
        """監控單個池的數據質量"""
        pool_id = pool_data.get("pool_address", "unknown")
        pool_name = f"{pool_data.get('token0', '?')}/{pool_data.get('token1', '?')}"
        
        # 異常檢測
        tvl_alert = self.anomaly_detector.check_tvl_drop(
            pool_id, pool_name, pool_data.get("tvl", 0)
        )
        
        apy_alert = self.anomaly_detector.check_apy_anomaly(
            pool_id, pool_name, pool_data.get("apy", 0)
        )
        
        liquidity_alert = self.anomaly_detector.check_low_liquidity(
            pool_id, pool_name, 
            pool_data.get("tvl", 0),
            pool_data.get("volume_24h", 0)
        )
        
        volume_ratio_alert = self.anomaly_detector.check_volume_tvl_ratio(
            pool_id, pool_name,
            pool_data.get("tvl", 0),
            pool_data.get("volume_24h", 0)
        )
        
        # 計算質量指標
        completeness = self.quality_calculator.calculate_data_completeness(pool_data)
        
        tvl_consistency = self.quality_calculator.calculate_data_consistency(
            pool_data.get("tvl_std_dev", 0),
            pool_data.get("tvl", 1)
        )
        
        liquidity_score = self.quality_calculator.calculate_liquidity_score(
            pool_data.get("tvl", 0),
            pool_data.get("volume_24h", 0)
        )
        
        risk_score = self.quality_calculator.calculate_risk_score(
            pool_data.get("apy", 0),
            pool_data.get("tvl", 0)
        )
        
        # 組裝監控報告
        report = {
            "pool_id": pool_id,
            "pool_name": pool_name,
            "protocol": pool_data.get("protocol", "unknown"),
            "chain": pool_data.get("chain", "unknown"),
            "metrics": {
                "tvl": pool_data.get("tvl", 0),
                "apy": pool_data.get("apy", 0),
                "volume_24h": pool_data.get("volume_24h", 0)
            },
            "quality_scores": {
                "completeness": round(completeness, 3),
                "consistency": round(tvl_consistency, 3),
                "liquidity": round(liquidity_score, 3),
                "risk": round(risk_score, 3)
            },
            "alerts": {
                "tvl_drop": tvl_alert,
                "apy_anomaly": apy_alert,
                "low_liquidity": liquidity_alert,
                "volume_ratio": volume_ratio_alert
            },
            "data_sources": pool_data.get("sources", []),
            "timestamp": int(time.time())
        }
        
        return report
    
    def get_pool_recommendation(self, report: Dict) -> str:
        """根據報告給出推薦"""
        scores = report["quality_scores"]
        
        # 計算總分
        total_score = (
            scores["completeness"] * 0.2 +
            scores["consistency"] * 0.2 +
            scores["liquidity"] * 0.3 +
            scores["risk"] * 0.3
        )
        
        if total_score >= 0.8:
            return "EXCELLENT - Highly recommended"
        elif total_score >= 0.6:
            return "GOOD - Recommended with caution"
        elif total_score >= 0.4:
            return "FAIR - Consider alternatives"
        else:
            return "POOR - Not recommended"
    
    def save_report(self, report: Dict, filename: str = "lp_quality_report.json"):
        """保存報告到文件"""
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"LP quality report saved to {filename}")


# 測試函數
def test_monitor():
    """測試監控系統"""
    monitor = LPDataQualityMonitor()
    
    # 模擬池數據
    pool_data = {
        "pool_address": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
        "protocol": "uniswap_v3",
        "chain": "ethereum",
        "token0": "USDC",
        "token1": "ETH",
        "tvl": 75000000,
        "apy": 15.5,
        "volume_24h": 50000000,
        "tvl_std_dev": 500000,
        "sources": ["defillama", "uniswap_v3"]
    }
    
    # 監控
    report = monitor.monitor_pool(pool_data)
    
    print("\n" + "="*70)
    print("LP DATA QUALITY MONITORING REPORT")
    print("="*70)
    print(f"Pool: {report['pool_name']} on {report['protocol']}")
    print(f"Chain: {report['chain']}")
    print(f"\nMetrics:")
    print(f"  TVL: ${report['metrics']['tvl']:,.0f}")
    print(f"  APY: {report['metrics']['apy']:.2f}%")
    print(f"  24h Volume: ${report['metrics']['volume_24h']:,.0f}")
    
    print(f"\nQuality Scores:")
    for metric, value in report['quality_scores'].items():
        print(f"  {metric.capitalize()}: {value:.3f}")
    
    recommendation = monitor.get_pool_recommendation(report)
    print(f"\nRecommendation: {recommendation}")
    
    return report


if __name__ == "__main__":
    test_monitor()

