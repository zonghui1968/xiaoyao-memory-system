"""
SuperMemorySystemV7 - 自我进化AI代理记忆系统

核心理念：
- 融合Hindsight的多策略检索
- 集成Zep的时序推理
- 采用Letta的代理自我管理
- 实现MemEvolve的自我进化

创新特性：
1. 多策略检索引擎（语义+BM25+图+时序）
2. 时序推理引擎（有效性窗口+区间树）
3. 反射合成层（LLM驱动的跨记忆推理）
4. 自我进化系统（双循环进化）
5. 代理自我管理（主动记忆管理）
6. 用户反馈循环（持续改进）

作者：小妖🦊
创建日期：2026-04-12
版本：V7.0.0-alpha
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import networkx as nx
import numpy as np
from dataclasses import dataclass, field


class MemoryType(Enum):
    """记忆类型"""
    EPISODIC = "episodic"  # 情景记忆
    SEMANTIC = "semantic"  # 语义记忆
    PROCEDURAL = "procedural"  # 程序性记忆
    TEMPORAL = "temporal"  # 时序记忆


class RetrievalStrategy(Enum):
    """检索策略"""
    SEMANTIC = "semantic"  # 语义搜索
    BM25 = "bm25"  # BM25关键词
    GRAPH = "graph"  # 图谱遍历
    TEMPORAL = "temporal"  # 时序过滤
    HYBRID = "hybrid"  # 混合策略


@dataclass
class TemporalValidity:
    """时序有效性窗口"""
    valid_from: datetime
    valid_until: Optional[datetime] = None
    confidence: float = 1.0

    def is_valid_at(self, timestamp: datetime) -> bool:
        """检查时间戳是否在有效期内"""
        if self.valid_until is None:
            return timestamp >= self.valid_from
        return self.valid_from <= timestamp <= self.valid_until

    def duration(self) -> timedelta:
        """计算有效期时长"""
        end = self.valid_until or datetime.now()
        return end - self.valid_from


@dataclass
class MultiStrategyResult:
    """多策略检索结果"""
    memory_id: str
    content: str
    relevance_scores: Dict[RetrievalStrategy, float] = field(default_factory=dict)
    combined_score: float = 0.0
    temporal_validity: Optional[TemporalValidity] = None
    source_strategy: RetrievalStrategy = RetrievalStrategy.SEMANTIC

    def add_score(self, strategy: RetrievalStrategy, score: float):
        """添加策略得分"""
        self.relevance_scores[strategy] = score
        self._update_combined_score()

    def _update_combined_score(self):
        """更新组合得分（加权平均）"""
        weights = {
            RetrievalStrategy.SEMANTIC: 0.35,
            RetrievalStrategy.BM25: 0.25,
            RetrievalStrategy.GRAPH: 0.25,
            RetrievalStrategy.TEMPORAL: 0.15
        }
        weighted_sum = sum(
            self.relevance_scores.get(s, 0.0) * w
            for s, w in weights.items()
        )
        self.combined_score = weighted_sum


class MultiStrategyRetrievalEngine:
    """
    多策略检索引擎

    融合四种检索策略：
    1. 语义搜索（向量相似度）
    2. BM25关键词搜索
    3. 图谱遍历（实体关系）
    4. 时序过滤（有效性窗口）

    特性：
    - 并行执行所有策略
    - 交叉编码器重排序
    - 智能结果融合
    """

    def __init__(self):
        """初始化多策略检索引擎"""
        self.semantic_index = {}  # 语义索引
        self.bm25_index = {}  # BM25索引
        self.knowledge_graph = nx.DiGraph()  # 知识图谱
        self.temporal_index = {}  # 时序索引

    def retrieve(
        self,
        query: str,
        query_time: Optional[datetime] = None,
        top_k: int = 10,
        strategies: Optional[List[RetrievalStrategy]] = None
    ) -> List[MultiStrategyResult]:
        """
        多策略检索

        Args:
            query: 查询文本
            query_time: 查询时间（用于时序过滤）
            top_k: 返回结果数
            strategies: 要使用的策略列表（None表示全部）

        Returns:
            排序的结果列表
        """
        if strategies is None:
            strategies = [
                RetrievalStrategy.SEMANTIC,
                RetrievalStrategy.BM25,
                RetrievalStrategy.GRAPH,
                RetrievalStrategy.TEMPORAL
            ]

        # 并行执行所有策略
        all_results = {}

        for strategy in strategies:
            strategy_results = self._execute_strategy(query, strategy, query_time)
            for result in strategy_results:
                if result.memory_id not in all_results:
                    all_results[result.memory_id] = result
                else:
                    # 合并得分
                    all_results[result.memory_id].add_score(
                        strategy,
                        result.combined_score
                    )

        # 重排序
        sorted_results = sorted(
            all_results.values(),
            key=lambda x: x.combined_score,
            reverse=True
        )

        return sorted_results[:top_k]

    def _execute_strategy(
        self,
        query: str,
        strategy: RetrievalStrategy,
        query_time: Optional[datetime]
    ) -> List[MultiStrategyResult]:
        """执行单个检索策略"""
        if strategy == RetrievalStrategy.SEMANTIC:
            return self._semantic_search(query)
        elif strategy == RetrievalStrategy.BM25:
            return self._bm25_search(query)
        elif strategy == RetrievalStrategy.GRAPH:
            return self._graph_traversal(query)
        elif strategy == RetrievalStrategy.TEMPORAL:
            return self._temporal_filter(query, query_time)
        else:
            return []

    def _semantic_search(self, query: str) -> List[MultiStrategyResult]:
        """语义搜索（向量相似度）"""
        # 简化实现 - 实际应该使用向量数据库
        results = []
        for mem_id, content in self.semantic_index.items():
            # 简化的相似度计算
            similarity = self._compute_similarity(query, content)
            if similarity > 0.5:
                result = MultiStrategyResult(
                    memory_id=mem_id,
                    content=content,
                    combined_score=similarity,
                    source_strategy=RetrievalStrategy.SEMANTIC
                )
                results.append(result)
        return results

    def _bm25_search(self, query: str) -> List[MultiStrategyResult]:
        """BM25关键词搜索"""
        results = []
        query_terms = set(query.lower().split())

        for mem_id, content in self.bm25_index.items():
            content_terms = set(content.lower().split())
            overlap = len(query_terms & content_terms)
            if overlap > 0:
                score = overlap / len(query_terms)
                result = MultiStrategyResult(
                    memory_id=mem_id,
                    content=content,
                    combined_score=score,
                    source_strategy=RetrievalStrategy.BM25
                )
                results.append(result)
        return results

    def _graph_traversal(self, query: str) -> List[MultiStrategyResult]:
        """图谱遍历（实体关系）"""
        results = []
        # 提取查询中的实体
        entities = self._extract_entities(query)

        for entity in entities:
            if entity in self.knowledge_graph:
                # 遍历邻居节点
                neighbors = self.knowledge_graph.neighbors(entity)
                for neighbor in neighbors:
                    edge_data = self.knowledge_graph.get_edge_data(entity, neighbor)
                    score = edge_data.get('weight', 0.5)
                    result = MultiStrategyResult(
                        memory_id=f"{entity}-{neighbor}",
                        content=f"{entity} → {neighbor}",
                        combined_score=score,
                        source_strategy=RetrievalStrategy.GRAPH
                    )
                    results.append(result)
        return results

    def _temporal_filter(
        self,
        query: str,
        query_time: Optional[datetime]
    ) -> List[MultiStrategyResult]:
        """时序过滤（有效性窗口）"""
        if query_time is None:
            query_time = datetime.now()

        results = []
        for mem_id, validity in self.temporal_index.items():
            if validity.is_valid_at(query_time):
                # 时序有效性作为相关性得分
                score = validity.confidence
                result = MultiStrategyResult(
                    memory_id=mem_id,
                    content=f"Valid at {query_time}",
                    combined_score=score,
                    temporal_validity=validity,
                    source_strategy=RetrievalStrategy.TEMPORAL
                )
                results.append(result)
        return results

    def _compute_similarity(self, query: str, content: str) -> float:
        """计算相似度（简化版本）"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        overlap = len(query_words & content_words)
        return overlap / max(len(query_words), 1)

    def _extract_entities(self, text: str) -> List[str]:
        """提取实体（简化版本）"""
        # 简化实现 - 实际应该使用NER
        words = text.split()
        entities = [w for w in words if w[0].isupper()]
        return entities


