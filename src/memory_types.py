"""
小妖AI原生知识记忆系统 (XMS) - 基础类型定义

定义四层记忆架构的核心数据结构

作者：小妖🦊
创建日期：2026-04-12
基于：VCP梦系统学习 + AI原生设计
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from enum import Enum
import uuid


class MemoryType(Enum):
    """记忆类型"""
    FACT = "fact"  # 事实性知识
    PROCEDURE = "procedure"  # 程序性知识
    CONCEPT = "concept"  # 概念性知识
    EXPERIENCE = "experience"  # 经验性知识
    META = "meta"  # 元认知知识


class MemoryImportance(Enum):
    """记忆重要性"""
    CRITICAL = 5  # 关键
    HIGH = 4  # 高
    MEDIUM = 3  # 中
    LOW = 2  # 低
    TRIVIAL = 1  # 琐碎


@dataclass
class Memory:
    """基础记忆单元"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    memory_type: MemoryType = MemoryType.FACT
    importance: MemoryImportance = MemoryImportance.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None  # 向量表示

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "importance": self.importance.value,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "tags": list(self.tags),
            "metadata": self.metadata,
            "embedding_length": len(self.embedding) if self.embedding else 0
        }

    def update_access(self):
        """更新访问记录"""
        self.access_count += 1
        self.last_accessed = datetime.now()


@dataclass
class WorkingMemoryItem(Memory):
    """工作记忆项 - 实时任务处理"""
    task_context: str = ""
    priority: int = 3  # 1-5，5最高
    status: str = "active"  # active, completed, blocked
    ttl_seconds: Optional[int] = None  # 生存时间
    expires_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


@dataclass
class ShortTermMemoryItem(Memory):
    """短期记忆项 - 会话上下文"""
    session_id: str = ""
    conversation_turn: int = 0
    related_tasks: List[str] = field(default_factory=list)
    decay_rate: float = 0.1  # 遗忘速率

    def get_activation(self) -> float:
        """计算激活度"""
        # 简单实现：基于访问次数和时间
        time_factor = 1.0
        if self.last_accessed:
            hours_since_access = (datetime.now() - self.last_accessed).total_seconds() / 3600
            time_factor = max(0.1, 1.0 - self.decay_rate * hours_since_access)

        access_factor = min(1.0, self.access_count / 10.0)
        return time_factor * access_factor


@dataclass
class LongTermMemoryItem(Memory):
    """长期记忆项 - 持久化知识"""
    knowledge_graph_id: Optional[str] = None  # 知识图谱节点ID
    abstraction_level: int = 0  # 抽象层次（0=具体，越高越抽象）
    source_memories: List[str] = field(default_factory=list)  # 来源记忆ID
    verified: bool = False  # 是否已验证
    confidence: float = 1.0  # 置信度


@dataclass
class KnowledgeGraphNode:
    """知识图谱节点"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_name: str = ""
    entity_type: str = ""  # person, concept, event, etc.
    description: str = ""
    importance: float = 0.5
    memory_ids: List[str] = field(default_factory=list)  # 关联的记忆ID
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "entity_name": self.entity_name,
            "entity_type": self.entity_type,
            "description": self.description,
            "importance": self.importance,
            "memory_count": len(self.memory_ids),
            "attributes": self.attributes
        }


@dataclass
class KnowledgeGraphEdge:
    """知识图谱边"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = ""
    target_id: str = ""
    relation_type: str = ""  # related_to, causes, is_part_of, etc.
    weight: float = 1.0
    evidence: List[str] = field(default_factory=list)  # 证据记忆ID
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "weight": self.weight,
            "evidence_count": len(self.evidence),
            "created_at": self.created_at.isoformat()
        }


