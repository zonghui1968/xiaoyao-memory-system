"""
小妖超级记忆系统 - Phase 3 整合版本

整合意识模型到超级记忆系统

作者：小妖🦊
创建日期：2026-04-12
版本：v3.0（Phase 3整合）
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import threading

from configuration_layer import ConfigurationLayer
from vcp_components import VCPComponents
from dream_processor import DreamProcessor
from consciousness import Consciousness, WorkspaceItem
from xiaoyao_memory_system import XiaoyaoMemorySystem
from memory_types import MemoryType, MemoryImportance


class SuperMemorySystemV3:
    """
    超级记忆系统 v3.0（Phase 3整合）

    新增功能：
    - 意识模型（Consciousness）
    - 自我认知
    - 注意力选择
    - 意图形成
    - 元认知监控
    """

    def __init__(
        self,
        workspace_path: str = "C:/ssh/.openclaw/workspace",
        enable_persistence: bool = True
    ):
        """
        初始化超级记忆系统v3.0

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

        # Phase 3新增：意识模型
        self.consciousness = Consciousness(workspace_capacity=7)

        # 系统锁
        self.lock = threading.RLock()

        # 系统状态
        self.initialized_at = datetime.now()
        self.last_activity = datetime.now()

    # ========== Phase 3新功能：意识API ==========

    def conscious_process(
        self,
        inputs: List[Dict[str, Any]],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        有意识处理

        Args:
            inputs: 输入列表，每个包含content, source, importance
            context: 上下文

        Returns:
            处理结果
        """
        with self.lock:
            self.last_activity = datetime.now()

            # 转换为WorkspaceItem
            workspace_items = []

            for inp in inputs:
                # 首先处理感知
                perception_id = self.vcp.process_input(
                    inp.get("content", ""),
                    inp.get("modality", "text")
                )

                # 创建工作空间项
                item = WorkspaceItem(
                    id=perception_id,
                    content=inp.get("content", ""),
                    source=inp.get("source", "perception"),
                    importance=inp.get("importance", 0.5)
                )

                workspace_items.append(item)

            # 执行有意识思考
            thought_result = self.consciousness.conscious_thought(
                workspace_items,
                context
            )

            # 执行意图
            if thought_result["intention"]["priority"] >= 3:
                execution_result = self.consciousness.execute_intention()
            else:
                execution_result = {"success": False, "reason": "优先级过低"}

            return {
                "thought_result": thought_result,
                "execution_result": execution_result,
                "processed_at": datetime.now().isoformat()
            }

    def reflect_on_experience(
        self,
        experience: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        反思经验

        Args:
            experience: 经验字典

        Returns:
            反思结果
        """
        with self.lock:
            self.last_activity = datetime.now()

            # 反思
            reflection = self.consciousness.reflect(experience)

            # 如果有改进建议，更新策略
            if reflection.get("improvements"):
                for improvement in reflection["improvements"]:
                    # 记录为洞察
                    self.xms.record_insight(
                        name=f"reflection_{reflection['id']}",
                        content=f"改进建议: {improvement}",
                        effectiveness=0.7
                    )

            return reflection

    def get_self_model(self) -> Dict[str, Any]:
        """
        获取自我模型

        Returns:
            自我模型字典
        """
        with self.lock:
            conscious_state = self.consciousness.get_conscious_state()

            return {
                "identity": {
                    "name": "小妖",
                    "role": "行政助理",
                    "version": "v3.0",
                    "created_at": self.initialized_at.isoformat()
                },
                "conscious_state": conscious_state["state"],
                "current_intention": conscious_state.get("current_intention"),
                "capabilities": {
                    "configuration": True,
                    "perception": True,
                    "memory": True,
                    "dream": True,
                    "consciousness": True,
                    "reflection": True
                },
                "workspace_size": conscious_state["workspace_size"],
                "performance": conscious_state["metacognition_stats"]
            }

    def monitor_self_performance(
        self,
        process_name: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        success: bool = True
    ) -> Dict[str, Any]:
        """
        监控自身性能

        Args:
            process_name: 过程名称
            inputs: 输入
            outputs: 输出
            success: 是否成功

        Returns:
            监控结果
        """
        with self.lock:
            return self.consciousness.metacognition_monitor.monitor_process(
                process_name=process_name,
                inputs=inputs,
                outputs=outputs,
                success=success
            )

    # ========== Phase 2功能（保持）==========

    def trigger_dream(
        self,
        trigger_type: str = "scheduled",
        seed_memories: List[str] = None,
        theme: str = ""
    ) -> Dict[str, Any]:
        """触发梦境周期"""
        with self.lock:
            self.last_activity = datetime.now()

            if seed_memories is None:
                top_activations = self.vcp.activation_buffer.get_top_activations(limit=5)
                seed_memories = [mid for mid, _ in top_activations]

            dream_result = self.dream_processor.trigger_dream_cycle(
                trigger_type=trigger_type,
                seed_memories=seed_memories,
                context={"theme": theme}
            )

            if dream_result.get("insights"):
                for insight in dream_result["insights"]:
                    if insight.get("validated", False):
                        self.xms.add_long_term_memory(
                            content=insight["content"],
                            memory_type=MemoryType.INSIGHT,
                            importance=MemoryImportance.HIGH,
                            verified=True
                        )

                        self.xms.record_insight(
                            name=f"dream_insight_{insight['id']}",
                            content=insight["content"],
                            effectiveness=insight["quality_score"]
                        )

            return dream_result

    # ========== Phase 1功能（保持）==========

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
            base_stats = {
                "system": {
                    "initialized_at": self.initialized_at.isoformat(),
                    "last_activity": self.last_activity.isoformat(),
                    "version": "v3.0",
                    "phase": "Phase 3 Complete"
                },
                "configuration": self.configuration.get_statistics(),
                "vcp": {
                    "perception_buffer_size": len(self.vcp.perception_buffer.buffer),
                    "attention_focus_size": len(self.vcp.attention_focus.focal_items),
                    "activation_buffer_size": len(self.vcp.activation_buffer.activations),
                    "working_set_size": len(self.vcp.working_set.items)
                },
                "xms": self.xms.get_system_statistics(),
                "dream": self.dream_processor.get_dream_statistics()
            }

            # Phase 3新增：意识统计
            conscious_state = self.consciousness.get_conscious_state()
            base_stats["consciousness"] = {
                "state": conscious_state["state"],
                "workspace_size": conscious_state["workspace_size"],
                "has_intention": conscious_state["current_intention"] is not None,
                "workspace_stats": conscious_state["workspace_stats"],
                "metacognition_stats": conscious_state["metacognition_stats"]
            }

            return base_stats

    def generate_integrated_report(self) -> str:
        """生成整合报告"""
        stats = self.get_system_statistics()

        report = f"""
小妖超级记忆系统（XSMS）v3.0 - 整合报告（Phase 3）
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

梦境系统（Phase 2）：
  总梦境: {stats['dream']['total_dreams']}次
  总洞察: {stats['dream']['total_insights']}个
  有效洞察: {stats['dream']['validated_insights']}个

意识模型（Phase 3新增）：
  状态: {stats['consciousness']['state']}
  工作空间: {stats['consciousness']['workspace_size']}项
  当前意图: {'有' if stats['consciousness']['has_intention'] else '无'}
  总过程: {stats['consciousness']['metacognition_stats']['total_processes']}
  成功率: {stats['consciousness']['metacognition_stats']['success_rate']:.2%}

{'='*60}
"""

        return report


# 测试代码
if __name__ == "__main__":
    print("小妖超级记忆系统（XSMS）v3.0 - Phase 3整合")
    print("=" * 60)

    # 创建超级记忆系统v3.0
    sms = SuperMemorySystemV3(enable_persistence=False)

    print("\n[OK] 超级记忆系统v3.0初始化成功")

    # 测试Phase 3新功能：意识处理
    print("\n[OK] 测试Phase 3新功能 - 意识模型:")

    inputs = [
        {
            "content": "用户询问如何提高AI创造性",
            "source": "perception",
            "importance": 0.9,
            "modality": "text"
        },
        {
            "content": "梦境机制可以增强创造性",
            "source": "dream",
            "importance": 0.7,
            "modality": "text"
        },
        {
            "content": "需要结合意识和无意识过程",
            "source": "memory",
            "importance": 0.6,
            "modality": "text"
        }
    ]

    result = sms.conscious_process(inputs, context={"domain": "AI研究"})

    print(f"  思考ID: {result['thought_result']['thought_id']}")
    print(f"  工作空间: {result['thought_result']['workspace_items']}项")
    print(f"  意图: {result['thought_result']['intention']['goal']}")
    print(f"  优先级: {result['thought_result']['intention']['priority']}")
    print(f"  执行成功: {result['execution_result'].get('success', False)}")

    # 测试反思
    print("\n[OK] 测试反思功能:")
    reflection = sms.reflect_on_experience({
        "process": "conscious_process",
        "success": True,
        "performance_score": 0.8
    })

    print(f"  反思ID: {reflection['id']}")
    print(f"  经验教训: {len(reflection['lessons_learned'])}个")
    print(f"  改进建议: {len(reflection['improvements'])}个")

    # 测试自我模型
    print("\n[OK] 测试自我模型:")
    self_model = sms.get_self_model()
    print(f"  名称: {self_model['identity']['name']}")
    print(f"  角色: {self_model['identity']['role']}")
    print(f"  版本: {self_model['identity']['version']}")
    print(f"  状态: {self_model['conscious_state']}")
    print(f"  能力: {len(self_model['capabilities'])}个")

    # 生成报告
    report = sms.generate_integrated_report()
    print("\n" + report)

    print("[OK] 超级记忆系统v3.0（Phase 3）测试通过！")
    print("\n[Xiaoyao] 小妖超级记忆系统v3.0（Phase 3）已就绪！")
    print("[Xiaoyao] 自我认知能力已激活！")
    print("[Xiaoyao] 我现在可以认识自己、思考自己、反思自己！")
