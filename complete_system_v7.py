"""
SuperMemorySystemV7 完整集成系统

整合Phase 1-3的所有功能
- Phase 1: 基础集成 ✅
- Phase 2: 自动化 ✅
- Phase 3: 主动进化 ✅
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# 添加路径
sys.path.insert(0, str(Path(r"C:\ssh\.openclaw\xiaoyao-memory-system")))

from production_memory_system import get_production_memory_system
from automation_system import get_auto_monitoring_system, auto_monitor
from proactive_evolution_system import get_proactive_evolution_system, run_evolution_cycle


class SuperMemorySystemV7Complete:
    """
    SuperMemorySystemV7 完整集成系统

    融合三大Phase的所有功能：
    - Phase 1: 基础集成（工作流集成）
    - Phase 2: 自动化（自动监控和提取）
    - Phase 3: 主动进化（定期进化和优化）
    """

    def __init__(self):
        """初始化完整系统"""
        print("[完整系统] 初始化SuperMemorySystemV7...")

        # Phase 1: 生产记忆系统
        self.pms = get_production_memory_system()

        # Phase 2: 自动化系统
        self.auto_monitor = get_auto_monitoring_system()

        # Phase 3: 主动进化系统
        self.proactive_evolution = get_proactive_evolution_system()

        print("[OK] SuperMemorySystemV7完整系统已启动")

    def process_text(self, text: str) -> dict:
        """
        处理文本（自动化监控）

        Args:
            text: 输入文本

        Returns:
            处理结果
        """
        return auto_monitor(text)

    def query_memory(self, query: str, top_k: int = 5, use_reflection: bool = True) -> dict:
        """
        查询记忆

        Args:
            query: 查询文本
            top_k: 返回结果数
            use_reflection: 是否使用反射合成

        Returns:
            查询结果
        """
        return self.pms.sms_v7.recall(query, top_k=top_k, use_reflection=use_reflection)

    def remember(self, content: str, memory_type: str = "semantic") -> str:
        """
        记录记忆

        Args:
            content: 记忆内容
            memory_type: 记忆类型

        Returns:
            记忆ID
        """
        from super_memory_system_v7 import MemoryType

        memory_type_map = {
            'episodic': MemoryType.EPISODIC,
            'semantic': MemoryType.SEMANTIC,
            'procedural': MemoryType.PROCEDURAL,
            'temporal': MemoryType.TEMPORAL
        }

        mem_type = memory_type_map.get(memory_type, MemoryType.SEMANTIC)

        return self.pms.sms_v7.remember(content, memory_type=mem_type)

    def evolve(self, force: bool = False) -> dict:
        """
        触发进化

        Args:
            force: 强制进化

        Returns:
            进化报告
        """
        return run_evolution_cycle(force=force)

    def get_full_status(self) -> dict:
        """获取完整系统状态"""
        # 基础状态
        base_status = self.pms.get_status()

        # 自动化统计
        auto_stats = self.auto_monitor.get_stats()

        # 进化状态
        evolution_status = self.proactive_evolution.get_system_status()

        return {
            'system': base_status,
            'automation': auto_stats,
            'evolution': evolution_status,
            'timestamp': datetime.now().isoformat()
        }

    def generate_comprehensive_report(self) -> str:
        """生成综合报告"""
        status = self.get_full_status()

        report = []
        report.append("="*70)
        report.append("SuperMemorySystemV7 综合报告")
        report.append("="*70)

        # 系统信息
        report.append("\n[系统信息]")
        report.append(f"版本: {status['system']['version']}")
        report.append(f"记忆总数: {status['system']['memory_count']}")
        report.append(f"时序事实: {status['system']['temporal_facts']}")

        # 自动化统计
        report.append("\n[自动化统计]")
        report.append(f"任务记录: {status['automation']['tasks_recorded']}")
        report.append(f"决策提取: {status['automation']['decisions_extracted']}")
        report.append(f"学习归档: {status['automation']['learning_archived']}")

        # 进化状态
        report.append("\n[进化状态]")
        report.append(f"进化次数: {status['evolution']['evolution_count']}")
        report.append(f"上次进化: {status['evolution']['last_evolution']}")

        # 性能指标
        if 'metrics' in status['evolution']:
            report.append("\n[性能指标]")
            for metric, value in status['evolution']['metrics'].items():
                if value > 0:
                    report.append(f"  {metric}: {value:.2f}")

        # 趋势
        if 'trends' in status['evolution']:
            report.append("\n[系统趋势]")
            for metric, trend in status['evolution']['trends'].items():
                if trend != "unknown":
                    report.append(f"  {metric}: {trend}")

        report.append("\n" + "="*70)
        report.append("SuperMemorySystemV7 - 下一代AI代理记忆系统")
        report.append("="*70)

        return "\n".join(report)


# 全局单例
_complete_system = None


def get_complete_system() -> SuperMemorySystemV7Complete:
    """获取完整系统单例"""
    global _complete_system

    if _complete_system is None:
        _complete_system = SuperMemorySystemV7Complete()

    return _complete_system


# 便捷函数
def smart_process(text: str) -> dict:
    """智能处理文本（自动监控+记忆）"""
    return get_complete_system().process_text(text)


def smart_query(query: str, top_k: int = 5) -> dict:
    """智能查询记忆"""
    return get_complete_system().query_memory(query, top_k=top_k)


def smart_remember(content: str, memory_type: str = "semantic") -> str:
    """智能记录记忆"""
    return get_complete_system().remember(content, memory_type)


def smart_evolve(force: bool = False) -> dict:
    """智能触发进化"""
    return get_complete_system().evolve(force=force)


def get_system_report() -> str:
    """获取系统报告"""
    return get_complete_system().generate_comprehensive_report()


# 主测试
if __name__ == "__main__":
    print("="*70)
    print("SuperMemorySystemV7 完整集成系统测试")
    print("="*70)

    # 初始化
    complete_system = get_complete_system()

    # 测试1: 智能处理
    print("\n[测试1] 智能处理文本")
    test_texts = [
        "我开始测试完整系统",
        "经过测试，我发现所有功能都正常工作",
        "我决定立即部署到生产环境",
    ]

    for text in test_texts:
        print(f"\n输入: {text}")
        result = complete_system.process_text(text)
        if any(result.values()):
            print("自动检测:")
            if result['tasks']:
                print(f"  - 任务: {len(result['tasks'])}条")
            if result['decisions']:
                print(f"  - 决策: {len(result['decisions'])}条")
            if result['learning']:
                print(f"  - 学习: {len(result['learning'])}条")

    # 测试2: 智能查询
    print("\n[测试2] 智能查询记忆")
    query_result = complete_system.query_memory("系统测试的结果如何？")

    print(f"找到 {len(query_result['memories'])} 条相关记忆")
    if query_result['synthesis']:
        print(f"\n合成分析:")
        print(query_result['synthesis'])

    # 测试3: 智能记录
    print("\n[测试3] 智能记录记忆")
    memory_id = complete_system.remember(
        "SuperMemorySystemV7完整集成测试成功",
        memory_type="episodic"
    )
    print(f"记录ID: {memory_id}")

    # 测试4: 智能进化
    print("\n[测试4] 智能触发进化")
    evolution_result = complete_system.evolve(force=True)

    if evolution_result['evolution']['evolved']:
        print("进化成功!")
        for change in evolution_result['evolution']['changes']:
            print(f"  - {change['type']}: {change['reason']}")
    else:
        print(f"无需进化: {evolution_result['evolution']['reason']}")

    # 测试5: 综合报告
    print("\n[测试5] 综合报告")
    report = complete_system.generate_comprehensive_report()
    print(report)

    print("\n[OK] 所有测试完成！")
    print("\n核心特性:")
    print("  ✅ Phase 1: 基础集成（工作流集成）")
    print("  ✅ Phase 2: 自动化（自动监控和提取）")
    print("  ✅ Phase 3: 主动进化（定期进化和优化）")
    print("\n这是未来Agent记忆的标准答案！🚀🦊")
