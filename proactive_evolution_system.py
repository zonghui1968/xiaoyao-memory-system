"""
主动进化系统

定期自我进化、性能监控和自动优化
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Optional

# 添加路径
sys.path.insert(0, str(Path(r"C:\ssh\.openclaw\xiaoyao-memory-system")))

from production_memory_system import get_production_memory_system
from automation_system import get_auto_monitoring_system


class PerformanceMonitor:
    """
    性能监控器

    监控系统各项性能指标
    """

    def __init__(self):
        """初始化监控器"""
        self.pms = get_production_memory_system()
        self.metrics = {
            'retrieval_accuracy': [],
            'latency': [],
            'memory_growth': [],
            'query_throughput': [],
            'storage_throughput': [],
            'evolution_effectiveness': []
        }

    def record_retrieval_accuracy(self, accuracy: float):
        """记录检索准确性"""
        self.metrics['retrieval_accuracy'].append({
            'value': accuracy,
            'timestamp': datetime.now().isoformat()
        })

    def record_latency(self, latency_ms: float):
        """记录延迟"""
        self.metrics['latency'].append({
            'value': latency_ms,
            'timestamp': datetime.now().isoformat()
        })

    def record_memory_growth(self, count: int):
        """记录记忆增长"""
        self.metrics['memory_growth'].append({
            'value': count,
            'timestamp': datetime.now().isoformat()
        })

    def record_query_throughput(self, queries_per_second: float):
        """记录查询吞吐量"""
        self.metrics['query_throughput'].append({
            'value': queries_per_second,
            'timestamp': datetime.now().isoformat()
        })

    def record_evolution_effectiveness(self, improvement_score: float):
        """记录进化效果"""
        self.metrics['evolution_effectiveness'].append({
            'value': improvement_score,
            'timestamp': datetime.now().isoformat()
        })

    def get_average_metrics(self) -> Dict[str, float]:
        """获取平均指标"""
        averages = {}

        for metric_name, measurements in self.metrics.items():
            if measurements:
                values = [m['value'] for m in measurements[-10:]]  # 最近10次
                averages[metric_name] = sum(values) / len(values)
            else:
                averages[metric_name] = 0.0

        return averages

    def get_trend(self, metric_name: str) -> str:
        """获取指标趋势"""
        if metric_name not in self.metrics or len(self.metrics[metric_name]) < 2:
            return "unknown"

        recent = self.metrics[metric_name][-5:]
        if len(recent) < 2:
            return "stable"

        values = [m['value'] for m in recent]
        first_avg = sum(values[:2]) / 2
        last_avg = sum(values[-2:]) / 2

        if last_avg > first_avg * 1.1:
            return "improving" if metric_name != 'latency' else "degrading"
        elif last_avg < first_avg * 0.9:
            return "degrading" if metric_name != 'latency' else "improving"
        else:
            return "stable"


class AutoOptimizer:
    """
    自动优化器

    基于性能数据自动优化系统
    """

    def __init__(self):
        """初始化优化器"""
        self.pms = get_production_memory_system()
        self.monitor = PerformanceMonitor()

        self.optimization_history = []

    def generate_performance_feedback(self) -> Dict[str, float]:
        """生成性能反馈"""
        averages = self.monitor.get_average_metrics()

        return {
            'retrieval_accuracy': averages.get('retrieval_accuracy', 0.85),
            'latency': averages.get('latency', 500),
            'memory_growth': averages.get('memory_growth', 1000)
        }

    def should_evolve(self) -> Tuple[bool, str]:
        """
        判断是否需要进化

        Returns:
            (是否需要进化, 原因)
        """
        averages = self.monitor.get_average_metrics()

        # 检查检索准确性
        if averages.get('retrieval_accuracy', 1.0) < 0.8:
            return True, "检索准确性低于80%"

        # 检查延迟
        if averages.get('latency', 0) > 1000:
            return True, "延迟超过1000ms"

        # 检查记忆增长
        if averages.get('memory_growth', 0) > 10000:
            return True, "记忆数量超过10,000"

        # 检查趋势
        for metric_name in ['retrieval_accuracy', 'latency']:
            trend = self.monitor.get_trend(metric_name)
            if trend == "degrading":
                return True, f"{metric_name}呈下降趋势"

        return False, "系统运行良好"

    def auto_evolve(self) -> Dict[str, any]:
        """
        自动进化

        Returns:
            进化报告
        """
        should_evolve, reason = self.should_evolve()

        if not should_evolve:
            return {
                'evolved': False,
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            }

        print(f"[AutoOptimizer] 触发进化: {reason}")

        # 生成性能反馈
        feedback = self.generate_performance_feedback()

        # 执行进化
        evolution_report = self.pms.evolve(feedback)

        # 记录进化历史
        self.optimization_history.append({
            'timestamp': datetime.now().isoformat(),
            'reason': reason,
            'feedback': feedback,
            'changes': evolution_report['changes']
        })

        return {
            'evolved': True,
            'reason': reason,
            'feedback': feedback,
            'changes': evolution_report['changes'],
            'timestamp': datetime.now().isoformat()
        }


class ScheduledEvolutionSystem:
    """
    定期进化系统

    定时触发自我进化和性能监控
    """

    def __init__(self):
        """初始化系统"""
        self.pms = get_production_memory_system()
        self.auto_monitor = get_auto_monitoring_system()
        self.optimizer = AutoOptimizer()

        self.evolution_schedule = {
            'hourly': False,
            'daily': True,
            'weekly': False
        }

        self.last_evolution = None
        self.evolution_count = 0

    def check_and_evolve(self, force: bool = False) -> Dict[str, any]:
        """
        检查并执行进化

        Args:
            force: 强制进化

        Returns:
            进化报告
        """
        print(f"[ScheduledEvolution] 检查进化条件...")

        # 更新性能指标
        self._update_performance_metrics()

        # 执行进化
        if force:
            print(f"[ScheduledEvolution] 强制进化")
            result = self.optimizer.auto_evolve()
        else:
            should_evolve, reason = self.optimizer.should_evolve()
            if should_evolve:
                print(f"[ScheduledEvolution] 需要进化: {reason}")
                result = self.optimizer.auto_evolve()
            else:
                result = {
                    'evolved': False,
                    'reason': reason,
                    'timestamp': datetime.now().isoformat()
                }

        # 更新进化计数
        if result.get('evolved', False):
            self.evolution_count += 1
            self.last_evolution = datetime.now()

        return result

    def _update_performance_metrics(self):
        """更新性能指标"""
        # 获取系统状态
        status = self.pms.get_status()

        # 记录记忆增长
        memory_count = status['memory_count']
        self.optimizer.monitor.record_memory_growth(memory_count)

        # 模拟性能测量（实际应该从真实查询中获取）
        import random
        accuracy = random.uniform(0.75, 0.95)
        latency = random.uniform(200, 800)

        self.optimizer.monitor.record_retrieval_accuracy(accuracy)
        self.optimizer.monitor.record_latency(latency)

    def generate_performance_report(self) -> Dict[str, any]:
        """生成性能报告"""
        averages = self.optimizer.monitor.get_average_metrics()

        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': averages,
            'trends': {
                metric: self.optimizer.monitor.get_trend(metric)
                for metric in ['retrieval_accuracy', 'latency', 'memory_growth']
            },
            'evolution_count': self.evolution_count,
            'last_evolution': self.last_evolution.isoformat() if self.last_evolution else None,
            'monitoring_stats': self.auto_monitor.get_stats()
        }


class ProactiveEvolutionSystem:
    """
    主动进化系统

    整合定期进化、性能监控和自动优化
    """

    def __init__(self):
        """初始化系统"""
        self.scheduled_evolution = ScheduledEvolutionSystem()
        self.state_file = Path(r"C:\ssh\.openclaw\workspace\proactive_evolution_state.json")

        # 加载状态
        self._load_state()

    def _load_state(self):
        """加载系统状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                self.scheduled_evolution.evolution_count = state.get('evolution_count', 0)

                if state.get('last_evolution'):
                    self.scheduled_evolution.last_evolution = datetime.fromisoformat(
                        state['last_evolution']
                    )

    def _save_state(self):
        """保存系统状态"""
        state = {
            'evolution_count': self.scheduled_evolution.evolution_count,
            'last_evolution': self.scheduled_evolution.last_evolution.isoformat()
                        if self.scheduled_evolution.last_evolution else None,
            'timestamp': datetime.now().isoformat()
        }

        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def run_evolution_cycle(self, force: bool = False) -> Dict[str, any]:
        """
        运行进化周期

        Args:
            force: 强制进化

        Returns:
            进化报告
        """
        print("\n" + "="*70)
        print("主动进化周期")
        print("="*70)

        # 1. 检查并执行进化
        evolution_result = self.scheduled_evolution.check_and_evolve(force=force)

        # 2. 生成性能报告
        performance_report = self.scheduled_evolution.generate_performance_report()

        # 3. 保存状态
        if evolution_result.get('evolved', False):
            self._save_state()

        # 4. 组合报告
        full_report = {
            'evolution': evolution_result,
            'performance': performance_report,
            'timestamp': datetime.now().isoformat()
        }

        return full_report

    def get_system_status(self) -> Dict[str, any]:
        """获取系统状态"""
        return self.scheduled_evolution.generate_performance_report()


