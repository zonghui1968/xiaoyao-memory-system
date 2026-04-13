"""
SuperMemorySystemV9 - Phase 4: 知识图谱

基于Phase 3，添加Temporal ER Triples和Fact Checker

作者：小妖🦊
创建日期：2026-04-13
版本：9.3.0-alpha (Phase 4)
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


@dataclass
class TemporalERTriple:
    """
    时序实体关系三元组（Temporal ER Triple）

    格式：(entity1, relation, entity2, timestamp)

    Example:
        ("团队", "决定使用", "Clerk", "2026-04-13")
        ("Kai", "调试", "OAuth", "2026-04-12")
    """
    entity1: str
    relation: str
    entity2: str
    timestamp: str
    source_memory_id: str = ""
    confidence: float = 1.0

    def to_tuple(self) -> Tuple[str, str, str, str]:
        """转换为元组"""
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


@dataclass
class MemoryDrawer:
    """记忆抽屉"""
    drawer_id: str
    content: str
    created_at: str
    metadata: dict = field(default_factory=dict)
    vector: List[float] = field(default_factory=list)
    is_critical: bool = False
    er_triples: List[TemporalERTriple] = field(default_factory=list)  # NEW


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
    """
    Fact Checker（事实检查器）

    检测记忆中的矛盾和冲突
    """

    def __init__(self):
        """初始化Fact Checker"""
        self.entity_relations: Dict[Tuple[str, str], EntityRelation] = {}
        self.contradictions: List[dict] = []

    def add_triple(self, triple: TemporalERTriple) -> Optional[dict]:
        """
        添加三元组并检查矛盾

        Args:
            triple: 时序ER三元组

        Returns:
            如果发现矛盾，返回矛盾信息；否则返回None
        """
        key = (triple.entity1, triple.entity2)

        # 检查是否已存在相同实体对
        if key in self.entity_relations:
            existing = self.entity_relations[key]

            # 检查关系是否矛盾
            if existing.relation != triple.relation:
                # 潜在矛盾：同一实体对有不同关系
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

            # 更新现有关系
            existing.last_seen = triple.timestamp
            existing.count += 1
            existing.confidence = min(1.0, existing.confidence + 0.1)

        else:
            # 创建新关系
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
        """
        获取实体的所有关系

        Args:
            entity: 实体名称

        Returns:
            关系列表
        """
        relations = []

        for key, relation in self.entity_relations.items():
            if entity in key:
                relations.append(relation)

        return relations

    def check_contradictions(self) -> List[dict]:
        """
        获取所有矛盾

        Returns:
            矛盾列表
        """
        return self.contradictions.copy()

    def get_entity_graph(self, entity: str, max_depth: int = 2) -> Dict[str, List[str]]:
        """
        获取实体关系图

        Args:
            entity: 中心实体
            max_depth: 最大深度

        Returns:
            {实体: [相关实体]}
        """
        graph = {entity: []}

        # 第一层
        relations = self.get_entity_relations(entity)
        for rel in relations:
            other = rel.entity2 if rel.entity1 == entity else rel.entity1
            graph[entity].append(other)
            graph[other] = []

            # 第二层
            if max_depth >= 2:
                sub_relations = self.get_entity_relations(other)
                for sub_rel in sub_relations:
                    sub_other = sub_rel.entity2 if sub_rel.entity1 == other else sub_rel.entity1
                    if sub_other != entity:
                        graph[other].append(sub_other)

        return graph


class SuperMemorySystemV9_Phase4:
    """
    超级记忆系统V9 - Phase 4版本

    Phase 1-3创新：
    1-7. (继承自Phase 3)

    Phase 4创新：
    8. Temporal ER Triples - 时序实体关系三元组
    9. Fact Checker - 矛盾检测
    10. 实体关系查询
    11. 知识图谱可视化
    """

    def __init__(self, dimension: int = 1536):
        """初始化系统"""
        self.version = "9.3.0-alpha (Phase 4: 知识图谱)"
        self.dimension = dimension

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
                '事实检查'  # NEW
            ],
            'interaction_style': '温暖、专业、细致'
        }

        self.l1_critical_facts: List[str] = []

        # === NEW: Phase 4 - 知识图谱 ===

        # Temporal ER Triples
        self.er_triples: List[TemporalERTriple] = []

        # Fact Checker
        self.fact_checker = FactChecker()

        # 实体索引
        self.entity_index: Dict[str, Set[str]] = defaultdict(set)

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
            'er_triples': 0,  # NEW
            'unique_entities': 0,  # NEW
            'contradictions': 0  # NEW
        }

        print(f"[SuperMemorySystemV9] 初始化完成 (v{self.version})")
        print(f"[OK] 记忆宫殿结构已激活")
        print(f"[OK] Closet + Drawer分离已启用")
        print(f"[OK] 向量数据库已就绪")
        print(f"[OK] 分层检索系统（L0-L3）已启用")
        print(f"[OK] Temporal ER Triples已启用")
        print(f"[OK] Fact Checker已就绪")

        self._calculate_l0_tokens()

    def remember(self, content: str, memory_type: MemoryType = MemoryType.SEMANTIC,
                 tags: List[str] = None, metadata: dict = None,
                 wing: str = None, room: str = None,
                 is_critical: bool = False,
                 extract_entities: bool = True) -> str:
        """
        记录记忆（Phase 4增强）

        NEW: 自动提取实体和关系
        """
        memory_id = f"mem_{datetime.now().timestamp()}_{hash(content) % 10000:04d}"

        # 创建向量
        vector = self._embed(content)

        # 自动判断关键事实
        if is_critical:
            pass
        else:
            is_critical = self._auto_detect_critical(content, memory_type, tags)

        # === NEW: Phase 4 - 提取实体和关系 ===
        er_triples = []
        if extract_entities:
            er_triples = self._extract_entity_relations(content, memory_id)

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
            er_triples=er_triples  # NEW
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
                'is_critical': is_critical
            }
        )
        self.stats['total_vectors'] += 1

        # 兼容V8格式
        memory = {
            'id': memory_id,
            'content': content,
            'type': memory_type.value,
            'tags': tags or [],
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'vector': vector,
            'gravity_score': 0.0,
            'is_critical': is_critical,
            'er_triples': [t.to_tuple() for t in er_triples]  # NEW
        }
        self.memories[memory_id] = memory
        self.memory_index[memory_type.value].add(memory_id)
        self.stats['total_memories'] += 1

        # 如果是关键事实，添加到L1
        if is_critical:
            self._add_to_l1_critical(content)
            self.stats['critical_facts'] += 1

        # === NEW: Phase 4 - 处理ER Triples ===
        for triple in er_triples:
            self.er_triples.append(triple)
            self.stats['er_triples'] += 1

            # 添加到实体索引
            self.entity_index[triple.entity1].add(memory_id)
            self.entity_index[triple.entity2].add(memory_id)
            self.stats['unique_entities'] = len(self.entity_index)

            # Fact Checker检查
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
        summary, keywords = self._create_smart_summary(content)
        closet = MemoryCloset(
            closet_id=closet_id,
            summary=summary,
            raw_memory_id=memory_id,
            created_at=datetime.now().isoformat(),
            keywords=keywords,
            is_critical=is_critical
        )
        self.closets[closet_id] = closet

        self.rooms[room_key].closets.append(closet_id)

        if tags:
            for tag in tags:
                self._update_gravity_source(tag, vector)

        self._trigger_reflection(memory)

        critical_mark = " [关键事实]" if is_critical else ""
        er_mark = f" [{len(er_triples)}个三元组]" if er_triples else ""
        print(f"[记忆{critical_mark}{er_mark}] {memory_type.value}: {content[:50]}...")
        print(f"  → Wing: {wing}, Hall: {hall.value}, Room: {room}")

        return memory_id

    def _extract_entity_relations(self, content: str, memory_id: str) -> List[TemporalERTriple]:
        """
        提取实体关系三元组（Phase 4新增）

        Args:
            content: 内容
            memory_id: 记忆ID

        Returns:
            三元组列表
        """
        triples = []
        timestamp = datetime.now().strftime("%Y-%m-%d")

        # 简化实现：使用模式匹配
        # 模式1: 主语 + 动词 + 宾语
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

                # 根据模式确定关系
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

    def query_entity_relations(self, entity: str, max_depth: int = 1) -> Dict[str, List[dict]]:
        """
        查询实体关系（Phase 4新增）

        Args:
            entity: 实体名称
            max_depth: 最大深度

        Returns:
            {实体: [关系列表]}
        """
        result = {entity: []}

        # 获取实体的所有关系
        relations = self.fact_checker.get_entity_relations(entity)

        for rel in relations:
            other = rel.entity2 if rel.entity1 == entity else rel.entity1

            result[entity].append({
                'relation': rel.relation,
                'other_entity': other,
                'confidence': rel.confidence,
                'count': rel.count,
                'first_seen': rel.first_seen,
                'last_seen': rel.last_seen
            })

            # 递归查询
            if max_depth > 1:
                sub_result = self.query_entity_relations(other, max_depth - 1)
                for key, value in sub_result.items():
                    if key not in result:
                        result[key] = value

        return result

    def get_knowledge_graph(self, entity: str = None, max_depth: int = 2) -> dict:
        """
        获取知识图谱（Phase 4新增）

        Args:
            entity: 中心实体（None表示全局图谱）
            max_depth: 最大深度

        Returns:
            知识图谱数据
        """
        if entity:
            # 以实体为中心的图谱
            graph = self.fact_checker.get_entity_graph(entity, max_depth)
            return {
                'type': 'entity_centric',
                'center': entity,
                'graph': graph,
                'timestamp': datetime.now().isoformat()
            }
        else:
            # 全局图谱
            all_entities = list(self.entity_index.keys())
            graph = {}

            for e in all_entities[:50]:  # 限制数量
                graph[e] = []
                relations = self.fact_checker.get_entity_relations(e)
                for rel in relations:
                    other = rel.entity2 if rel.entity1 == e else rel.entity1
                    graph[e].append({
                        'entity': other,
                        'relation': rel.relation,
                        'confidence': rel.confidence
                    })

            return {
                'type': 'global',
                'entities': len(all_entities),
                'graph': graph,
                'timestamp': datetime.now().isoformat()
            }

    def check_contradictions(self) -> List[dict]:
        """
        检查矛盾（Phase 4新增）

        Returns:
            矛盾列表
        """
        return self.fact_checker.check_contradictions()

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

    def wake_up(self, query: str = None,
               auto_search: bool = True,
               search_threshold: float = 0.7) -> dict:
        """Wake-up机制"""
        self.stats['wake_up_calls'] += 1

        result = {
            'L0': self.l0_identity.copy(),
            'L1': self.l1_critical_facts.copy(),
            'total_tokens': self.stats['l0_tokens'] + self.stats['l1_tokens'],
            'query': query,
            'auto_search_triggered': False,
            'L2_results': [],
            'L3_results': []
        }

        if query and auto_search:
            l2_results = self.recall_l2_room(query, top_k=3)

            if l2_results['memories'] and l2_results['memories'][0]['similarity'] >= search_threshold:
                result['auto_search_triggered'] = True
                result['L2_results'] = l2_results['memories']
                result['total_tokens'] += sum(len(m['content'].split()) for m in l2_results['memories'][:2])

                print(f"[Wake-up] L2搜索触发，找到{len(l2_results['memories'])}条相关记忆")
            else:
                l3_results = self.recall_l3_deep(query, top_k=5)

                if l3_results['memories'] and l3_results['memories'][0]['similarity'] >= search_threshold:
                    result['auto_search_triggered'] = True
                    result['L3_results'] = l3_results['memories']
                    result['total_tokens'] += sum(len(m['content'].split()) for m in l3_results['memories'][:3])

                    print(f"[Wake-up] L3深度搜索触发，找到{len(l3_results['memories'])}条相关记忆")

        return result

    def recall_l0_identity(self) -> dict:
        """L0: Identity召回"""
        return {
            'identity': self.l0_identity.copy(),
            'tokens': self.stats['l0_tokens']
        }

    def recall_l1_critical(self) -> dict:
        """L1: Critical Facts召回"""
        return {
            'critical_facts': self.l1_critical_facts.copy(),
            'count': len(self.l1_critical_facts),
            'tokens': self.stats['l1_tokens']
        }

    def recall_l2_room(self, query: str, wing: str = None,
                      hall: HallType = None, room: str = None,
                      top_k: int = 5) -> dict:
        """L2: Room Recall"""
        query_vector = self._embed(query)

        if room or (wing and hall):
            filter_dict = {}
            if wing:
                filter_dict['wing'] = wing
            if room:
                filter_dict['room'] = room

            vector_results = self.vector_db.search(query_vector, top_k=top_k, filter_dict=filter_dict)

            results = []
            for memory_id, similarity in vector_results:
                if memory_id in self.memories:
                    memory = self.memories[memory_id]
                    results.append({
                        'memory_id': memory_id,
                        'content': memory['content'],
                        'similarity': similarity,
                        'type': memory['type'],
                        'tags': memory['tags'],
                        'created_at': memory['created_at']
                    })

            return {
                'memories': results,
                'room': f"{wing}/{hall.value if hall else '?'}/{room}" if wing else 'all',
                'count': len(results),
                'layer': 'L2_room'
            }

        return self.recall_l3_deep(query, top_k=top_k)

    def recall_l3_deep(self, query: str, top_k: int = 10,
                      use_semantic_search: bool = True) -> dict:
        """L3: Deep Search"""
        query_vector = self._embed(query)

        if use_semantic_search:
            vector_results = self.vector_db.search(query_vector, top_k=top_k, filter_dict=None)

            results = []
            for memory_id, similarity in vector_results:
                if memory_id in self.memories:
                    memory = self.memories[memory_id]
                    results.append({
                        'memory_id': memory_id,
                        'content': memory['content'],
                        'similarity': similarity,
                        'type': memory['type'],
                        'tags': memory['tags'],
                        'created_at': memory['created_at']
                    })

            return {
                'memories': results,
                'count': len(results),
                'layer': 'L3_deep'
            }

    def _create_smart_summary(self, content: str, max_length: int = 100) -> Tuple[str, List[str]]:
        """创建智能摘要"""
        if len(content) <= max_length:
            summary = content
        else:
            summary = content[:max_length-3] + "..."

        keywords = self._extract_keywords(content)
        return summary, keywords

    def _extract_keywords(self, content: str, top_k: int = 5) -> List[str]:
        """提取关键词"""
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
                print(f"[新Tunnel] 连接: {wing}/{room_name} ←→ {existing_wing}/{room_name}")

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

    def write_diary(self, content: str, tags: List[str] = None):
        """写日记"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'content': content,
            'tags': tags or [],
            'memory_count': self.stats['total_memories'],
            'reflection_count': self.stats['total_reflections']
        }

        self.diary_entries.append(entry)
        self.stats['diary_entries'] += 1

        self.remember(
            f"[日记] {content}",
            memory_type=MemoryType.REFLECTIVE,
            tags=tags or ['diary', 'self-reflection'],
            extract_entities=False  # 日志不提取实体
        )

        print(f"[日记] 已记录")

    def get_status(self) -> dict:
        """获取系统状态"""
        return {
            'version': self.version,
            'stats': self.stats.copy(),
            'memory_distribution': {
                mem_type: len(ids)
                for mem_type, ids in self.memory_index.items()
            },
            'wing_count': self.stats['total_wings'],
            'room_count': self.stats['total_rooms'],
            'tunnel_count': self.stats['total_tunnels'],
            'vector_count': self.stats['total_vectors'],
            'critical_facts_count': self.stats['critical_facts'],
            'l0_tokens': self.stats['l0_tokens'],
            'l1_tokens': self.stats['l1_tokens'],
            'wake_up_calls': self.stats['wake_up_calls'],
            'er_triples_count': self.stats['er_triples'],  # NEW
            'unique_entities': self.stats['unique_entities'],  # NEW
            'contradictions_count': self.stats['contradictions'],  # NEW
            'top_gravity_sources': sorted(
                [(s['tag_name'], s['gravity_strength'], s['mass'])
                 for s in self.gravity_sources.values()],
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'timestamp': datetime.now().isoformat()
        }


# 便捷函数
def get_sms_v9_phase4() -> SuperMemorySystemV9_Phase4:
    """获取SMSv9 Phase 4单例"""
    return SuperMemorySystemV9_Phase4()


# 测试
if __name__ == "__main__":
    print("="*70)
    print("SuperMemorySystemV9 - Phase 4: 知识图谱")
    print("Temporal ER Triples + Fact Checker")
    print("="*70)

    # 初始化
    sms = get_sms_v9_phase4()

    # 测试1: 记录记忆（自动提取ER三元组）
    print("\n[测试1] 记录记忆（自动提取ER三元组）")
    memories = [
        ("团队决定使用Clerk而非Auth0，因为定价和开发者体验更好。", "semantic",
         ["认证", "Clerk", "决策"], None, "OAuth"),

        ("之前我们选择Auth0，但发现成本太高。", "semantic",
         ["认证", "Auth0", "成本"], None, "OAuth"),

        ("Kai调试OAuth花了2小时，发现是时区配置错误。", "episodic",
         ["认证", "调试", "Kai"], None, "OAuth"),

        ("我喜欢使用TypeScript，类型安全让我更自信。", "semantic",
         ["偏好", "TypeScript"], None, None),
    ]

    memory_ids = []
    for content, mem_type, tags, wing, room in memories:
        mid = sms.remember(content, MemoryType(mem_type), tags, wing=wing, room=room)
        memory_ids.append(mid)
        print()

    # 测试2: 查看ER三元组
    print("\n[测试2] 查看ER三元组")
    print(f"ER三元组总数: {len(sms.er_triples)}")
    for i, triple in enumerate(sms.er_triples[:5], 1):
        print(f"{i}. {triple}")

    # 测试3: 查询实体关系
    print("\n[测试3] 查询实体关系")
    entity_relations = sms.query_entity_relations("团队", max_depth=1)
    print(f"\n'团队'的关系:")
    for entity, relations in entity_relations.items():
        print(f"  {entity}:")
        for rel in relations:
            print(f"    - {rel['relation']} -> {rel['other_entity']} (置信度: {rel['confidence']:.2f})")

    # 测试4: 知识图谱
    print("\n[测试4] 知识图谱")
    kg = sms.get_knowledge_graph(entity="团队", max_depth=2)
    print(f"\n图谱类型: {kg['type']}")
    print(f"中心实体: {kg['center']}")
    print(f"\n图谱结构:")
    for entity, connections in kg['graph'].items():
        print(f"  {entity} -> {', '.join(connections)}")

    # 测试5: 检查矛盾
    print("\n[测试5] 检查矛盾")
    contradictions = sms.check_contradictions()
    print(f"发现 {len(contradictions)} 个矛盾:")
    for i, con in enumerate(contradictions, 1):
        print(f"{i}. {con}")

    # 测试6: 全局知识图谱
    print("\n[测试6] 全局知识图谱")
    global_kg = sms.get_knowledge_graph(entity=None)
    print(f"实体总数: {global_kg['entities']}")

    # 测试7: 系统状态
    print("\n[测试7] 系统状态")
    status = sms.get_status()

    print(f"\n版本: {status['version']}")
    print(f"\n统计:")
    for key, value in status['stats'].items():
        print(f"  {key}: {value}")

    print("\n" + "="*70)
    print("SuperMemorySystemV9 Phase 4 测试完成！")
    print("核心创新：Temporal ER Triples + Fact Checker + 知识图谱")
    print("="*70)
