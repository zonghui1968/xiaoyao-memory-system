"""
SuperMemorySystemV9 - Phase 5: AAAK压缩实验（可选）

基于Phase 4，添加AAAK压缩和评估压缩vs质量的权衡

作者：小妖🦊
创建日期：2026-04-13
版本：9.4.0-alpha (Phase 5)

注意：这是实验性功能。压缩可能降低记忆质量，建议谨慎使用。
"""

import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
import json
import hashlib
import math
import re
from collections import defaultdict

# 添加路径
sys.path.insert(0, str(Path(r"C:\ssh\.openclaw\xiaoyao-memory-system")))


class MemoryType(Enum):
    """记忆类型"""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    TEMPORAL = "temporal"
    REFLECTIVE = "reflective"


class HallType(Enum):
    """记忆厅类型"""
    FACTS = "hall_facts"
    EVENTS = "hall_events"
    DISCOVERIES = "hall_discoveries"
    PREFERENCES = "hall_preferences"
    ADVICE = "hall_advice"


class RecallLayer(Enum):
    """召回层级"""
    L0_IDENTITY = "L0_identity"
    L1_CRITICAL = "L1_critical"
    L2_ROOM = "L2_room"
    L3_DEEP = "L3_deep"


class CompressionLevel(Enum):
    """压缩级别"""
    NONE = "none"           # 不压缩
    LOW = "low"             # 轻度压缩（~20% reduction）
    MEDIUM = "medium"       # 中度压缩（~50% reduction）
    HIGH = "high"           # 高度压缩（~80% reduction）
    EXTREME = "extreme"     # 极限压缩（~95% reduction）


@dataclass
class TemporalERTriple:
    """时序实体关系三元组"""
    entity1: str
    relation: str
    entity2: str
    timestamp: str
    source_memory_id: str = ""
    confidence: float = 1.0

    def to_tuple(self) -> Tuple[str, str, str, str]:
        return (self.entity1, self.relation, self.entity2, self.timestamp)

    def __str__(self) -> str:
        return f"({self.entity1}, {self.relation}, {self.entity2}, {self.timestamp})"


@dataclass
class EntityRelation:
    """实体关系"""
    entity1: str
    entity2: str
    relation: str
    first_seen: str
    last_seen: str
    count: int = 1
    confidence: float = 1.0


@dataclass
class MemoryRoom:
    """记忆房间"""
    room_name: str
    wing: str
    hall: HallType
    closets: List[str] = field(default_factory=list)
    tunnels: List[str] = field(default_factory=list)


@dataclass
class MemoryWing:
    """记忆翼"""
    wing_name: str
    wing_type: str
    halls: Dict[HallType, Dict[str, MemoryRoom]] = field(default_factory=dict)

    def __post_init__(self):
        if not self.halls:
            for hall_type in HallType:
                self.halls[hall_type] = {}


@dataclass
class MemoryCloset:
    """记忆壁橱"""
    closet_id: str
    summary: str
    raw_memory_id: str
    created_at: str
    keywords: List[str] = field(default_factory=list)
    is_critical: bool = False
    compressed: bool = False  # NEW
    compression_ratio: float = 1.0  # NEW


@dataclass
class MemoryDrawer:
    """记忆抽屉"""
    drawer_id: str
    content: str
    created_at: str
    metadata: dict = field(default_factory=dict)
    vector: List[float] = field(default_factory=list)
    is_critical: bool = False
    er_triples: List[TemporalERTriple] = field(default_factory=list)
    compressed: bool = False  # NEW
    original_length: int = 0  # NEW
    compressed_length: int = 0  # NEW


class SimpleVectorDB:
    """简化向量数据库"""

    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self.vectors: Dict[str, List[float]] = {}
        self.metadata: Dict[str, dict] = {}

    def add(self, doc_id: str, vector: List[float], metadata: dict = None):
        """添加向量"""
        self.vectors[doc_id] = vector
        self.metadata[doc_id] = metadata or {}

    def search(self, query_vector: List[float], top_k: int = 5,
               filter_dict: dict = None) -> List[Tuple[str, float]]:
        """语义搜索"""
        results = []

        for doc_id, vector in self.vectors.items():
            if filter_dict:
                if doc_id not in self.metadata:
                    continue
                metadata = self.metadata[doc_id]
                match = True
                for key, value in filter_dict.items():
                    if metadata.get(key) != value:
                        match = False
                        break
                if not match:
                    continue

            similarity = self._cosine_similarity(query_vector, vector)
            results.append((doc_id, similarity))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)


