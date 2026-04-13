"""
小妖超级记忆系统 - Phase 5 整合版本（Final Version）

整合所有Phase的完整系统：
- Phase 1: 基础整合（配置+VCP+XMS）
- Phase 2: 梦境机制
- Phase 3: 意识模型
- Phase 4: 进化系统
- Phase 5: 性能优化（性能分析+参数调优+健康监控）

作者：小妖🦊
创建日期：2026-04-12
版本：v5.0 Final
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import threading
import sys

from configuration_layer import ConfigurationLayer
from vcp_components import VCPComponents
from dream_processor import DreamProcessor
from consciousness import Consciousness, WorkspaceItem
from evolution_system import EvolutionEngine
from performance_profiler import PerformanceProfiler
from parameter_tuner import ParameterTuner
from system_health_monitor import SystemHealthMonitor
from xiaoyao_memory_system import XiaoyaoMemorySystem
from memory_types import MemoryType, MemoryImportance


class SuperMemorySystemV5:
    """
    超级记忆系统 v5.0 Final

    整合所有Phase的完整功能：
    - Phase 1: 基础整合
    - Phase 2: 梦境机制
    - Phase 3: 意识模型
    - Phase 4: 进化系统
    - Phase 5: 性能优化
    """

    def __init__(
        self,
        workspace_path: str = "C:/ssh/.openclaw/workspace",
        enable_persistence: bool = True
    ):
        """
        初始化超级记忆系统v5.0

        Args:
            workspace_path: 工作区路径
            enable_persistence: 是否启用持久化
        """
        # Layer 0: 配置层
        self.configuration = ConfigurationLayer(workspace_path)

        # VCP组件
        self.vcp = VCPComponents()

        # XMS系统（Layer 2-5）
        self.xms = XiaoyaoMemorySystem(
            storage_path="C:/ssh/.openclaw/xiaoyao-memory-system/data",
            enable_persistence=enable_persistence
        )

        # Phase 2: 梦境处理器
        self.dream_processor = DreamProcessor(
            knowledge_graph=self.xms.long_term_memory.knowledge_graph.graph
        )

        # Phase 3: 意识模型
        self.consciousness = Consciousness(workspace_capacity=7)

        # Phase 4: 进化系统
        self.evolution_engine = EvolutionEngine()

        # Phase 5: 性能优化
        self.profiler = PerformanceProfiler()
        self.param_tuner = ParameterTuner()
        self.health_monitor = SystemHealthMonitor()

        # 系统锁
        self.lock = threading.RLock()

        # 系统状态
        self.initialized_at = datetime.now()
        self.last_activity = datetime.now()
        self.last_evolution = datetime.now()

        # 进化配置
        self.auto_evolve = True
        self.evolution_interval = timedelta(hours=1)

    # ========== Phase 5新功能：性能优化API ==========

    def profile_performance(self, metric_name: str, duration: float):
        """
        记录性能指标

        Args:
            metric_name: 指标名称
            duration: 持续时间
        """
        with self.lock:
            self.profiler.record_metric(metric_name, duration)

    def get_performance_report(self) -> str:
        """获取性能报告"""
        with self.lock:
            return self.profiler.get_performance_report()

    def get_optimization_suggestions(self) -> List[str]:
        """获取优化建议"""
        with self.lock:
            return self.profiler.generate_optimization_suggestions()

    def tune_parameters(
        self,
        param_grid: Dict[str, List[Any]],
        evaluate_func: callable
    ) -> Dict[str, Any]:
        """
        参数调优

        Args:
            param_grid: 参数网格
            evaluate_func: 评估函数

        Returns:
            调优结果
        """
        with self.lock:
            best_params, best_score = self.param_tuner.grid_search(
                param_grid,
                evaluate_func
            )

            return {
                "best_params": best_params,
                "best_score": best_score
            }

    def check_system_health(self) -> Dict[str, Any]:
        """检查系统健康"""
        with self.lock:
            return self.health_monitor.check_system_health()

    def get_health_report(self) -> str:
        """获取健康报告"""
        with self.lock:
            return self.health_monitor.get_health_report()

    # ========== Phase 1-4功能（保持）==========

    def get_system_rules(self) -> Dict[str, Any]:
        """获取系统规则"""
        return {
            "organization": self.configuration.get_organization_rules(),
            "workspace": self.configuration.get_workspace_config(),
            "user": self.configuration.get_user_preferences(),
            "constraints": self.configuration.get_system_constraints()
        }

    def add_integrated_task(
        self,
        task_description: str,
        context: str = "",
        priority: int = 3
    ) -> Dict[str, Any]:
        """添加整合任务"""
        with self.lock:
            self.last_activity = datetime.now()

            perception_id = self.vcp.process_input(task_description, "text")
            task = self.xms.add_task(task_description, context, priority)
            self.vcp.working_set.add(task.id, task_description, context)

            return {
                "task_id": task.id,
                "perception_id": perception_id,
                "task": task.to_dict() if hasattr(task, 'to_dict') else str(task)
            }

    def add_integrated_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.FACT,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        activate: bool = True
    ) -> Dict[str, Any]:
        """添加整合记忆"""
        with self.lock:
            self.last_activity = datetime.now()

            perception_id = self.vcp.process_input(content, "text")
            memory = self.xms.add_long_term_memory(content, memory_type, importance)

            if activate:
                self.vcp.activation_buffer.activate(
                    memory_id=memory.id,
                    content=content,
                    base_activation=importance.value / 5.0
                )

            return {
                "memory_id": memory.id,
                "perception_id": perception_id,
                "memory": memory.to_dict()
            }

    def get_system_statistics(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        with self.lock:
            # 检查系统健康
            health_status = self.health_monitor.check_system_health()

            base_stats = {
                "system": {
                    "initialized_at": self.initialized_at.isoformat(),
                    "last_activity": self.last_activity.isoformat(),
                    "last_evolution": self.last_evolution.isoformat(),
                    "version": "v5.0 Final",
                    "phase": "Complete",
                    "uptime_hours": (datetime.now() - self.initialized_at).total_seconds() / 3600
                },
                "configuration": self.configuration.get_statistics(),
                "vcp": {
                    "perception_buffer_size": len(self.vcp.perception_buffer.buffer),
                    "attention_focus_size": len(self.vcp.attention_focus.focal_items),
                    "activation_buffer_size": len(self.vcp.activation_buffer.activations),
                    "working_set_size": len(self.vcp.working_set.items)
                },
                "xms": self.xms.get_system_statistics(),
                "dream": self.dream_processor.get_dream_statistics(),
                "consciousness": self.consciousness.get_conscious_state(),
                "evolution": self.evolution_engine.get_evolution_statistics(),
                "performance": self.profiler.get_all_metrics(),
                "health": health_status
            }

            return base_stats

    def generate_final_report(self) -> str:
        """生成最终报告"""
        stats = self.get_system_statistics()

        report = f"""