@dataclass
class MetaMemoryItem:
    """元记忆项 - 关于记忆的记忆"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    memory_type: str = ""  # strategy, pattern, insight
    content: str = ""
    effectiveness: float = 0.0  # 有效性评分
    usage_count: int = 0
    last_used: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def update_effectiveness(self, new_score: float):
        """更新有效性（使用移动平均）"""
        if self.effectiveness == 0.0:
            self.effectiveness = new_score
        else:
            # 简单的移动平均
            self.effectiveness = 0.7 * self.effectiveness + 0.3 * new_score
        self.usage_count += 1
        self.last_used = datetime.now()


@dataclass
class MemoryOperation:
    """记忆操作记录"""
    operation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    operation_type: str = ""  # synthesis, refinement, innovation
    source_memories: List[str] = field(default_factory=list)
    result_content: str = ""
    result_type: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_overall_score(self) -> float:
        """获取综合分数"""
        if not self.scores:
            return 0.0
        return sum(self.scores.values()) / len(self.scores)


@dataclass
class Problem:
    """问题定义（用于问题驱动触发）"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    problem_type: str = ""  # user_question, contradiction, knowledge_gap, reflection
    description: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 3
    status: str = "open"  # open, processing, solved, deferred
    created_at: datetime = field(default_factory=datetime.now)
    related_memories: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "problem_type": self.problem_type,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "related_memories_count": len(self.related_memories)
        }


# 类型别名
MemoryID = str
GraphID = str
ProblemID = str


# 工厂函数
def create_memory(
    content: str,
    memory_type: MemoryType = MemoryType.FACT,
    importance: MemoryImportance = MemoryImportance.MEDIUM,
    **kwargs
) -> Memory:
    """创建记忆的工厂函数"""
    return Memory(
        content=content,
        memory_type=memory_type,
        importance=importance,
        **kwargs
    )


def create_working_memory(
    content: str,
    task_context: str = "",
    priority: int = 3,
    ttl_seconds: Optional[int] = None,
    **kwargs
) -> WorkingMemoryItem:
    """创建工作记忆项的工厂函数"""
    item = WorkingMemoryItem(
        content=content,
        task_context=task_context,
        priority=priority,
        ttl_seconds=ttl_seconds,
        **kwargs
    )

    # 设置过期时间
    if ttl_seconds is not None:
        from datetime import timedelta
        item.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)

    return item


def create_knowledge_node(
    entity_name: str,
    entity_type: str,
    description: str = "",
    **kwargs
) -> KnowledgeGraphNode:
    """创建知识图谱节点的工厂函数"""
    return KnowledgeGraphNode(
        entity_name=entity_name,
        entity_type=entity_type,
        description=description,
        **kwargs
    )


def create_knowledge_edge(
    source_id: str,
    target_id: str,
    relation_type: str,
    weight: float = 1.0,
    **kwargs
) -> KnowledgeGraphEdge:
    """创建知识图谱边的工厂函数"""
    return KnowledgeGraphEdge(
        source_id=source_id,
        target_id=target_id,
        relation_type=relation_type,
        weight=weight,
        **kwargs
    )


if __name__ == "__main__":
    # 测试代码
    print("小妖AI原生知识记忆系统 - 基础类型定义")
    print("=" * 60)

    # 创建不同类型的记忆
    fact_memory = create_memory(
        content="Python是一种解释型编程语言",
        memory_type=MemoryType.FACT,
        importance=MemoryImportance.HIGH,
        tags={"programming", "python", "language"}
    )

    working_memory = create_working_memory(
        content="实现知识图谱构建功能",
        task_context="XMS系统开发",
        priority=5,
        ttl_seconds=3600
    )

    knowledge_node = create_knowledge_node(
        entity_name="Python",
        entity_type="programming_language",
        description="一种高级编程语言"
    )

    print("\n✅ 基础类型定义测试通过")
    print(f"  事实记忆: {fact_memory.content[:30]}...")
    print(f"  工作记忆: {working_memory.content[:30]}...")
    print(f"  知识节点: {knowledge_node.entity_name}")

    print("\n系统基础架构就绪！")
