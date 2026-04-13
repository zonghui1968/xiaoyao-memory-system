"""
小妖AI原生知识记忆系统 - 工作记忆层（Working Memory Layer）

第一层：实时感知、任务执行、交互缓冲

作者：小妖🦊
创建日期：2026-04-12
"""

import heapq
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict

from memory_types import (
    WorkingMemoryItem,
    MemoryID,
    create_working_memory,
    MemoryImportance
)


class WorkingMemoryLayer:
    """
    工作记忆层

    职责：
    - 维护当前任务上下文
    - 管理实时感知信息
    - 任务优先级调度
    - 自动清理过期项
    """

    def __init__(self, capacity: int = 100):
        """
        初始化工作记忆层

        Args:
            capacity: 最大容量（默认100项）
        """
        self.capacity = capacity
        self.memories: Dict[MemoryID, WorkingMemoryItem] = {}
        self.priority_queue = []  # 优先级队列
        self.lock = threading.RLock()
        self.task_contexts: Dict[str, List[MemoryID]] = defaultdict(list)

        # 统计信息
        self.stats = {
            "total_added": 0,
            "total_removed": 0,
            "total_expired": 0,
            "current_count": 0
        }

    def add(
        self,
        content: str,
        task_context: str = "",
        priority: int = 3,
        ttl_seconds: Optional[int] = None,
        **kwargs
    ) -> WorkingMemoryItem:
        """
        添加工作记忆项

        Args:
            content: 记忆内容
            task_context: 任务上下文
            priority: 优先级（1-5，5最高）
            ttl_seconds: 生存时间（秒）
            **kwargs: 其他属性

        Returns:
            创建的工作记忆项
        """
        with self.lock:
            # 检查容量
            if len(self.memories) >= self.capacity:
                self._evict_lowest_priority()

            # 创建记忆项
            item = create_working_memory(
                content=content,
                task_context=task_context,
                priority=priority,
                ttl_seconds=ttl_seconds,
                **kwargs
            )

            # 添加到存储
            self.memories[item.id] = item
            self.task_contexts[task_context].append(item.id)

            # 添加到优先级队列（负数，因为heapq是最小堆）
            heapq.heappush(self.priority_queue, (-priority, item.id))

            # 更新统计
            self.stats["total_added"] += 1
            self.stats["current_count"] = len(self.memories)

            return item

    def get(self, memory_id: MemoryID) -> Optional[WorkingMemoryItem]:
        """
        获取工作记忆项

        Args:
            memory_id: 记忆ID

        Returns:
            工作记忆项，如果不存在或已过期返回None
        """
        with self.lock:
            item = self.memories.get(memory_id)

            if item is None:
                return None

            # 检查是否过期
            if item.is_expired():
                self.remove(memory_id)
                self.stats["total_expired"] += 1
                return None

            # 更新访问记录
            item.update_access()

            return item

    def get_by_context(self, task_context: str) -> List[WorkingMemoryItem]:
        """
        按任务上下文获取所有相关记忆

        Args:
            task_context: 任务上下文

        Returns:
            工作记忆项列表
        """
        with self.lock:
            memory_ids = self.task_contexts.get(task_context, [])

            items = []
            for memory_id in memory_ids:
                item = self.get(memory_id)
                if item is not None:
                    items.append(item)

            # 按优先级排序
            items.sort(key=lambda x: x.priority, reverse=True)

            return items

    def get_active_tasks(self, max_count: int = 10) -> List[WorkingMemoryItem]:
        """
        获取当前活跃任务（优先级最高的）

        Args:
            max_count: 最大返回数量

        Returns:
            活跃任务列表
        """
        with self.lock:
            # 清理过期项
            self._cleanup_expired()

            # 获取所有活跃项
            active_items = [
                item for item in self.memories.values()
                if item.status == "active" and not item.is_expired()
            ]

            # 按优先级排序
            active_items.sort(key=lambda x: x.priority, reverse=True)

            return active_items[:max_count]

    def update_status(self, memory_id: MemoryID, status: str):
        """
        更新记忆项状态

        Args:
            memory_id: 记忆ID
            status: 新状态（active, completed, blocked）
        """
        with self.lock:
            item = self.memories.get(memory_id)
            if item is not None:
                item.status = status
                item.modified_at = datetime.now()

    def remove(self, memory_id: MemoryID) -> bool:
        """
        移除记忆项

        Args:
            memory_id: 记忆ID

        Returns:
            是否成功移除
        """
        with self.lock:
            item = self.memories.pop(memory_id, None)
            if item is None:
                return False

            # 从任务上下文中移除
            if item.task_context in self.task_contexts:
                self.task_contexts[item.task_context].remove(memory_id)

            # 更新统计
            self.stats["total_removed"] += 1
            self.stats["current_count"] = len(self.memories)

            return True

    def clear_context(self, task_context: str):
        """
        清理特定任务上下文的所有记忆

        Args:
            task_context: 任务上下文
        """
        with self.lock:
            memory_ids = self.task_contexts.get(task_context, []).copy()

            for memory_id in memory_ids:
                self.remove(memory_id)

            # 清空上下文列表
            self.task_contexts[task_context] = []

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        with self.lock:
            stats = self.stats.copy()

            # 添加实时统计
            active_count = sum(
                1 for item in self.memories.values()
                if item.status == "active" and not item.is_expired()
            )

            stats["active_count"] = active_count
            stats["completed_count"] = stats["current_count"] - active_count

            # 按优先级分布
            priority_distribution = defaultdict(int)
            for item in self.memories.values():
                if not item.is_expired():
                    priority_distribution[item.priority] += 1

            stats["priority_distribution"] = dict(priority_distribution)

            return stats

    def _evict_lowest_priority(self):
        """驱逐优先级最低的项（LRU策略）"""
        if not self.priority_queue:
            return

        # 找到最低优先级的活跃项
        while self.priority_queue:
            neg_priority, memory_id = self.priority_queue[0]
            heapq.heappop(self.priority_queue)

            item = self.memories.get(memory_id)
            if item is not None and not item.is_expired():
                # 找到有效项，移除它
                self.remove(memory_id)
                break

    def _cleanup_expired(self):
        """清理所有过期项"""
        expired_ids = [
            memory_id
            for memory_id, item in self.memories.items()
            if item.is_expired()
        ]

        for memory_id in expired_ids:
            self.remove(memory_id)
            self.stats["total_expired"] += 1


