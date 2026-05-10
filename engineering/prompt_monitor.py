"""
工程化工具 —— Prompt 生产监控

监控指标：
- 总调用次数
- 成功率
- 平均延迟
- 平均Token消耗
- 格式合规率
- 用户满意度
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class PromptMonitor:
    """Prompt 生产监控"""

    def __init__(self):
        self.metrics = {
            "total_calls": 0,
            "success_count": 0,
            "fail_count": 0,
            "success_rate": 0.0,
            "total_latency": 0.0,
            "avg_latency": 0.0,
            "total_tokens": 0,
            "avg_tokens": 0,
            "format_compliance_rate": 0.0,
            "user_satisfaction": 0.0,
        }

    def record_call(self, result: dict):
        """记录一次调用"""
        self.metrics["total_calls"] += 1

        if result.get("success", True):
            self.metrics["success_count"] += 1
        else:
            self.metrics["fail_count"] += 1

        latency = result.get("latency", 0)
        self.metrics["total_latency"] += latency

        tokens = result.get("tokens", 0)
        self.metrics["total_tokens"] += tokens

        total = self.metrics["total_calls"]
        if total > 0:
            self.metrics["success_rate"] = self.metrics["success_count"] / total
            self.metrics["avg_latency"] = self.metrics["total_latency"] / total
            self.metrics["avg_tokens"] = self.metrics["total_tokens"] / total

    def alert_if_degraded(self):
        """指标劣化告警"""
        alerts = []
        if self.metrics["total_calls"] > 10 and self.metrics["success_rate"] < 0.95:
            alerts.append(f"[告警] Prompt成功率低于95%！当前: {self.metrics['success_rate']:.1%}")
        if self.metrics["avg_latency"] > 3.0:
            alerts.append(f"[告警] Prompt平均延迟超过3秒！当前: {self.metrics['avg_latency']:.2f}s")
        if self.metrics["avg_tokens"] > 2000:
            alerts.append(f"[告警] 平均Token消耗超过2000！当前: {self.metrics['avg_tokens']:.0f}")
        return alerts

    def get_summary(self) -> dict:
        """获取监控摘要"""
        return dict(self.metrics)


if __name__ == "__main__":
    monitor = PromptMonitor()

    # 模拟一些调用记录
    test_results = [
        {"success": True, "latency": 1.2, "tokens": 500},
        {"success": True, "latency": 0.8, "tokens": 350},
        {"success": False, "latency": 2.5, "tokens": 100},
        {"success": True, "latency": 1.5, "tokens": 800},
        {"success": True, "latency": 0.9, "tokens": 420},
    ]

    for result in test_results:
        monitor.record_call(result)

    print("监控摘要:")
    summary = monitor.get_summary()
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")

    alerts = monitor.alert_if_degraded()
    if alerts:
        print(f"\n告警信息:")
        for alert in alerts:
            print(f"  {alert}")
    else:
        print(f"\n无告警，系统运行正常。")