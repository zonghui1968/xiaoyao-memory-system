"""
长期记忆层增强版 - 向量数据库集成
添加LanceDB支持 + 语义搜索
"""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import threading
import numpy as np
from datetime import datetime

# 导入基础类
try:
    from .long_term_memory_layer import LongTermMemoryLayer, LongTermMemoryItem
    from .memory_types import MemoryType, MemoryImportance
except ImportError:
    from long_term_memory_layer import LongTermMemoryLayer, LongTermMemoryItem
    from memory_types import MemoryType, MemoryImportance


class VectorStore:
    """
    向量存储（LanceDB集成）

    功能：
    - 存储文档向量
    - 语义相似度搜索
    - 批量导入
    """

    def __init__(
        self,
        db_path: str = "data/lancedb",
        table_name: str = "memories",
        embedding_dim: int = 1536  # OpenAI embedding dimension
    ):
        """
        初始化向量存储

        Args:
            db_path: 数据库路径
            table_name: 表名
            embedding_dim: 向量维度
        """
        self.db_path = Path(db_path)
        self.table_name = table_name
        self.embedding_dim = embedding_dim
        self.lock = threading.RLock()

        # 尝试导入lancedb
        try:
            import lancedb
            self.lancedb = lancedb
            self.enabled = True

            # 连接数据库
            self.db = lancedb.connect(str(self.db_path))

            # 尝试打开已有表，或创建新表
            try:
                self.table = self.db.open_table(table_name)
            except Exception:
                # 表不存在，创建新表
                schema = self._create_schema()
                self.table = self.db.create_table(table_name, schema=schema)

            print(f"[OK] LanceDB已启用: {self.db_path}")

        except ImportError:
            print("[WARNING] LanceDB未安装，向量搜索功能不可用")
            print("   安装: pip install lancedb")
            self.enabled = False
            self.db = None
            self.table = None

        except Exception as e:
            print(f"[ERROR] LanceDB初始化失败: {e}")
            self.enabled = False
            self.db = None
            self.table = None

        # 统计信息
        self.stats = {
            "total_vectors": 0,
            "search_count": 0,
            "last_search_time": None
        }

    def _create_schema(self):
        """创建LanceDB表结构"""
        import pyarrow as pa

        schema = pa.schema([
            pa.field("id", pa.string()),
            pa.field("content", pa.string()),
            pa.field("memory_type", pa.string()),
            pa.field("importance", pa.float32()),
            pa.field("created_at", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), self.embedding_dim))
        ])

        return schema

    def add_memory(
        self,
        memory_id: str,
        content: str,
        memory_type: str,
        importance: float,
        created_at: str,
        embedding: Optional[np.ndarray] = None
    ) -> bool:
        """
        添加记忆到向量存储

        Args:
            memory_id: 记忆ID
            content: 记忆内容
            memory_type: 记忆类型
            importance: 重要性
            created_at: 创建时间
            embedding: 向量（如果为None，会生成）

        Returns:
            是否成功
        """
        if not self.enabled:
            return False

        with self.lock:
            try:
                # 如果没有提供向量，生成伪向量
                if embedding is None:
                    embedding = self._generate_mock_embedding(content)

                # 添加到表
                self.table.add([{
                    "id": memory_id,
                    "content": content,
                    "memory_type": memory_type,
                    "importance": importance,
                    "created_at": created_at,
                    "vector": embedding.tolist()
                }])

                self.stats["total_vectors"] += 1
                return True

            except Exception as e:
                print(f"[ERROR] 添加向量失败: {e}")
                return False

    def search(
        self,
        query_embedding: np.ndarray,
        limit: int = 20,
        metric: str = "cosine"
    ) -> List[Dict[str, Any]]:
        """
        向量相似度搜索

        Args:
            query_embedding: 查询向量
            limit: 返回数量
            metric: 距离度量（cosine, l2）

        Returns:
            搜索结果列表
        """
        if not self.enabled:
            return []

        with self.lock:
            try:
                import time
                start = time.time()

                # 执行搜索
                results = self.table.search(
                    query_embedding.tolist()
                ).limit(limit).metric(metric).to_df()

                # 更新统计
                self.stats["search_count"] += 1
                self.stats["last_search_time"] = time.time() - start

                # 转换结果格式
                formatted_results = []
                for _, row in results.iterrows():
                    formatted_results.append({
                        "id": row.get("id"),
                        "content": row.get("content"),
                        "memory_type": row.get("memory_type"),
                        "importance": row.get("importance"),
                        "score": row.get("_distance", 0.0)  # LanceDB使用_distance
                    })

                return formatted_results

            except Exception as e:
                print(f"[ERROR] 向量搜索失败: {e}")
                return []

    def _generate_mock_embedding(self, text: str) -> np.ndarray:
        """
        生成伪向量（用于测试）

        实际应用中应使用真实的embedding模型
        """
        # 基于文本hash生成伪向量
        hash_val = hash(text)
        np.random.seed(hash_val % (2**32))
        return np.random.randn(self.embedding_dim).astype(np.float32)

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.stats.copy()

        if self.enabled and self.table:
            try:
                stats["total_vectors"] = len(self.table)
            except Exception:
                pass

        return stats


