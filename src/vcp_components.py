"""
小妖超级记忆系统 - VCP组件（VCP Components）

实现VCP梦系统的核心组件：
- 感知缓冲（PerceptionBuffer）
- 注意力焦点（AttentionFocus）
- 激活缓冲（ActivationBuffer）
- 工作集（WorkingSet）

作者：小妖🦊
创建日期：2026-04-12
基于：VCP梦系统设计
"""

import random
import threading
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import deque
import numpy as np


class PerceptionBuffer:
    """
    感知缓冲（VCP组件）

    功能：
    - 临时存储感知输入
    - 快速衰减（感觉记忆）
    - 注意力预选择
    """

    def __init__(self, capacity: int = 1000, decay_seconds: float = 2.0):
        """
        初始化感知缓冲

        Args:
            capacity: 容量
            decay_seconds: 衰减时间（秒）
        """
        self.capacity = capacity
        self.decay_seconds = decay_seconds

        self.buffer = deque(maxlen=capacity)
        self.lock = threading.RLock()

        self.stats = {
            "total_perceptions": 0,
            "total_decayed": 0
        }

    def add_perception(self, content: str, modality: str = "text", importance: float = 0.5) -> str:
        """
        添加感知

        Args:
            content: 感知内容
            modality: 模态（text, image, audio等）
            importance: 重要性（0-1）

        Returns:
            感知ID
        """
        with self.lock:
            perception = {
                "id": f"percep_{len(self.buffer)}_{datetime.now().timestamp()}",
                "content": content,
                "modality": modality,
                "importance": importance,
                "timestamp": datetime.now(),
                "accessed": False
            }

            self.buffer.append(perception)
            self.stats["total_perceptions"] += 1

            return perception["id"]

    def get_perception(self, perception_id: str) -> Optional[Dict[str, Any]]:
        """
        获取感知

        Args:
            perception_id: 感知ID

        Returns:
            感知对象，如果不存在或已过期返回None
        """
        with self.lock:
            # 清理过期感知
            self._cleanup_decayed()

            for perception in self.buffer:
                if perception["id"] == perception_id:
                    perception["accessed"] = True
                    return perception

            return None

    def get_active_perceptions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取活跃感知（未过期的）

        Args:
            limit: 返回数量

        Returns:
            感知列表
        """
        with self.lock:
            self._cleanup_decayed()

            active = [p for p in self.buffer if not p.get("decayed", False)]

            # 按重要性和时间排序
            active.sort(
                key=lambda p: (
                    p["importance"],
                    -p["timestamp"].timestamp()
                ),
                reverse=True
            )

            return active[:limit]

    def _cleanup_decayed(self):
        """清理过期的感知"""
        now = datetime.now()
        decayed_count = 0

        for perception in self.buffer:
            if perception.get("decayed", False):
                continue

            age = (now - perception["timestamp"]).total_seconds()

            if age > self.decay_seconds:
                perception["decayed"] = True
                decayed_count += 1

        self.stats["total_decayed"] += decayed_count


class AttentionFocus:
    """
    注意力焦点（VCP组件）

    功能：
    - 注意力分配
    - 焦点选择
    - 容量限制（约7±2项）
    """

    def __init__(self, capacity: int = 7):
        """
        初始化注意力焦点

        Args:
            capacity: 容量（默认7，符合米勒定律）
        """
        self.capacity = capacity
        self.focal_items = []
        self.lock = threading.RLock()

    def set_focus(self, items: List[Dict[str, Any]]):
        """
        设置注意力焦点

        Args:
            items: 焦点项列表
        """
        with self.lock:
            # 按重要性排序
            items.sort(key=lambda x: x.get("importance", 0.5), reverse=True)

            # 限制容量
            self.focal_items = items[:self.capacity]

    def add_focus(self, item: Dict[str, Any]):
        """
        添加焦点项

        Args:
            item: 焦点项
        """
        with self.lock:
            self.focal_items.append(item)

            # 如果超过容量，移除最不重要的
            if len(self.focal_items) > self.capacity:
                self.focal_items.sort(
                    key=lambda x: x.get("importance", 0.5),
                    reverse=True
                )
                self.focal_items = self.focal_items[:self.capacity]

    def get_focal_items(self) -> List[Dict[str, Any]]:
        """获取焦点项"""
        with self.lock:
            return self.focal_items.copy()

    def clear_focus(self):
        """清空焦点"""
        with self.lock:
            self.focal_items = []


class ActivationBuffer:
    """
    激活缓冲（VCP组件）

    功能：
    - 存储激活记忆
    - 激活度计算
    - 衰减机制
    """

    def __init__(self, capacity: int = 500, decay_rate: float = 0.1):
        """
        初始化激活缓冲

        Args:
            capacity: 容量
            decay_rate: 衰减率（每小时）
        """
        self.capacity = capacity
        self.decay_rate = decay_rate

        self.activations: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()

    def activate(self, memory_id: str, content: str, base_activation: float = 1.0):
        """
        激活记忆

        Args:
            memory_id: 记忆ID
            content: 内容
            base_activation: 基础激活度
        """
        with self.lock:
            now = datetime.now()

            if memory_id in self.activations:
                # 提升激活度
                self.activations[memory_id]["activation"] = min(2.0,
                    self.activations[memory_id]["activation"] + 0.5
                )
                self.activations[memory_id]["last_activated"] = now
            else:
                # 新激活
                self.activations[memory_id] = {
                    "id": memory_id,
                    "content": content,
                    "activation": base_activation,
                    "created_at": now,
                    "last_activated": now
                }

    def get_activation(self, memory_id: str) -> float:
        """
        获取激活度

        Args:
            memory_id: 记忆ID

        Returns:
            激活度（0-1）
        """
        with self.lock:
            if memory_id not in self.activations:
                return 0.0

            activation = self.activations[memory_id]

            # 计算衰减
            now = datetime.now()
            hours_since = (now - activation["last_activated"]).total_seconds() / 3600

            decayed_activation = activation["activation"] * (1.0 - self.decay_rate) ** hours_since

            return max(0.0, min(1.0, decayed_activation))

    def get_top_activations(self, limit: int = 20) -> List[Tuple[str, float]]:
        """
        获取激活度最高的记忆

        Args:
            limit: 返回数量

        Returns:
            [(memory_id, activation)] 列表
        """
        with self.lock:
            # 计算当前激活度
            current_activations = [
                (mid, self.get_activation(mid))
                for mid in self.activations.keys()
            ]

            # 排序
            current_activations.sort(key=lambda x: x[1], reverse=True)

            return current_activations[:limit]


class WorkingSet:
    """
    工作集（VCP组件）

    功能：
    - 当前工作记忆集合
    - 快速访问
    - 上下文相关
    """

    def __init__(self, capacity: int = 50):
        """
        初始化工作集

        Args:
            capacity: 容量
        """
        self.capacity = capacity
        self.items: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()

    def add(self, item_id: str, content: str, context: str = ""):
        """
        添加到工作集

        Args:
            item_id: 项ID
            content: 内容
            context: 上下文
        """
        with self.lock:
            self.items[item_id] = {
                "id": item_id,
                "content": content,
                "context": context,
                "added_at": datetime.now(),
                "last_accessed": datetime.now()
            }

            # 如果超过容量，移除最久未访问的
            if len(self.items) > self.capacity:
                items_list = list(self.items.values())
                items_list.sort(key=lambda x: x["last_accessed"])

                # 移除最旧的
                for item in items_list[:len(self.items) - self.capacity]:
                    del self.items[item["id"]]

    def get(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        获取工作项

        Args:
            item_id: 项ID

        Returns:
            工作项
        """
        with self.lock:
            item = self.items.get(item_id)

            if item:
                item["last_accessed"] = datetime.now()

            return item

    def get_context_items(self, context: str) -> List[Dict[str, Any]]:
        """
        获取特定上下文的工作项

        Args:
            context: 上下文

        Returns:
            工作项列表
        """
        with self.lock:
            items = [
                item for item in self.items.values()
                if item["context"] == context
            ]

            items.sort(key=lambda x: x["last_accessed"], reverse=True)

            return items

    def clear_context(self, context: str):
        """
        清理特定上下文

        Args:
            context: 上下文
        """
        with self.lock:
            to_remove = [
                item_id for item_id, item in self.items.items()
                if item["context"] == context
            ]

            for item_id in to_remove:
                del self.items[item_id]