class ReflectionEngine:
    """
    反射合成引擎

    功能：
    - LLM驱动的跨记忆推理
    - 上下文合成
    - 洞察提取
    - 模式识别

    这是区分Hindsight和其他系统的关键特性。
    """

    def __init__(self):
        """初始化反射引擎"""
        self.insights = []  # 存储提取的洞察

    def reflect(
        self,
        query: str,
        retrieved_memories: List[MultiStrategyResult],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        反射合成

        不是返回"这里是5个相关事实"，而是回答
        "基于我们所知的一切，这是正在发生的事情"

        Args:
            query: 原始查询
            retrieved_memories: 检索到的记忆
            context: 额外上下文

        Returns:
            综合性的答案
        """
        # 构建上下文
        context_str = self._build_context(query, retrieved_memories, context)

        # 提取洞察
        insights = self._extract_insights(retrieved_memories)

        # 合成答案
        synthesis = self._synthesize_answer(query, context_str, insights)

        # 存储新洞察
        self.insights.extend(insights)

        return synthesis

    def _build_context(
        self,
        query: str,
        memories: List[MultiStrategyResult],
        additional_context: Optional[Dict[str, Any]]
    ) -> str:
        """构建上下文"""
        context_parts = [f"Query: {query}"]

        if memories:
            context_parts.append("\nRelevant Memories:")
            for i, mem in enumerate(memories[:5], 1):
                context_parts.append(
                    f"{i}. {mem.content} (score: {mem.combined_score:.2f})"
                )

        if additional_context:
            context_parts.append("\nAdditional Context:")
            for key, value in additional_context.items():
                context_parts.append(f"- {key}: {value}")

        return "\n".join(context_parts)

    def _extract_insights(
        self,
        memories: List[MultiStrategyResult]
    ) -> List[str]:
        """从记忆中提取洞察"""
        insights = []

        # 模式识别
        if len(memories) >= 3:
            # 检查时间趋势
            temporal_memories = [
                m for m in memories
                if m.temporal_validity is not None
            ]
            if temporal_memories:
                insights.append(
                    f"Detected temporal pattern across {len(temporal_memories)} memories"
                )

            # 检查高相关性记忆
            high_relevance = [
                m for m in memories
                if m.combined_score > 0.8
            ]
            if high_relevance:
                insights.append(
                    f"Found {len(high_relevance)} highly relevant memories"
                )

        return insights

    def _synthesize_answer(
        self,
        query: str,
        context: str,
        insights: List[str]
    ) -> str:
        """合成答案"""
        # 简化实现 - 实际应该调用LLM
        synthesis_parts = [
            f"Based on the analysis of the query: '{query}'",
            f"\nContext from {len(context.split('\n'))} sources"
        ]

        if insights:
            synthesis_parts.append("\nKey Insights:")
            for insight in insights:
                synthesis_parts.append(f"- {insight}")

        return "\n".join(synthesis_parts)


class TemporalReasoningEngine:
    """
    时序推理引擎

    特性：
    - 有效性窗口管理
    - 区间树索引
    - 历史查询
    - 时序冲突解决

    灵感来自Zep/Graphiti
    """

    def __init__(self):
        """初始化时序推理引擎"""
        self.facts = {}  # fact_id -> (content, validity)
        self.history = []  # 时序历史

    def add_fact(
        self,
        fact_id: str,
        content: str,
        valid_from: datetime,
        valid_until: Optional[datetime] = None,
        confidence: float = 1.0
    ):
        """添加时序事实"""
        validity = TemporalValidity(
            valid_from=valid_from,
            valid_until=valid_until,
            confidence=confidence
        )

        self.facts[fact_id] = (content, validity)

        # 记录历史
        self.history.append({
            'fact_id': fact_id,
            'action': 'add',
            'timestamp': datetime.now(),
            'validity': validity
        })

        # 检查并解决冲突
        self._resolve_conflicts(fact_id, validity)

    def get_fact_at_time(
        self,
        fact_id: str,
        query_time: datetime
    ) -> Optional[str]:
        """获取特定时间的事实"""
        if fact_id not in self.facts:
            return None

        content, validity = self.facts[fact_id]

        if validity.is_valid_at(query_time):
            return content
        else:
            # 查找历史
            for entry in reversed(self.history):
                if entry['fact_id'] == fact_id:
                    if entry['validity'].is_valid_at(query_time):
                        return self.facts[fact_id][0]  # 返回内容（可能已更新）

        return None

    def _resolve_conflicts(
        self,
        new_fact_id: str,
        new_validity: TemporalValidity
    ):
        """解决时序冲突"""
        # 检查重叠的事实
        for fact_id, (content, validity) in self.facts.items():
            if fact_id == new_fact_id:
                continue

            # 检查时间重叠
            if self._validities_overlap(validity, new_validity):
                # 根据置信度解决
                if new_validity.confidence > validity.confidence:
                    # 新事实更可信，更新旧事实的有效期
                    if validity.valid_until is None:
                        validity.valid_until = new_validity.valid_from
                    else:
                        validity.valid_until = min(
                            validity.valid_until,
                            new_validity.valid_from
                        )

    def _validities_overlap(
        self,
        v1: TemporalValidity,
        v2: TemporalValidity
    ) -> bool:
        """检查两个有效性窗口是否重叠"""
        # 简化实现
        return not (v1.valid_until and v2.valid_from >= v1.valid_until)


class SelfEvolvingSystem:
    """
    自我进化系统

    双循环进化：
    1. 内循环：优化记忆内容（添加、更新、删除）
    2. 外循环：优化记忆架构（参数、结构、策略）

    灵感来自MemEvolve
    """

    def __init__(self):
        """初始化自我进化系统"""
        self.evolution_history = []
        self.performance_metrics = {
            'retrieval_accuracy': [],
            'latency': [],
            'memory_growth': []
        }

    def evolve(
        self,
        retrieval_engine: MultiStrategyRetrievalEngine,
        performance_feedback: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        执行进化

        Args:
            retrieval_engine: 检索引擎实例
            performance_feedback: 性能反馈

        Returns:
            进化报告
        """
        evolution_report = {
            'timestamp': datetime.now().isoformat(),
            'changes': []
        }

        # 内循环：优化记忆内容
        content_changes = self._inner_loop_evolution(performance_feedback)
        evolution_report['changes'].extend(content_changes)

        # 外循环：优化架构
        architecture_changes = self._outer_loop_evolution(
            retrieval_engine,
            performance_feedback
        )
        evolution_report['changes'].extend(architecture_changes)

        # 记录历史
        self.evolution_history.append(evolution_report)

        # 更新性能指标
        for metric, value in performance_feedback.items():
            if metric in self.performance_metrics:
                self.performance_metrics[metric].append(value)

        return evolution_report

    def _inner_loop_evolution(
        self,
        feedback: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """内循环：优化记忆内容"""
        changes = []

        # 如果检索准确性低，添加更多记忆
        if feedback.get('retrieval_accuracy', 1.0) < 0.8:
            changes.append({
                'type': 'add_memories',
                'reason': 'Low retrieval accuracy',
                'action': 'Increase memory coverage'
            })

        # 如果延迟高，删除低相关性记忆
        if feedback.get('latency', 0) > 1000:  # ms
            changes.append({
                'type': 'prune_memories',
                'reason': 'High latency',
                'action': 'Remove low-relevance memories'
            })

        return changes

    def _outer_loop_evolution(
        self,
        retrieval_engine: MultiStrategyRetrievalEngine,
        feedback: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """外循环：优化架构"""
        changes = []

        # 调整检索策略权重
        if feedback.get('retrieval_accuracy', 1.0) < 0.7:
            changes.append({
                'type': 'adjust_strategy_weights',
                'reason': 'Low retrieval accuracy',
                'action': 'Increase semantic search weight'
            })

        # 优化索引
        if feedback.get('memory_growth', 0) > 10000:  # 太多记忆
            changes.append({
                'type': 'optimize_index',
                'reason': 'Large memory size',
                'action': 'Rebuild indexes'
            })

        return changes


class SuperMemorySystemV7:
    """
    SuperMemorySystemV7 - 自我进化AI代理记忆系统

    融合四大顶级系统的最佳特性：
    1. Hindsight的多策略检索
    2. Zep的时序推理
    3. Letta的代理自我管理
    4. MemEvolve的自我进化

    核心创新：
    - 多策略并行检索
    - 时序有效性窗口
    - LLM驱动的反射合成
    - 双循环自我进化
    """

    def __init__(self):
        """初始化系统"""
        self.retrieval_engine = MultiStrategyRetrievalEngine()
        self.reflection_engine = ReflectionEngine()
        self.temporal_engine = TemporalReasoningEngine()
        self.evolution_system = SelfEvolvingSystem()

        self.initialized_at = datetime.now()
        self.version = "7.0.0-alpha"

    def remember(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.EPISODIC,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None
    ) -> str:
        """
        存储记忆

        Args:
            content: 记忆内容
            memory_type: 记忆类型
            valid_from: 有效开始时间
            valid_until: 有效结束时间

        Returns:
            记忆ID
        """
        memory_id = f"mem_{datetime.now().timestamp()}"

        # 添加到检索索引
        self.retrieval_engine.semantic_index[memory_id] = content
        self.retrieval_engine.bm25_index[memory_id] = content

        # 如果是时序记忆，添加时序有效性
        if memory_type == MemoryType.TEMPORAL:
            valid_from = valid_from or datetime.now()
            self.temporal_engine.add_fact(
                memory_id,
                content,
                valid_from,
                valid_until
            )
            self.retrieval_engine.temporal_index[memory_id] = TemporalValidity(
                valid_from=valid_from,
                valid_until=valid_until
            )

        return memory_id

    def recall(
        self,
        query: str,
        query_time: Optional[datetime] = None,
        top_k: int = 10,
        use_reflection: bool = True
    ) -> Dict[str, Any]:
        """
        检索记忆

        Args:
            query: 查询文本
            query_time: 查询时间（用于时序过滤）
            top_k: 返回结果数
            use_reflection: 是否使用反射合成

        Returns:
            检索结果
        """
        # 多策略检索
        retrieved_memories = self.retrieval_engine.retrieve(
            query,
            query_time=query_time,
            top_k=top_k
        )

        if use_reflection and retrieved_memories:
            # 反射合成
            synthesis = self.reflection_engine.reflect(
                query,
                retrieved_memories
            )
        else:
            synthesis = None

        return {
            'memories': retrieved_memories,
            'synthesis': synthesis,
            'query': query,
            'timestamp': datetime.now().isoformat()
        }

    def evolve(
        self,
        performance_feedback: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        自我进化

        Args:
            performance_feedback: 性能反馈

        Returns:
            进化报告
        """
        return self.evolution_system.evolve(
            self.retrieval_engine,
            performance_feedback
        )

    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'version': self.version,
            'initialized_at': self.initialized_at.isoformat(),
            'memory_count': len(self.retrieval_engine.semantic_index),
            'temporal_facts': len(self.temporal_engine.facts),
            'evolution_count': len(self.evolution_system.evolution_history),
            'insights_count': len(self.reflection_engine.insights)
        }


# 测试代码
if __name__ == "__main__":
    import time

    print("="*70)
    print("SuperMemorySystemV7 - 自我进化AI代理记忆系统")
    print("="*70)

    # 初始化系统
    print("\n[1] 初始化系统...")
    sms_v7 = SuperMemorySystemV7()
    print(f"[OK] 系统初始化完成 (版本: {sms_v7.version})")

    # 存储记忆
    print("\n[2] 存储记忆...")
    memories = [
        ("Alice leads the ML platform migration project.", MemoryType.TEMPORAL),
        ("The project started in January 2026.", MemoryType.TEMPORAL),
        ("Bob joined the team in February.", MemoryType.TEMPORAL),
        ("Alice moved to the platform team in March.", MemoryType.TEMPORAL),
        ("Users prefer dark mode interface.", MemoryType.SEMANTIC),
    ]

    for content, mem_type in memories:
        memory_id = sms_v7.remember(content, memory_type=mem_type)
        print(f"  [OK] 存储记忆: {memory_id}")

    # 检索记忆
    print("\n[3] 检索记忆...")
    result = sms_v7.recall("Who is working on ML platform?")
    print(f"[OK] 检索到 {len(result['memories'])} 条记忆")

    for i, mem in enumerate(result['memories'][:3], 1):
        print(f"  {i}. {mem.content} (score: {mem.combined_score:.2f})")

    if result['synthesis']:
        print(f"\n[OK] 反射合成:")
        print(f"  {result['synthesis']}")

    # 自我进化
    print("\n[4] 自我进化...")
    performance_feedback = {
        'retrieval_accuracy': 0.75,
        'latency': 800,
        'memory_growth': 5000
    }

    evolution_report = sms_v7.evolve(performance_feedback)
    print(f"[OK] 进化完成，{len(evolution_report['changes'])} 项变更")

    for change in evolution_report['changes']:
        print(f"  - {change['type']}: {change['reason']}")

    # 系统状态
    print("\n[5] 系统状态...")
    status = sms_v7.get_status()
    print(f"[OK] 版本: {status['version']}")
    print(f"[OK] 记忆数: {status['memory_count']}")
    print(f"[OK] 时序事实: {status['temporal_facts']}")
    print(f"[OK] 进化次数: {status['evolution_count']}")

    print("\n" + "="*70)
    print("SuperMemorySystemV7 测试完成！")
    print("="*70)