class WorkingMemoryManager:
    """
    工作记忆管理器

    提供更高级的工作记忆管理功能
    """

    def __init__(self, capacity: int = 100):
        self.layer = WorkingMemoryLayer(capacity)

    def add_task(
        self,
        task_description: str,
        context: str = "",
        priority: int = 3,
        ttl_hours: float = 24.0
    ) -> WorkingMemoryItem:
        """
        添加任务

        Args:
            task_description: 任务描述
            context: 任务上下文
            priority: 优先级
            ttl_hours: 生存时间（小时）

        Returns:
            创建的任务项
        """
        ttl_seconds = int(ttl_hours * 3600)

        return self.layer.add(
            content=task_description,
            task_context=context,
            priority=priority,
            ttl_seconds=ttl_seconds,
            status="active"
        )

    def complete_task(self, memory_id: MemoryID) -> bool:
        """
        完成任务

        Args:
            memory_id: 任务ID

        Returns:
            是否成功
        """
        item = self.layer.get(memory_id)
        if item is None:
            return False

        self.layer.update_status(memory_id, "completed")

        # 完成的任务可以立即清理（设置短TTL）
        if item.expires_at is None:
            from datetime import timedelta
            item.expires_at = datetime.now() + timedelta(minutes=5)

        return True

    def get_next_task(self) -> Optional[WorkingMemoryItem]:
        """
        获取下一个要处理的任务（优先级最高的活跃任务）

        Returns:
            任务项，如果没有活跃任务返回None
        """
        active_tasks = self.layer.get_active_tasks(max_count=1)

        return active_tasks[0] if active_tasks else None

    def get_context_tasks(self, context: str) -> List[WorkingMemoryItem]:
        """
        获取特定上下文的所有任务

        Args:
            context: 任务上下文

        Returns:
            任务列表
        """
        return self.layer.get_by_context(context)

    def summarize_status(self) -> str:
        """
        摘要状态

        Returns:
            状态摘要字符串
        """
        stats = self.layer.get_statistics()

        summary = f"""
工作记忆层状态摘要：
--------------------
当前记忆数: {stats['current_count']}/{stats.get('capacity', 'N/A')}
活跃任务数: {stats.get('active_count', 0)}
已完成任务数: {stats.get('completed_count', 0)}

统计：
- 总添加: {stats['total_added']}
- 总移除: {stats['total_removed']}
- 总过期: {stats['total_expired']}

优先级分布：
"""

        priority_dist = stats.get("priority_distribution", {})
        for priority in sorted(priority_dist.keys(), reverse=True):
            count = priority_dist[priority]
            summary += f"  优先级{priority}: {count}项\n"

        return summary


# 测试代码
if __name__ == "__main__":
    print("小妖AI原生知识记忆系统 - 工作记忆层")
    print("=" * 60)

    # 创建工作记忆管理器
    manager = WorkingMemoryManager(capacity=50)

    # 添加一些任务
    task1 = manager.add_task(
        task_description="实现知识图谱构建",
        context="XMS开发",
        priority=5,
        ttl_hours=8
    )

    task2 = manager.add_task(
        task_description="编写单元测试",
        context="XMS开发",
        priority=3,
        ttl_hours=4
    )

    task3 = manager.add_task(
        task_description="设计用户界面",
        context="UI设计",
        priority=4,
        ttl_hours=6
    )

    print("\n✅ 任务添加成功")
    print(f"  任务1: {task1.content}")
    print(f"  任务2: {task2.content}")
    print(f"  任务3: {task3.content}")

    # 获取下一个任务
    next_task = manager.get_next_task()
    print(f"\n🎯 下一个任务: {next_task.content if next_task else '无'}")

    # 获取XMS开发上下文的任务
    xms_tasks = manager.get_context_tasks("XMS开发")
    print(f"\n📋 XMS开发任务数: {len(xms_tasks)}")
    for task in xms_tasks:
        print(f"  - {task.content} (优先级: {task.priority})")

    # 完成一个任务
    manager.complete_task(task1.id)
    print(f"\n✅ 任务已标记为完成: {task1.content}")

    # 打印状态摘要
    print("\n" + manager.summarize_status())

    print("\n✅ 工作记忆层测试通过！")
