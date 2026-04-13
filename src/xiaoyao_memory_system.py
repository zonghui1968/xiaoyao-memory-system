"""
小妖AI原生知识记忆系统 - 统一系统接口

整合四层记忆架构，提供统一的API

作者：小妖🦊
创建日期：2026-04-12
版本：v1.0
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import threading

from memory_types import (
    Memory,
    WorkingMemoryItem,
    ShortTermMemoryItem,
    LongTermMemoryItem,
    MemoryType,
    MemoryImportance,
    MemoryID,
    Problem
)

from working_memory_layer import WorkingMemoryManager
from short_term_memory_layer import ShortTermMemoryManager
from long_term_memory_layer import LongTermMemoryLayer
from meta_memory_layer import MetaMemoryManager


class XiaoyaoMemorySystem:
    """
    小妖AI原生知识记忆系统

    四层记忆架构：
    1. 工作记忆层 - 实时任务处理
    2. 短期记忆层 - 会话上下文
    3. 长期记忆层 - 知识图谱
    4. 元记忆层 - 系统自我认知
    """

    def __init__(
        self,
        storage_path: str = "C:/ssh/.openclaw/xiaoyao-memory-system/data",
        enable_persistence: bool = True
    ):
        """
        初始化记忆系统

        Args:
            storage_path: 存储路径
            enable_persistence: 是否启用持久化
        """
        self.storage_path = storage_path
        self.enable_persistence = enable_persistence

        # 初始化四层记忆
        self.working_memory = WorkingMemoryManager(capacity=100)
        self.short_term_memory = ShortTermMemoryManager(max_sessions=50)
        self.long_term_memory = LongTermMemoryLayer(
            storage_path=f"{storage_path}/long_term",
            enable_persistence=enable_persistence
        )
        self.meta_memory = MetaMemoryManager()

        # 系统锁
        self.lock = threading.RLock()

        # 系统状态
        self.initialized_at = datetime.now()
        self.last_activity = datetime.now()

        # 统计信息
        self.stats = {
            "total_queries": 0,
            "total_additions": 0,
            "total_retrievals": 0
        }

    # ========== 工作记忆层 API ==========

    def add_task(
        self,
        task_description: str,
        context: str = "",
        priority: int = 3,
        ttl_hours: float = 24.0
    ) -> WorkingMemoryItem:
        """
        添加任务到工作记忆

        Args:
            task_description: 任务描述
            context: 任务上下文
            priority: 优先级（1-5）
            ttl_hours: 生存时间（小时）

        Returns:
            创建的工作记忆项
        """
        with self.lock:
            self.last_activity = datetime.now()
            self.stats["total_additions"] += 1

            return self.working_memory.add_task(
                task_description=task_description,
                context=context,
                priority=priority,
                ttl_hours=ttl_hours
            )

    def get_next_task(self) -> Optional[WorkingMemoryItem]:
        """
        获取下一个任务

        Returns:
            下一个要处理的任务，如果没有返回None
        """
        with self.lock:
            self.last_activity = datetime.now()
            self.stats["total_retrievals"] += 1

            return self.working_memory.get_next_task()

    def complete_task(self, task_id: MemoryID) -> bool:
        """
        完成任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功
        """
        with self.lock:
            return self.working_memory.complete_task(task_id)

    # ========== 短期记忆层 API ==========

    def record_conversation(
        self,
        session_id: str,
        user_input: str,
        assistant_response: str
    ):
        """
        记录对话

        Args:
            session_id: 会话ID
            user_input: 用户输入
            assistant_response: 助手响应
        """
        with self.lock:
            self.last_activity = datetime.now()
            self.stats["total_additions"] += 1

            self.short_term_memory.record_conversation(
                session_id,
                user_input,
                assistant_response
            )

    def get_conversation_history(
        self,
        session_id: str,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取对话历史

        Args:
            session_id: 会话ID
            count: 返回数量

        Returns:
            对话轮次列表
        """
        with self.lock:
            self.last_activity = datetime.now()
            self.stats["total_retrievals"] += 1

            return self.short_term_memory.layer.get_conversation_history(
                session_id,
                count
            )

    def add_session_memory(
        self,
        session_id: str,
        content: str,
        memory_type: MemoryType = MemoryType.EXPERIENCE,
        importance: MemoryImportance = MemoryImportance.MEDIUM
    ) -> ShortTermMemoryItem:
        """
        添加会话记忆

        Args:
            session_id: 会话ID
            content: 记忆内容
            memory_type: 记忆类型
            importance: 重要性

        Returns:
            创建的短期记忆项
        """
        with self.lock:
            self.last_activity = datetime.now()
            self.stats["total_additions"] += 1

            return self.short_term_memory.layer.add_memory(
                session_id=session_id,
                content=content,
                memory_type=memory_type,
                importance=importance
            )

    # ========== 长期记忆层 API ==========

    def add_long_term_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.FACT,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        verified: bool = False
    ) -> LongTermMemoryItem:
        """
        添加长期记忆

        Args:
            content: 记忆内容
            memory_type: 记忆类型
            importance: 重要性
            verified: 是否已验证

        Returns:
            创建的长期记忆项
        """
        with self.lock:
            self.last_activity = datetime.now()
            self.stats["total_additions"] += 1

            return self.long_term_memory.add_memory(
                content=content,
                memory_type=memory_type,
                importance=importance,
                verified=verified
            )

    def search_long_term_memory(
        self,
        query: str,
        limit: int = 20
    ) -> List[tuple]:
        """
        搜索长期记忆

        Args:
            query: 查询字符串
            limit: 返回数量

        Returns:
            [(记忆项, 相似度分数)] 列表
        """
        with self.lock:
            self.last_activity = datetime.now()
            self.stats["total_queries"] += 1

            return self.long_term_memory.search_memories(query, limit)

    def query_knowledge_graph(
        self,
        entity_name: str,
        max_depth: int = 3,
        max_results: int = 20
    ) -> List[tuple]:
        """
        查询知识图谱

        Args:
            entity_name: 实体名称
            max_depth: 最大深度
            max_results: 最大结果数

        Returns:
            [(实体ID, 关联分数, 距离)] 列表
        """
        with self.lock:
            self.last_activity = datetime.now()
            self.stats["total_queries"] += 1

            # 查找实体
            entities = self.long_term_memory.knowledge_graph.find_entities(
                entity_name
            )

            if not entities:
                return []

            # 查询关联
            seed_entity = entities[0].id
            return self.long_term_memory.knowledge_graph.query_associations(
                seed_entity,
                max_depth,
                max_results
            )

    # ========== 元记忆层 API ==========

    def add_strategy(
        self,
        name: str,
        content: str,
        effectiveness: float = 0.0
    ):
        """
        添加学习策略

        Args:
            name: 策略名称
            content: 策略内容
            effectiveness: 有效性
        """
        with self.lock:
            self.meta_memory.layer.add_strategy(
                name=name,
                content=content,
                effectiveness=effectiveness
            )

    def record_insight(
        self,
        name: str,
        content: str,
        effectiveness: float = 0.5
    ):
        """
        记录洞察

        Args:
            name: 洞察名称
            content: 洞察内容
            effectiveness: 有效性
        """
        with self.lock:
            self.meta_memory.layer.add_insight(
                name=name,
                content=content,
                effectiveness=effectiveness
            )

    def learn_from_success(self, strategy_name: str, context: Dict[str, Any]):
        """
        从成功中学习

        Args:
            strategy_name: 策略名称
            context: 上下文
        """
        with self.lock:
            self.meta_memory.learn_from_success(strategy_name, context)

    def get_best_strategy(self, problem_type: str) -> Optional[str]:
        """
        获取最佳策略

        Args:
            problem_type: 问题类型

        Returns:
            策略内容，如果没有返回None
        """
        with self.lock:
            strategy = self.meta_memory.layer.get_best_strategy(
                strategy_type=problem_type,
                min_usage=1
            )

            return strategy.content if strategy else None

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
                    "uptime_hours": (datetime.now() - self.initialized_at).total_seconds() / 3600,
                    "total_queries": self.stats["total_queries"],
                    "total_additions": self.stats["total_additions"],
                    "total_retrievals": self.stats["total_retrievals"]
                },
                "working_memory": self.working_memory.layer.get_statistics(),
                "short_term_memory": self.short_term_memory.layer.get_statistics(),
                "long_term_memory": self.long_term_memory.get_statistics(),
                "meta_memory": self.meta_memory.layer.get_statistics()
            }

    def generate_summary_report(self) -> str:
        """
        生成摘要报告

        Returns:
            报告字符串
        """
        stats = self.get_system_statistics()

        report = f"""
小妖AI原生知识记忆系统 - 摘要报告
{'='*60}

系统信息：
  初始化时间: {stats['system']['initialized_at']}
  运行时长: {stats['system']['uptime_hours']:.1f}小时
  总查询: {stats['system']['total_queries']}
  总添加: {stats['system']['total_additions']}
  总检索: {stats['system']['total_retrievals']}

工作记忆层：
  当前任务: {stats['working_memory']['current_count']}/{stats['working_memory'].get('capacity', 'N/A')}
  活跃任务: {stats['working_memory']['active_count']}

短期记忆层：
  活跃会话: {stats['short_term_memory']['current_active_sessions']}
  对话轮次: {stats['short_term_memory']['total_conversation_turns']}
  总记忆: {stats['short_term_memory']['total_memories']}

长期记忆层：
  总记忆: {stats['long_term_memory']['current_memories']}
  知识图谱节点: {stats['long_term_memory']['total_nodes']}
  知识图谱边: {stats['long_term_memory']['total_edges']}

元记忆层：
  策略数: {stats['meta_memory']['current_strategies']}
  模式数: {stats['meta_memory']['current_patterns']}
  洞察数: {stats['meta_memory']['current_insights']}
  操作历史: {stats['meta_memory']['operation_history_size']}

{'='*60}
"""

        return report


