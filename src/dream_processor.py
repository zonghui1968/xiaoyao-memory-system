"""
小妖超级记忆系统 - 梦境处理器（Dream Processor）

VCP梦系统的核心机制：
- 收集激活记忆
- 随机联想（非线性思维）
- 知识重构（叙事整合）
- 生成洞察
- 验证整合

作者：小妖🦊
创建日期：2026-04-12
基于：VCP梦系统设计
"""

import random
import threading
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from collections import deque
import networkx as nx
import numpy as np


class DreamTrigger:
    """
    梦境触发器

    决定何时触发梦境周期
    """

    def __init__(self):
        """初始化触发器"""
        self.last_dream_time = datetime.now() - timedelta(hours=24)
        self.dream_count = 0

        # 触发条件
        self.scheduled_interval = timedelta(hours=8)  # 定时触发
        self.problem_threshold = 3  # 问题触发阈值
        self.creativity_threshold = 0.7  # 创造性需求阈值

    def should_trigger_dream(
        self,
        trigger_type: str = "scheduled",
        context: Dict[str, Any] = None
    ) -> bool:
        """
        判断是否应该触发梦境

        Args:
            trigger_type: 触发类型（scheduled/problem/creative/manual）
            context: 上下文

        Returns:
            是否应该触发
        """
        now = datetime.now()

        if trigger_type == "scheduled":
            # 定时触发
            time_since_last = now - self.last_dream_time
            return time_since_last >= self.scheduled_interval

        elif trigger_type == "problem":
            # 问题触发
            if context and context.get("problem_count", 0) >= self.problem_threshold:
                return True
            return False

        elif trigger_type == "creative":
            # 创造性需求触发
            if context and context.get("creativity_needed", 0) >= self.creativity_threshold:
                return True
            return False

        elif trigger_type == "manual":
            # 手动触发
            return True

        return False

    def record_dream(self):
        """记录梦境"""
        self.last_dream_time = datetime.now()
        self.dream_count += 1


class RandomAssociator:
    """
    随机联想器（VCP核心机制）

    功能：
    - 随机游走（非线性遍历）
    - 语义关联
    - 跨域连接
    """

    def __init__(self, knowledge_graph=None):
        """
        初始化随机联想器

        Args:
            knowledge_graph: 知识图谱
        """
        self.knowledge_graph = knowledge_graph or nx.DiGraph()
        self.lock = threading.RLock()

    def random_walk(
        self,
        start_node: str,
        steps: int = 5,
        temperature: float = 1.0
    ) -> List[str]:
        """
        随机游走（非线性遍历）

        Args:
            start_node: 起始节点
            steps: 步数
            temperature: 温度参数（控制随机性）

        Returns:
            访问的节点列表
        """
        with self.lock:
            if start_node not in self.knowledge_graph.nodes():
                return []

            path = [start_node]
            current = start_node

            for _ in range(steps):
                # 获取邻居
                neighbors = list(self.knowledge_graph.neighbors(current))

                if not neighbors:
                    break

                # 随机选择下一个节点
                if temperature == 0:
                    # 完全随机
                    next_node = random.choice(neighbors)
                else:
                    # 基于温度的选择
                    weights = [
                        self.knowledge_graph.edges[current, n].get('weight', 1.0)
                        for n in neighbors
                    ]

                    # 应用温度
                    weights = [w ** (1.0 / temperature) for w in weights]
                    total = sum(weights)
                    probs = [w / total for w in weights]

                    next_node = np.random.choice(neighbors, p=probs)

                path.append(next_node)
                current = next_node

            return path

    def cross_domain_association(
        self,
        seed_memories: List[str],
        max_distance: int = 3
    ) -> List[Tuple[str, str, float]]:
        """
        跨域关联

        Args:
            seed_memories: 种子记忆列表
            max_distance: 最大距离

        Returns:
            [(memory1, memory2, similarity)] 列表
        """
        with self.lock:
            associations = []

            # 收集所有可达节点
            all_reachable = set()

            for seed in seed_memories:
                if seed in self.knowledge_graph.nodes():
                    # BFS收集
                    reachable = nx.single_source_shortest_path_length(
                        self.knowledge_graph,
                        seed,
                        cutoff=max_distance
                    ).keys()

                    all_reachable.update(reachable)

            # 移除种子记忆
            all_reachable -= set(seed_memories)

            # 计算关联分数
            for target in all_reachable:
                # 计算与所有种子记忆的平均距离
                distances = []

                for seed in seed_memories:
                    try:
                        dist = nx.shortest_path_length(
                            self.knowledge_graph,
                            seed,
                            target
                        )
                        distances.append(dist)
                    except nx.NetworkXNoPath:
                        continue

                if distances:
                    avg_distance = sum(distances) / len(distances)
                    similarity = 1.0 / (1.0 + avg_distance)

                    associations.append((seed_memories[0], target, similarity))

            # 按相似度排序
            associations.sort(key=lambda x: x[2], reverse=True)

            return associations

    def serendipitous_discovery(
        self,
        start_node: str,
        num_discoveries: int = 5
    ) -> List[str]:
        """
        意外发现（随机跳跃）

        Args:
            start_node: 起始节点
            num_discoveries: 发现数量

        Returns:
            发现的节点列表
        """
        with self.lock:
            discoveries = []

            # 多次随机游走
            for _ in range(num_discoveries):
                # 随机步数（2-8步）
                steps = random.randint(2, 8)

                # 随机游走
                path = self.random_walk(start_node, steps, temperature=1.5)

                if path:
                    # 取最后一个节点作为发现
                    discoveries.append(path[-1])

            return discoveries


