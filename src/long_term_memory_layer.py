"""
小妖AI原生知识记忆系统 - 长期记忆层（Long-Term Memory Layer）

第三层：知识图谱、语义向量、持久化存储

作者：小妖🦊
创建日期：2026-04-12
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
import threading
import json
from pathlib import Path

from memory_types import (
    LongTermMemoryItem,
    KnowledgeGraphNode,
    KnowledgeGraphEdge,
    MemoryID,
    GraphID,
    MemoryType,
    MemoryImportance
)


class KnowledgeGraph:
    """
    知识图谱

    使用NetworkX实现，支持：
    - 实体和关系的存储
    - 图算法（最短路径、社区发现等）
    - 图查询和遍历
    """

    def __init__(self):
        """初始化知识图谱"""
        self.graph = nx.DiGraph()
        self.nodes: Dict[GraphID, KnowledgeGraphNode] = {}
        self.edges: Dict[GraphID, KnowledgeGraphEdge] = {}
        self.lock = threading.RLock()

    def add_node(
        self,
        entity_name: str,
        entity_type: str,
        description: str = "",
        **kwargs
    ) -> KnowledgeGraphNode:
        """
        添加节点

        Args:
            entity_name: 实体名称
            entity_type: 实体类型
            description: 描述
            **kwargs: 其他属性

        Returns:
            创建的节点
        """
        with self.lock:
            # 检查是否已存在
            for node in self.nodes.values():
                if node.entity_name == entity_name and node.entity_type == entity_type:
                    # 更新现有节点
                    node.description = description or node.description
                    node.attributes.update(kwargs)
                    return node

            # 创建新节点
            node = KnowledgeGraphNode(
                entity_name=entity_name,
                entity_type=entity_type,
                description=description,
                **kwargs
            )

            self.nodes[node.id] = node

            # 添加到NetworkX图
            self.graph.add_node(
                node.id,
                entity_name=entity_name,
                entity_type=entity_type,
                importance=node.importance
            )

            return node

    def add_edge(
        self,
        source_id: GraphID,
        target_id: GraphID,
        relation_type: str,
        weight: float = 1.0,
        evidence: List[str] = None
    ) -> Optional[KnowledgeGraphEdge]:
        """
        添加边

        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            relation_type: 关系类型
            weight: 权重
            evidence: 证据

        Returns:
            创建的边，如果节点不存在返回None
        """
        with self.lock:
            # 检查节点是否存在
            if source_id not in self.nodes or target_id not in self.nodes:
                return None

            # 检查边是否已存在
            edge_id = f"{source_id}_{target_id}_{relation_type}"

            if edge_id in self.edges:
                # 更新现有边
                edge = self.edges[edge_id]
                edge.weight = max(edge.weight, weight)
                if evidence:
                    edge.evidence.extend(evidence)
                return edge

            # 创建新边
            edge = KnowledgeGraphEdge(
                id=edge_id,
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                weight=weight,
                evidence=evidence or []
            )

            self.edges[edge.id] = edge

            # 添加到NetworkX图
            self.graph.add_edge(
                source_id,
                target_id,
                relation_type=relation_type,
                weight=weight
            )

            return edge

    def query_associations(
        self,
        seed_entity: GraphID,
        max_depth: int = 3,
        max_results: int = 20
    ) -> List[Tuple[GraphID, float, int]]:
        """
        查询关联实体

        Args:
            seed_entity: 种子实体ID
            max_depth: 最大深度
            max_results: 最大结果数

        Returns:
            [(实体ID, 关联分数, 距离)] 列表
        """
        with self.lock:
            if seed_entity not in self.nodes:
                return []

            results = []

            # 使用BFS遍历
            for target_id in self.graph.nodes():
                if target_id == seed_entity:
                    continue

                try:
                    # 计算最短路径
                    path = nx.shortest_path(
                        self.graph,
                        seed_entity,
                        target_id
                    )
                    distance = len(path) - 1

                    if distance <= max_depth:
                        # 计算关联分数
                        score = self._calculate_association_score(
                            seed_entity,
                            target_id,
                            distance
                        )

                        results.append((target_id, score, distance))

                except nx.NetworkXNoPath:
                    continue

            # 按分数排序
            results.sort(key=lambda x: x[1], reverse=True)

            return results[:max_results]

    def find_entities(
        self,
        entity_name: str,
        entity_type: str = None
    ) -> List[KnowledgeGraphNode]:
        """
        查找实体

        Args:
            entity_name: 实体名称（支持模糊匹配）
            entity_type: 实体类型（可选）

        Returns:
            匹配的节点列表
        """
        with self.lock:
            results = []

            entity_name_lower = entity_name.lower()

            for node in self.nodes.values():
                # 名称匹配
                if entity_name_lower in node.entity_name.lower():
                    # 类型过滤
                    if entity_type is None or node.entity_type == entity_type:
                        results.append(node)

            return results

    def get_node(self, node_id: GraphID) -> Optional[KnowledgeGraphNode]:
        """获取节点"""
        return self.nodes.get(node_id)

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            # 节点类型分布
            type_distribution = {}
            for node in self.nodes.values():
                type_distribution[node.entity_type] = \
                    type_distribution.get(node.entity_type, 0) + 1

            # 关系类型分布
            relation_distribution = {}
            for edge in self.edges.values():
                relation_distribution[edge.relation_type] = \
                    relation_distribution.get(edge.relation_type, 0) + 1

            return {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "type_distribution": type_distribution,
                "relation_distribution": relation_distribution,
                "density": nx.density(self.graph)
            }

    def _calculate_association_score(
        self,
        source: GraphID,
        target: GraphID,
        distance: int
    ) -> float:
        """
        计算关联分数

        Args:
            source: 源节点
            target: 目标节点
            distance: 距离

        Returns:
            关联分数
        """
        # 1. 距离惩罚
        distance_penalty = 1.0 / (1.0 + distance)

        # 2. 路径权重
        try:
            path = nx.shortest_path(self.graph, source, target)
            path_weight = 1.0

            for i in range(len(path) - 1):
                edge_data = self.graph.get_edge_data(path[i], path[i+1])
                if edge_data:
                    path_weight *= edge_data.get('weight', 1.0)

        except nx.NetworkXNoPath:
            path_weight = 0.0

        # 3. 节点重要性
        target_importance = self.nodes[target].importance

        # 综合分数
        score = distance_penalty * path_weight * target_importance

        return score


class LongTermMemoryLayer:
    """
    长期记忆层

    职责：
    - 持久化记忆存储
    - 知识图谱管理
    - 语义向量检索
    - 概念抽象
    """

    def __init__(
        self,
        storage_path: str = "data/long_term_memory",
        enable_persistence: bool = True
    ):
        """
        初始化长期记忆层

        Args:
            storage_path: 存储路径
            enable_persistence: 是否启用持久化
        """
        self.storage_path = Path(storage_path)
        self.enable_persistence = enable_persistence

        # 创建存储目录
        if enable_persistence:
            self.storage_path.mkdir(parents=True, exist_ok=True)

        # 核心组件
        self.knowledge_graph = KnowledgeGraph()
        self.memories: Dict[MemoryID, LongTermMemoryItem] = {}
        self.lock = threading.RLock()

        # 统计信息
        self.stats = {
            "total_memories": 0,
            "total_nodes": 0,
            "total_edges": 0,
            "verified_memories": 0
        }

        # 加载已有数据
        if enable_persistence:
            self._load()

    def add_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.FACT,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        verified: bool = False,
        **kwargs
    ) -> LongTermMemoryItem:
        """
        添加长期记忆

        Args:
            content: 记忆内容
            memory_type: 记忆类型
            importance: 重要性
            verified: 是否已验证
            **kwargs: 其他属性

        Returns:
            创建的长期记忆项
        """
        with self.lock:
            memory = LongTermMemoryItem(
                content=content,
                memory_type=memory_type,
                importance=importance,
                verified=verified,
                **kwargs
            )

            self.memories[memory.id] = memory

            # 提取实体和关系
            self._extract_entities_and_relations(memory)

            # 更新统计
            self.stats["total_memories"] += 1
            if verified:
                self.stats["verified_memories"] += 1

            # 持久化
            if self.enable_persistence:
                self._save_memory(memory)

            return memory

    def get_memory(self, memory_id: MemoryID) -> Optional[LongTermMemoryItem]:
        """
        获取记忆

        Args:
            memory_id: 记忆ID

        Returns:
            长期记忆项
        """
        with self.lock:
            memory = self.memories.get(memory_id)
            if memory:
                memory.update_access()

            return memory

    def search_memories(
        self,
        query: str,
        limit: int = 20
    ) -> List[Tuple[LongTermMemoryItem, float]]:
        """
        搜索记忆

        Args:
            query: 查询字符串
            limit: 返回数量

        Returns:
            [(记忆项, 相似度分数)] 列表
        """
        with self.lock:
            # 简单实现：基于关键词匹配
            query_lower = query.lower()

            results = []
            for memory in self.memories.values():
                # 计算匹配分数
                score = self._calculate_similarity(query_lower, memory)

                if score > 0:
                    results.append((memory, score))

            # 按分数排序
            results.sort(key=lambda x: x[1], reverse=True)

            return results[:limit]

    def get_knowledge_graph(self) -> KnowledgeGraph:
        """获取知识图谱"""
        return self.knowledge_graph

    def _extract_entities_and_relations(self, memory: LongTermMemoryItem):
        """
        从记忆中提取实体和关系

        Args:
            memory: 记忆项
        """
        # 简单实现：基于启发式规则
        # 实际应用中应使用NER模型

        # 提取实体（简化版）
        words = memory.content.split()

        for i, word in enumerate(words):
            # 大写开头的词可能是实体
            if word and word[0].isupper() and len(word) > 2:
                entity_type = self._guess_entity_type(word)

                node = self.knowledge_graph.add_node(
                    entity_name=word,
                    entity_type=entity_type,
                    description=f"从记忆中提取: {memory.content[:50]}..."
                )

                # 关联到记忆
                if node.id not in memory.metadata.get("graph_nodes", []):
                    memory.metadata.setdefault("graph_nodes", []).append(node.id)

        # 提取关系（简化版）
        if len(words) >= 3:
            for i in range(len(words) - 2):
                # 寻找"是"、"有"等关系词
                if words[i+1] in ["是", "是", "有", "包含"]:
                    source = self.knowledge_graph.find_entities(words[i])
                    target = self.knowledge_graph.find_entities(words[i+2])

                    if source and target:
                        self.knowledge_graph.add_edge(
                            source_id=source[0].id,
                            target_id=target[0].id,
                            relation_type="related_to",
                            evidence=[memory.id]
                        )

    def _guess_entity_type(self, word: str) -> str:
        """猜测实体类型"""
        # 简单实现
        type_patterns = {
            "Python": "programming_language",
            "Java": "programming_language",
            "JavaScript": "programming_language",
            "AI": "concept",
            "ML": "concept",
            "深度学习": "concept",
        }

        return type_patterns.get(word, "unknown")

    def _calculate_similarity(self, query_lower: str, memory: LongTermMemoryItem) -> float:
        """
        计算查询与记忆的相似度

        Args:
            query_lower: 查询字符串（小写）
            memory: 记忆项

        Returns:
            相似度分数
        """
        content_lower = memory.content.lower()

        # 简单的词重叠计算
        query_words = set(query_lower.split())
        content_words = set(content_lower.split())

        if not query_words:
            return 0.0

        overlap = query_words & content_words

        # Jaccard相似度
        similarity = len(overlap) / len(query_words | content_words)

        return similarity

    def _save_memory(self, memory: LongTermMemoryItem):
        """保存记忆到文件"""
        memory_file = self.storage_path / f"{memory.id}.json"

        data = {
            "memory": memory.to_dict(),
            "saved_at": datetime.now().isoformat()
        }

        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load(self):
        """加载已有数据"""
        # 加载记忆
        for memory_file in self.storage_path.glob("*.json"):
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                memory_dict = data["memory"]
                memory = LongTermMemoryItem(
                    id=memory_dict["id"],
                    content=memory_dict["content"],
                    memory_type=MemoryType(memory_dict["memory_type"]),
                    importance=MemoryImportance(memory_dict["importance"]),
                    created_at=datetime.fromisoformat(memory_dict["created_at"]),
                    **memory_dict.get("metadata", {})
                )

                self.memories[memory.id] = memory

            except Exception as e:
                print(f"加载记忆失败 {memory_file}: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            stats = self.stats.copy()
            stats.update(self.knowledge_graph.get_statistics())
            stats["current_memories"] = len(self.memories)

            return stats


# 测试代码
if __name__ == "__main__":
    print("小妖AI原生知识记忆系统 - 长期记忆层")
    print("=" * 60)

    # 创建长期记忆层（不持久化）
    layer = LongTermMemoryLayer(enable_persistence=False)

    # 添加一些记忆
    memory1 = layer.add_memory(
        content="Python是一种解释型、高级编程语言",
        memory_type=MemoryType.FACT,
        importance=MemoryImportance.HIGH,
        verified=True
    )

    memory2 = layer.add_memory(
        content="深度学习是机器学习的一个分支",
        memory_type=MemoryType.CONCEPT,
        importance=MemoryImportance.HIGH,
        verified=True
    )

    memory3 = layer.add_memory(
        content="今天我学习了Python的基础语法",
        memory_type=MemoryType.EXPERIENCE,
        importance=MemoryImportance.MEDIUM
    )

    print("\n✅ 记忆添加成功")
    print(f"  记忆1: {memory1.content}")
    print(f"  记忆2: {memory2.content}")
    print(f"  记忆3: {memory3.content}")

    # 搜索记忆
    print("\n🔍 搜索'Python':")
    results = layer.search_memories("Python", limit=5)

    for memory, score in results:
        print(f"  - {memory.content[:50]}... (相似度: {score:.2f})")

    # 获取知识图谱统计
    graph_stats = layer.knowledge_graph.get_statistics()
    print(f"\n📊 知识图谱统计:")
    print(f"  节点数: {graph_stats['total_nodes']}")
    print(f"  边数: {graph_stats['total_edges']}")
    print(f"  节点类型分布: {graph_stats['type_distribution']}")

    # 查询关联
    if graph_stats['total_nodes'] > 0:
        node_id = list(layer.knowledge_graph.nodes.keys())[0]
        print(f"\n🔗 查询'{node_id}'的关联:")
        associations = layer.knowledge_graph.query_associations(node_id)

        for target_id, score, distance in associations[:5]:
            node = layer.knowledge_graph.get_node(target_id)
            print(f"  - {node.entity_name if node else target_id} (分数: {score:.2f}, 距离: {distance})")

    print("\n✅ 长期记忆层测试通过！")