class VCPComponents:
    """
    VCP组件集合

    整合所有VCP组件
    """

    def __init__(self):
        """初始化VCP组件"""
        self.perception_buffer = PerceptionBuffer()
        self.attention_focus = AttentionFocus()
        self.activation_buffer = ActivationBuffer()
        self.working_set = WorkingSet()

    def process_input(self, content: str, modality: str = "text") -> str:
        """
        处理输入（感知→注意力→激活）

        Args:
            content: 输入内容
            modality: 模态

        Returns:
            处理后的感知ID
        """
        # 1. 添加到感知缓冲
        perception_id = self.perception_buffer.add_perception(
            content=content,
            modality=modality,
            importance=0.5
        )

        # 2. 如果足够重要，添加到注意力焦点
        perception = self.perception_buffer.get_perception(perception_id)
        if perception and perception["importance"] > 0.6:
            self.attention_focus.add_focus(perception)

        # 3. 激活相关记忆
        self.activation_buffer.activate(
            memory_id=perception_id,
            content=content,
            base_activation=perception["importance"]
        )

        return perception_id

    def get_active_context(self) -> Dict[str, Any]:
        """
        获取活跃上下文

        Returns:
            上下文字典
        """
        return {
            "perceptions": self.perception_buffer.get_active_perceptions(limit=10),
            "focal_items": self.attention_focus.get_focal_items(),
            "top_activations": self.activation_buffer.get_top_activations(limit=10),
            "working_set_size": len(self.working_set.items)
        }


