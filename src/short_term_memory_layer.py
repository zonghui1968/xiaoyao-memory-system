"""
小妖AI原生知识记忆系统 - 短期记忆层（Short-Term Memory Layer）

第二层：会话上下文、对话历史、任务队列

作者：小妖🦊
创建日期：2026-04-12
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import deque, defaultdict
import threading

from memory_types import (
    ShortTermMemoryItem,
    MemoryID,
    Memory,
    MemoryType,
    MemoryImportance
)


class SessionContext:
    """
    会话上下文

    管理单个对话会话的上下文信息
    """

    def __init__(
        self,
        session_id: str,
        max_turns: int = 100,
        ttl_hours: float = 24.0
    ):
        """
        初始化会话上下文

        Args:
            session_id: 会话ID
            max_turns: 最大对话轮次
            ttl_hours: 生存时间（小时）
        """
        self.session_id = session_id
        self.max_turns = max_turns
        self.ttl_hours = ttl_hours

        self.created_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(hours=ttl_hours)
        self.last_activity = datetime.now()

        # 对话历史（使用deque自动限制大小）
        self.conversation_history = deque(maxlen=max_turns)

        # 会话记忆
        self.memories: Dict[MemoryID, ShortTermMemoryItem] = {}

        # 会话元数据
        self.metadata: Dict[str, Any] = {}

    def is_expired(self) -> bool:
        """检查会话是否过期"""
        return datetime.now() > self.expires_at

    def add_turn(self, user_input: str, assistant_response: str):
        """
        添加对话轮次

        Args:
            user_input: 用户输入
            assistant_response: 助手响应
        """
        turn = {
            "timestamp": datetime.now(),
            "user_input": user_input,
            "assistant_response": assistant_response
        }

        self.conversation_history.append(turn)
        self.last_activity = datetime.now()

        # 延长过期时间
        self.expires_at = datetime.now() + timedelta(hours=self.ttl_hours)

    def get_recent_turns(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的对话轮次

        Args:
            count: 返回数量

        Returns:
            对话轮次列表
        """
        history_list = list(self.conversation_history)
        return history_list[-count:]

    def add_memory(self, memory: ShortTermMemoryItem):
        """
        添加记忆

        Args:
            memory: 短期记忆项
        """
        self.memories[memory.id] = memory
        self.last_activity = datetime.now()

    def get_memory(self, memory_id: MemoryID) -> Optional[ShortTermMemoryItem]:
        """
        获取记忆

        Args:
            memory_id: 记忆ID

        Returns:
            短期记忆项
        """
        return self.memories.get(memory_id)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "conversation_turns": len(self.conversation_history),
            "memory_count": len(self.memories),
            "metadata": self.metadata
        }


class ShortTermMemoryLayer:
    """
    短期记忆层

    职责：
    - 管理会话上下文
    - 维护对话历史
    - 任务队列管理
    - 记忆激活度跟踪
    """

    def __init__(self, max_sessions: int = 50, max_memories_per_session: int = 200):
        """
        初始化短期记忆层

        Args:
            max_sessions: 最大会话数
            max_memories_per_session: 每个会话的最大记忆数
        """
        self.max_sessions = max_sessions
        self.max_memories_per_session = max_memories_per_session

        self.sessions: Dict[str, SessionContext] = {}
        self.lock = threading.RLock()

        # 任务队列
        self.task_queue: List[Dict[str, Any]] = []

        # 统计信息
        self.stats = {
            "total_sessions": 0,
            "total_conversation_turns": 0,
            "total_memories": 0,
            "active_sessions": 0
        }

    def get_or_create_session(
        self,
        session_id: str,
        max_turns: int = 100,
        ttl_hours: float = 24.0
    ) -> SessionContext:
        """
        获取或创建会话

        Args:
            session_id: 会话ID
            max_turns: 最大对话轮次
            ttl_hours: 生存时间（小时）

        Returns:
            会话上下文
        """
        with self.lock:
            # 清理过期会话
            self._cleanup_expired_sessions()

            # 获取或创建会话
            if session_id not in self.sessions:
                self.sessions[session_id] = SessionContext(
                    session_id=session_id,
                    max_turns=max_turns,
                    ttl_hours=ttl_hours
                )
                self.stats["total_sessions"] += 1
                self.stats["active_sessions"] = len(self.sessions)

            return self.sessions[session_id]

    def add_conversation_turn(
        self,
        session_id: str,
        user_input: str,
        assistant_response: str
    ):
        """
        添加对话轮次

        Args:
            session_id: 会话ID
            user_input: 用户输入
            assistant_response: 助手响应
        """
        with self.lock:
            session = self.get_or_create_session(session_id)
            session.add_turn(user_input, assistant_response)

            self.stats["total_conversation_turns"] += 1

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
            session = self.sessions.get(session_id)
            if session is None:
                return []

            return session.get_recent_turns(count)

    def add_memory(
        self,
        session_id: str,
        content: str,
        memory_type: MemoryType = MemoryType.EXPERIENCE,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        **kwargs
    ) -> ShortTermMemoryItem:
        """
        添加记忆到会话

        Args:
            session_id: 会话ID
            content: 记忆内容
            memory_type: 记忆类型
            importance: 重要性
            **kwargs: 其他属性

        Returns:
            创建的短期记忆项
        """
        with self.lock:
            session = self.get_or_create_session(session_id)

            # 检查容量
            if len(session.memories) >= self.max_memories_per_session:
                self._evict_lowest_activation(session)

            # 创建记忆
            memory = ShortTermMemoryItem(
                content=content,
                memory_type=memory_type,
                importance=importance,
                session_id=session_id,
                **kwargs
            )

            session.add_memory(memory)

            self.stats["total_memories"] += 1

            return memory

    def get_memory(self, session_id: str, memory_id: MemoryID) -> Optional[ShortTermMemoryItem]:
        """
        获取记忆

        Args:
            session_id: 会话ID
            memory_id: 记忆ID

        Returns:
            短期记忆项
        """
        with self.lock:
            session = self.sessions.get(session_id)
            if session is None:
                return None

            memory = session.get_memory(memory_id)
            if memory:
                memory.update_access()

            return memory

    def get_session_memories(
        self,
        session_id: str,
        limit: int = 20
    ) -> List[ShortTermMemoryItem]:
        """
        获取会话的所有记忆

        Args:
            session_id: 会话ID
            limit: 返回数量限制

        Returns:
            记忆列表（按激活度排序）
        """
        with self.lock:
            session = self.sessions.get(session_id)
            if session is None:
                return []

            memories = list(session.memories.values())

            # 按激活度排序
            memories.sort(key=lambda m: m.get_activation(), reverse=True)

            return memories[:limit]

    def get_active_sessions(self) -> List[SessionContext]:
        """
        获取所有活跃会话

        Returns:
            活跃会话列表
        """
        with self.lock:
            self._cleanup_expired_sessions()

            sessions = list(self.sessions.values())

            # 按最后活动时间排序
            sessions.sort(key=lambda s: s.last_activity, reverse=True)

            return sessions

    def close_session(self, session_id: str) -> bool:
        """
        关闭会话

        Args:
            session_id: 会话ID

        Returns:
            是否成功
        """
        with self.lock:
            session = self.sessions.pop(session_id, None)
            if session is None:
                return False

            self.stats["active_sessions"] = len(self.sessions)
            return True

    def _cleanup_expired_sessions(self):
        """清理过期会话"""
        expired_sessions = [
            session_id
            for session_id, session in self.sessions.items()
            if session.is_expired()
        ]

        for session_id in expired_sessions:
            self.close_session(session_id)

    def _evict_lowest_activation(self, session: SessionContext):
        """驱逐激活度最低的记忆"""
        memories = list(session.memories.values())

        if not memories:
            return

        # 找到激活度最低的
        lowest_memory = min(memories, key=lambda m: m.get_activation())

        # 移除
        del session.memories[lowest_memory.id]

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        with self.lock:
            stats = self.stats.copy()

            # 添加实时统计
            stats["current_active_sessions"] = len(self.sessions)

            # 按会话统计记忆数
            memory_distribution = []
            for session in self.sessions.values():
                memory_distribution.append({
                    "session_id": session.session_id,
                    "memory_count": len(session.memories),
                    "conversation_turns": len(session.conversation_history),
                    "last_activity": session.last_activity.isoformat()
                })

            stats["memory_distribution"] = memory_distribution

            return stats


