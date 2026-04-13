"""
小妖AI原生知识记忆系统 - 元记忆层（Meta-Memory Layer）

第四层：系统自我认知、策略优化、记忆评估

作者：小妖🦊
创建日期：2026-04-12
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import threading
import json
from pathlib import Path
from enum import Enum

from memory_types import (
    MetaMemoryItem,
    MemoryOperation,
    Problem,
    MemoryID,
)


class StrategyType(Enum):
    """策略类型"""
    RETRIEVAL = "retrieval"  # 检索策略
    CONSolidATION = "consolidation"  # 巩固策略
    ACTIVATION = "activation"  # 激活策略
    ORGANIZATION = "organization"  # 组织策略


class MetaMemoryLayer:
    """
    元记忆层

    职责：
    - 系统自我认知
    - 学习策略管理
    - 记忆质量评估
    - 进化历史跟踪
    """

    def __init__(self, storage_path: str = "data/meta_memory"):
        """
        初始化元记忆层

        Args:
            storage_path: 存储路径
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # 核心数据结构
        self.strategies: Dict[str, MetaMemoryItem] = {}
        self.patterns: Dict[str, MetaMemoryItem] = {}
        self.insights: Dict[str, MetaMemoryItem] = {}

        # 操作历史
        self.operation_history: List[MemoryOperation] = []

        # 问题跟踪
        self.problems: Dict[str, Problem] = {}

        # 性能指标
        self.metrics: Dict[str, float] = {}

        self.lock = threading.RLock()

        # 统计信息
        self.stats = {
            "total_strategies": 0,
            "total_patterns": 0,
            "total_insights": 0,
            "total_operations": 0,
            "total_problems": 0
        }

    def add_strategy(
        self,
        name: str,
        content: str,
        context: Dict[str, Any] = None,
        effectiveness: float = 0.0
    ) -> MetaMemoryItem:
        """
        添加学习策略

        Args:
            name: 策略名称
            content: 策略内容
            context: 上下文
            effectiveness: 有效性（初始值）

        Returns:
            创建的元记忆项
        """
        with self.lock:
            strategy = MetaMemoryItem(
                memory_type="strategy",
                content=content,
                effectiveness=effectiveness,
                context=context or {}
            )

            self.strategies[name] = strategy

            self.stats["total_strategies"] += 1

            self._save_meta_memory("strategy", name, strategy)

            return strategy

    def add_pattern(
        self,
        name: str,
        content: str,
        context: Dict[str, Any] = None,
        effectiveness: float = 0.0
    ) -> MetaMemoryItem:
        """
        添加模式

        Args:
            name: 模式名称
            content: 模式描述
            context: 上下文
            effectiveness: 有效性

        Returns:
            创建的元记忆项
        """
        with self.lock:
            pattern = MetaMemoryItem(
                memory_type="pattern",
                content=content,
                effectiveness=effectiveness,
                context=context or {}
            )

            self.patterns[name] = pattern

            self.stats["total_patterns"] += 1

            self._save_meta_memory("pattern", name, pattern)

            return pattern

    def add_insight(
        self,
        name: str,
        content: str,
        context: Dict[str, Any] = None,
        effectiveness: float = 0.0
    ) -> MetaMemoryItem:
        """
        add洞察

        Args:
            name: 洞察名称
            content: 洞察内容
            context: 上下文
            effectiveness: 有效性

        Returns:
            创建的元记忆项
        """
        with self.lock:
            insight = MetaMemoryItem(
                memory_type="insight",
                content=content,
                effectiveness=effectiveness,
                context=context or {}
            )

            self.insights[name] = insight

            self.stats["total_insights"] += 1

            self._save_meta_memory("insight", name, insight)

            return insight

    def record_operation(self, operation: MemoryOperation):
        """
        记录记忆操作

        Args:
            operation: 记忆操作
        """
        with self.lock:
            self.operation_history.append(operation)

            # 只保留最近1000条
            if len(self.operation_history) > 1000:
                self.operation_history = self.operation_history[-1000:]

            self.stats["total_operations"] += 1

    def add_problem(
        self,
        problem_type: str,
        description: str,
        priority: int = 3,
        context: Dict[str, Any] = None
    ) -> Problem:
        """
        添加问题

        Args:
            problem_type: 问题类型
            description: 描述
            priority: 优先级
            context: 上下文

        Returns:
            创建的问题
        """
        with self.lock:
            problem = Problem(
                problem_type=problem_type,
                description=description,
                priority=priority,
                context=context or {}
            )

            self.problems[problem.id] = problem

            self.stats["total_problems"] += 1

            return problem

    def solve_problem(self, problem_id: str, solution: str):
        """
        解决问题

        Args:
            problem_id: 问题ID
            solution: 解决方案
        """
        with self.lock:
            problem = self.problems.get(problem_id)
            if problem:
                problem.status = "solved"
                problem.context["solution"] = solution

                # 可能产生新的洞察
                self.add_insight(
                    name=f"solution_{problem_id[:8]}",
                    content=f"问题: {problem.description}\n解决方案: {solution}",
                    effectiveness=0.5
                )

    def get_strategy(self, name: str) -> Optional[MetaMemoryItem]:
        """获取策略"""
        return self.strategies.get(name)

    def get_pattern(self, name: str) -> Optional[MetaMemoryItem]:
        """获取模式"""
        return self.patterns.get(name)

    def get_insight(self, name: str) -> Optional[MetaMemoryItem]:
        """获取洞察"""
        return self.insights.get(name)

    def get_problem(self, problem_id: str) -> Optional[Problem]:
        """获取问题"""
        return self.problems.get(problem_id)

    def get_active_problems(self) -> List[Problem]:
        """获取活跃问题"""
        with self.lock:
            return [
                problem for problem in self.problems.values()
                if problem.status == "open"
            ]

    def update_strategy_effectiveness(self, name: str, new_score: float):
        """
        更新策略有效性

        Args:
            name: 策略名称
            new_score: 新的评分
        """
        with self.lock:
            strategy = self.strategies.get(name)
            if strategy:
                strategy.update_effectiveness(new_score)

    def get_best_strategy(
        self,
        strategy_type: str = None,
        min_usage: int = 0
    ) -> Optional[MetaMemoryItem]:
        """
        获取最佳策略

        Args:
            strategy_type: 策略类型
            min_usage: 最小使用次数

        Returns:
            最佳策略
        """
        with self.lock:
            candidates = []

            for strategy in self.strategies.values():
                # 过滤类型
                if strategy_type and strategy.context.get("type") != strategy_type:
                    continue

                # 过滤使用次数
                if strategy.usage_count < min_usage:
                    continue

                candidates.append(strategy)

            if not candidates:
                return None

            # 按有效性排序
            candidates.sort(key=lambda s: s.effectiveness, reverse=True)

            return candidates[0]

    def analyze_performance(self) -> Dict[str, Any]:
        """
        分析性能

        Returns:
            性能分析报告
        """
        with self.lock:
            report = {
                "timestamp": datetime.now().isoformat(),
                "strategies": {
                    "total": len(self.strategies),
                    "high_effectiveness": len([
                        s for s in self.strategies.values()
                        if s.effectiveness >= 0.8
                    ]),
                    "avg_effectiveness": (
                        sum(s.effectiveness for s in self.strategies.values()) /
                        len(self.strategies)
                        if self.strategies else 0.0
                    )
                },
                "patterns": {
                    "total": len(self.patterns),
                    "frequently_used": len([
                        p for p in self.patterns.values()
                        if p.usage_count >= 5
                    ])
                },
                "insights": {
                    "total": len(self.insights),
                    "recent_count": len([
                        i for i in self.insights.values()
                        if i.last_used and
                        (datetime.now() - i.last_used).days < 7
                    ])
                },
                "operations": {
                    "total": len(self.operation_history),
                    "avg_score": (
                        sum(op.get_overall_score() for op in self.operation_history[-100:]) /
                        min(100, len(self.operation_history))
                        if self.operation_history else 0.0
                    )
                },
                "problems": {
                    "total": len(self.problems),
                    "open": len([p for p in self.problems.values() if p.status == "open"]),
                    "solved": len([p for p in self.problems.values() if p.status == "solved"])
                }
            }

            return report

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            stats = self.stats.copy()

            # 添加实时统计
            stats["current_strategies"] = len(self.strategies)
            stats["current_patterns"] = len(self.patterns)
            stats["current_insights"] = len(self.insights)
            stats["current_problems"] = len(self.problems)
            stats["operation_history_size"] = len(self.operation_history)

            return stats

    def _save_meta_memory(self, memory_type: str, name: str, item: MetaMemoryItem):
        """保存元记忆到文件"""
        file_path = self.storage_path / f"{memory_type}_{name}.json"

        data = {
            "name": name,
            "type": memory_type,
            "content": item.content,
            "effectiveness": item.effectiveness,
            "usage_count": item.usage_count,
            "last_used": item.last_used.isoformat() if item.last_used else None,
            "context": item.context,
            "saved_at": datetime.now().isoformat()
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


class MetaMemoryManager:
    """
    元记忆管理器

    提供更高级的元记忆管理功能
    """

    def __init__(self):
        self.layer = MetaMemoryLayer()

    def learn_from_success(self, strategy_name: str, context: Dict[str, Any]):
        """
        从成功中学习

        Args:
            strategy_name: 策略名称
            context: 上下文
        """
        strategy = self.layer.get_strategy(strategy_name)
        if strategy:
            # 更新有效性
            self.layer.update_strategy_effectiveness(strategy_name, 0.9)

            # 记录模式
            self.layer.add_pattern(
                name=f"success_pattern_{strategy_name}",
                content=f"策略'{strategy_name}'在特定上下文中成功",
                context=context,
                effectiveness=0.8
            )

    def learn_from_failure(self, strategy_name: str, context: Dict[str, Any]):
        """
        从失败中学习

        Args:
            strategy_name: 策略名称
            context: 上下文
        """
        strategy = self.layer.get_strategy(strategy_name)
        if strategy:
            # 更新有效性
            self.layer.update_strategy_effectiveness(strategy_name, 0.3)

            # 添加问题
            self.layer.add_problem(
                problem_type="strategy_failure",
                description=f"策略'{strategy_name}'失败",
                priority=4,
                context={**context, "strategy": strategy_name}
            )

    def recommend_strategy(
        self,
        problem_type: str,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """
        推荐策略

        Args:
            problem_type: 问题类型
            context: 上下文

        Returns:
            推荐的策略名称
        """
        # 查找相关策略
        best_strategy = self.layer.get_best_strategy(
            strategy_type=problem_type,
            min_usage=1
        )

        if best_strategy and best_strategy.effectiveness >= 0.7:
            return best_strategy.content

        return None

    def generate_report(self) -> str:
        """
        生成性能报告

        Returns:
            报告字符串
        """
        performance = self.layer.analyze_performance()

        report = f"""
元记忆层性能报告
=================
生成时间: {performance['timestamp']}

策略统计：
  总数: {performance['strategies']['total']}
  高效策略: {performance['strategies']['high_effectiveness']}
  平均有效性: {performance['strategies']['avg_effectiveness']:.2%}

模式统计：
  总数: {performance['patterns']['total']}
  常用模式: {performance['patterns']['frequently_used']}

洞察统计：
  总数: {performance['insights']['total']}
  最近使用: {performance['insights']['recent_count']}

操作统计：
  总数: {performance['operations']['total']}
  平均分数: {performance['operations']['avg_score']:.2%}

问题统计：
  总数: {performance['problems']['total']}
  待解决: {performance['problems']['open']}
  已解决: {performance['problems']['solved']}
"""

        return report


# 测试代码
if __name__ == "__main__":
    print("小妖AI原生知识记忆系统 - 元记忆层")
    print("=" * 60)

    # 创建元记忆管理器
    manager = MetaMemoryManager()

    # 添加一些策略
    manager.layer.add_strategy(
        name="semantic_search",
        content="使用语义向量检索相关记忆",
        context={"type": "retrieval"},
        effectiveness=0.85
    )

    manager.layer.add_strategy(
        name="graph_association",
        content="通过知识图谱查找关联实体",
        context={"type": "retrieval"},
        effectiveness=0.75
    )

    manager.layer.add_strategy(
        name="periodic_consolidation",
        content="定期整合短期记忆到长期记忆",
        context={"type": "consolidation"},
        effectiveness=0.70
    )

    print("\n✅ 策略添加成功")

    # 添加一些模式
    manager.layer.add_pattern(
        name="learning_pattern",
        content="通过实践加深理解",
        context={"domain": "learning"},
        effectiveness=0.80
    )

    # 添加一些洞察
    manager.layer.add_insight(
        name="self_awareness",
        content="系统能够识别自己的知识边界",
        effectiveness=0.90
    )

    print("\n✅ 模式和洞察添加成功")

    # 添加问题
    problem = manager.layer.add_problem(
        problem_type="knowledge_gap",
        description="系统缺乏关于深度学习的知识",
        priority=5,
        context={"domain": "AI"}
    )

    print(f"\n✅ 问题添加成功: {problem.description}")

    # 从成功中学习
    manager.learn_from_success(
        "semantic_search",
        {"query": "Python编程", "results": 10}
    )

    print("\n✅ 从成功中学习完成")

    # 推荐策略
    recommended = manager.recommend_strategy(
        "retrieval",
        {"query": "LLM微调"}
    )

    print(f"\n💡 推荐策略: {recommended}")

    # 生成报告
    report = manager.generate_report()
    print("\n" + report)

    print("\n✅ 元记忆层测试通过！")