# 测试代码
if __name__ == "__main__":
    print("小妖超级记忆系统 - VCP组件")
    print("=" * 60)

    # 创建VCP组件
    vcp = VCPComponents()

    # 测试感知缓冲
    print("\n[OK] 测试感知缓冲:")
    percep_id = vcp.process_input("用户询问了关于Python的问题", "text")
    print(f"  添加感知: {percep_id}")

    active_perceptions = vcp.perception_buffer.get_active_perceptions(limit=5)
    print(f"  活跃感知数: {len(active_perceptions)}")

    # 测试注意力焦点
    print("\n[OK] 测试注意力焦点:")
    vcp.attention_focus.add_focus({
        "content": "重要任务",
        "importance": 0.9
    })

    focal_items = vcp.attention_focus.get_focal_items()
    print(f"  焦点项数: {len(focal_items)}")

    # 测试激活缓冲
    print("\n[OK] 测试激活缓冲:")
    vcp.activation_buffer.activate("mem_001", "Python知识", 0.8)
    vcp.activation_buffer.activate("mem_002", "知识图谱", 0.6)

    top_activations = vcp.activation_buffer.get_top_activations(limit=5)
    print(f"  激活记忆数: {len(top_activations)}")

    # 测试工作集
    print("\n[OK] 测试工作集:")
    vcp.working_set.add("item_001", "实现知识图谱", "开发")
    vcp.working_set.add("item_002", "编写测试", "开发")

    context_items = vcp.working_set.get_context_items("开发")
    print(f"  开发上下文项数: {len(context_items)}")

    # 获取活跃上下文
    print("\n[OK] 活跃上下文:")
    context = vcp.get_active_context()
    print(f"  感知: {len(context['perceptions'])}")
    print(f"  焦点: {len(context['focal_items'])}")
    print(f"  激活: {len(context['top_activations'])}")
    print(f"  工作集: {context['working_set_size']}")

    print("\n[OK] VCP组件测试通过！")
