"""
小妖超级记忆系统 - 系统健康监控器（System Health Monitor）

功能：
- 系统状态监控
- 资源使用监控
- 异常检测
- 健康报告

作者：小妖🦊
创建日期：2026-04-12
"""

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import deque


class HealthMetric:
    """健康指标"""

    def __init__(self, name: str, threshold: float, severity: str = "warning"):
        """
        初始化健康指标

        Args:
            name: 指标名称
            threshold: 阈值
            severity: 严重程度（info, warning, critical）
        """
        self.name = name
        self.threshold = threshold
        self.severity = severity
        self.history = deque(maxlen=100)
        self.alerts = []

    def record(self, value: float):
        """记录值"""
        self.history.append({
            "value": value,
            "timestamp": datetime.now().isoformat()
        })

        # 检查是否超过阈值
        if value > self.threshold:
            self.alerts.append({
                "value": value,
                "threshold": self.threshold,
                "timestamp": datetime.now().isoformat()
            })


class SystemHealthMonitor:
    """
    系统健康监控器

    功能：
    - CPU使用率监控
    - 内存使用监控
    - 磁盘使用监控
    - 异常检测
    """

    def __init__(self):
        """初始化系统健康监控器"""
        self.metrics = {}
        self.lock = threading.RLock()

        # 定义监控指标
        self._init_metrics()

        self.monitoring_enabled = True
        self.check_interval = 60  # 秒
        self.last_check = None

    def _init_metrics(self):
        """初始化监控指标"""
        # CPU使用率
        self.metrics["cpu_percent"] = HealthMetric(
            "cpu_percent",
            threshold=80.0,
            severity="warning"
        )

        # 内存使用率
        self.metrics["memory_percent"] = HealthMetric(
            "memory_percent",
            threshold=85.0,
            severity="warning"
        )

        # 磁盘使用率
        self.metrics["disk_percent"] = HealthMetric(
            "disk_percent",
            threshold=90.0,
            severity="warning"
        )

        # 响应时间（秒）
        self.metrics["response_time"] = HealthMetric(
            "response_time",
            threshold=5.0,
            severity="warning"
        )

    def check_system_health(self) -> Dict[str, Any]:
        """
        检查系统健康状态

        Returns:
            健康状态字典
        """
        with self.lock:
            if not self.monitoring_enabled:
                return {"status": "disabled"}

            self.last_check = datetime.now()

            health_status = {
                "timestamp": self.last_check.isoformat(),
                "status": "healthy",
                "metrics": {},
                "alerts": []
            }

            if PSUTIL_AVAILABLE:
                # CPU使用率
                cpu_percent = psutil.cpu_percent(interval=1)
                self.metrics["cpu_percent"].record(cpu_percent)
                health_status["metrics"]["cpu_percent"] = cpu_percent

                if cpu_percent > self.metrics["cpu_percent"].threshold:
                    health_status["alerts"].append({
                        "type": "cpu",
                        "severity": self.metrics["cpu_percent"].severity,
                        "message": f"CPU使用率过高: {cpu_percent:.1f}%"
                    })

                # 内存使用率
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                self.metrics["memory_percent"].record(memory_percent)
                health_status["metrics"]["memory_percent"] = memory_percent

                if memory_percent > self.metrics["memory_percent"].threshold:
                    health_status["alerts"].append({
                        "type": "memory",
                        "severity": self.metrics["memory_percent"].severity,
                        "message": f"内存使用率过高: {memory_percent:.1f}%"
                    })

                # 磁盘使用率
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
                self.metrics["disk_percent"].record(disk_percent)
                health_status["metrics"]["disk_percent"] = disk_percent

                if disk_percent > self.metrics["disk_percent"].threshold:
                    health_status["alerts"].append({
                        "type": "disk",
                        "severity": self.metrics["disk_percent"].severity,
                        "message": f"磁盘使用率过高: {disk_percent:.1f}%"
                    })
            else:
                # psutil不可用，使用模拟数据
                for metric_name in ["cpu_percent", "memory_percent", "disk_percent"]:
                    # 模拟健康数据
                    value = 50.0
                    self.metrics[metric_name].record(value)
                    health_status["metrics"][metric_name] = value

                health_status["alerts"].append({
                    "type": "system",
                    "severity": "info",
                    "message": "psutil未安装，使用模拟数据"
                })

            # 确定总体状态
            if len(health_status["alerts"]) > 0:
                # 检查是否有critical级别的alert
                if any(a["severity"] == "critical" for a in health_status["alerts"]):
                    health_status["status"] = "critical"
                else:
                    health_status["status"] = "warning"

            return health_status

    def get_metric_history(self, metric_name: str) -> List[Dict[str, Any]]:
        """
        获取指标历史

        Args:
            metric_name: 指标名称

        Returns:
            历史记录
        """
        with self.lock:
            if metric_name not in self.metrics:
                return []

            return list(self.metrics[metric_name].history)

    def get_metric_alerts(self, metric_name: str = None) -> List[Dict[str, Any]]:
        """
        获取告警

        Args:
            metric_name: 指标名称（可选，不指定则返回所有）

        Returns:
            告警列表
        """
        with self.lock:
            if metric_name:
                if metric_name not in self.metrics:
                    return []
                return self.metrics[metric_name].alerts
            else:
                all_alerts = []
                for metric in self.metrics.values():
                    all_alerts.extend(metric.alerts)
                return all_alerts

    def get_health_report(self) -> str:
        """
        生成健康报告

        Returns:
            报告字符串
        """
        health_status = self.check_system_health()

        report = "系统健康报告\n"
        report += "=" * 60 + "\n\n"

        report += f"检查时间: {health_status['timestamp']}\n"
        report += f"系统状态: {health_status['status'].upper()}\n\n"

        report += "资源使用:\n"
        report += "-" * 60 + "\n"

        for metric_name, value in health_status["metrics"].items():
            metric = self.metrics[metric_name]
            threshold = metric.threshold

            status_icon = "✓"
            if value > threshold:
                status_icon = "⚠"

            report += f"{status_icon} {metric_name}: {value:.1f}% (阈值: {threshold:.1f}%)\n"

        # 告警
        if health_status["alerts"]:
            report += "\n告警:\n"
            report += "-" * 60 + "\n"

            for alert in health_status["alerts"]:
                severity_icon = "⚠" if alert["severity"] == "warning" else "⚠⚠"
                report += f"{severity_icon} {alert['message']}\n"

        return report

    def get_quick_status(self) -> Dict[str, Any]:
        """
        获取快速状态

        Returns:
            状态字典
        """
        health_status = self.check_system_health()

        return {
            "status": health_status["status"],
            "cpu": health_status["metrics"]["cpu_percent"],
            "memory": health_status["metrics"]["memory_percent"],
            "disk": health_status["metrics"]["disk_percent"],
            "alerts_count": len(health_status["alerts"])
        }