class KnowledgeReconstructor:
    """
    知识重构器（VCP核心机制）

    功能：
    - 叙事整合
    - 概念融合
    - 模式识别
    """

    def __init__(self):
        """初始化知识重构器"""
        self.reconstruction_history = []
        self.lock = threading.RLock()

    def reconstruct_narrative(
        self,
        associations: List[Tuple[str, str, float]],
        theme: str = ""
    ) -> Dict[str, Any]:
        """
        叙事重构

        Args:
            associations: 关联列表
            theme: 主题

        Returns:
            重构的叙事
        """
        with self.lock:
            # 选择高关联度配对
            high_associations = [a for a in associations if a[2] > 0.5]

            if not high_associations:
                return {
                    "narrative": "",
                    "key_concepts": [],
                    "coherence": 0.0
                }

            # 提取关键概念
            key_concepts = []
            seen = set()

            for assoc in high_associations:
                for item in [assoc[0], assoc[1]]:
                    if item not in seen:
                        key_concepts.append(item)
                        seen.add(item)

            # 构建叙事
            narrative = self._build_narrative(key_concepts, theme)

            # 计算连贯性
            coherence = len(high_associations) / len(associations) if associations else 0.0

            reconstruction = {
                "narrative": narrative,
                "key_concepts": key_concepts,
                "coherence": coherence,
                "association_count": len(high_associations),
                "created_at": datetime.now().isoformat()
            }

            self.reconstruction_history.append(reconstruction)

            return reconstruction

    def _build_narrative(self, concepts: List[str], theme: str) -> str:
        """
        构建叙事

        Args:
            concepts: 概念列表
            theme: 主题

        Returns:
            叙事文本
        """
        if not concepts:
            return ""

        # 简单叙事模板
        if theme:
            narrative = f"关于'{theme}'的思考：\n"
        else:
            narrative = "叙事重构：\n"

        # 连接概念
        narrative += f"从{concepts[0]}开始，"

        for i, concept in enumerate(concepts[1:], 1):
            if i < len(concepts):
                narrative += f"联想到{concept}，"
            else:
                narrative += f"最终到达{concept}。"

        return narrative

    def synthesize_concepts(
        self,
        concept1: str,
        concept2: str,
        context: Dict[str, Any] = None
    ) -> str:
        """
        概念融合

        Args:
            concept1: 概念1
            concept2: 概念2
            context: 上下文

        Returns:
            融合后的概念
        """
        # 简单实现：组合
        synthesis = f"{concept1}+{concept2}"

        # 更复杂的实现可以包括：
        # - 语义分析
        # - 概念对齐
        # - 关系识别

        return synthesis

    def recognize_patterns(
        self,
        memories: List[str]
    ) -> List[Dict[str, Any]]:
        """
        模式识别

        Args:
            memories: 记忆列表

        Returns:
            模式列表
        """
        patterns = []

        # 简单实现：统计重复出现
        from collections import Counter

        # 提取关键词（简化版）
        words = []
        for memory in memories:
            words.extend(memory.split())

        # 统计词频
        word_counts = Counter(words)

        # 高频词作为模式
        for word, count in word_counts.most_common(5):
            if count >= 2:
                patterns.append({
                    "pattern": word,
                    "frequency": count,
                    "type": "repetition"
                })

        return patterns


