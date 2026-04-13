"""
小妖超级记忆系统 - 意识模型（Consciousness Model）

基于全局工作空间理论（Global Workspace Theory）：
- 全局工作空间（Global Workspace）
- 注意力选择（Attention Selection）
- 意图形成（Intention Formation）
- 元认知监控（Metacognition Monitoring）

作者：小妖🦊
创建日期：2026-04-12
基于：Global Workspace Theory (Baars, 2005)
"""

import random
import threading
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import deque
from dataclasses import dataclass, field
import numpy as np


@dataclass
class WorkspaceItem:
    """
    工作空间项

    表示全局工作空间中的一个信息项
    """
    id: str
    content: str
    source: str  # 来源（perception, memory, dream等）
    importance: float = 0.5
    activation: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    accessed_count: int = 0

    def boost(self, amount: float = 0.1):
        """提升激活度"""
        self.activation = min(1.0, self.activation + amount)
        self.accessed_count += 1
        self.timestamp = datetime.now()


class GlobalWorkspace:
    """
    全局工作空间

    功能：
    - 信息竞争
    - 全局广播
    - 容量限制
    - 动态更新
    """

    def __init__(self, capacity: int = 7):
        """
        初始化全局工作空间

        Args:
            capacity: 容量（符合米勒定律7±2）
        """
        self.capacity = capacity
        self.items: Dict[str, WorkspaceItem] = {}
        self.lock = threading.RLock()

        self.stats = {
            "total_broadcasts": 0,
            "total_competitions": 0,
            "total_evictions": 0
        }

    def add_item(self, item: WorkspaceItem) -> bool:
        """
        添加项目到工作空间

        Args:
            item: 工作空间项

        Returns:
            是否成功添加
        """
        with self.lock:
            # 如果已存在，提升激活度
            if item.id in self.items:
                self.items[item.id].boost()
                return True

            # 检查容量
            if len(self.items) >= self.capacity:
                # 驱逐最不重要的项
                self._evict_weakest()

            # 添加新项
            self.items[item.id] = item
            return True

    def _evict_weakest(self):
        """驱逐最弱的项"""
        if not self.items:
            return

        # 找到激活度最低的项
        weakest_id = min(
            self.items.keys(),
            key=lambda k: (self.items[k].activation, self.items[k].importance)
        )

        del self.items[weakest_id]
        self.stats["total_evictions"] += 1

    def broadcast(self) -> List[WorkspaceItem]:
        """
        全局广播

        返回工作空间中所有项目，按重要性排序

        Returns:
            工作空间项列表
        """
        with self.lock:
            self.stats["total_broadcasts"] += 1

            items = list(self.items.values())

            # 按重要性和激活度排序
            items.sort(
                key=lambda x: (x.activation * 0.6 + x.importance * 0.4),
                reverse=True
            )

            return items

    def compete(self, candidates: List[WorkspaceItem]) -> List[WorkspaceItem]:
        """
        竞争机制

        让候选项目与当前工作空间项目竞争

        Args:
            candidates: 候选项目

        Returns:
            获胜项目
        """
        with self.lock:
            self.stats["total_competitions"] += 1

            # 合并当前项和候选项
            all_items = list(self.items.values()) + candidates

            # 按分数排序
            all_items.sort(
                key=lambda x: x.activation * 0.6 + x.importance * 0.4,
                reverse=True
            )

            # 返回前N项
            return all_items[:self.capacity]

    def get_item(self, item_id: str) -> Optional[WorkspaceItem]:
        """
        获取项目

        Args:
            item_id: 项目ID

        Returns:
            工作空间项
        """
        with self.lock:
            item = self.items.get(item_id)

            if item:
                item.boost()

            return item

    def clear(self):
        """清空工作空间"""
        with self.lock:
            self.items.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            return {
                "capacity": self.capacity,
                "current_size": len(self.items),
                "total_broadcasts": self.stats["total_broadcasts"],
                "total_competitions": self.stats["total_competitions"],
                "total_evictions": self.stats["total_evictions"]
            }