# 测试代码
if __name__ == "__main__":
    print("小妖AI原生知识记忆系统 - 统一接口")
    print("=" * 60)

    # 创建系统
    system = XiaoyaoMemorySystem(enable_persistence=False)

    # 添加一些任务
    task1 = system.add_task(
        task_description="实现知识图谱构建",
        context="XMS开发",
        priority=5
    )

    task2 = system.add_task(
        task_description="编写单元测试",
        context="XMS开发",
        priority=3
    )

    print("\n✅ 任务添加成功")

    # 记录对话
    system.record_conversation(
        session_id="test-session",
        user_input="你好，我是小妖",
        assistant_response="你好！很高兴认识你"
    )

    print("\n✅ 对话记录成功")

    # 添加长期记忆
    memory1 = system.add_long_term_memory(
        content="Python是一种高级编程语言",
        memory_type=MemoryType.FACT,
        importance=MemoryImportance.HIGH,
        verified=True
    )

    memory2 = system.add_long_term_memory(
        content="知识图谱用于表示实体和关系",
        memory_type=MemoryType.CONCEPT,
        importance=MemoryImportance.HIGH
    )

    print("\n✅ 长期记忆添加成功")

    # 添加策略
    system.add_strategy(
        name="semantic_search",
        content="使用语义向量检索相关记忆",
        effectiveness=0.85
    )

    print("\n✅ 策略添加成功")

    # 记录洞察
    system.record_insight(
        name="first_insight",
        content="四层记忆架构能够有效组织知识",
        effectiveness=0.8
    )

    print("\n✅ 洞察记录成功")

    # 生成报告
    report = system.generate_summary_report()
    print("\n" + report)

    print("✅ 系统测试通过！")
    print("\n🦊 小妖AI原生知识记忆系统已就绪！")