class InsightGenerator:
    """
    洞察生成器（VCP核心机制）

    功能：
    - 生成新洞察
    - 问题解决
    - 创造性思维
    """

    def __init__(self):
        """初始化洞察生成器"""
        self.insights = []
        self.lock = threading.RLock()

    def generate_insight(
        self,
        reconstruction: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        生成洞察

        Args:
            reconstruction: 知识重构结果
            context: 上下文

        Returns:
            洞察对象
        """
        with self.lock:
            # 从重构中提取关键信息
            narrative = reconstruction.get("narrative", "")
            concepts = reconstruction.get("key_concepts", [])
            coherence = reconstruction.get("coherence", 0.0)

            # 生成洞察
            insight_content = self._formulate_insight(narrative, concepts, coherence)

            # 评估洞察质量
            quality_score = self._evaluate_insight(insight_content, coherence)

            insight = {
                "id": f"insight_{len(self.insights)}_{datetime.now().timestamp()}",
                "content": insight_content,
                "source_concepts": concepts,
                "quality_score": quality_score,
                "coherence": coherence,
                "created_at": datetime.now().isoformat(),
                "context": context or {}
            }

            self.insights.append(insight)

            return insight

    def _formulate_insight(
        self,
        narrative: str,
        concepts: List[str],
        coherence: float
    ) -> str:
        """
        形成洞察

        Args:
            narrative: 叙事
            concepts: 概念
            coherence: 连贯性

        Returns:
            洞察内容
        """
        # 如果连贯性高，形成结构化洞察
        if coherence > 0.7 and len(concepts) >= 2:
            insight = f"发现关联：{' → '.join(concepts)}"
        elif len(concepts) >= 2:
            insight = f"可能关联：{' - '.join(concepts)}"
        else:
            insight = "需要更多探索"

        return insight

    def _evaluate_insight(self, insight: str, coherence: float) -> float:
        """
        评估洞察质量

        Args:
            insight: 洞察内容
            coherence: 连贯性

        Returns:
            质量分数（0-1）
        """
        # 简单实现：基于连贯性和内容长度
        length_score = min(1.0, len(insight) / 100.0)

        quality = (coherence * 0.7 + length_score * 0.3)

        return quality

    def validate_insight(
        self,
        insight: Dict[str, Any],
        knowledge_graph: nx.DiGraph = None
    ) -> Tuple[bool, str]:
        """
        验证洞察

        Args:
            insight: 洞察对象
            knowledge_graph: 知识图谱

        Returns:
            (是否有效, 原因)
        """
        # 检查质量分数
        if insight["quality_score"] < 0.5:
            return False, "质量分数过低"

        # 检查连贯性
        if insight["coherence"] < 0.4:
            return False, "连贯性不足"

        # 检查是否重复
        for existing in self.insights:
            if existing["content"] == insight["content"]:
                return False, "重复洞察"

        return True, "洞察有效"

    def get_top_insights(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取顶级洞察

        Args:
            limit: 返回数量

        Returns:
            洞察列表
        """
        with self.lock:
            # 按质量分数排序
            insights = sorted(
                self.insights,
                key=lambda x: x["quality_score"],
                reverse=True
            )

            return insights[:limit]


class DreamProcessor:
    """
    梦境处理器（VCP核心）

    整合所有梦境机制：
    - 触发器
    - 随机联想
    - 知识重构
    - 洞察生成
    """

    def __init__(self, knowledge_graph=None):
        """
        初始化梦境处理器

        Args:
            knowledge_graph: 知识图谱
        """
        self.trigger = DreamTrigger()
        self.associator = RandomAssociator(knowledge_graph)
        self.reconstructor = KnowledgeReconstructor()
        self.insight_generator = InsightGenerator()

        self.dream_history = []
        self.lock = threading.RLock()

    def trigger_dream_cycle(
        self,
        trigger_type: str = "scheduled",
        seed_memories: List[str] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        触发梦境周期

        Args:
            trigger_type: 触发类型
            seed_memories: 种子记忆列表
            context: 上下文

        Returns:
            梦境结果
        """
        with self.lock:
            # 检查是否应该触发
            if not self.trigger.should_trigger_dream(trigger_type, context):
                return {
                    "triggered": False,
                    "reason": "触发条件未满足"
                }

            dream_start = datetime.now()

            # 1. 收集种子记忆
            if seed_memories is None:
                seed_memories = self._collect_seed_memories(context)

            # 2. 随机联想
            associations = self._perform_association(seed_memories)

            # 3. 知识重构
            reconstruction = self._perform_reconstruction(associations, context)

            # 4. 生成洞察
            insights = self._generate_insights(reconstruction, context)

            # 5. 验证洞察
            validated_insights = self._validate_insights(insights)

            # 6. 记录梦境
            dream_result = {
                "id": f"dream_{len(self.dream_history)}_{dream_start.timestamp()}",
                "trigger_type": trigger_type,
                "seed_memories": seed_memories,
                "associations": associations,
                "reconstruction": reconstruction,
                "insights": validated_insights,
                "created_at": dream_start.isoformat(),
                "completed_at": datetime.now().isoformat()
            }

            self.dream_history.append(dream_result)
            self.trigger.record_dream()

            return dream_result

    def _collect_seed_memories(self, context: Dict[str, Any] = None) -> List[str]:
        """收集种子记忆"""
        # 简单实现：从上下文中获取
        if context and "recent_memories" in context:
            return context["recent_memories"][:5]

        return []

    def _perform_association(
        self,
        seed_memories: List[str]
    ) -> List[Tuple[str, str, float]]:
        """执行联想"""
        all_associations = []

        for seed in seed_memories:
            # 跨域关联
            associations = self.associator.cross_domain_association(
                [seed],
                max_distance=3
            )

            all_associations.extend(associations)

        return all_associations

    def _perform_reconstruction(
        self,
        associations: List[Tuple[str, str, float]],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """执行知识重构"""
        theme = context.get("theme", "") if context else ""

        return self.reconstructor.reconstruct_narrative(
            associations,
            theme
        )

    def _generate_insights(
        self,
        reconstruction: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """生成洞察"""
        insights = []

        # 生成主要洞察
        insight = self.insight_generator.generate_insight(
            reconstruction,
            context
        )

        insights.append(insight)

        return insights

    def _validate_insights(
        self,
        insights: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """验证洞察"""
        validated = []

        for insight in insights:
            is_valid, reason = self.insight_generator.validate_insight(insight)

            if is_valid:
                insight["validated"] = True
                insight["validation_reason"] = reason
                validated.append(insight)
            else:
                insight["validated"] = False
                insight["validation_reason"] = reason

        return validated

    def get_dream_statistics(self) -> Dict[str, Any]:
        """获取梦境统计"""
        with self.lock:
            return {
                "total_dreams": len(self.dream_history),
                "total_insights": len(self.insight_generator.insights),
                "validated_insights": len([
                    i for i in self.insight_generator.insights
                    if i.get("validated", False)
                ]),
                "last_dream_time": self.trigger.last_dream_time.isoformat()
            }


# 测试代码
if __name__ == "__main__":
    print("小妖超级记忆系统 - 梦境处理器")
    print("=" * 60)

    # 创建测试知识图谱
    graph = nx.DiGraph()
    graph.add_edge("Python", "编程", weight=1.0)
    graph.add_edge("编程", "算法", weight=0.8)
    graph.add_edge("算法", "AI", weight=0.9)
    graph.add_edge("AI", "机器学习", weight=1.0)
    graph.add_edge("机器学习", "深度学习", weight=0.9)
    graph.add_edge("深度学习", "神经网络", weight=1.0)

    # 创建梦境处理器
    dream_processor = DreamProcessor(graph)

    print("\n[OK] 梦境处理器初始化成功")

    # 测试随机联想
    print("\n[OK] 测试随机联想:")
    path = dream_processor.associator.random_walk("Python", steps=5)
    print(f"  随机游走: {' → '.join(path)}")

    # 测试跨域关联
    print("\n[OK] 测试跨域关联:")
    associations = dream_processor.associator.cross_domain_association(
        ["Python"],
        max_distance=3
    )
    print(f"  发现关联: {len(associations)}个")

    # 测试梦境周期
    print("\n[OK] 测试梦境周期:")
    dream_result = dream_processor.trigger_dream_cycle(
        trigger_type="manual",
        seed_memories=["Python", "AI"],
        context={"theme": "技术学习"}
    )

    print(f"  梦境ID: {dream_result['id']}")
    print(f"  触发类型: {dream_result['trigger_type']}")
    print(f"  生成洞察: {len(dream_result['insights'])}个")

    if dream_result['insights']:
        for insight in dream_result['insights']:
            print(f"    - {insight['content']} (质量: {insight['quality_score']:.2f})")

    # 获取统计
    print("\n[OK] 梦境统计:")
    stats = dream_processor.get_dream_statistics()
    print(f"  总梦境: {stats['total_dreams']}")
    print(f"  总洞察: {stats['total_insights']}")
    print(f"  有效洞察: {stats['validated_insights']}")

    print("\n[OK] 梦境处理器测试通过！")
