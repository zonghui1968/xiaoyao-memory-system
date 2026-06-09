"""
向量存储模块 - Vector Store Module

提供可插拔的向量存储后端：
- SimpleVectorStore: 基于MD5哈希的轻量实现（无需外部依赖）
- LanceDBVectorStore: 基于LanceDB的真实向量搜索（可选sentence-transformers）

使用:
    from src.vector_store import SimpleVectorStore, LanceDBVectorStore

    store = SimpleVectorStore(dimension=1536)
    store.add("mem_001", "团队决定使用Clerk", {"wing": "工作"})
    results = store.search("认证方案选型", top_k=5)
"""

import logging
import hashlib
import math
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# =============================================================================
# 抽象基类
# =============================================================================

class VectorStore(ABC):
    """向量存储抽象基类"""

    @abstractmethod
    def add(self, id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """添加一条记录"""
        ...

    @abstractmethod
    def search(self, query_text: str, top_k: int = 5,
               filter_dict: Optional[Dict[str, str]] = None) -> List[Tuple[str, float]]:
        """搜索最相似的记录。返回 [(id, similarity_score), ...]"""
        ...

    @abstractmethod
    def delete(self, id: str) -> bool:
        """删除一条记录"""
        ...

    @abstractmethod
    def count(self) -> int:
        """返回记录总数"""
        ...


# =============================================================================
# MD5哈希工具
# =============================================================================

def _md5_embed(text: str, dimension: int = 384) -> List[float]:
    """基于MD5哈希生成伪向量（轻量回退方案）"""
    hash_hex = hashlib.md5(text.encode()).hexdigest()
    vector: List[float] = []
    for i in range(0, min(len(hash_hex), dimension * 2), 2):
        byte_val = int(hash_hex[i:i + 2], 16)
        normalized = (byte_val - 128) / 128.0
        vector.append(normalized)
    while len(vector) < dimension:
        vector.append(0.0)
    return vector[:dimension]


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """计算余弦相似度"""
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


# =============================================================================
# 简单向量存储 (MD5 hash, 零外部依赖)
# =============================================================================

class SimpleVectorStore(VectorStore):
    """
    基于MD5哈希的简单向量存储。

    优点: 零外部依赖，快速
    缺点: 语义搜索精度低，不适用于生产级语义检索
    适用: 开发、测试、小规模应用
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self._data: Dict[str, Dict[str, Any]] = {}

    def add(self, id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        if not id or not text:
            return False
        self._data[id] = {
            "text": text,
            "vector": _md5_embed(text, self.dimension),
            "metadata": metadata or {},
        }
        return True

    def search(self, query_text: str, top_k: int = 5,
               filter_dict: Optional[Dict[str, str]] = None) -> List[Tuple[str, float]]:
        if not self._data:
            return []

        query_vec = _md5_embed(query_text, self.dimension)
        scored: List[Tuple[str, float]] = []

        for id, entry in self._data.items():
            # 应用元数据过滤
            if filter_dict:
                meta = entry.get("metadata", {})
                if not all(meta.get(k) == v for k, v in filter_dict.items()):
                    continue
            sim = _cosine_similarity(query_vec, entry["vector"])
            scored.append((id, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def delete(self, id: str) -> bool:
        if id in self._data:
            del self._data[id]
            return True
        return False

    def count(self) -> int:
        return len(self._data)


# =============================================================================
# LanceDB向量存储 (真实向量搜索)
# =============================================================================

class LanceDBVectorStore(VectorStore):
    """
    基于LanceDB的真实向量存储。

    优先使用sentence-transformers进行文本嵌入，不可用时回退到MD5。
    支持元数据过滤、持久化存储。
    """

    def __init__(self, db_path: Optional[str] = None,
                 dimension: int = 384,
                 table_name: str = "memories"):
        self.dimension = dimension
        self.table_name = table_name
        self._db_path = db_path or str(
            Path(__file__).parent.parent / "data" / "lancedb_store"
        )
        self._model = None
        self._table = None
        self._lancedb_available = False

        self._init_backend()

    def _init_backend(self):
        """初始化LanceDB后端"""
        try:
            import lancedb
            import pyarrow as pa

            Path(self._db_path).mkdir(parents=True, exist_ok=True)
            db = lancedb.connect(self._db_path)

            # 检查表是否存在
            try:
                self._table = db.open_table(self.table_name)
                logger.info("LanceDB table '%s' opened", self.table_name)
            except Exception:
                # 创建新表
                schema = pa.schema([
                    pa.field("id", pa.string()),
                    pa.field("text", pa.string()),
                    pa.field("vector", pa.list_(pa.float32(), self.dimension)),
                    pa.field("metadata_json", pa.string()),
                ])
                self._table = db.create_table(self.table_name, schema=schema)
                logger.info("LanceDB table '%s' created", self.table_name)

            self._lancedb_available = True
            logger.info("LanceDB vector store initialized at %s", self._db_path)
        except ImportError:
            logger.warning(
                "LanceDB not installed. Falling back to SimpleVectorStore. "
                "Install with: pip install lancedb pyarrow"
            )
            self._lancedb_available = False
        except Exception as e:
            logger.error("Failed to initialize LanceDB: %s", e)
            self._lancedb_available = False

    def _get_embedding(self, text: str) -> List[float]:
        """获取文本嵌入向量"""
        # 尝试使用sentence-transformers
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("Using sentence-transformers for embeddings")
            except ImportError:
                logger.info(
                    "sentence-transformers not installed, using MD5 embeddings. "
                    "Install with: pip install sentence-transformers"
                )
                self._model = False  # 标记已尝试
            except Exception as e:
                logger.warning("Failed to load sentence-transformers: %s", e)
                self._model = False

        if self._model and self._model is not False:
            try:
                embedding = self._model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            except Exception as e:
                logger.warning("Embedding failed, falling back to MD5: %s", e)

        return _md5_embed(text, self.dimension)

    def _maybe_create_index(self):
        """如果需要，创建向量索引"""
        if not self._table:
            return
        try:
            # LanceDB 0.5+ uses create_index on table directly
            if hasattr(self._table, "create_index"):
                self._table.create_index()
                logger.debug("Vector index created")
        except Exception:
            pass  # 索引可能已存在，忽略

    def add(self, id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        if not id or not text:
            return False

        if not self._lancedb_available:
            return self._fallback.add(id, text, metadata)

        try:
            import pyarrow as pa
            import json

            vector = self._get_embedding(text)
            metadata_json = json.dumps(metadata or {}, ensure_ascii=False)

            self._table.add([{
                "id": id,
                "text": text,
                "vector": vector,
                "metadata_json": metadata_json,
            }])
            return True
        except Exception as e:
            logger.error("Failed to add to LanceDB: %s", e)
            return False

    def search(self, query_text: str, top_k: int = 5,
               filter_dict: Optional[Dict[str, str]] = None) -> List[Tuple[str, float]]:
        if not self._lancedb_available:
            return self._fallback.search(query_text, top_k, filter_dict)

        try:
            query_vec = self._get_embedding(query_text)

            # LanceDB search
            results = self._table.search(query_vec).limit(top_k).to_list()

            scored: List[Tuple[str, float]] = []
            for r in results:
                rid = r.get("id", "")
                dist = r.get("_distance", 0.0)
                # 转换距离为相似度 (LanceDB返回L2距离)
                similarity = 1.0 / (1.0 + dist)

                # 应用元数据过滤
                if filter_dict:
                    import json
                    meta = json.loads(r.get("metadata_json", "{}"))
                    if not all(meta.get(k) == v for k, v in filter_dict.items()):
                        continue

                scored.append((rid, similarity))

            return scored[:top_k]
        except Exception as e:
            logger.error("LanceDB search failed: %s", e)
            return self._fallback.search(query_text, top_k, filter_dict)

    def delete(self, id: str) -> bool:
        if not self._lancedb_available:
            return self._fallback.delete(id)
        try:
            self._table.delete(f"id = '{id}'")
            return True
        except Exception as e:
            logger.error("LanceDB delete failed: %s", e)
            return False

    def count(self) -> int:
        if not self._lancedb_available:
            return self._fallback.count()
        try:
            return self._table.count_rows()
        except Exception:
            return 0

    @property
    def _fallback(self) -> SimpleVectorStore:
        """获取回退存储"""
        if not hasattr(self, '__fallback'):
            object.__setattr__(self, '__fallback', SimpleVectorStore(self.dimension))
        return object.__getattribute__(self, '__fallback')