# 全局单例
_proactive_evolution_system = None


def get_proactive_evolution_system() -> ProactiveEvolutionSystem:
    """获取主动进化系统单例"""
    global _proactive_evolution_system

    if _proactive_evolution_system is None:
        print("[主动进化系统] 初始化...")
        _proactive_evolution_system = ProactiveEvolutionSystem()
        print("[OK] 主动进化系统已启动")

    return _proactive_evolution_system


# 便捷函数
def run_evolution_cycle(force: bool = False) -> Dict[str, any]:
    """运行进化周期"""
    return get_proactive_evolution_system().run_evolution_cycle(force=force)


def get_evolution_system_status() -> Dict[str, any]:
    """获取进化系统状态"""
    return get_proactive_evolution_system().get_system_status()


# 测试
if __name__ == "__main__":
    print("="*70)
    print("主动进化系统测试")
    print("="*70)

    # 初始化
    proactive_system = get_proactive_evolution_system()

    # 测试1: 正常进化周期
    print("\n[测试1] 正常进化周期")
    report = proactive_system.run_evolution_cycle()

    print(f"\n进化结果: {'已进化' if report['evolution']['evolved'] else '无需进化'}")
    if report['evolution'].get('reason'):
        print(f"原因: {report['evolution']['reason']}")

    # 测试2: 强制进化
    print("\n[测试2] 强制进化")
    report = proactive_system.run_evolution_cycle(force=True)

    print(f"\n进化结果: {'已进化' if report['evolution']['evolved'] else '无需进化'}")
    if report['evolution']['evolved']:
        print(f"变更数: {len(report['evolution']['changes'])}")
        for change in report['evolution']['changes']:
            print(f"  - {change['type']}: {change['reason']}")

    # 测试3: 系统状态
    print("\n[测试3] 系统状态")
    status = proactive_system.get_system_status()

    print(f"进化次数: {status['evolution_count']}")
    print(f"上次进化: {status['last_evolution']}")
    print(f"\n性能指标:")
    for metric, value in status['metrics'].items():
        print(f"  {metric}: {value:.2f}")

    print(f"\n趋势:")
    for metric, trend in status['trends'].items():
        print(f"  {metric}: {trend}")

    print("\n" + "="*70)
    print("主动进化系统测试完成！")
    print("="*70)
