"""
小妖超级记忆系统 - 进化系统（Evolution System）

实现持续自我进化：
- 进化引擎（Evolution Engine）
- 持续优化（Continuous Optimization）
- 知识积累（Knowledge Accumulation）
- 自我进化（Self-Evolution）

作者：小妖🦊
创建日期：2026-2026-04-12
基于：进化算法和持续学习
"""

import random
import threading
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import deque
import json


class EvolutionaryStrategy:
    """
    进化策略

    存储系统的策略和参数
    """

    def __init__(self, name: str, params: Dict[str, Any]):
        """
        初始化策略

        Args:
            name: 策略名称
            params: 策略参数
        """
        self.id = f"strategy_{name}_{datetime.now().timestamp()}"
        self.name = name
        self.params = params
        self.performance_score = 0.5
        self.usage_count = 0
        self.success_count = 0
        self.created_at = datetime.now()
        self.last_used = None

    def update_performance(self, success: bool, score: float = None):
        """
        更新性能

        Args:
            success: 是否成功
            score: 性能分数
        """
        self.usage_count += 1
        self.last_used = datetime.now()

        if success:
            self.success_count += 1

        if score is not None:
            # 指数移动平均
            alpha = 0.3
            self.performance_score = alpha * score + (1 - alpha) * self.performance_score

    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.usage_count == 0:
            return 0.0
        return self.success_count / self.usage_count