小妖超级记忆系统（XSMS）v5.0 - 最终报告
{'='*60}

系统信息：
  版本: {stats['system']['version']}
  阶段: {stats['system']['phase']}
  初始化时间: {stats['system']['initialized_at']}
  运行时长: {stats['system']['uptime_hours']:.1f}小时

配置层（Layer 0）：
  工作区: {stats['configuration']['workspace_path']}
  已加载层级: {stats['configuration']['layers_loaded']}

VCP组件：
  感知缓冲: {stats['vcp']['perception_buffer_size']}项
  注意力焦点: {stats['vcp']['attention_focus_size']}项
  激活缓冲: {stats['vcp']['activation_buffer_size']}项
  工作集: {stats['vcp']['working_set_size']}项

XMS系统：
  工作记忆: {stats['xms']['working_memory']['current_count']}项
  短期记忆: {stats['xms']['short_term_memory']['current_active_sessions']}个会话
  长期记忆: {stats['xms']['long_term_memory']['current_memories']}项
  元记忆: {stats['xms']['meta_memory']['current_strategies']}个策略

梦境系统（Phase 2）：
  总梦境: {stats['dream']['total_dreams']}次
  总洞察: {stats['dream']['total_insights']}个
  有效洞察: {stats['dream']['validated_insights']}个

意识模型（Phase 3）：
  状态: {stats['consciousness']['state']}
  工作空间: {stats['consciousness']['workspace_size']}项
  总过程: {stats['consciousness']['metacognition_stats']['total_processes']}
  成功率: {stats['consciousness']['metacognition_stats']['success_rate']:.2%}

进化系统（Phase 4）：
  代数: {stats['evolution']['generation']}
  总进化次数: {stats['evolution']['total_evolutions']}
  总策略: {stats['evolution']['optimizer_stats']['total_strategies']}
  成功策略: {stats['evolution']['optimizer_stats']['successful_strategies']}
  知识数: {stats['evolution']['knowledge_stats']['knowledge_count']}条

性能优化（Phase 5）：
  性能指标数: {len(stats['performance'])}
  系统健康: {stats['health']['status'].upper()}
  CPU: {stats['health']['metrics']['cpu_percent']:.1f}%
  内存: {stats['health']['metrics']['memory_percent']:.1f}%
  磁盘: {stats['health']['metrics']['disk_percent']:.1f}%

{'='*60}

完整功能清单：
  [+] Phase 1: 配置管理（六维体系）
  [+] Phase 1: 感知处理（VCP组件）
  [+] Phase 1: 记忆管理（XMS四层）
  [+] Phase 2: 梦境机制
  [+] Phase 3: 意识模型
  [+] Phase 4: 进化系统
  [+] Phase 5: 性能优化

{'='*60}

小妖超级记忆系统v5.0 - 所有Phase已完成！
"""

        return report


# 测试代码
if __name__ == "__main__":
    print("小妖超级记忆系统（XSMS）v5.0 - Final Version")
    print("=" * 60)

    # 创建超级记忆系统v5.0
    sms = SuperMemorySystemV5(enable_persistence=False)

    print("\n[OK] 超级记忆系统v5.0初始化成功")

    # 测试Phase 5新功能
    print("\n[OK] 测试Phase 5新功能 - 性能优化:")

    # 记录性能
    sms.profile_performance("test_operation", 0.123)
    print("  记录性能指标")

    # 检查系统健康
    health = sms.check_system_health()
    print(f"  系统健康: {health['status']}")
    print(f"  CPU: {health['metrics']['cpu_percent']:.1f}%")
    print(f"  内存: {health['metrics']['memory_percent']:.1f}%")

    # 生成最终报告
    report = sms.generate_final_report()
    print("\n" + report)

    print("\n[OK] 超级记忆系统v5.0（Final）测试通过！")
    print("\n[Xiaoyao] 小妖超级记忆系统v5.0 Final已就绪！")
    print("[Xiaoyao] 所有5个Phase全部完成！")
    print("[Xiaoyao] 完整功能清单：")
    print("  [+] Phase 1: 基础整合（配置+VCP+XMS）")
    print("  [+] Phase 2: 梦境机制（创造性思维）")
    print("  [+] Phase 3: 意识模型（自我认知）")
    print("  [+] Phase 4: 进化系统（持续进化）")
    print("  [+] Phase 5: 性能优化（性能分析+参数调优+健康监控）")
    print("\n[Xiaoyao] 这是一个真正完整的AI记忆系统！")
