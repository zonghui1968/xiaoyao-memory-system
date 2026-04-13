"""
SuperMemorySystemV6 - 小妖超级记忆系统v6.0
集成Graphify知识图谱查询层 + WAL协议增强 + 网络可视化

作者：小妖🦊
创建日期：2026-04-12
版本：v6.0
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import logging
import threading
import time

# 导入基础记忆系统
try:
    from .xiaoyao_memory_system import XiaoyaoMemorySystem
    from .graphify_query_layer import GraphifyQueryLayer
except ImportError:
    from xiaoyao_memory_system import XiaoyaoMemorySystem
    from graphify_query_layer import GraphifyQueryLayer

logger = logging.getLogger(__name__)


class SuperMemorySystemV6(XiaoyaoMemorySystem):
    """
    小妖超级记忆系统v6.0

    在XiaoyaoMemorySystem（四层记忆架构）基础上新增：
    1. Graphify知识图谱查询层（第五层）
    2. WAL协议增强（图谱自动同步）
    3. 混合查询引擎（语义 + 图谱）
    4. 关系网络可视化
    5. 性能优化和缓存机制

    五层记忆架构：
    1. 工作记忆层 - 实时任务处理
    2. 短期记忆层 - 会话上下文
    3. 长期记忆层 - 语义记忆
    4. 元记忆层 - 系统自我认知
    5. 图谱查询层 - 结构化知识关系 ⭐新增
    """

    def __init__(
        self,
        storage_path: str = "C:/ssh/.openclaw/xiaoyao-memory-system/data",
        enable_persistence: bool = True,
        graphify_graph_path: Optional[str] = None,
        graphify_cache_enabled: bool = True,
        wal_graph_sync: bool = True
    ):
        """
        初始化v6.0系统

        Args:
            storage_path: 存储路径
            enable_persistence: 是否启用持久化
            graphify_graph_path: 知识图谱路径
            graphify_cache_enabled: 是否启用图谱缓存
            wal_graph_sync: 是否启用WAL图谱同步
        """
        # 初始化父类（XiaoyaoMemorySystem - 四层记忆）
        super().__init__(storage_path, enable_persistence)

        # 初始化Graphify查询层（第五层）
        self.graphify_layer: Optional[GraphifyQueryLayer] = None
        self.graphify_enabled = False

        if graphify_graph_path:
            try:
                self.graphify_layer = GraphifyQueryLayer(
                    graph_path=graphify_graph_path,
                    cache_enabled=graphify_cache_enabled
                )
                self.graphify_enabled = True
                logger.info(f"✅ Graphify查询层已初始化: {graphify_graph_path}")
            except Exception as e:
                logger.warning(f"⚠️ Graphify初始化失败: {e}")
                self.graphify_layer = None
                self.graphify_enabled = False
        else:
            logger.info("ℹ️ Graphify未启用")

        # WAL协议：图谱同步配置
        self.wal_graph_sync = wal_graph_sync
        self.wal_log_path = Path(storage_path) / "wal" / "graph_sync.log"
        self.wal_log_path.parent.mkdir(parents=True, exist_ok=True)

        # 性能统计
        self.v6_stats = {
            "graph_queries": 0,
            "hybrid_queries": 0,
            "graph_syncs": 0,
            "visualizations": 0
        }

        logger.info("🚀 SuperMemorySystemV6初始化完成")

    # ========== WAL协议：图谱同步 ==========

    def _log_to_wal(self, event_type: str, data: Dict[str, Any]):
        """
        记录事件到WAL日志

        Args:
            event_type: 事件类型
            data: 事件数据
        """
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "data": data
            }

            with open(self.wal_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        except Exception as e:
            logger.error(f"WAL日志记录失败: {e}")

    def _sync_to_graphify(self, memory_id: str, content: str, metadata: Optional[Dict[str, Any]]):
        """
        WAL协议：同步记忆到Graphify图谱

        当前实现：简化版本，只记录到WAL日志
        完整实现需要：
        1. 提取实体和关系
        2. 更新graph.json
        3. 重新加载图谱

        Args:
            memory_id: 记忆ID
            content: 记忆内容
            metadata: 元数据
        """
        if not self.wal_graph_sync or not self.graphify_enabled:
            return

        # 记录到WAL日志
        self._log_to_wal("memory_added", {
            "memory_id": memory_id,
            "content": content,
            "metadata": metadata
        })

        self.v6_stats["graph_syncs"] += 1

        # TODO: 实现完整的图谱同步
        # 1. 使用LLM提取实体和关系
        # 2. 转换为Graphify格式
        # 3. 合并到graph.json
        # 4. 调用self.graphify_layer.reload()

    # ========== 增强的记忆添加API ==========

    def add_memory(
        self,
        content: str,
        memory_type: str = "episodic",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        添加记忆（增强：WAL图谱同步）

        Args:
            content: 记忆内容
            memory_type: 记忆类型
            metadata: 元数据

        Returns:
            记忆ID
        """
        # 生成记忆ID
        memory_id = f"mem_{datetime.now().strftime('%Y%m%d%H%M%S')}_{id(content)}"

        # 调用父类方法添加到记忆系统
        # 注意：XiaoyaoMemorySystem使用record_conversation或add_task
        # 这里我们创建一个通用的添加方法
        try:
            # 添加到长期记忆层
            if hasattr(self, 'long_term_memory'):
                self.long_term_memory.add_memory(
                    content=content,
                    memory_type=memory_type,
                    metadata=metadata or {}
                )
        except Exception as e:
            logger.error(f"添加记忆失败: {e}")

        # WAL协议：同步到图谱
        self._sync_to_graphify(memory_id, content, metadata)

        return memory_id

    # ========== 混合查询引擎 ==========

    def query_hybrid(
        self,
        query: str,
        max_results: int = 20,
        graph_depth: int = 3,
        semantic_weight: float = 0.6
    ) -> Dict[str, Any]:
        """
        混合查询：语义搜索 + 图谱遍历

        Args:
            query: 查询文本
            max_results: 最大结果数
            graph_depth: 图谱遍历深度
            semantic_weight: 语义搜索权重（0-1）

        Returns:
            合并的查询结果
        """
        self.v6_stats["hybrid_queries"] += 1

        results = {
            'query': query,
            'semantic': [],
            'graph': [],
            'merged': [],
            'stats': {}
        }

        # 1. 语义搜索（XMS原有功能）
        semantic_scores = []
        try:
            # 这里需要调用长期记忆层的搜索
            if hasattr(self, 'long_term_memory'):
                semantic_results = self.long_term_memory.search(query, limit=max_results)
                results['semantic'] = semantic_results
                semantic_scores = [r.get('score', 0) for r in semantic_results]
        except Exception as e:
            logger.error(f"语义搜索失败: {e}")

        # 2. 图谱查询（Graphify新增功能）
        graph_scores = []
        if self.graphify_enabled:
            try:
                graph_results = self.graphify_layer.query(
                    question=query,
                    max_depth=graph_depth,
                    max_results=max_results
                )
                results['graph'] = graph_results
                # 归一化图谱分数（邻居数）
                max_neighbors = max([r.get('neighbors', 0) for r in graph_results], default=1)
                graph_scores = [r.get('neighbors', 0) / max_neighbors for r in graph_results]
            except Exception as e:
                logger.error(f"图谱查询失败: {e}")

        # 3. 合并结果（加权平均）
        results['merged'] = self._merge_results(
            results['semantic'],
            semantic_scores,
            results['graph'],
            graph_scores,
            semantic_weight,
            max_results
        )

        # 统计信息
        results['stats'] = {
            'semantic_count': len(results['semantic']),
            'graph_count': len(results['graph']),
            'merged_count': len(results['merged']),
            'semantic_weight': semantic_weight
        }

        return results

    def _merge_results(
        self,
        semantic_results: List[Dict],
        semantic_scores: List[float],
        graph_results: List[Dict],
        graph_scores: List[float],
        semantic_weight: float,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        合并语义搜索和图谱查询结果（加权平均）

        Args:
            semantic_results: 语义搜索结果
            semantic_scores: 语义分数
            graph_results: 图谱查询结果
            graph_scores: 图谱分数
            semantic_weight: 语义权重
            max_results: 最大结果数

        Returns:
            合并后的结果列表
        """
        merged = {}
        graph_weight = 1.0 - semantic_weight

        # 添加语义结果
        for i, result in enumerate(semantic_results):
            score = semantic_scores[i] if i < len(semantic_scores) else 0
            result_id = result.get('id', f"semantic_{i}")
            merged[result_id] = {
                'id': result_id,
                'source': 'semantic',
                'score': score * semantic_weight,
                'data': result
            }

        # 添加图谱结果（合并或新增）
        for i, result in enumerate(graph_results):
            score = graph_scores[i] if i < len(graph_scores) else 0
            result_id = result.get('id', f"graph_{i}")

            if result_id in merged:
                # 合并分数
                merged[result_id]['score'] += score * graph_weight
                merged[result_id]['source'] = 'hybrid'
            else:
                merged[result_id] = {
                    'id': result_id,
                    'source': 'graph',
                    'score': score * graph_weight,
                    'data': result
                }

        # 转换为列表并排序
        result_list = list(merged.values())
        result_list.sort(key=lambda x: x['score'], reverse=True)

        return result_list[:max_results]

    # ========== 关系网络分析 ==========

    def find_relations(
        self,
        concept: str,
        max_depth: int = 2,
        max_relations: int = 50
    ) -> List[Dict[str, Any]]:
        """
        查找概念之间的关系网络

        Args:
            concept: 起始概念
            max_depth: 最大深度
            max_relations: 最大关系数

        Returns:
            关系列表
        """
        if not self.graphify_enabled:
            logger.warning("Graphify未启用，无法查找关系")
            return []

        self.v6_stats["graph_queries"] += 1

        try:
            # 查找相关节点
            related_nodes = self.graphify_layer.query(
                question=concept,
                max_depth=max_depth,
                max_results=max_relations
            )

            # 构建关系网络
            relations = []
            for node in related_nodes:
                node_id = node.get('id')
                explanation = self.graphify_layer.explain(node_id)

                if explanation:
                    # 获取边信息
                    edges = explanation.get('edges', [])
                    for edge in edges:
                        relations.append({
                            'source': node_id,
                            'target': edge.get('target'),
                            'relation': edge.get('relation')
                        })

                        if len(relations) >= max_relations:
                            break

                if len(relations) >= max_relations:
                    break

            return relations

        except Exception as e:
            logger.error(f"查找关系失败: {e}")
            return []

    def find_shortest_path(
        self,
        source: str,
        target: str
    ) -> Optional[List[str]]:
        """
        查找两个概念之间的最短路径

        Args:
            source: 起始概念
            target: 目标概念

        Returns:
            路径节点列表
        """
        if not self.graphify_enabled:
            logger.warning("Graphify未启用，无法查找路径")
            return None

        self.v6_stats["graph_queries"] += 1

        try:
            return self.graphify_layer.path(source, target)
        except Exception as e:
            logger.error(f"查找路径失败: {e}")
            return None

    def explain_concept(self, concept: str) -> Optional[Dict[str, Any]]:
        """
        解释概念（结合语义记忆 + 图谱）

        Args:
            concept: 概念名称

        Returns:
            概念解释
        """
        explanation = {
            'concept': concept,
            'semantic': None,
            'graph': None,
            'timestamp': datetime.now().isoformat()
        }

        # 1. 语义记忆中的解释
        try:
            if hasattr(self, 'long_term_memory'):
                semantic_results = self.long_term_memory.search(concept, limit=5)
                if semantic_results:
                    explanation['semantic'] = semantic_results
        except Exception as e:
            logger.error(f"语义搜索失败: {e}")

        # 2. 图谱中的解释
        if self.graphify_enabled:
            try:
                # 尝试直接查找节点
                if concept in self.graphify_layer.G.nodes():
                    explanation['graph'] = self.graphify_layer.explain(concept)
                else:
                    # 查询相关节点
                    related = self.graphify_layer.query(concept, max_results=1)
                    if related:
                        explanation['graph'] = self.graphify_layer.explain(related[0]['id'])
            except Exception as e:
                logger.error(f"图谱查询失败: {e}")

        return explanation if explanation['semantic'] or explanation['graph'] else None

    def analyze_knowledge_network(self) -> Dict[str, Any]:
        """
        分析知识网络

        Returns:
            网络分析结果
        """
        if not self.graphify_enabled:
            return {
                'error': 'Graphify未启用',
                'timestamp': datetime.now().isoformat()
            }

        try:
            # 中心性分析
            centrality = self.graphify_layer.analyze_centrality(top_n=10)

            # 关联组发现
            communities = self.graphify_layer.find_communities()

            # 图谱统计
            stats = self.graphify_layer.get_statistics()

            return {
                'centrality': centrality,
                'communities': communities,
                'statistics': stats,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"网络分析失败: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    # ========== 网络可视化 ==========

    def visualize_network(
        self,
        output_path: Optional[str] = None,
        max_nodes: int = 100,
        layout: str = "spring",
        node_size: int = 500,
        figsize: tuple = (16, 12)
    ) -> Optional[str]:
        """
        生成关系网络可视化

        Args:
            output_path: 输出文件路径
            max_nodes: 最大节点数
            layout: 布局算法（spring, circular, random, kamada_kawai）
            node_size: 节点大小
            figsize: 图像大小

        Returns:
            输出文件路径
        """
        if not self.graphify_enabled:
            logger.warning("Graphify未启用，无法生成可视化")
            return None

        self.v6_stats["visualizations"] += 1

        try:
            import matplotlib
            matplotlib.use('Agg')  # 无GUI后端
            import matplotlib.pyplot as plt
            import networkx as nx

            G = self.graphify_layer.G

            # 限制节点数
            if G.number_of_nodes() > max_nodes:
                # 选择度中心性最高的节点
                centrality = nx.degree_centrality(G)
                top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
                nodes_to_keep = {node for node, _ in top_nodes}
                G = G.subgraph(nodes_to_keep)

            # 绘制图谱
            plt.figure(figsize=figsize)

            # 选择布局
            if layout == "spring":
                pos = nx.spring_layout(G, k=2, iterations=50)
            elif layout == "circular":
                pos = nx.circular_layout(G)
            elif layout == "random":
                pos = nx.random_layout(G)
            elif layout == "kamada_kawai":
                pos = nx.kamada_kawai_layout(G)
            else:
                pos = nx.spring_layout(G, k=2, iterations=50)

            # 绘制节点
            nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=node_size, alpha=0.8)

            # 绘制边
            nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.5, arrows=True)

            # 绘制标签
            node_labels = {node: node.split('_')[-1][:15] for node in G.nodes()}  # 简短标签
            nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8)

            plt.title("Knowledge Graph Network - SuperMemorySystemV6", fontsize=16)
            plt.axis('off')

            # 保存或返回
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                plt.savefig(output_path, dpi=150, bbox_inches='tight')
                plt.close()
                logger.info(f"✅ 网络可视化已保存: {output_path}")
                return str(output_path)
            else:
                # 保存到默认位置
                default_dir = Path(self.storage_path) / "visualizations"
                default_dir.mkdir(parents=True, exist_ok=True)
                default_path = default_dir / f"network_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                plt.savefig(default_path, dpi=150, bbox_inches='tight')
                plt.close()
                logger.info(f"✅ 网络可视化已保存: {default_path}")
                return str(default_path)

        except Exception as e:
            logger.error(f"网络可视化生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    # ========== 性能统计和优化 ==========

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        获取性能统计

        Returns:
            性能统计数据
        """
        stats = {
            'v6_stats': self.v6_stats.copy(),
            'graphify': {},
            'timestamp': datetime.now().isoformat()
        }

        # Graphify统计
        if self.graphify_enabled:
            stats['graphify'] = self.graphify_layer.get_statistics()

        # XMS统计（继承自父类）
        stats['xms_stats'] = self.stats.copy()

        return stats

    def optimize_performance(self):
        """优化性能"""
        # 清空图谱缓存
        if self.graphify_enabled:
            self.graphify_layer.clear_cache()
            logger.info("✅ 图谱缓存已清空")

        # TODO: 其他优化措施
        logger.info("✅ 性能优化已完成")

    def export_graph_data(self, output_path: str) -> bool:
        """
        导出图谱数据

        Args:
            output_path: 输出文件路径

        Returns:
            是否成功
        """
        if not self.graphify_enabled:
            logger.warning("Graphify未启用")
            return False

        try:
            import networkx as nx
            from networkx.readwrite import json_graph

            graph_data = json_graph.node_link_data(self.graphify_layer.G)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ 图谱数据已导出: {output_path}")
            return True

        except Exception as e:
            logger.error(f"导出失败: {e}")
            return False

    def get_system_info(self) -> Dict[str, Any]:
        """
        获取系统信息

        Returns:
            系统信息字典
        """
        return {
            'version': 'v6.0',
            'initialized_at': self.initialized_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'graphify_enabled': self.graphify_enabled,
            'wal_graph_sync': self.wal_graph_sync,
            'storage_path': self.storage_path,
            'stats': self.get_performance_stats()
        }