class LongTermMemoryLayerV2(LongTermMemoryLayer):
    """
    长期记忆层V2 - 增强版

    新增功能：
    1. 向量数据库支持（LanceDB）
    2. 语义搜索
    3. 混合搜索（关键词 + 向量）
    """

    def __init__(
        self,
        storage_path: str = "data/long_term_memory",
        enable_persistence: bool = True,
        enable_vector_store: bool = True,
        vector_db_path: str = "data/lancedb"
    ):
        """
        初始化V2长期记忆层

        Args:
            storage_path: 存储路径
            enable_persistence: 是否启用持久化
            enable_vector_store: 是否启用向量存储
            vector_db_path: 向量数据库路径
        """
        # 初始化父类
        super().__init__(storage_path, enable_persistence)

        # 初始化向量存储
        self.vector_store: Optional[VectorStore] = None
        self.enable_vector_store = enable_vector_store

        if enable_vector_store:
            self.vector_store = VectorStore(db_path=vector_db_path)

        print(f"[OK] LongTermMemoryLayerV2初始化完成")
        print(f"   向量存储: {'启用' if self.vector_store and self.vector_store.enabled else '禁用'}")

    def add_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.FACT,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        verified: bool = False,
        add_to_vector: bool = True,
        **kwargs
    ) -> LongTermMemoryItem:
        """
        添加记忆（增强：自动添加到向量存储）

        Args:
            content: 记忆内容
            memory_type: 记忆类型
            importance: 重要性
            verified: 是否已验证
            add_to_vector: 是否添加到向量存储
            **kwargs: 其他属性

        Returns:
            创建的长期记忆项
        """
        # 调用父类方法
        memory = super().add_memory(
            content=content,
            memory_type=memory_type,
            importance=importance,
            verified=verified,
            **kwargs
        )

        # 添加到向量存储
        if add_to_vector and self.vector_store and self.vector_store.enabled:
            self.vector_store.add_memory(
                memory_id=memory.id,
                content=memory.content,
                memory_type=memory.memory_type.value,
                importance=memory.importance.value,
                created_at=memory.created_at.isoformat()
            )

        return memory

    def search(
        self,
        query: str,
        limit: int = 20,
        method: str = "hybrid",
        vector_weight: float = 0.6
    ) -> List[Dict[str, Any]]:
        """
        搜索记忆（增强版）

        Args:
            query: 查询字符串
            limit: 返回数量
            method: 搜索方法（keyword, vector, hybrid）
            vector_weight: 向量搜索权重（仅hybrid模式）

        Returns:
            搜索结果列表
        """
        results = {
            "query": query,
            "method": method,
            "keyword_results": [],
            "vector_results": [],
            "merged_results": [],
            "limit": limit
        }

        # 1. 关键词搜索
        if method in ["keyword", "hybrid"]:
            keyword_results = self.search_memories(query, limit)
            results["keyword_results"] = [
                {
                    "id": mem.id,
                    "content": mem.content,
                    "memory_type": mem.memory_type.value,
                    "importance": mem.importance.value,
                    "score": float(score),
                    "source": "keyword"
                }
                for mem, score in keyword_results
            ]

        # 2. 向量搜索
        if method in ["vector", "hybrid"] and self.vector_store and self.vector_store.enabled:
            query_embedding = self.vector_store._generate_mock_embedding(query)
            vector_results = self.vector_store.search(query_embedding, limit)

            # LanceDB返回的是distance，需要转换为similarity
            for result in vector_results:
                # distance越小越相似，转换为score（0-1）
                result["score"] = max(0.0, 1.0 - result.get("score", 0.0))
                result["source"] = "vector"

            results["vector_results"] = vector_results

        # 3. 混合搜索（合并结果）
        if method == "hybrid":
            results["merged_results"] = self._merge_search_results(
                results["keyword_results"],
                results["vector_results"],
                vector_weight,
                limit
            )
        elif method == "keyword":
            results["merged_results"] = results["keyword_results"]
        elif method == "vector":
            results["merged_results"] = results["vector_results"]

        return results["merged_results"]

    def _merge_search_results(
        self,
        keyword_results: List[Dict],
        vector_results: List[Dict],
        vector_weight: float,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        合并关键词和向量搜索结果

        Args:
            keyword_results: 关键词搜索结果
            vector_results: 向量搜索结果
            vector_weight: 向量搜索权重
            limit: 返回数量

        Returns:
            合并后的结果
        """
        keyword_weight = 1.0 - vector_weight

        # 使用字典去重和合并分数
        merged = {}

        # 添加关键词结果
        for result in keyword_results:
            result_id = result["id"]
            merged[result_id] = {
                **result,
                "score": result["score"] * keyword_weight
            }

        # 添加或合并向量结果
        for result in vector_results:
            result_id = result["id"]

            if result_id in merged:
                # 已存在，合并分数
                merged[result_id]["score"] += result["score"] * vector_weight
                merged[result_id]["source"] = "hybrid"
            else:
                # 不存在，添加新结果
                merged[result_id] = {
                    **result,
                    "score": result["score"] * vector_weight
                }

        # 转换为列表并排序
        result_list = list(merged.values())
        result_list.sort(key=lambda x: x["score"], reverse=True)

        return result_list[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = super().get_statistics()

        if self.vector_store:
            stats["vector_store"] = self.vector_store.get_statistics()

        return stats