# 测试代码
if __name__ == "__main__":
    print("小妖超级记忆系统 - 系统健康监控器")
    print("=" * 60)

    monitor = SystemHealthMonitor()

    print("\n[OK] 系统健康监控器初始化成功")

    # 检查系统健康
    print("\n[OK] 检查系统健康:")
    health_status = monitor.check_system_health()

    print(f"  状态: {health_status['status']}")
    print(f"  CPU使用率: {health_status['metrics']['cpu_percent']:.1f}%")
    print(f"  内存使用率: {health_status['metrics']['memory_percent']:.1f}%")
    print(f"  磁盘使用率: {health_status['metrics']['disk_percent']:.1f}%")
    print(f"  告警数: {len(health_status['alerts'])}")

    if health_status['alerts']:
        print("\n  告警详情:")
        for alert in health_status['alerts']:
            print(f"    - {alert['message']}")

    # 健康报告
    print("\n[OK] 健康报告:")
    report = monitor.get_health_report()
    print(report)

    # 快速状态
    print("\n[OK] 快速状态:")
    quick_status = monitor.get_quick_status()

    print(f"  状态: {quick_status['status']}")
    print(f"  CPU: {quick_status['cpu']:.1f}%")
    print(f"  内存: {quick_status['memory']:.1f}%")
    print(f"  磁盘: {quick_status['disk']:.1f}%")
    print(f"  告警: {quick_status['alerts_count']}")

    print("\n[OK] 系统健康监控器测试通过！")
    print("\n[Xiaoyao] 系统健康监控器已就绪，可以开始监控！")