class FactChecker:
    """Fact Checker（事实检查器）"""

    def __init__(self):
        self.entity_relations: Dict[Tuple[str, str], EntityRelation] = {}
        self.contradictions: List[dict] = []

    def add_triple(self, triple: TemporalERTriple) -> Optional[dict]:
        """添加三元组并检查矛盾"""
        key = (triple.entity1, triple.entity2)

        if key in self.entity_relations:
            existing = self.entity_relations[key]

            if existing.relation != triple.relation:
                contradiction = {
                    'type': 'relation_conflict',
                    'entity1': triple.entity1,
                    'entity2': triple.entity2,
                    'relation1': existing.relation,
                    'relation2': triple.relation,
                    'timestamp1': existing.first_seen,
                    'timestamp2': triple.timestamp,
                    'confidence': 0.7
                }

                self.contradictions.append(contradiction)
                return contradiction

            existing.last_seen = triple.timestamp
            existing.count += 1
            existing.confidence = min(1.0, existing.confidence + 0.1)

        else:
            self.entity_relations[key] = EntityRelation(
                entity1=triple.entity1,
                entity2=triple.entity2,
                relation=triple.relation,
                first_seen=triple.timestamp,
                last_seen=triple.timestamp,
                count=1,
                confidence=triple.confidence
            )

        return None

    def get_entity_relations(self, entity: str) -> List[EntityRelation]:
        """获取实体的所有关系"""
        relations = []

        for key, relation in self.entity_relations.items():
            if entity in key:
                relations.append(relation)

        return relations

    def check_contradictions(self) -> List[dict]:
        """获取所有矛盾"""
        return self.contradictions.copy()

    def get_entity_graph(self, entity: str, max_depth: int = 2) -> Dict[str, List[str]]:
        """获取实体关系图"""
        graph = {entity: []}

        relations = self.get_entity_relations(entity)
        for rel in relations:
            other = rel.entity2 if rel.entity1 == entity else rel.entity1
            graph[entity].append(other)
            graph[other] = []

            if max_depth >= 2:
                sub_relations = self.get_entity_relations(other)
                for sub_rel in sub_relations:
                    sub_other = sub_rel.entity2 if sub_rel.entity1 == other else sub_rel.entity1
                    if sub_other != entity:
                        graph[other].append(sub_other)

        return graph


