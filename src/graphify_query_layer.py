"""
GraphifyQueryLayer - 知识图谱查询层
XMS系统的第四层：图谱查询层
"""

import json
import networkx as nx
from networkx.readwrite import json_graph
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GraphifyQueryLayer:
    """
    知识图谱查询层 - XMS的第四层

    功能：
    1. 加载和缓存知识图谱
    2. BFS/DFS遍历查询
    3. 最短路径查询
    4. 节点解释和关系分析
    5. 中心性分析
    6. 关联组发现
    """

    def __init__(self, graph_path: str, cache_enabled: bool = True):
        """
        初始化图谱查询层

        Args:
            graph_path: graph.json文件路径
            cache_enabled: 是否启用缓存
        """
        self.graph_path = Path(graph_path)
        self.cache_enabled = cache_enabled
        self.G: Optional[nx.Graph] = None
        self.query_cache: Dict[str, Any] = {}
        self.last_loaded: Optional[datetime] = None

        # 性能统计
        self.query_count = 0
        self.cache_hits = 0
        self.total_query_time = 0.0

        # 加载图谱
        self._load_graph()

    def _load_graph(self):
        """加载知识图谱"""
        if not self.graph_path.exists():
            logger.warning(f"图谱文件不存在: {self.graph_path}")
            self.G = nx.Graph()
            return

        try:
            graph_data = json.loads(self.graph_path.read_text(encoding='utf-8'))
            self.G = json_graph.node_link_graph(graph_data)
            self.last_loaded = datetime.now()
            logger.info(f"图谱加载成功: {self.G.number_of_nodes()}个节点, {self.G.number_of_edges()}条边")
        except Exception as e:
            logger.error(f"图谱加载失败: {e}")
            self.G = nx.Graph()

    def reload(self):
        """重新加载图谱（用于增量更新）"""
        self._load_graph()
        self.query_cache.clear()  # 清空缓存
        logger.info("图谱已重新加载，缓存已清空")

    def query(
        self,
        question: str,
        max_depth: int = 3,
        max_results: int = 20,
        method: str = "bfs"
    ) -> List[Dict[str, Any]]:
        """
        自然语言查询 - BFS/DFS遍历

        Args:
            question: 查询问题
            max_depth: 最大遍历深度
            max_results: 最大结果数
            method: "bfs" 或 "dfs"

        Returns:
            相关节点列表
        """
        import time
        start_time = time.time()

        # 检查缓存
        cache_key = f"query:{question}:{max_depth}:{max_results}:{method}"
        if self.cache_enabled and cache_key in self.query_cache:
            self.cache_hits += 1
            return self.query_cache[cache_key]

        results = []

        if self.G.number_of_nodes() == 0:
            logger.warning("图谱为空，无法查询")
            return results

        # 从多个起始节点开始遍历
        start_nodes = list(self.G.nodes())[:5]

        for start_node in start_nodes:
            if len(results) >= max_results:
                break

            if method == "bfs":
                visited = self._bfs(start_node, max_depth)
            else:
                visited = self._dfs(start_node, max_depth)

            # 转换为结果格式
            for node in visited:
                if len(results) >= max_results:
                    break

                if not any(r['id'] == node for r in results):
                    node_data = self.G.nodes[node]
                    results.append({
                        'id': node,
                        'type': node_data.get('type', 'unknown'),
                        'source_file': node_data.get('source_file', 'unknown'),
                        'source_location': node_data.get('source_location', 'unknown'),
                        'neighbors': len(list(self.G.neighbors(node)))
                    })

        # 更新统计
        query_time = time.time() - start_time
        self.query_count += 1
        self.total_query_time += query_time

        # 缓存结果
        if self.cache_enabled:
            self.query_cache[cache_key] = results

        logger.debug(f"查询完成: {len(results)}个结果, 耗时{query_time*1000:.2f}ms")
        return results

    def _bfs(self, start_node: str, max_depth: int) -> List[str]:
        """BFS遍历"""
        visited = set()
        queue = [(start_node, 0)]

        while queue:
            node, depth = queue.pop(0)
            if node in visited or depth > max_depth:
                continue

            visited.add(node)

            for neighbor in self.G.neighbors(node):
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1))

        return list(visited)

    def _dfs(self, start_node: str, max_depth: int) -> List[str]:
        """DFS遍历"""
        visited = set()

        def dfs_recursive(node: str, depth: int):
            if node in visited or depth > max_depth:
                return
            visited.add(node)
            for neighbor in self.G.neighbors(node):
                dfs_recursive(neighbor, depth + 1)

        dfs_recursive(start_node, 0)
        return list(visited)

    def path(self, source: str, target: str) -> Optional[List[str]]:
        """
        最短路径查询

        Args:
            source: 起始节点
            target: 目标节点

        Returns:
            路径节点列表，如果不存在则返回None
        """
        # 检查缓存
        cache_key = f"path:{source}:{target}"
        if self.cache_enabled and cache_key in self.query_cache:
            return self.query_cache[cache_key]

        if source not in self.G.nodes() or target not in self.G.nodes():
            return None

        if nx.has_path(self.G, source, target):
            path = nx.shortest_path(self.G, source, target)

            # 缓存结果
            if self.cache_enabled:
                self.query_cache[cache_key] = path

            return path

        return None

    def explain(self, node: str) -> Optional[Dict[str, Any]]:
        """
        节点解释 - 详细节点信息

        Args:
            node: 节点ID

        Returns:
            节点详细信息
        """
        if node not in self.G.nodes():
            return None

        node_data = self.G.nodes[node]
        neighbors = list(self.G.neighbors(node))

        # 获取边信息
        edges = []
        for neighbor in neighbors[:10]:  # 限制前10个
            edge_data = self.G.get_edge_data(node, neighbor)
            edges.append({
                'target': neighbor,
                'relation': edge_data.get('relation', 'connected') if edge_data else 'connected'
            })

        return {
            'id': node,
            'type': node_data.get('type', 'unknown'),
            'source_file': node_data.get('source_file', 'unknown'),
            'source_location': node_data.get('source_location', 'unknown'),
            'neighbor_count': len(neighbors),
            'neighbors': neighbors[:10],
            'edges': edges
        }

    def analyze_centrality(self, top_n: int = 10) -> Dict[str, List[Tuple[str, float]]]:
        """
        中心性分析

        Args:
            top_n: 返回前N个节点

        Returns:
            中心性指标字典
        """
        if self.G.number_of_nodes() == 0:
            return {
                'degree': [],
                'betweenness': [],
                'closeness': []
            }

        # 度中心性
        degree_centrality = nx.degree_centrality(self.G)
        top_degree = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:top_n]

        # 介数中心性
        betweenness_centrality = nx.betweenness_centrality(self.G) if self.G.number_of_nodes() > 2 else {}
        top_betweenness = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:top_n]

        # 接近中心性
        try:
            closeness_centrality = nx.closeness_centrality(self.G)
            top_closeness = sorted(closeness_centrality.items(), key=lambda x: x[1], reverse=True)[:top_n]
        except:
            top_closeness = []

        return {
            'degree': top_degree,
            'betweenness': top_betweenness,
            'closeness': top_closeness
        }

    def find_communities(self) -> List[Dict[str, Any]]:
        """
        关联组发现

        Returns:
            关联组列表
        """
        if self.G.number_of_nodes() == 0:
            return []

        communities = []

        # 使用连通分量
        if self.G.is_directed():
            components = list(nx.weakly_connected_components(self.G))
        else:
            components = list(nx.connected_components(self.G))

        for i, component in enumerate(components):
            communities.append({
                'id': i,
                'size': len(component),
                'nodes': list(component)
            })

        return communities

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取图谱统计信息

        Returns:
            统计信息字典
        """
        return {
            'nodes': self.G.number_of_nodes(),
            'edges': self.G.number_of_edges(),
            'is_directed': self.G.is_directed(),
            'is_connected': nx.is_connected(self.G) if not self.G.is_directed() else nx.is_weakly_connected(self.G),
            'last_loaded': self.last_loaded.isoformat() if self.last_loaded else None,
            'query_count': self.query_count,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': self.cache_hits / self.query_count if self.query_count > 0 else 0,
            'avg_query_time_ms': (self.total_query_time / self.query_count * 1000) if self.query_count > 0 else 0
        }

    def clear_cache(self):
        """清空查询缓存"""
        self.query_cache.clear()
        logger.info("查询缓存已清空")

    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        return {
            'enabled': self.cache_enabled,
            'size': len(self.query_cache),
            'keys': list(self.query_cache.keys())
        }
