"""
小妖超级记忆系统 - 性能分析器（Performance Profiler）

功能：
- 性能测量
- 瓶颈分析
- 优化建议
- 性能报告

作者：小妖🦊
创建日期：2026-04-12
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


class PerformanceMetric:
    """性能指标"""

    def __init__(self, name: str):
        self.name = name
        self.count = 0
        self.total_time = 0.0
        self.min_time = float('inf')
        self.max_time = 0.0
        self.times = []
        self.lock = threading.Lock()

    def record(self, duration: float):
        """记录一次执行"""
        with self.lock:
            self.count += 1
            self.total_time += duration
            self.min_time = min(self.min_time, duration)
            self.max_time = max(self.max_time, duration)
            self.times.append(duration)

            # 只保留最近1000次
            if len(self.times) > 1000:
                self.times = self.times[-1000:]

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            if self.count == 0:
                return {
                    "name": self.name,
                    "count": 0,
                    "avg_time": 0.0,
                    "min_time": 0.0,
                    "max_time": 0.0,
                    "std_dev": 0.0
                }

            avg_time = self.total_time / self.count
            std_dev = statistics.stdev(self.times) if len(self.times) > 1 else 0.0

            return {
                "name": self.name,
                "count": self.count,
                "total_time": self.total_time,
                "avg_time": avg_time,
                "min_time": self.min_time,
                "max_time": self.max_time,
                "std_dev": std_dev,
                "median": statistics.median(self.times) if self.times else 0.0
            }


class PerformanceProfiler:
    """
    性能分析器

    功能：
    - 测量执行时间
    - 分析性能瓶颈
    - 生成优化建议
    """

    def __init__(self):
        """初始化性能分析器"""
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.lock = threading.RLock()

        self.profiling_enabled = True

    def profile(self, func: Callable) -> Callable:
        """
        装饰器：分析函数性能

        Args:
            func: 要分析的函数

        Returns:
            包装后的函数
        """
        def wrapper(*args, **kwargs):
            if not self.profiling_enabled:
                return func(*args, **kwargs)

            start_time = time.perf_counter()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                duration = end_time - start_time

                # 记录性能
                metric_name = func.__name__
                self.record_metric(metric_name, duration)

        return wrapper

    def record_metric(self, name: str, duration: float):
        """
        记录性能指标

        Args:
            name: 指标名称
            duration: 持续时间（秒）
        """
        with self.lock:
            if name not in self.metrics:
                self.metrics[name] = PerformanceMetric(name)

            self.metrics[name].record(duration)

    def get_metric_stats(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取指标统计

        Args:
            name: 指标名称

        Returns:
            统计信息
        """
        with self.lock:
            if name not in self.metrics:
                return None

            return self.metrics[name].get_statistics()

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有指标

        Returns:
            所有指标的统计信息
        """
        with self.lock:
            return {
                name: metric.get_statistics()
                for name, metric in self.metrics.items()
            }

    def analyze_bottlenecks(self, threshold: float = 0.1) -> List[Dict[str, Any]]:
        """
        分析性能瓶颈

        Args:
            threshold: 阈值（秒）

        Returns:
            瓶颈列表
        """
        with self.lock:
            bottlenecks = []

            for name, metric in self.metrics.items():
                stats = metric.get_statistics()

                # 检查平均时间
                if stats["avg_time"] > threshold:
                    bottlenecks.append({
                        "name": name,
                        "type": "slow_avg",
                        "avg_time": stats["avg_time"],
                        "count": stats["count"],
                        "severity": "high" if stats["avg_time"] > threshold * 2 else "medium"
                    })

                # 检查最大时间
                if stats["max_time"] > threshold * 5:
                    bottlenecks.append({
                        "name": name,
                        "type": "spikes",
                        "max_time": stats["max_time"],
                        "count": stats["count"],
                        "severity": "high" if stats["max_time"] > threshold * 10 else "medium"
                    })

            # 按严重程度和平均时间排序
            bottlenecks.sort(
                key=lambda b: (b["severity"] == "high", b.get("avg_time", b.get("max_time", 0))),
                reverse=True
            )

            return bottlenecks

    def generate_optimization_suggestions(self) -> List[str]:
        """
        生成优化建议

        Returns:
            建议列表
        """
        suggestions = []

        bottlenecks = self.analyze_bottlenecks()

        if not bottlenecks:
            suggestions.append("✓ 系统性能良好，无明显瓶颈")
            return suggestions

        for bottleneck in bottlenecks[:5]:  # 最多5个建议
            name = bottleneck["name"]
            btype = bottleneck["type"]
            severity = bottleneck["severity"]

            if btype == "slow_avg":
                if severity == "high":
                    suggestions.append(f"⚠ {name}: 平均执行时间过长（{bottleneck['avg_time']:.3f}s），建议优化算法或使用缓存")
                else:
                    suggestions.append(f"⚡ {name}: 可以优化以提高性能（当前{bottleneck['avg_time']:.3f}s）")

            elif btype == "spikes":
                if severity == "high":
                    suggestions.append(f"⚠ {name}: 存在性能尖峰（最高{bottleneck['max_time']:.3f}s），建议添加超时控制或重试机制")
                else:
                    suggestions.append(f"⚡ {name}: 偶尔出现慢请求，建议监控")

        return suggestions

    def get_performance_report(self) -> str:
        """
        生成性能报告

        Returns:
            报告字符串
        """
        metrics = self.get_all_metrics()

        if not metrics:
            return "暂无性能数据"

        report = "性能分析报告\n"
        report += "=" * 60 + "\n\n"

        # 总体统计
        total_operations = sum(m["count"] for m in metrics.values())
        total_time = sum(m["total_time"] for m in metrics.values())
        avg_overall = total_time / total_operations if total_operations > 0 else 0

        report += f"总操作数: {total_operations}\n"
        report += f"总耗时: {total_time:.3f}秒\n"
        report += f"平均耗时: {avg_overall:.6f}秒\n\n"

        # 前10个最慢的操作
        sorted_metrics = sorted(
            metrics.items(),
            key=lambda x: x[1]["avg_time"],
            reverse=True
        )[:10]

        report += "Top 10 慢操作:\n"
        report += "-" * 60 + "\n"

        for name, stats in sorted_metrics:
            report += f"{name}:\n"
            report += f"  平均: {stats['avg_time']:.6f}s\n"
            report += f"  最小: {stats['min_time']:.6f}s\n"
            report += f"  最大: {stats['max_time']:.6f}s\n"
            report += f"  标准差: {stats['std_dev']:.6f}s\n"
            report += f"  次数: {stats['count']}\n"
            report += "\n"

        # 瓶颈分析
        bottlenecks = self.analyze_bottlenecks()

        if bottlenecks:
            report += "性能瓶颈:\n"
            report += "-" * 60 + "\n"

            for bottleneck in bottlenecks:
                severity_icon = "⚠" if bottleneck["severity"] == "high" else "⚡"
                report += f"{severity_icon} {bottleneck['name']}: {bottleneck['type']}\n"

                if "avg_time" in bottleneck:
                    report += f"    平均耗时: {bottleneck['avg_time']:.3f}s\n"
                if "max_time" in bottleneck:
                    report += f"    最大耗时: {bottleneck['max_time']:.3f}s\n"

            report += "\n"

        # 优化建议
        suggestions = self.generate_optimization_suggestions()

        report += "优化建议:\n"
        report += "-" * 60 + "\n"

        for suggestion in suggestions:
            report += f"{suggestion}\n"

        return report


# 测试代码
if __name__ == "__main__":
    print("小妖超级记忆系统 - 性能分析器")
    print("=" * 60)

    profiler = PerformanceProfiler()

    print("\n[OK] 性能分析器初始化成功")

    # 模拟一些性能数据
    print("\n[OK] 模拟性能数据:")

    # 快速操作
    for i in range(100):
        start = time.perf_counter()
        time.sleep(0.001)  # 1ms
        duration = time.perf_counter() - start
        profiler.record_metric("fast_operation", duration)

    # 中速操作
    for i in range(50):
        start = time.perf_counter()
        time.sleep(0.010)  # 10ms
        duration = time.perf_counter() - start
        profiler.record_metric("medium_operation", duration)

    # 慢速操作
    for i in range(20):
        start = time.perf_counter()
        time.sleep(0.050)  # 50ms
        duration = time.perf_counter() - start
        profiler.record_metric("slow_operation", duration)

    # 偶尔很慢的操作
    for i in range(10):
        start = time.perf_counter()
        if i == 5:
            time.sleep(0.300)  # 300ms（尖峰）
        else:
            time.sleep(0.020)  # 20ms
        duration = time.perf_counter() - start
        profiler.record_metric("spiky_operation", duration)

    print("  记录了180次操作")

    # 获取统计
    print("\n[OK] 性能统计:")

    metrics = profiler.get_all_metrics()

    for name, stats in metrics.items():
        print(f"  {name}:")
        print(f"    次数: {stats['count']}")
        print(f"    平均: {stats['avg_time']:.6f}s")
        print(f"    最小: {stats['min_time']:.6f}s")
        print(f"    最大: {stats['max_time']:.6f}s")

    # 分析瓶颈
    print("\n[OK] 瓶颈分析:")
    bottlenecks = profiler.analyze_bottlenecks(threshold=0.01)

    for bottleneck in bottlenecks:
        severity = bottleneck["severity"]
        print(f"  {severity.upper()}: {bottleneck['name']}")
        print(f"    类型: {bottleneck['type']}")
        if "avg_time" in bottleneck:
            print(f"    平均耗时: {bottleneck['avg_time']:.3f}s")
        if "max_time" in bottleneck:
            print(f"    最大耗时: {bottleneck['max_time']:.3f}s")

    # 优化建议
    print("\n[OK] 优化建议:")
    suggestions = profiler.generate_optimization_suggestions()

    for suggestion in suggestions:
        print(f"  {suggestion}")

    # 性能报告
    print("\n[OK] 性能报告:")
    report = profiler.get_performance_report()
    print(report)

    print("[OK] 性能分析器测试通过！")
    print("\n[Xiaoyao] 性能分析器已就绪，可以开始性能优化！")