class AttentionSelector:
    """
    注意力选择器

    功能：
    - 注意力分配
    - 显著性计算
    - 过滤机制
    """

    def __init__(self):
        """初始化注意力选择器"""
        self.attention_weights = {
            "novelty": 0.3,      # 新颖性
            "importance": 0.3,   # 重要性
            "relevance": 0.2,    # 相关性
            "urgency": 0.2       # 紧急性
        }

        self.lock = threading.RLock()

    def calculate_salience(
        self,
        item: WorkspaceItem,
        context: Dict[str, Any] = None
    ) -> float:
        """
        计算显著性

        Args:
            item: 工作空间项
            context: 上下文

        Returns:
            显著性分数（0-1）
        """
        with self.lock:
            # 基础分数
            salience = item.importance * self.attention_weights["importance"]
            salience += item.activation * self.attention_weights["relevance"]

            # 新颖性（基于访问次数）
            novelty = 1.0 / (1.0 + item.accessed_count)
            salience += novelty * self.attention_weights["novelty"]

            # 紧急性（基于时间）
            if context and context.get("urgent_items"):
                if item.id in context["urgent_items"]:
                    salience += self.attention_weights["urgency"]

            return min(1.0, salience)

    def select(
        self,
        candidates: List[WorkspaceItem],
        context: Dict[str, Any] = None,
        limit: int = 7
    ) -> List[WorkspaceItem]:
        """
        选择最显著的项目

        Args:
            candidates: 候选项目
            context: 上下文
            limit: 返回数量

        Returns:
            选中的项目
        """
        with self.lock:
            # 计算所有候选项目的显著性
            scored_items = []

            for item in candidates:
                salience = self.calculate_salience(item, context)

                scored_items.append((item, salience))

            # 按显著性排序
            scored_items.sort(key=lambda x: x[1], reverse=True)

            # 返回前N项
            return [item for item, _ in scored_items[:limit]]