class AAAKCompressor:
    """
    AAAK压缩器（实验性）

    AAAK = Adaptive Algorithmic Knowledge Compression
    自适应算法知识压缩

    警告：压缩可能降低记忆质量！
    """

    def __init__(self):
        """初始化压缩器"""
        self.compression_stats = {
            'total_compressed': 0,
            'total_original_bytes': 0,
            'total_compressed_bytes': 0,
            'quality_scores': []
        }

    def compress(self, text: str, level: CompressionLevel) -> Tuple[str, dict]:
        """
        压缩文本

        Args:
            text: 原始文本
            level: 压缩级别

        Returns:
            (压缩后的文本, 压缩信息)
        """
        original_length = len(text)

        if level == CompressionLevel.NONE:
            return text, {
                'compressed': False,
                'original_length': original_length,
                'compressed_length': original_length,
                'compression_ratio': 1.0,
                'quality_score': 1.0
            }

        # 根据压缩级别选择策略
        if level == CompressionLevel.LOW:
            compressed = self._compress_low(text)
        elif level == CompressionLevel.MEDIUM:
            compressed = self._compress_medium(text)
        elif level == CompressionLevel.HIGH:
            compressed = self._compress_high(text)
        elif level == CompressionLevel.EXTREME:
            compressed = self._compress_extreme(text)
        else:
            compressed = text

        compressed_length = len(compressed)
        compression_ratio = compressed_length / original_length if original_length > 0 else 1.0

        # 评估质量（简化：基于压缩比例）
        quality_score = self._assess_quality(text, compressed, level)

        self.compression_stats['total_compressed'] += 1
        self.compression_stats['total_original_bytes'] += original_length
        self.compression_stats['total_compressed_bytes'] += compressed_length
        self.compression_stats['quality_scores'].append(quality_score)

        return compressed, {
            'compressed': True,
            'level': level.value,
            'original_length': original_length,
            'compressed_length': compressed_length,
            'compression_ratio': compression_ratio,
            'quality_score': quality_score
        }

    def _compress_low(self, text: str) -> str:
        """轻度压缩（~20% reduction）"""
        # 移除多余空格
        compressed = re.sub(r'\s+', ' ', text)
        # 移除常见冗余词
        stopwords = ['的', '了', '是', '在']
        for word in stopwords:
            compressed = compressed.replace(f' {word} ', ' ')
        return compressed.strip()

    def _compress_medium(self, text: str) -> str:
        """中度压缩（~50% reduction）"""
        # 保留关键句子
        sentences = text.split('。')
        # 保留前50%的句子
        keep_count = max(1, int(len(sentences) * 0.5))
        compressed = '。'.join(sentences[:keep_count])
        return compressed.strip()

    def _compress_high(self, text: str) -> str:
        """高度压缩（~80% reduction）"""
        # 提取关键词
        keywords = self._extract_keywords(text, top_k=10)
        # 创建关键词摘要
        compressed = ' '.join(keywords)
        return compressed

    def _compress_extreme(self, text: str) -> str:
        """极限压缩（~95% reduction）"""
        # 只保留最核心的词
        keywords = self._extract_keywords(text, top_k=3)
        compressed = ' '.join(keywords)
        return compressed

    def _extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        """提取关键词"""
        content_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        words = content_clean.split()
        stopwords = {'的', '了', '是', '在', '和', '与', '或', '但', '如果', '就'}
        words_filtered = [w for w in words if len(w) > 1 and w not in stopwords]

        word_freq = {}
        for word in words_filtered:
            word_freq[word] = word_freq.get(word, 0) + 1

        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [word for word, freq in top_words]

    def _assess_quality(self, original: str, compressed: str, level: CompressionLevel) -> float:
        """
        评估压缩质量

        Returns:
            质量分数 (0.0-1.0)
        """
        # 简化实现：基于压缩比例
        ratio = len(compressed) / len(original) if len(original) > 0 else 1.0

        # 质量评分
        if level == CompressionLevel.LOW:
            # 轻度压缩：质量损失小
            return 0.95 + (ratio * 0.05)
        elif level == CompressionLevel.MEDIUM:
            # 中度压缩：质量损失中等
            return 0.70 + (ratio * 0.20)
        elif level == CompressionLevel.HIGH:
            # 高度压缩：质量损失大
            return 0.40 + (ratio * 0.30)
        elif level == CompressionLevel.EXTREME:
            # 极限压缩：质量损失非常大
            return 0.20 + (ratio * 0.30)
        else:
            return 1.0

    def get_stats(self) -> dict:
        """获取压缩统计"""
        avg_quality = 0.0
        if self.compression_stats['quality_scores']:
            avg_quality = sum(self.compression_stats['quality_scores']) / len(self.compression_stats['quality_scores'])

        overall_ratio = 1.0
        if self.compression_stats['total_original_bytes'] > 0:
            overall_ratio = self.compression_stats['total_compressed_bytes'] / self.compression_stats['total_original_bytes']

        return {
            'total_compressed': self.compression_stats['total_compressed'],
            'total_original_bytes': self.compression_stats['total_original_bytes'],
            'total_compressed_bytes': self.compression_stats['total_compressed_bytes'],
            'overall_compression_ratio': overall_ratio,
            'average_quality_score': avg_quality,
            'space_saved': self.compression_stats['total_original_bytes'] - self.compression_stats['total_compressed_bytes']
        }


