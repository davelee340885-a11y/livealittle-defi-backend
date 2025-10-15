"""
數據質量監控和異常檢測系統
"""

import time
import json
from typing import Dict, List, Optional
from collections import deque
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PriceHistory:
    """價格歷史記錄"""
    def __init__(self, max_size: int = 100):
        self.history = deque(maxlen=max_size)
    
    def add(self, price: float, timestamp: int):
        """添加價格記錄"""
        self.history.append({"price": price, "timestamp": timestamp})
    
    def get_recent(self, seconds: int = 60) -> List[Dict]:
        """獲取最近 N 秒的價格記錄"""
        current_time = int(time.time())
        cutoff_time = current_time - seconds
        return [h for h in self.history if h["timestamp"] >= cutoff_time]
    
    def get_last_price(self) -> Optional[float]:
        """獲取最後一個價格"""
        if self.history:
            return self.history[-1]["price"]
        return None


class AnomalyDetector:
    """異常檢測器"""
    def __init__(self):
        self.price_histories = {}  # token -> PriceHistory
        self.alerts = []
    
    def _get_history(self, token: str) -> PriceHistory:
        """獲取或創建價格歷史"""
        if token not in self.price_histories:
            self.price_histories[token] = PriceHistory()
        return self.price_histories[token]
    
    def check_price_volatility(self, token: str, new_price: float, threshold: float = 0.10) -> Optional[Dict]:
        """檢查價格劇烈波動（超過閾值百分比）"""
        history = self._get_history(token)
        last_price = history.get_last_price()
        
        if last_price is None:
            # 第一次記錄，不檢查
            history.add(new_price, int(time.time()))
            return None
        
        # 計算變化百分比
        change_percent = abs(new_price - last_price) / last_price
        
        if change_percent > threshold:
            alert = {
                "type": "high_volatility",
                "token": token,
                "old_price": last_price,
                "new_price": new_price,
                "change_percent": change_percent * 100,
                "threshold_percent": threshold * 100,
                "timestamp": int(time.time()),
                "severity": "warning" if change_percent < 0.20 else "critical"
            }
            
            self.alerts.append(alert)
            logger.warning(
                f"⚠️  High volatility detected for {token}: "
                f"{change_percent*100:.2f}% change "
                f"(${last_price:.2f} → ${new_price:.2f})"
            )
            
            history.add(new_price, int(time.time()))
            return alert
        
        history.add(new_price, int(time.time()))
        return None
    
    def check_data_source_divergence(
        self, 
        token: str, 
        datapoints: List, 
        consensus_price: float, 
        threshold: float = 0.05
    ) -> Optional[Dict]:
        """檢查數據源分歧"""
        divergent_sources = []
        
        for dp in datapoints:
            if not dp.is_valid:
                continue
            
            deviation = abs(dp.price - consensus_price) / consensus_price
            
            if deviation > threshold:
                divergent_sources.append({
                    "source": dp.source,
                    "price": dp.price,
                    "deviation_percent": deviation * 100
                })
        
        # 如果超過 1/3 的數據源分歧
        if len(divergent_sources) >= len(datapoints) / 3:
            alert = {
                "type": "data_divergence",
                "token": token,
                "consensus_price": consensus_price,
                "divergent_sources": divergent_sources,
                "timestamp": int(time.time()),
                "severity": "warning"
            }
            
            self.alerts.append(alert)
            logger.warning(
                f"⚠️  Data divergence detected for {token}: "
                f"{len(divergent_sources)} sources deviate from consensus"
            )
            
            return alert
        
        return None
    
    def check_source_delay(self, sources: List, max_delay: int = 120) -> List[Dict]:
        """檢查數據源延遲"""
        current_time = int(time.time())
        delayed_sources = []
        
        for source in sources:
            if source.last_update == 0:
                continue  # 從未更新過，跳過
            
            delay = current_time - source.last_update
            
            if delay > max_delay:
                alert = {
                    "type": "source_delay",
                    "source": source.name,
                    "delay_seconds": delay,
                    "max_delay_seconds": max_delay,
                    "timestamp": current_time,
                    "severity": "warning" if delay < 300 else "critical"
                }
                
                delayed_sources.append(alert)
                self.alerts.append(alert)
                logger.warning(
                    f"⚠️  Source delay detected: {source.name} "
                    f"({delay}s since last update)"
                )
        
        return delayed_sources
    
    def check_system_failure(self, sources: List) -> Optional[Dict]:
        """檢查系統性故障（超過 2/3 數據源失效）"""
        unavailable_count = sum(1 for s in sources if not s.is_available)
        total_count = len(sources)
        
        if unavailable_count >= (total_count * 2 / 3):
            alert = {
                "type": "system_failure",
                "unavailable_sources": unavailable_count,
                "total_sources": total_count,
                "timestamp": int(time.time()),
                "severity": "critical"
            }
            
            self.alerts.append(alert)
            logger.error(
                f"🚨 CRITICAL: System failure detected! "
                f"{unavailable_count}/{total_count} sources unavailable"
            )
            
            return alert
        
        return None
    
    def get_recent_alerts(self, seconds: int = 300) -> List[Dict]:
        """獲取最近的警報"""
        current_time = int(time.time())
        cutoff_time = current_time - seconds
        return [a for a in self.alerts if a["timestamp"] >= cutoff_time]
    
    def clear_old_alerts(self, max_age: int = 3600):
        """清理舊警報"""
        current_time = int(time.time())
        cutoff_time = current_time - max_age
        self.alerts = [a for a in self.alerts if a["timestamp"] >= cutoff_time]