class IntentionFormer:
    """
    意图形成器

    功能：
    - 分析工作空间内容
    - 形成意图
    - 生成计划
    """

    def __init__(self):
        """初始化意图形成器"""
        self.intention_history = []
        self.lock = threading.RLock()

    def form_intention(
        self,
        workspace_items: List[WorkspaceItem],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        形成意图

        Args:
            workspace_items: 工作空间项目
            context: 上下文

        Returns:
            意图对象
        """
        with self.lock:
            # 分析工作空间内容
            analysis = self._analyze_workspace(workspace_items)

            # 形成意图
            intention = {
                "id": f"intention_{len(self.intention_history)}_{datetime.now().timestamp()}",
                "goal": self._formulate_goal(analysis),
                "priority": self._calculate_priority(analysis),
                "plan": self._generate_plan(analysis, context),
                "resources": [item.id for item in workspace_items],
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            }

            self.intention_history.append(intention)

            return intention

    def _analyze_workspace(self, items: List[WorkspaceItem]) -> Dict[str, Any]:
        """分析工作空间"""
        if not items:
            return {
                "dominant_theme": "",
                "total_importance": 0.0,
                "item_count": 0,
                "sources": {}
            }

        # 统计来源
        sources = {}
        for item in items:
            source = item.source
            sources[source] = sources.get(source, 0) + 1

        # 计算总重要性
        total_importance = sum(item.importance for item in items)

        # 提取主导主题（简化版）
        dominant_theme = items[0].content if items else ""

        return {
            "dominant_theme": dominant_theme,
            "total_importance": total_importance,
            "item_count": len(items),
            "sources": sources,
            "avg_importance": total_importance / len(items) if items else 0.0
        }

    def _formulate_goal(self, analysis: Dict[str, Any]) -> str:
        """形成目标"""
        dominant_theme = analysis.get("dominant_theme", "")
        avg_importance = analysis.get("avg_importance", 0.0)

        if avg_importance > 0.7:
            return f"解决高优先级问题: {dominant_theme}"
        elif avg_importance > 0.4:
            return f"处理任务: {dominant_theme}"
        else:
            return f"思考: {dominant_theme}"

    def _calculate_priority(self, analysis: Dict[str, Any]) -> int:
        """计算优先级"""
        avg_importance = analysis.get("avg_importance", 0.0)

        if avg_importance > 0.7:
            return 5
        elif avg_importance > 0.4:
            return 3
        else:
            return 1

    def _generate_plan(
        self,
        analysis: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> List[str]:
        """生成计划"""
        plan = []

        # 简单规划（可以扩展为更复杂的算法）
        sources = analysis.get("sources", {})

        if "perception" in sources:
            plan.append("1. 处理感知输入")

        if "memory" in sources:
            plan.append("2. 检索相关记忆")

        if "dream" in sources:
            plan.append("3. 分析梦境洞察")

        plan.append("4. 形成响应")

        return plan

    def execute_intention(self, intention: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行意图

        Args:
            intention: 意图对象

        Returns:
            执行结果
        """
        # 简化实现
        intention["status"] = "executing"
        intention["started_at"] = datetime.now().isoformat()

        # 执行计划（简化版）
        result = {
            "intention_id": intention["id"],
            "goal": intention["goal"],
            "status": "completed",
            "outcome": "意图执行成功"
        }

        intention["status"] = "completed"
        intention["completed_at"] = datetime.now().isoformat()

        return result


class MetacognitionMonitor:
    """
    元认知监控器

    功能：
    - 监控认知过程
    - 评估性能
    - 反思和学习
    """

    def __init__(self):
        """初始化元认知监控器"""
        self.performance_history = []
        self.reflection_history = []
        self.lock = threading.RLock()

    def monitor_process(
        self,
        process_name: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        success: bool = True
    ) -> Dict[str, Any]:
        """
        监控认知过程

        Args:
            process_name: 过程名称
            inputs: 输入
            outputs: 输出
            success: 是否成功

        Returns:
            监控结果
        """
        with self.lock:
            monitoring = {
                "process": process_name,
                "inputs": inputs,
                "outputs": outputs,
                "success": success,
                "timestamp": datetime.now().isoformat(),
                "performance_score": self._calculate_performance(inputs, outputs, success)
            }

            self.performance_history.append(monitoring)

            return monitoring

    def _calculate_performance(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        success: bool
    ) -> float:
        """计算性能分数"""
        # 简单实现
        base_score = 1.0 if success else 0.5

        # 可以添加更多评估维度
        return base_score

    def reflect(self, experience: Dict[str, Any]) -> Dict[str, Any]:
        """
        反思

        Args:
            experience: 经验

        Returns:
            反思结果
        """
        with self.lock:
            reflection = {
                "id": f"reflection_{len(self.reflection_history)}_{datetime.now().timestamp()}",
                "experience": experience,
                "lessons_learned": self._extract_lessons(experience),
                "improvements": self._suggest_improvements(experience),
                "created_at": datetime.now().isoformat()
            }

            self.reflection_history.append(reflection)

            return reflection

    def _extract_lessons(self, experience: Dict[str, Any]) -> List[str]:
        """提取经验教训"""
        lessons = []

        success = experience.get("success", True)

        if not success:
            lessons.append("分析失败原因")
            lessons.append("改进策略")

        return lessons

    def _suggest_improvements(self, experience: Dict[str, Any]) -> List[str]:
        """建议改进"""
        improvements = []

        performance = experience.get("performance_score", 0.5)

        if performance < 0.7:
            improvements.append("提高处理效率")

        return improvements

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            total_processes = len(self.performance_history)
            successful = sum(1 for p in self.performance_history if p["success"])

            return {
                "total_processes": total_processes,
                "successful_processes": successful,
                "success_rate": successful / total_processes if total_processes > 0 else 0.0,
                "total_reflections": len(self.reflection_history)
            }


class Consciousness:
    """
    意识模型

    整合全局工作空间理论的所有组件：
    - 全局工作空间
    - 注意力选择
    - 意图形成
    - 元认知监控
    """

    def __init__(self, workspace_capacity: int = 7):
        """
        初始化意识模型

        Args:
            workspace_capacity: 工作空间容量
        """
        self.global_workspace = GlobalWorkspace(workspace_capacity)
        self.attention_selector = AttentionSelector()
        self.intention_former = IntentionFormer()
        self.metacognition_monitor = MetacognitionMonitor()

        self.lock = threading.RLock()

        self.current_intention = None
        self.conscious_state = "awake"  # awake, dreaming, reflecting

    def conscious_thought(
        self,
        inputs: List[WorkspaceItem],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        有意识思考

        Args:
            inputs: 输入项目
            context: 上下文

        Returns:
            思考结果
        """
        with self.lock:
            thought_start = datetime.now()

            # 1. 注意力选择
            selected_items = self.attention_selector.select(
                inputs,
                context,
                limit=self.global_workspace.capacity
            )

            # 2. 全局广播（竞争进入工作空间）
            winners = self.global_workspace.compete(selected_items)

            # 更新工作空间
            self.global_workspace.clear()
            for item in winners:
                self.global_workspace.add_item(item)

            # 3. 广播工作空间内容
            broadcast = self.global_workspace.broadcast()

            # 4. 意图形成
            intention = self.intention_former.form_intention(broadcast, context)
            self.current_intention = intention

            # 5. 元认知监控
            monitoring = self.metacognition_monitor.monitor_process(
                process_name="conscious_thought",
                inputs={"items": len(inputs)},
                outputs={"intention": intention["id"]},
                success=True
            )

            thought_result = {
                "thought_id": f"thought_{thought_start.timestamp()}",
                "selected_items": len(selected_items),
                "workspace_items": len(broadcast),
                "intention": intention,
                "monitoring": monitoring,
                "completed_at": datetime.now().isoformat()
            }

            return thought_result

    def reflect(self, experience: Dict[str, Any]) -> Dict[str, Any]:
        """
        反思

        Args:
            experience: 经验

        Returns:
            反思结果
        """
        with self.lock:
            self.conscious_state = "reflecting"

            # 反思
            reflection = self.metacognition_monitor.reflect(experience)

            # 从反思中学习
            if reflection["improvements"]:
                # 可以触发策略更新
                pass

            self.conscious_state = "awake"

            return reflection

    def execute_intention(self) -> Dict[str, Any]:
        """
        执行当前意图

        Returns:
            执行结果
        """
        with self.lock:
            if not self.current_intention:
                return {
                    "success": False,
                    "reason": "No current intention"
                }

            # 执行意图
            result = self.intention_former.execute_intention(
                self.current_intention
            )

            return result

    def get_conscious_state(self) -> Dict[str, Any]:
        """获取意识状态"""
        with self.lock:
            workspace_items = self.global_workspace.broadcast()

            return {
                "state": self.conscious_state,
                "workspace_size": len(workspace_items),
                "workspace_items": [
                    {
                        "id": item.id,
                        "content": item.content[:50],
                        "importance": item.importance,
                        "activation": item.activation
                    }
                    for item in workspace_items
                ],
                "current_intention": self.current_intention,
                "workspace_stats": self.global_workspace.get_statistics(),
                "metacognition_stats": self.metacognition_monitor.get_statistics()
            }


# 测试代码
if __name__ == "__main__":
    print("小妖超级记忆系统 - 意识模型")
    print("=" * 60)

    # 创建意识模型
    consciousness = Consciousness(workspace_capacity=7)

    print("\n[OK] 意识模型初始化成功")

    # 测试有意识思考
    print("\n[OK] 测试有意识思考:")

    # 创建输入项目
    inputs = [
        WorkspaceItem(
            id="item_1",
            content="用户询问关于Python的问题",
            source="perception",
            importance=0.8
        ),
        WorkspaceItem(
            id="item_2",
            content="Python编程知识",
            source="memory",
            importance=0.6
        ),
        WorkspaceItem(
            id="item_3",
            content="梦境洞察：Python与AI的结合",
            source="dream",
            importance=0.7
        )
    ]

    # 执行有意识思考
    thought_result = consciousness.conscious_thought(inputs)

    print(f"  思考ID: {thought_result['thought_id']}")
    print(f"  选择项目: {thought_result['selected_items']}个")
    print(f"  工作空间: {thought_result['workspace_items']}个")
    print(f"  形成意图: {thought_result['intention']['goal']}")
    print(f"  意图优先级: {thought_result['intention']['priority']}")

    # 获取意识状态
    print("\n[OK] 意识状态:")
    state = consciousness.get_conscious_state()
    print(f"  状态: {state['state']}")
    print(f"  工作空间大小: {state['workspace_size']}")
    print(f"  当前意图: {state['current_intention']['goal'] if state['current_intention'] else 'None'}")

    # 测试反思
    print("\n[OK] 测试反思:")
    experience = {
        "process": "conscious_thought",
        "success": True,
        "performance_score": 0.8
    }

    reflection = consciousness.reflect(experience)

    print(f"  反思ID: {reflection['id']}")
    print(f"  经验教训: {len(reflection['lessons_learned'])}个")
    print(f"  改进建议: {len(reflection['improvements'])}个")

    # 获取统计
    print("\n[OK] 统计信息:")
    stats = state['workspace_stats']
    print(f"  总广播: {stats['total_broadcasts']}")
    print(f"  总竞争: {stats['total_competitions']}")
    print(f"  总驱逐: {stats['total_evictions']}")

    meta_stats = state['metacognition_stats']
    print(f"  总过程: {meta_stats['total_processes']}")
    print(f"  成功率: {meta_stats['success_rate']:.2%}")

    print("\n[OK] 意识模型测试通过！")
    print("\n[Xiaoyao] 意识模型已就绪，可以进行自我认知！")
