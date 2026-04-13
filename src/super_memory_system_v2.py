"""
小妖超级记忆系统 - Phase 2 整合版本

整合梦境处理器到超级记忆系统

作者：小妖🦊
创建日期：2026-04-12
版本：v2.1（Phase 2整合）
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import threading
import networkx as nx

from configuration_layer import ConfigurationLayer
from vcp_components import VCPComponents
from dream_processor import DreamProcessor
from xiaoyao_memory_system import XiaoyaoMemorySystem
from memory_types import MemoryType, MemoryImportance


class SuperMemorySystemV2:
    """
    超级记忆系统 v2.1（Phase 2整合）

    新增功能：
    - 梦境处理器（DreamProcessor）
    - 创造性思维
    - 随机联想
    - 洞察生成
    """

    def __init__(
        self,
        workspace_path: str = "C:/ssh/.openclaw/workspace",
        enable_persistence: bool = True
    ):
        """
        初始化超级记忆系统v2.1

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

        # Phase 2新增：梦境处理器
        self.dream_processor = DreamProcessor(
            knowledge_graph=self.xms.long_term_memory.knowledge_graph.graph
        )

        # 系统锁
        self.lock = threading.RLock()

        # 系统状态
        self.initialized_at = datetime.now()
        self.last_activity = datetime.now()

    # ========== Phase 2新功能：梦境API ==========

    def trigger_dream(
        self,
        trigger_type: str = "scheduled",
        seed_memories: List[str] = None,
        theme: str = ""
    ) -> Dict[str, Any]:
        """
        触发梦境周期

        Args:
            trigger_type: 触发类型（scheduled/problem/creative/manual）
            seed_memories: 种子记忆列表
            theme: 主题

        Returns:
            梦境结果
        """
        with self.lock:
            self.last_activity = datetime.now()

            # 如果没有提供种子记忆，从激活缓冲中获取
            if seed_memories is None:
                top_activations = self.vcp.activation_buffer.get_top_activations(limit=5)
                seed_memories = [mid for mid, _ in top_activations]

            # 触发梦境
            dream_result = self.dream_processor.trigger_dream_cycle(
                trigger_type=trigger_type,
                seed_memories=seed_memories,
                context={"theme": theme}
            )

            # 如果生成了有效洞察，整合到记忆系统
            if dream_result.get("insights"):
                for insight in dream_result["insights"]:
                    if insight.get("validated", False):
                        # 添加到长期记忆
                        self.xms.add_long_term_memory(
                            content=insight["content"],
                            memory_type=MemoryType.INSIGHT,
                            importance=MemoryImportance.HIGH,
                            verified=True
                        )

                        # 添加到元记忆
                        self.xms.record_insight(
                            name=f"dream_insight_{insight['id']}",
                            content=insight["content"],
                            effectiveness=insight["quality_score"]
                        )

            return dream_result

    def explore_associations(
        self,
        concept: str,
        max_depth: int = 3,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        探索关联（创造性联想）

        Args:
            concept: 起始概念
            max_depth: 最大深度
            limit: 返回数量

        Returns:
            关联列表
        """
        with self.lock:
            self.last_activity = datetime.now()

            # 使用XMS查询知识图谱
            xms_associations = self.xms.query_knowledge_graph(
                entity_name=concept,
                max_depth=max_depth,
                max_results=limit
            )

            # 使用梦境处理器进行跨域关联
            dream_associations = self.dream_processor.associator.cross_domain_association(
                [concept],
                max_distance=max_depth
            )

            # 整合结果
            integrated_associations = []

            # XMS关联
            for entity_id, score, distance in xms_associations:
                integrated_associations.append({
                    "source": "xms",
                    "target": entity_id,
                    "score": score,
                    "distance": distance
                })

            # 梦境关联
            for source, target, similarity in dream_associations:
                integrated_associations.append({
                    "source": "dream",
                    "source_concept": source,
                    "target": target,
                    "score": similarity
                })

            # 按分数排序
            integrated_associations.sort(
                key=lambda x: x["score"],
                reverse=True
            )

            return integrated_associations[:limit]

    def generate_creative_insight(
        self,
        problem: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        生成创造性洞察

        Args:
            problem: 问题描述
            context: 上下文

        Returns:
            洞察结果
        """
        with self.lock:
            self.last_activity = datetime.now()

            # 1. 搜索相关知识
            related_memories = self.xms.search_long_term_memory(problem, limit=10)

            # 2. 提取关键概念
            seed_concepts = [m[0].content[:50] for m in related_memories[:5]]

            # 3. 触发创造性梦境
            dream_result = self.trigger_dream(
                trigger_type="creative",
                seed_memories=seed_concepts,
                theme=problem
            )

            # 4. 提取洞察
            insights = dream_result.get("insights", [])

            return {
                "problem": problem,
                "insights": insights,
                "dream_id": dream_result.get("id"),
                "generated_at": datetime.now().isoformat()
            }

    # ========== 保持Phase 1的所有API ==========

    def get_system_rules(self) -> Dict[str, Any]:
        """获取系统规则"""
        return {
            "organization": self.configuration.get_organization_rules(),
            "workspace": self.configuration.get_workspace_config(),
            "user": self.configuration.get_user_preferences(),
            "constraints": self.configuration.get_system_constraints()
        }

    def validate_action(self, action: str) -> tuple[bool, str]:
        """验证操作"""
        return self.configuration.validate_action(action)

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

    def get_next_integrated_task(self) -> Optional[Dict[str, Any]]:
        """获取下一个整合任务"""
        with self.lock:
            self.last_activity = datetime.now()

            task = self.xms.get_next_task()

            if task is None:
                return None

            context = self.vcp.get_active_context()

            return {
                "task": task,
                "context": context
            }

    def record_integrated_conversation(
        self,
        session_id: str,
        user_input: str,
        assistant_response: str
    ):
        """记录整合对话"""
        with self.lock:
            self.last_activity = datetime.now()

            self.vcp.process_input(user_input, "text")
            self.vcp.process_input(assistant_response, "text")

            self.xms.record_conversation(session_id, user_input, assistant_response)

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
            base_stats = {
                "system": {
                    "initialized_at": self.initialized_at.isoformat(),
                    "last_activity": self.last_activity.isoformat(),
                    "version": "v2.1",
                    "phase": "Phase 2 Complete"
                },
                "configuration": self.configuration.get_statistics(),
                "vcp": {
                    "perception_buffer_size": len(self.vcp.perception_buffer.buffer),
                    "attention_focus_size": len(self.vcp.attention_focus.focal_items),
                    "activation_buffer_size": len(self.vcp.activation_buffer.activations),
                    "working_set_size": len(self.vcp.working_set.items)
                },
                "xms": self.xms.get_system_statistics()
            }

            # Phase 2新增：梦境统计
            base_stats["dream"] = self.dream_processor.get_dream_statistics()

            return base_stats

    def generate_integrated_report(self) -> str:
        """生成整合报告"""
        stats = self.get_system_statistics()

        report = f"""
小妖超级记忆系统（XSMS）v2.1 - 整合报告（Phase 2）
{'='*60}

系统信息：
  版本: {stats['system']['version']}
  阶段: {stats['system']['phase']}
  初始化时间: {stats['system']['initialized_at']}
  运行时长: {(datetime.now() - self.initialized_at).total_seconds() / 3600:.1f}小时

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

梦境系统（Phase 2新增）：
  总梦境: {stats['dream']['total_dreams']}次
  总洞察: {stats['dream']['total_insights']}个
  有效洞察: {stats['dream']['validated_insights']}个

{'='*60}
"""

        return report


# 测试代码
if __name__ == "__main__":
    print("小妖超级记忆系统（XSMS）v2.1 - Phase 2整合")
    print("=" * 60)

    # 创建超级记忆系统v2.1
    sms = SuperMemorySystemV2(enable_persistence=False)

    print("\n[OK] 超级记忆系统v2.1初始化成功")

    # 测试梦境功能
    print("\n[OK] 测试梦境功能（Phase 2新功能）:")

    # 添加一些记忆作为种子
    sms.add_integrated_memory(
        "Python是一种高级编程语言",
        MemoryType.FACT,
        MemoryImportance.HIGH
    )

    sms.add_integrated_memory(
        "AI需要大量数据进行训练",
        MemoryType.CONCEPT,
        MemoryImportance.HIGH
    )

    sms.add_integrated_memory(
        "深度学习使用神经网络",
        MemoryType.CONCEPT,
        MemoryImportance.HIGH
    )

    print("  添加种子记忆成功")

    # 触发梦境
    dream_result = sms.trigger_dream(
        trigger_type="manual",
        theme="AI技术学习"
    )

    print(f"  梦境触发成功: {dream_result['id']}")
    print(f"  生成洞察: {len(dream_result['insights'])}个")

    if dream_result['insights']:
        for insight in dream_result['insights']:
            status = "[有效]" if insight.get('validated') else "[无效]"
            print(f"    {status} {insight['content']}")

    # 测试关联探索
    print("\n[OK] 测试关联探索:")
    associations = sms.explore_associations("Python", max_depth=2, limit=5)
    print(f"  发现关联: {len(associations)}个")

    # 生成报告
    report = sms.generate_integrated_report()
    print("\n" + report)

    print("[OK] 超级记忆系统v2.1测试通过！")
    print("\n[Xiaoyao] 小妖超级记忆系统v2.1（Phase 2）已就绪！")
    print("[Xiaoyao] 创造性思维能力已激活！")
