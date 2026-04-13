"""
小妖超级记忆系统 - 整合系统（Integrated System）

整合六维体系、VCP组件和XMS四层架构

作者：小妖🦊
创建日期：2026-04-12
版本：v2.0（超级记忆系统）
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import threading

from configuration_layer import ConfigurationLayer
from vcp_components import VCPComponents
from xiaoyao_memory_system import XiaoyaoMemorySystem
from memory_types import MemoryType, MemoryImportance


class SuperMemorySystem:
    """
    超级记忆系统（XSMS）

    五层架构：
    0. 配置层（六维体系）
    2. 工作记忆层（XMS + VCP）
    3. 短期记忆层（XMS + VCP）
    4. 长期记忆层（XMS + VCP）
    5. 元认知层（XMS + VCP）
    """

    def __init__(
        self,
        workspace_path: str = "C:/ssh/.openclaw/workspace",
        enable_persistence: bool = True
    ):
        """
        初始化超级记忆系统

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

        # 系统锁
        self.lock = threading.RLock()

        # 系统状态
        self.initialized_at = datetime.now()
        self.last_activity = datetime.now()

    # ========== Layer 0: 配置层 API ==========

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

    # ========== Layer 2: 工作记忆层 API（整合XMS + VCP）==========

    def add_integrated_task(
        self,
        task_description: str,
        context: str = "",
        priority: int = 3
    ) -> Dict[str, Any]:
        """
        添加整合任务（XMS任务 + VCP感知）

        Args:
            task_description: 任务描述
            context: 上下文
            priority: 优先级

        Returns:
            任务信息
        """
        with self.lock:
            self.last_activity = datetime.now()

            # VCP: 处理输入
            perception_id = self.vcp.process_input(task_description, "text")

            # XMS: 添加任务
            task = self.xms.add_task(
                task_description=task_description,
                context=context,
                priority=priority
            )

            # VCP: 添加到工作集
            self.vcp.working_set.add(
                item_id=task.id,
                content=task_description,
                context=context
            )

            return {
                "task_id": task.id,
                "perception_id": perception_id,
                "task": task.to_dict() if hasattr(task, 'to_dict') else str(task)
            }

    def get_next_integrated_task(self) -> Optional[Dict[str, Any]]:
        """
        获取下一个整合任务

        Returns:
            任务信息
        """
        with self.lock:
            self.last_activity = datetime.now()

            # XMS: 获取下一个任务
            task = self.xms.get_next_task()

            if task is None:
                return None

            # VCP: 获取活跃上下文
            context = self.vcp.get_active_context()

            return {
                "task": task,
                "context": context
            }

    # ========== Layer 3: 短期记忆层 API（整合XMS + VCP）==========

    def record_integrated_conversation(
        self,
        session_id: str,
        user_input: str,
        assistant_response: str
    ):
        """
        记录整合对话

        Args:
            session_id: 会话ID
            user_input: 用户输入
            assistant_response: 助手响应
        """
        with self.lock:
            self.last_activity = datetime.now()

            # VCP: 处理输入
            self.vcp.process_input(user_input, "text")
            self.vcp.process_input(assistant_response, "text")

            # XMS: 记录对话
            self.xms.record_conversation(
                session_id=session_id,
                user_input=user_input,
                assistant_response=assistant_response
            )

    def get_integrated_context(self, session_id: str) -> Dict[str, Any]:
        """
        获取整合上下文

        Args:
            session_id: 会话ID

        Returns:
            上下文字典
        """
        with self.lock:
            self.last_activity = datetime.now()

            # XMS: 获取对话历史
            conversation = self.xms.get_conversation_history(session_id, count=10)

            # VCP: 获取活跃上下文
            vcp_context = self.vcp.get_active_context()

            return {
                "conversation": conversation,
                "vcp_context": vcp_context,
                "session_id": session_id
            }

    # ========== Layer 4: 长期记忆层 API（整合XMS + VCP）==========

    def add_integrated_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.FACT,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        activate: bool = True
    ) -> Dict[str, Any]:
        """
        添加整合记忆

        Args:
            content: 记忆内容
            memory_type: 记忆类型
            importance: 重要性
            activate: 是否激活

        Returns:
            记忆信息
        """
        with self.lock:
            self.last_activity = datetime.now()

            # VCP: 处理输入
            perception_id = self.vcp.process_input(content, "text")

            # XMS: 添加长期记忆
            memory = self.xms.add_long_term_memory(
                content=content,
                memory_type=memory_type,
                importance=importance
            )

            # VCP: 如果需要，激活记忆
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

    def search_integrated_memory(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        搜索整合记忆

        Args:
            query: 查询字符串
            limit: 返回数量

        Returns:
            记忆列表（XMS搜索 + VCP激活）
        """
        with self.lock:
            self.last_activity = datetime.now()

            # XMS: 搜索长期记忆
            xms_results = self.xms.search_long_term_memory(query, limit)

            # VCP: 获取激活记忆
            vcp_activations = self.vcp.activation_buffer.get_top_activations(limit)

            # 整合结果
            integrated_results = []

            for memory, score in xms_results:
                # 检查VCP激活度
                vcp_activation = self.vcp.activation_buffer.get_activation(memory.id)

                integrated_results.append({
                    "memory": memory.to_dict(),
                    "xms_score": score,
                    "vcp_activation": vcp_activation,
                    "combined_score": score * 0.7 + vcp_activation * 0.3
                })

            # 按综合分数排序
            integrated_results.sort(
                key=lambda x: x["combined_score"],
                reverse=True
            )

            return integrated_results[:limit]

    # ========== Layer 5: 元认知层 API（整合XMS + VCP）==========

    def add_integrated_strategy(
        self,
        name: str,
        content: str,
        effectiveness: float = 0.0
    ):
        """
        添加整合策略

        Args:
            name: 策略名称
            content: 策略内容
            effectiveness: 有效性
        """
        with self.lock:
            self.last_activity = datetime.now()

            # XMS: 添加策略
            self.xms.add_strategy(name, content, effectiveness)

            # VCP: 激活
            self.vcp.activation_buffer.activate(
                memory_id=f"strategy_{name}",
                content=content,
                base_activation=effectiveness
            )

    def record_integrated_insight(
        self,
        name: str,
        content: str,
        effectiveness: float = 0.5
    ):
        """
        记录整合洞察

        Args:
            name: 洞察名称
            content: 洞察内容
            effectiveness: 有效性
        """
        with self.lock:
            self.last_activity = datetime.now()

            # XMS: 记录洞察
            self.xms.record_insight(name, content, effectiveness)

            # VCP: 激活
            self.vcp.activation_buffer.activate(
                memory_id=f"insight_{name}",
                content=content,
                base_activation=effectiveness
            )

    # ========== 统计和报告 ==========

    def get_system_statistics(self) -> Dict[str, Any]:
        """
        获取系统统计信息

        Returns:
            统计信息字典
        """
        with self.lock:
            return {
                "system": {
                    "initialized_at": self.initialized_at.isoformat(),
                    "last_activity": self.last_activity.isoformat(),
                    "uptime_hours": (datetime.now() - self.initialized_at).total_seconds() / 3600
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

    def generate_integrated_report(self) -> str:
        """
        生成整合报告

        Returns:
            报告字符串
        """
        stats = self.get_system_statistics()

        report = f"""
小妖超级记忆系统（XSMS）- 整合报告
{'='*60}

系统信息：
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

{'='*60}
"""

        return report


# 测试代码
if __name__ == "__main__":
    print("小妖超级记忆系统（XSMS）- 整合系统")
    print("=" * 60)

    # 创建超级记忆系统
    sms = SuperMemorySystem(enable_persistence=False)

    print("\n[OK] 超级记忆系统初始化成功")

    # 测试Layer 0: 配置层
    print("\n[OK] 测试配置层:")
    rules = sms.get_system_rules()
    print(f"  组织规则存在: {rules['organization'].get('exists', False)}")

    # 测试Layer 2: 工作记忆层
    print("\n[OK] 测试工作记忆层:")
    task = sms.add_integrated_task(
        task_description="实现梦境处理器",
        context="VCP开发",
        priority=5
    )
    print(f"  添加任务: {task['task_id']}")

    # 测试Layer 3: 短期记忆层
    print("\n[OK] 测试短期记忆层:")
    sms.record_integrated_conversation(
        session_id="test-session",
        user_input="什么是VCP系统？",
        assistant_response="VCP是一个创造性思维系统..."
    )
    print(f"  对话记录成功")

    # 测试Layer 4: 长期记忆层
    print("\n[OK] 测试长期记忆层:")
    memory = sms.add_integrated_memory(
        content="VCP系统通过梦境机制实现创造性思维",
        memory_type=MemoryType.CONCEPT,
        importance=MemoryImportance.HIGH
    )
    print(f"  添加记忆: {memory['memory_id']}")

    # 测试Layer 5: 元认知层
    print("\n[OK] 测试元认知层:")
    sms.add_integrated_strategy(
        name="dream_trigger",
        content="定期触发梦境周期以发现新关联",
        effectiveness=0.8
    )
    print(f"  添加策略成功")

    # 生成报告
    report = sms.generate_integrated_report()
    print("\n" + report)

    print("[OK] 超级记忆系统测试通过！")
    print("\n[Xiaoyao] 小妖超级记忆系统（XSMS）已就绪！")