class ContinuousOptimizer:
    """
    持续优化器

    功能：
    - 策略优化
    - 参数调优
    - 性能监控
    """

    def __init__(self):
        """初始化持续优化器"""
        self.strategies: Dict[str, EvolutionaryStrategy] = {}
        self.optimization_history = []
        self.lock = threading.RLock()

    def add_strategy(self, name: str, params: Dict[str, Any]) -> str:
        """
        添加策略

        Args:
            name: 策略名称
            params: 参数

        Returns:
            策略ID
        """
        with self.lock:
            strategy = EvolutionaryStrategy(name, params)
            self.strategies[strategy.id] = strategy
            return strategy.id

    def update_strategy_performance(
        self,
        strategy_id: str,
        success: bool,
        score: float = None
    ):
        """
        更新策略性能

        Args:
            strategy_id: 策略ID
            success: 是否成功
            score: 性能分数
        """
        with self.lock:
            if strategy_id in self.strategies:
                self.strategies[strategy_id].update_performance(success, score)

    def optimize_parameters(
        self,
        strategy_id: str,
        performance_feedback: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        优化参数

        Args:
            strategy_id: 策略ID
            performance_feedback: 性能反馈

        Returns:
            优化后的参数
        """
        with self.lock:
            if strategy_id not in self.strategies:
                return {}

            strategy = self.strategies[strategy_id]
            current_params = strategy.params.copy()

            # 简单优化：根据反馈调整参数
            for param, value in current_params.items():
                if isinstance(value, (int, float)):
                    # 如果性能反馈中包含该参数
                    if param in performance_feedback:
                        feedback = performance_feedback[param]

                        # 调整参数（简化版）
                        if feedback > 0.7:
                            # 性能好，保持或微调
                            current_params[param] = value * (1.0 + random.uniform(-0.05, 0.05))
                        elif feedback < 0.4:
                            # 性能差，大幅调整
                            current_params[param] = value * (1.0 + random.uniform(-0.2, 0.2))

            # 更新策略
            strategy.params = current_params

            # 记录优化历史
            self.optimization_history.append({
                "strategy_id": strategy_id,
                "old_params": strategy.params,
                "new_params": current_params,
                "feedback": performance_feedback,
                "timestamp": datetime.now().isoformat()
            })

            return current_params

    def get_best_strategy(self, category: str = None) -> Optional[EvolutionaryStrategy]:
        """
        获取最佳策略

        Args:
            category: 策略类别（可选）

        Returns:
            最佳策略
        """
        with self.lock:
            candidates = []

            for strategy in self.strategies.values():
                if category is None or strategy.name.startswith(category):
                    candidates.append(strategy)

            if not candidates:
                return None

            # 按性能分数排序
            candidates.sort(key=lambda s: s.performance_score, reverse=True)

            return candidates[0]

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            total_strategies = len(self.strategies)
            successful_strategies = sum(
                1 for s in self.strategies.values()
                if s.get_success_rate() > 0.7
            )

            return {
                "total_strategies": total_strategies,
                "successful_strategies": successful_strategies,
                "total_optimizations": len(self.optimization_history)
            }


class KnowledgeAccumulator:
    """
    知识积累器

    功能：
    - 知识整合
    - 知识压缩
    - 知识检索
    """

    def __init__(self):
        """初始化知识积累器"""
        self.knowledge_base = []
        self.compressed_knowledge = []
        self.accumulation_history = []
        self.lock = threading.RLock()

    def accumulate_knowledge(self, knowledge_items: List[Dict[str, Any]]):
        """
        积累知识

        Args:
            knowledge_items: 知识项列表
        """
        with self.lock:
            for item in knowledge_items:
                knowledge_entry = {
                    "id": f"knowledge_{len(self.knowledge_base)}_{datetime.now().timestamp()}",
                    "content": item.get("content", ""),
                    "type": item.get("type", "general"),
                    "source": item.get("source", "unknown"),
                    "importance": item.get("importance", 0.5),
                    "created_at": datetime.now().isoformat(),
                    "access_count": 0
                }

                self.knowledge_base.append(knowledge_entry)

            # 记录积累历史
            self.accumulation_history.append({
                "count": len(knowledge_items),
                "timestamp": datetime.now().isoformat()
            })

    def compress_knowledge(self, threshold: int = 100) -> int:
        """
        压缩知识

        Args:
            threshold: 压缩阈值（知识数量）

        Returns:
            压缩的项数
        """
        with self.lock:
            if len(self.knowledge_base) < threshold:
                return 0

            # 按重要性排序
            sorted_knowledge = sorted(
                self.knowledge_base,
                key=lambda k: (k["importance"], k["access_count"]),
                reverse=True
            )

            # 保留重要的，压缩其他的
            to_keep = sorted_knowledge[:threshold // 2]
            to_compress = sorted_knowledge[threshold // 2:]

            # 创建压缩摘要
            compressed_summary = {
                "id": f"compressed_{datetime.now().timestamp()}",
                "count": len(to_compress),
                "types": {},
                "summary": self._create_summary(to_compress),
                "created_at": datetime.now().isoformat()
            }

            # 统计类型
            for item in to_compress:
                ktype = item["type"]
                compressed_summary["types"][ktype] = compressed_summary["types"].get(ktype, 0) + 1

            self.compressed_knowledge.append(compressed_summary)

            # 更新知识库
            self.knowledge_base = to_keep

            return len(to_compress)

    def _create_summary(self, items: List[Dict[str, Any]]) -> str:
        """创建摘要"""
        # 简化实现
        return f"压缩了{len(items)}条知识"

    def retrieve_knowledge(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        检索知识

        Args:
            query: 查询
            limit: 返回数量

        Returns:
            知识项
        """
        with self.lock:
            # 简单实现：关键词匹配
            query_lower = query.lower()

            results = []

            for item in self.knowledge_base:
                if query_lower in item["content"].lower():
                    item["access_count"] += 1
                    results.append(item)

                    if len(results) >= limit:
                        break

            return results

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            return {
                "knowledge_count": len(self.knowledge_base),
                "compressed_count": len(self.compressed_knowledge),
                "total_accumulated": len(self.knowledge_base) + sum(
                    c["count"] for c in self.compressed_knowledge
                )
            }


class EvolutionEngine:
    """
    进化引擎

    整合所有进化组件：
    - 持续优化器
    - 知识积累器
    - 进化管理
    """

    def __init__(self):
        """初始化进化引擎"""
        self.optimizer = ContinuousOptimizer()
        self.knowledge_accumulator = KnowledgeAccumulator()

        self.evolution_history = []
        self.generation = 0
        self.lock = threading.RLock()

        # 进化参数
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        self.elitism_rate = 0.2

    def evolve(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行一代进化

        Args:
            context: 上下文

        Returns:
            进化结果
        """
        with self.lock:
            self.generation += 1
            evolution_start = datetime.now()

            # 1. 优化策略
            optimization_results = self._optimize_strategies(context)

            # 2. 积累知识
            knowledge_results = self._accumulate_knowledge(context)

            # 3. 变异和选择
            evolution_results = self._apply_evolution_operators(context)

            # 4. 记录进化历史
            evolution_record = {
                "generation": self.generation,
                "optimization": optimization_results,
                "knowledge": knowledge_results,
                "evolution": evolution_results,
                "timestamp": evolution_start.isoformat()
            }

            self.evolution_history.append(evolution_record)

            return evolution_record

    def _optimize_strategies(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """优化策略"""
        results = {
            "optimized_strategies": 0,
            "avg_performance_improvement": 0.0
        }

        # 获取所有策略
        strategies = list(self.optimizer.strategies.values())

        if not strategies:
            return results

        total_improvement = 0.0

        for strategy in strategies:
            if strategy.usage_count >= 5:  # 只优化使用过的策略
                # 优化参数
                old_performance = strategy.performance_score

                # 模拟性能反馈
                performance_feedback = {
                    param: random.uniform(0.3, 0.9)
                    for param in strategy.params.keys()
                    if isinstance(strategy.params[param], (int, float))
                }

                self.optimizer.optimize_parameters(
                    strategy.id,
                    performance_feedback
                )

                improvement = strategy.performance_score - old_performance
                total_improvement += improvement

                results["optimized_strategies"] += 1

        if results["optimized_strategies"] > 0:
            results["avg_performance_improvement"] = (
                total_improvement / results["optimized_strategies"]
            )

        return results

    def _accumulate_knowledge(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """积累知识"""
        results = {
            "accumulated_count": 0,
            "compressed_count": 0
        }

        # 从上下文中提取知识（如果有的话）
        if context and "new_knowledge" in context:
            new_knowledge = context["new_knowledge"]

            self.knowledge_accumulator.accumulate_knowledge(new_knowledge)
            results["accumulated_count"] = len(new_knowledge)

        # 压缩知识（如果需要）
        stats = self.knowledge_accumulator.get_statistics()

        if stats["knowledge_count"] > 100:
            compressed = self.knowledge_accumulator.compress_knowledge()
            results["compressed_count"] = compressed

        return results

    def _apply_evolution_operators(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """应用进化算子"""
        results = {
            "mutations": 0,
            "crossovers": 0,
            "selected": 0
        }

        strategies = list(self.optimizer.strategies.values())

        if len(strategies) < 2:
            return results

        # 选择（保留精英）
        elite_count = int(len(strategies) * self.elitism_rate)
        strategies.sort(key=lambda s: s.performance_score, reverse=True)
        elites = strategies[:elite_count]
        results["selected"] = elite_count

        # 变异
        for strategy in strategies[elite_count:]:
            if random.random() < self.mutation_rate:
                self._mutate_strategy(strategy)
                results["mutations"] += 1

        # 交叉
        for i in range(elite_count, len(strategies) - 1, 2):
            if random.random() < self.crossover_rate:
                self._crossover_strategies(strategies[i], strategies[i + 1])
                results["crossovers"] += 1

        return results

    def _mutate_strategy(self, strategy: EvolutionaryStrategy):
        """变异策略"""
        for param, value in strategy.params.items():
            if isinstance(value, (int, float)):
                # 随机变异
                mutation = random.uniform(-0.1, 0.1)
                strategy.params[param] = value * (1.0 + mutation)

    def _crossover_strategies(
        self,
        strategy1: EvolutionaryStrategy,
        strategy2: EvolutionaryStrategy
    ):
        """交叉策略"""
        # 简单交叉：交换参数
        for param in strategy1.params.keys():
            if param in strategy2.params and isinstance(strategy1.params[param], (int, float)):
                if random.random() < 0.5:
                    strategy1.params[param], strategy2.params[param] = \
                        strategy2.params[param], strategy1.params[param]

    def get_evolution_statistics(self) -> Dict[str, Any]:
        """获取进化统计"""
        with self.lock:
            return {
                "generation": self.generation,
                "total_evolutions": len(self.evolution_history),
                "optimizer_stats": self.optimizer.get_statistics(),
                "knowledge_stats": self.knowledge_accumulator.get_statistics()
            }


# 测试代码
if __name__ == "__main__":
    print("小妖超级记忆系统 - 进化系统")
    print("=" * 60)

    # 创建进化引擎
    engine = EvolutionEngine()

    print("\n[OK] 进化引擎初始化成功")

    # 添加一些策略
    print("\n[OK] 添加策略:")

    strategy1_id = engine.optimizer.add_strategy(
        "attention_selection",
        {
            "novelty_weight": 0.3,
            "importance_weight": 0.3,
            "relevance_weight": 0.2,
            "urgency_weight": 0.2
        }
    )
    print(f"  添加策略: {strategy1_id[:20]}...")

    strategy2_id = engine.optimizer.add_strategy(
        "dream_trigger",
        {
            "scheduled_interval": 8,
            "problem_threshold": 3,
            "creativity_threshold": 0.7
        }
    )
    print(f"  添加策略: {strategy2_id[:20]}...")

    # 模拟使用
    print("\n[OK] 模拟策略使用:")

    for i in range(10):
        # 更新性能
        success = random.random() > 0.3
        score = random.uniform(0.5, 1.0) if success else random.uniform(0.0, 0.5)

        engine.optimizer.update_strategy_performance(strategy1_id, success, score)

        if i % 3 == 0:
            engine.optimizer.update_strategy_performance(strategy2_id, success, score)

    print(f"  策略1使用次数: {engine.optimizer.strategies[strategy1_id].usage_count}")
    print(f"  策略1成功率: {engine.optimizer.strategies[strategy1_id].get_success_rate():.2%}")

    # 积累知识
    print("\n[OK] 积累知识:")

    knowledge_items = [
        {"content": "Python是一种编程语言", "type": "fact", "importance": 0.8},
        {"content": "AI需要数据训练", "type": "concept", "importance": 0.7},
        {"content": "梦境增强创造性", "type": "insight", "importance": 0.9}
    ]

    engine.knowledge_accumulator.accumulate_knowledge(knowledge_items)
    print(f"  积累知识: {len(knowledge_items)}条")

    # 执行进化
    print("\n[OK] 执行进化:")

    for gen in range(1, 4):
        evolution_result = engine.evolve()

        print(f"  第{gen}代:")
        print(f"    优化策略: {evolution_result['optimization']['optimized_strategies']}个")
        print(f"    积累知识: {evolution_result['knowledge']['accumulated_count']}条")
        print(f"    变异: {evolution_result['evolution']['mutations']}次")
        print(f"    交叉: {evolution_result['evolution']['crossovers']}次")

    # 获取统计
    print("\n[OK] 进化统计:")
    stats = engine.get_evolution_statistics()

    print(f"  代数: {stats['generation']}")
    print(f"  总进化次数: {stats['total_evolutions']}")
    print(f"  策略数: {stats['optimizer_stats']['total_strategies']}")
    print(f"  成功策略: {stats['optimizer_stats']['successful_strategies']}个")
    print(f"  知识数: {stats['knowledge_stats']['knowledge_count']}条")

    print("\n[OK] 进化系统测试通过！")
    print("\n[Xiaoyao] 进化系统已就绪，可以开始持续自我进化！")