class DataQualityCalculator:
    """數據質量計算器"""
    @staticmethod
    def calculate_freshness(timestamp: int) -> float:
        """計算數據新鮮度 (0-1)"""
        current_time = int(time.time())
        age = current_time - timestamp
        
        # 60 秒內為 1.0，之後線性衰減
        if age <= 60:
            return 1.0
        elif age <= 300:  # 5 分鐘內
            return max(0, 1.0 - (age - 60) / 240)
        else:
            return 0.0
    
    @staticmethod
    def calculate_source_availability(available: int, total: int) -> float:
        """計算數據源可用性 (0-1)"""
        if total == 0:
            return 0.0
        return available / total
    
    @staticmethod
    def calculate_consistency(std_dev: float, price: float) -> float:
        """計算數據一致性 (0-1)"""
        if price == 0:
            return 0.0
        
        # 標準差越小，一致性越高
        coefficient_of_variation = std_dev / price
        
        # 轉換為 0-1 分數（CV < 0.01 為滿分）
        consistency = max(0, 1.0 - (coefficient_of_variation / 0.01))
        return min(1.0, consistency)
    
    @staticmethod
    def calculate_overall_quality(freshness: float, availability: float, consistency: float) -> float:
        """計算總體數據質量 (0-1)"""
        # 加權平均
        weights = {
            "freshness": 0.4,
            "availability": 0.3,
            "consistency": 0.3
        }
        
        overall = (
            freshness * weights["freshness"] +
            availability * weights["availability"] +
            consistency * weights["consistency"]
        )
        
        return overall