class SuperMemorySystemV9_Phase5:
    """
    超级记忆系统V9 - Phase 5版本（完整版）

    Phase 1-4创新：
    1-10. (继承自Phase 4)

    Phase 5创新（实验性）：
    11. AAAK压缩 - 自适应算法知识压缩
    12. 质量评估系统
    13. 压缩vs质量权衡分析
    """

    def __init__(self, dimension: int = 1536,
                 default_compression: CompressionLevel = CompressionLevel.NONE):
        """初始化系统"""
        self.version = "9.4.0-alpha (Phase 5: AAAK压缩 - 实验性)"
        self.dimension = dimension
        self.default_compression = default_compression

        # 记忆存储
        self.memories: Dict[str, dict] = {}
        self.memory_index: Dict[str, Set[str]] = {
            'episodic': set(),
            'semantic': set(),
            'procedural': set(),
            'temporal': set(),
            'reflective': set()
        }

        # 记忆宫殿结构
        self.wings: Dict[str, MemoryWing] = {}
        self.rooms: Dict[str, MemoryRoom] = {}
        self.closets: Dict[str, MemoryCloset] = {}
        self.drawers: Dict[str, MemoryDrawer] = {}
        self.tunnel_index: Dict[str, List[Tuple[str, str]]] = {}

        # 向量数据库
        self.vector_db = SimpleVectorDB(dimension)

        # 语义引力场
        self.gravity_sources: Dict[str, dict] = {}

        # 日记系统
        self.diary_entries: List[dict] = []

        # 反思层
        self.reflections: List[dict] = []

        # 分层检索系统
        self.l0_identity = {
            'system_name': 'SuperMemorySystemV9',
            'system_role': 'AI记忆助手',
            'capabilities': [
                '记忆存储和检索',
                '知识图谱构建',
                '语义搜索',
                '分层检索',
                '事实检查',
                '实验性压缩'  # NEW
            ],
            'interaction_style': '温暖、专业、细致'
        }

        self.l1_critical_facts: List[str] = []

        # Temporal ER Triples
        self.er_triples: List[TemporalERTriple] = []

        # Fact Checker
        self.fact_checker = FactChecker()

        # 实体索引
        self.entity_index: Dict[str, Set[str]] = defaultdict(set)

        # === NEW: Phase 5 - AAAK压缩器 ===
        self.compressor = AAAKCompressor()

        # 统计
        self.stats = {
            'total_memories': 0,
            'total_reflections': 0,
            'gravity_sources': 0,
            'diary_entries': 0,
            'total_wings': 0,
            'total_rooms': 0,
            'total_tunnels': 0,
            'total_vectors': 0,
            'critical_facts': 0,
            'l0_tokens': 0,
            'l1_tokens': 0,
            'wake_up_calls': 0,
            'er_triples': 0,
            'unique_entities': 0,
            'contradictions': 0,
            'compressed_memories': 0,  # NEW
            'compression_enabled': default_compression != CompressionLevel.NONE  # NEW
        }

        print(f"[SuperMemorySystemV9] 初始化完成 (v{self.version})")
        print(f"[OK] 记忆宫殿结构已激活")
        print(f"[OK] Closet + Drawer分离已启用")
        print(f"[OK] 向量数据库已就绪")
        print(f"[OK] 分层检索系统（L0-L3）已启用")
        print(f"[OK] Temporal ER Triples已启用")
        print(f"[OK] Fact Checker已就绪")
        if default_compression != CompressionLevel.NONE:
            print(f"[警告] AAAK压缩已启用（级别: {default_compression.value}）- 可能降低记忆质量！")
        else:
            print(f"[OK] AAAK压缩已禁用（推荐设置）")

        self._calculate_l0_tokens()

    def remember(self, content: str, memory_type: MemoryType = MemoryType.SEMANTIC,
                 tags: List[str] = None, metadata: dict = None,
                 wing: str = None, room: str = None,
                 is_critical: bool = False,
                 extract_entities: bool = True,
                 compress: bool = True) -> str:
        """
        记录记忆（Phase 5增强）

        NEW: 可选压缩
        """
        memory_id = f"mem_{datetime.now().timestamp()}_{hash(content) % 10000:04d}"

        # === NEW: Phase 5 - 压缩 ===
        original_content = content
        if compress and self.default_compression != CompressionLevel.NONE:
            # 关键事实不压缩
            if is_critical:
                compressed = False
            else:
                content, compression_info = self.compressor.compress(
                    content,
                    self.default_compression
                )
                if compression_info['compressed']:
                    self.stats['compressed_memories'] += 1

        # 创建向量（使用压缩后的内容）
        vector = self._embed(content)

        # 自动判断关键事实
        if is_critical:
            pass
        else:
            is_critical = self._auto_detect_critical(original_content, memory_type, tags)

        # 提取实体和关系（使用原始内容）
        er_triples = []
        if extract_entities:
            er_triples = self._extract_entity_relations(original_content, memory_id)

        # 创建Drawer
        drawer = MemoryDrawer(
            drawer_id=memory_id,
            content=content,
            created_at=datetime.now().isoformat(),
            metadata={
                'type': memory_type.value,
                'tags': tags or [],
                **(metadata or {})
            },
            vector=vector,
            is_critical=is_critical,
            er_triples=er_triples,
            compressed=compress and self.default_compression != CompressionLevel.NONE and not is_critical,
            original_length=len(original_content),
            compressed_length=len(content)
        )
        self.drawers[memory_id] = drawer

        # 添加到向量数据库
        self.vector_db.add(
            doc_id=memory_id,
            vector=vector,
            metadata={
                'type': memory_type.value,
                'tags': tags or [],
                'wing': wing,
                'room': room,
                'is_critical': is_critical,
                'compressed': drawer.compressed
            }
        )
        self.stats['total_vectors'] += 1

        # 兼容V8格式
        memory = {
            'id': memory_id,
            'content': content,
            'original_content': original_content if drawer.compressed else None,
            'type': memory_type.value,
            'tags': tags or [],
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'vector': vector,
            'gravity_score': 0.0,
            'is_critical': is_critical,
            'er_triples': [t.to_tuple() for t in er_triples],
            'compressed': drawer.compressed
        }
        self.memories[memory_id] = memory
        self.memory_index[memory_type.value].add(memory_id)
        self.stats['total_memories'] += 1

        # 如果是关键事实，添加到L1
        if is_critical:
            self._add_to_l1_critical(original_content)
            self.stats['critical_facts'] += 1

        # 处理ER Triples
        for triple in er_triples:
            self.er_triples.append(triple)
            self.stats['er_triples'] += 1

            self.entity_index[triple.entity1].add(memory_id)
            self.entity_index[triple.entity2].add(memory_id)
            self.stats['unique_entities'] = len(self.entity_index)

            contradiction = self.fact_checker.add_triple(triple)
            if contradiction:
                self.stats['contradictions'] += 1
                print(f"[Fact Checker] 发现潜在矛盾: {contradiction}")

        # 记忆宫殿组织
        if not wing:
            if tags and len(tags) > 0:
                wing = tags[0]
            else:
                wing = "default"

        if wing not in self.wings:
            self.wings[wing] = MemoryWing(
                wing_name=wing,
                wing_type='project' if wing.islower() else 'person'
            )
            self.stats['total_wings'] += 1
            print(f"[新Wing] 创建: {wing}")

        hall = self._auto_classify_hall(content, memory_type)

        if not room:
            room = self._extract_room_name(content, tags)

        room_key = f"{wing}/{hall.value}/{room}"
        if room_key not in self.rooms:
            new_room = MemoryRoom(
                room_name=room,
                wing=wing,
                hall=hall
            )
            self.rooms[room_key] = new_room
            self.wings[wing].halls[hall][room] = new_room
            self.stats['total_rooms'] += 1
            self._create_tunnel(room, wing, room_key)

        # 创建Closet
        closet_id = f"closet_{memory_id}"
        summary, keywords = self._create_smart_summary(original_content)
        closet = MemoryCloset(
            closet_id=closet_id,
            summary=summary,
            raw_memory_id=memory_id,
            created_at=datetime.now().isoformat(),
            keywords=keywords,
            is_critical=is_critical,
            compressed=drawer.compressed,
            compression_ratio=len(content)/len(original_content) if original_content else 1.0
        )
        self.closets[closet_id] = closet

        self.rooms[room_key].closets.append(closet_id)

        if tags:
            for tag in tags:
                self._update_gravity_source(tag, vector)

        self._trigger_reflection(memory)

        critical_mark = " [关键事实]" if is_critical else ""
        er_mark = f" [{len(er_triples)}个三元组]" if er_triples else ""
        compress_mark = f" [压缩 {drawer.compressed*100:.0f}%]" if drawer.compressed else ""
        print(f"[记忆{critical_mark}{er_mark}{compress_mark}] {memory_type.value}: {content[:50]}...")
        print(f"  → Wing: {wing}, Hall: {hall.value}, Room: {room}")

        return memory_id

    def get_compression_stats(self) -> dict:
        """
        获取压缩统计（Phase 5新增）

        Returns:
            压缩统计信息
        """
        return self.compressor.get_stats()

    def evaluate_compression_quality(self) -> dict:
        """
        评估压缩vs质量权衡（Phase 5新增）

        Returns:
            评估报告
        """
        stats = self.compressor.get_stats()

        # 评估
        evaluation = {
            'compression_level': self.default_compression.value,
            'total_compressed': stats['total_compressed'],
            'space_saved': stats['space_saved'],
            'space_saved_percent': (stats['space_saved'] / stats['total_original_bytes'] * 100) if stats['total_original_bytes'] > 0 else 0,
            'average_quality': stats['average_quality_score'],
            'recommendation': self._get_compression_recommendation(stats)
        }

        return evaluation

    def _get_compression_recommendation(self, stats: dict) -> str:
        """获取压缩建议"""
        avg_quality = stats['average_quality_score']

        if self.default_compression == CompressionLevel.NONE:
            return "压缩已禁用，这是推荐设置，可保持最佳记忆质量。"
        elif avg_quality >= 0.9:
            return "压缩质量优秀，可放心使用。"
        elif avg_quality >= 0.7:
            return "压缩质量良好，但建议监控重要记忆的完整性。"
        elif avg_quality >= 0.5:
            return "压缩质量中等，建议仅用于非关键记忆。"
        else:
            return "警告：压缩质量较低，强烈建议降低压缩级别或禁用压缩！"

    # 继承Phase 4的其他方法（简化）
    def _extract_entity_relations(self, content: str, memory_id: str) -> List[TemporalERTriple]:
        """提取实体关系三元组"""
        triples = []
        timestamp = datetime.now().strftime("%Y-%m-%d")

        patterns = [
            r'(\w+)决定使用(\w+)',
            r'(\w+)选择(\w+)',
            r'(\w+)调试(\w+)',
            r'(\w+)使用(\w+)',
            r'(\w+)喜欢(\w+)',
            r'(\w+)推荐(\w+)',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                entity1 = match.group(1)
                entity2 = match.group(2)

                if '决定使用' in pattern or '选择' in pattern:
                    relation = '决定使用'
                elif '调试' in pattern:
                    relation = '调试'
                elif '使用' in pattern:
                    relation = '使用'
                elif '喜欢' in pattern:
                    relation = '喜欢'
                elif '推荐' in pattern:
                    relation = '推荐'
                else:
                    relation = '相关'

                triple = TemporalERTriple(
                    entity1=entity1,
                    relation=relation,
                    entity2=entity2,
                    timestamp=timestamp,
                    source_memory_id=memory_id,
                    confidence=0.8
                )

                triples.append(triple)

        return triples

    def _auto_detect_critical(self, content: str, memory_type: MemoryType,
                             tags: List[str]) -> bool:
        """自动检测关键事实"""
        decision_keywords = ['决定', '选择', '确认', '锁定', '决策']
        if any(kw in content for kw in decision_keywords):
            return True

        if memory_type == MemoryType.SEMANTIC:
            tech_keywords = ['架构', '技术栈', '框架', '数据库', 'api', '认证']
            if any(kw in content.lower() for kw in tech_keywords):
                if 'vs' in content.lower() or '而非' in content or '不是' in content:
                    return True

        if tags:
            critical_tags = ['重要', '关键', 'critical', 'decision', '决策']
            if any(tag in critical_tags for tag in tags):
                return True

        return False

    def _add_to_l1_critical(self, content: str):
        """添加到L1关键事实列表"""
        if len(content) > 100:
            summary = content[:97] + "..."
        else:
            summary = content

        self.l1_critical_facts.append(summary)

        if len(self.l1_critical_facts) > 20:
            self.l1_critical_facts.pop(0)

        self._calculate_l1_tokens()

    def _calculate_l0_tokens(self):
        """计算L0层的token数"""
        l0_text = json.dumps(self.l0_identity, ensure_ascii=False)
        self.stats['l0_tokens'] = len(l0_text.split())

    def _calculate_l1_tokens(self):
        """计算L1层的token数"""
        l1_text = " | ".join(self.l1_critical_facts)
        self.stats['l1_tokens'] = len(l1_text.split())

    def _create_smart_summary(self, content: str, max_length: int = 100) -> Tuple[str, List[str]]:
        """创建智能摘要"""
        if len(content) <= max_length:
            summary = content
        else:
            summary = content[:max_length-3] + "..."

        keywords = self._extract_keywords_simple(content)
        return summary, keywords

    def _extract_keywords_simple(self, content: str, top_k: int = 5) -> List[str]:
        """提取关键词（简化版）"""
        content_clean = re.sub(r'[^\w\s]', ' ', content.lower())
        words = content_clean.split()
        stopwords = {'的', '了', '是', '在', '和', '与', '或', '但', '如果', '就'}
        words_filtered = [w for w in words if len(w) > 1 and w not in stopwords]

        word_freq = {}
        for word in words_filtered:
            word_freq[word] = word_freq.get(word, 0) + 1

        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [word for word, freq in top_words]

    def _auto_classify_hall(self, content: str, memory_type: MemoryType) -> HallType:
        """自动分类到Hall"""
        content_lower = content.lower()
        if memory_type == MemoryType.PROCEDURAL:
            if any(word in content_lower for word in ['方法', '如何', '步骤', '流程']):
                return HallType.ADVICE
            else:
                return HallType.DISCOVERIES
        elif memory_type == MemoryType.SEMANTIC:
            if any(word in content_lower for word in ['喜欢', '偏好', '习惯', '认为']):
                return HallType.PREFERENCES
            else:
                return HallType.DISCOVERIES
        elif memory_type == MemoryType.EPISODIC:
            if any(word in content_lower for word in ['决定', '选择', '确认', '锁定']):
                return HallType.FACTS
            else:
                return HallType.EVENTS
        else:
            return HallType.EVENTS

    def _extract_room_name(self, content: str, tags: List[str]) -> str:
        """提取房间名称"""
        if tags:
            return tags[0]
        keywords = ['认证', '数据库', 'api', 'ui', '算法', '系统', '模型']
        for keyword in keywords:
            if keyword in content.lower():
                return keyword
        return content[:2] if len(content) >= 2 else "默认"

    def _create_tunnel(self, room_name: str, wing: str, room_key: str):
        """创建Tunnel"""
        if room_name not in self.tunnel_index:
            self.tunnel_index[room_name] = []

        for existing_wing, existing_key in self.tunnel_index[room_name]:
            if existing_wing != wing:
                self.rooms[room_key].tunnels.append(existing_key)
                if existing_key in self.rooms:
                    self.rooms[existing_key].tunnels.append(room_key)
                self.stats['total_tunnels'] += 1

        self.tunnel_index[room_name].append((wing, room_key))

    def _embed(self, text: str) -> List[float]:
        """文本向量化"""
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()

        vector = []
        for i in range(0, min(len(hash_hex), self.dimension * 2), 2):
            byte_val = int(hash_hex[i:i+2], 16)
            normalized = (byte_val - 128) / 128.0
            vector.append(normalized)

        while len(vector) < self.dimension:
            vector.append(0.0)

        return vector[:self.dimension]

    def _update_gravity_source(self, tag: str, vector: List[float]):
        """更新语义引力源"""
        tag_id = f"tag_{hash(tag) % 10000:04d}"

        if tag_id in self.gravity_sources:
            self.gravity_sources[tag_id]['gravity_strength'] += 0.1
            self.gravity_sources[tag_id]['mass'] += 1.0
        else:
            self.gravity_sources[tag_id] = {
                'tag_id': tag_id,
                'tag_name': tag,
                'vector': vector,
                'gravity_strength': 1.0,
                'mass': 1.0
            }
            self.stats['gravity_sources'] += 1

    def _trigger_reflection(self, memory: dict):
        """触发反思"""
        if self.stats['total_memories'] % 10 == 0:
            insight = f"已积累{self.stats['total_memories']}条记忆，{self.stats['er_triples']}个ER三元组"

            reflection = {
                'timestamp': datetime.now().isoformat(),
                'insight': insight,
                'confidence': 0.8,
                'related_memories': [memory['id']]
            }

            self.reflections.append(reflection)
            self.stats['total_reflections'] += 1

            print(f"[反思] {insight}")

    def get_status(self) -> dict:
        """获取系统状态"""
        return {
            'version': self.version,
            'stats': self.stats.copy(),
            'memory_distribution': {
                mem_type: len(ids)
                for mem_type, ids in self.memory_index.items()
            },
            'compression_stats': self.get_compression_stats(),
            'compression_evaluation': self.evaluate_compression_quality(),
            'timestamp': datetime.now().isoformat()
        }


# 便捷函数
def get_sms_v9_phase5(compression: CompressionLevel = CompressionLevel.NONE) -> SuperMemorySystemV9_Phase5:
    """获取SMSv9 Phase 5单例"""
    return SuperMemorySystemV9_Phase5(default_compression=compression)


# 测试
if __name__ == "__main__":
    print("="*70)
    print("SuperMemorySystemV9 - Phase 5: AAAK压缩实验（可选）")
    print("压缩 vs 质量权衡分析")
    print("="*70)

    # 测试1: 无压缩（推荐）
    print("\n[测试1] 无压缩（推荐设置）")
    sms_none = get_sms_v9_phase5(compression=CompressionLevel.NONE)

    memories = [
        ("团队决定使用Clerk而非Auth0，因为定价和开发者体验更好。Clerk的API更简洁，文档更清晰，集成更快速。", "semantic",
         ["认证", "Clerk", "决策"], None, "OAuth"),

        ("Kai调试OAuth花了2小时，发现是时区配置错误导致token刷新失败。", "episodic",
         ["认证", "调试", "Kai"], None, "OAuth"),
    ]

    for content, mem_type, tags, wing, room in memories:
        sms_none.remember(content, MemoryType(mem_type), tags, wing=wing, room=room)
        print()

    # 测试2: 轻度压缩
    print("\n[测试2] 轻度压缩（~20% reduction）")
    sms_low = get_sms_v9_phase5(compression=CompressionLevel.LOW)

    for content, mem_type, tags, wing, room in memories:
        sms_low.remember(content, MemoryType(mem_type), tags, wing=wing, room=room)
        print()

    # 测试3: 中度压缩
    print("\n[测试3] 中度压缩（~50% reduction）")
    sms_medium = get_sms_v9_phase5(compression=CompressionLevel.MEDIUM)

    for content, mem_type, tags, wing, room in memories:
        sms_medium.remember(content, MemoryType(mem_type), tags, wing=wing, room=room)
        print()

    # 测试4: 高度压缩
    print("\n[测试4] 高度压缩（~80% reduction）")
    sms_high = get_sms_v9_phase5(compression=CompressionLevel.HIGH)

    for content, mem_type, tags, wing, room in memories:
        sms_high.remember(content, MemoryType(mem_type), tags, wing=wing, room=room)
        print()

    # 测试5: 评估报告
    print("\n[测试5] 压缩评估报告")
    print("\n--- 无压缩（推荐） ---")
    status_none = sms_none.get_status()
    eval_none = status_none['compression_evaluation']
    print(f"压缩级别: {eval_none['compression_level']}")
    print(f"平均质量: {eval_none['average_quality']:.3f}")
    print(f"建议: {eval_none['recommendation']}")

    print("\n--- 轻度压缩 ---")
    status_low = sms_low.get_status()
    eval_low = status_low['compression_evaluation']
    print(f"压缩级别: {eval_low['compression_level']}")
    print(f"压缩数量: {eval_low['total_compressed']}")
    print(f"空间节省: {eval_low['space_saved_percent']:.1f}%")
    print(f"平均质量: {eval_low['average_quality']:.3f}")
    print(f"建议: {eval_low['recommendation']}")

    print("\n--- 中度压缩 ---")
    status_medium = sms_medium.get_status()
    eval_medium = status_medium['compression_evaluation']
    print(f"压缩级别: {eval_medium['compression_level']}")
    print(f"压缩数量: {eval_medium['total_compressed']}")
    print(f"空间节省: {eval_medium['space_saved_percent']:.1f}%")
    print(f"平均质量: {eval_medium['average_quality']:.3f}")
    print(f"建议: {eval_medium['recommendation']}")

    print("\n--- 高度压缩 ---")
    status_high = sms_high.get_status()
    eval_high = status_high['compression_evaluation']
    print(f"压缩级别: {eval_high['compression_level']}")
    print(f"压缩数量: {eval_high['total_compressed']}")
    print(f"空间节省: {eval_high['space_saved_percent']:.1f}%")
    print(f"平均质量: {eval_high['average_quality']:.3f}")
    print(f"建议: {eval_high['recommendation']}")

    print("\n" + "="*70)
    print("SuperMemorySystemV9 Phase 5 测试完成！")
    print("核心创新：AAAK压缩 + 质量评估系统")
    print("建议：生产环境使用无压缩或轻度压缩")
    print("="*70)