class ShortTermMemoryManager:
    """
    短期记忆管理器

    提供更高级的短期记忆管理功能
    """

    def __init__(self, max_sessions: int = 50):
        self.layer = ShortTermMemoryLayer(max_sessions)

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
        self.layer.add_conversation_turn(
            session_id,
            user_input,
            assistant_response
        )

    def get_context_summary(self, session_id: str) -> str:
        """
        获取会话上下文摘要

        Args:
            session_id: 会话ID

        Returns:
            上下文摘要
        """
        session = self.layer.sessions.get(session_id)
        if session is None:
            return "会话不存在"

        recent_turns = session.get_recent_turns(5)
        memories = self.layer.get_session_memories(session_id, limit=10)

        summary = f"""
会话ID: {session_id}
创建时间: {session.created_at.strftime('%Y-%m-%d %H:%M')}
对话轮次: {len(session.conversation_history)}
记忆数: {len(session.memories)}

最近对话：
"""
        for turn in recent_turns:
            summary += f"  用户: {turn['user_input'][:50]}...\n"
            summary += f"  AI: {turn['assistant_response'][:50]}...\n\n"

        return summary


# 测试代码
if __name__ == "__main__":
    print("小妖AI原生知识记忆系统 - 短期记忆层")
    print("=" * 60)

    # 创建短期记忆管理器
    manager = ShortTermMemoryManager(max_sessions=10)

    # 记录一些对话
    session_id = "test-session-001"

    manager.record_conversation(
        session_id,
        "你好，我是小妖",
        "你好！很高兴认识你"
    )

    manager.record_conversation(
        session_id,
        "你能做什么？",
        "我可以帮助你管理知识、回答问题、进行思考"
    )

    manager.record_conversation(
        session_id,
        "告诉我关于Python的知识",
        "Python是一种高级编程语言，具有简洁的语法"
    )

    print("\n✅ 对话记录成功")

    # 添加一些记忆
    manager.layer.add_memory(
        session_id,
        content="用户对编程感兴趣",
        memory_type=MemoryType.EXPERIENCE,
        importance=MemoryImportance.MEDIUM
    )

    manager.layer.add_memory(
        session_id,
        content="用户询问了Python相关问题",
        memory_type=MemoryType.FACT,
        importance=MemoryImportance.LOW
    )

    print("\n✅ 记忆添加成功")

    # 获取上下文摘要
    summary = manager.get_context_summary(session_id)
    print("\n📋 会话摘要：")
    print(summary)

    # 获取统计信息
    stats = manager.layer.get_statistics()
    print("\n📊 统计信息：")
    print(f"  总会话数: {stats['total_sessions']}")
    print(f"  活跃会话: {stats['current_active_sessions']}")
    print(f"  对话轮次: {stats['total_conversation_turns']}")
    print(f"  总记忆数: {stats['total_memories']}")

    print("\n✅ 短期记忆层测试通过！")