class DataQualityMonitor:
    """數據質量監控器"""
    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.quality_calculator = DataQualityCalculator()
    
    def monitor_consensus(
        self, 
        token: str, 
        consensus: Dict, 
        datapoints: List,
        sources: List
    ) -> Dict:
        """監控共識數據質量"""
        # 異常檢測
        volatility_alert = self.anomaly_detector.check_price_volatility(
            token, consensus["price"]
        )
        
        divergence_alert = self.anomaly_detector.check_data_source_divergence(
            token, datapoints, consensus["price"]
        )
        
        delay_alerts = self.anomaly_detector.check_source_delay(sources)
        
        system_failure_alert = self.anomaly_detector.check_system_failure(sources)
        
        # 計算質量指標
        freshness = self.quality_calculator.calculate_freshness(consensus["timestamp"])
        
        available_sources = sum(1 for s in sources if s.is_available)
        availability = self.quality_calculator.calculate_source_availability(
            available_sources, len(sources)
        )
        
        consistency = self.quality_calculator.calculate_consistency(
            consensus["std_dev"], consensus["price"]
        )
        
        overall_quality = self.quality_calculator.calculate_overall_quality(
            freshness, availability, consistency
        )
        
        # 組裝監控報告
        report = {
            "token": token,
            "consensus_price": consensus["price"],
            "quality_metrics": {
                "freshness": round(freshness, 3),
                "availability": round(availability, 3),
                "consistency": round(consistency, 3),
                "overall_quality": round(overall_quality, 3)
            },
            "alerts": {
                "volatility": volatility_alert,
                "divergence": divergence_alert,
                "delays": delay_alerts,
                "system_failure": system_failure_alert
            },
            "data_sources": {
                "total": len(sources),
                "available": available_sources,
                "data_points": consensus["data_points"]
            },
            "timestamp": int(time.time())
        }
        
        return report
    
    def get_status_summary(self) -> Dict:
        """獲取狀態摘要"""
        recent_alerts = self.anomaly_detector.get_recent_alerts(seconds=300)
        
        critical_alerts = [a for a in recent_alerts if a.get("severity") == "critical"]
        warning_alerts = [a for a in recent_alerts if a.get("severity") == "warning"]
        
        return {
            "status": "critical" if critical_alerts else ("warning" if warning_alerts else "healthy"),
            "total_alerts": len(recent_alerts),
            "critical_alerts": len(critical_alerts),
            "warning_alerts": len(warning_alerts),
            "timestamp": int(time.time())
        }
    
    def save_report(self, report: Dict, filename: str = "data_quality_report.json"):
        """保存報告到文件"""
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Quality report saved to {filename}")


# 測試函數
def test_monitor():
    """測試監控系統"""
    monitor = DataQualityMonitor()
    
    # 模擬共識數據
    consensus = {
        "price": 3500.00,
        "std_dev": 2.5,
        "data_points": 3,
        "timestamp": int(time.time())
    }
    
    # 模擬數據點
    class MockDataPoint:
        def __init__(self, source, price, is_valid=True):
            self.source = source
            self.price = price
            self.is_valid = is_valid
    
    datapoints = [
        MockDataPoint("coingecko", 3501.0),
        MockDataPoint("defillama", 3499.5),
        MockDataPoint("binance", 3500.5)
    ]
    
    # 模擬數據源
    class MockSource:
        def __init__(self, name, is_available=True, last_update=None):
            self.name = name
            self.is_available = is_available
            self.last_update = last_update or int(time.time())
    
    sources = [
        MockSource("coingecko"),
        MockSource("defillama"),
        MockSource("binance")
    ]
    
    # 監控
    report = monitor.monitor_consensus("ETH", consensus, datapoints, sources)
    
    print("\n" + "="*60)
    print("DATA QUALITY MONITORING REPORT")
    print("="*60)
    print(f"Token: {report['token']}")
    print(f"Consensus Price: ${report['consensus_price']:.2f}")
    print(f"\nQuality Metrics:")
    for metric, value in report['quality_metrics'].items():
        print(f"  {metric.capitalize()}: {value:.3f}")
    
    print(f"\nData Sources: {report['data_sources']['available']}/{report['data_sources']['total']} available")
    
    status = monitor.get_status_summary()
    print(f"\nSystem Status: {status['status'].upper()}")
    print(f"Total Alerts: {status['total_alerts']}")
    
    return report


if __name__ == "__main__":
    test_monitor()

