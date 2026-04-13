"""
SuperMemorySystemV9 - Phase 3: 分层检索系统

基于Phase 2，添加L0-L3分层检索和wake-up机制

作者：小妖🦊
创建日期：2026-04-13
版本：9.2.0-alpha (Phase 3)
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
    L0_IDENTITY = "L0_identity"      # ~50 tokens, 始终加载
    L1_CRITICAL = "L1_critical"      # ~120 tokens, 始终加载
    L2_ROOM = "L2_room"              # 按需加载
    L3_DEEP = "L3_deep"              # 按需加载


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
    """记忆壁橱（Closet）"""
    closet_id: str
    summary: str
    raw_memory_id: str
    created_at: str
    keywords: List[str] = field(default_factory=list)
    is_critical: bool = False  # NEW: 标记为关键事实


@dataclass
class MemoryDrawer:
    """记忆抽屉（Drawer）"""
    drawer_id: str
    content: str
    created_at: str
    metadata: dict = field(default_factory=dict)
    vector: List[float] = field(default_factory=list)
    is_critical: bool = False  # NEW: 标记为关键事实


class SimpleVectorDB:
    """简化向量数据库（模拟ChromaDB）"""

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
            # 应用元数据过滤
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

            # 计算余弦相似度
            similarity = self._cosine_similarity(query_vector, vector)
            results.append((doc_id, similarity))

        # 排序
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


class SuperMemorySystemV9_Phase3:
    """
    超级记忆系统V9 - Phase 3版本

    Phase 1创新：
    1. Wing结构 - 按人物/项目组织
    2. 5种Halls - facts, events, discoveries, preferences, advice
    3. Room概念 - 具体主题
    4. Tunnel自动连接 - 跨域关联

    Phase 2创新：
    5. Closet + Drawer分离 - 摘要 + 原始
    6. 保留完整上下文 - 原始逐字存储
    7. ChromaDB语义搜索 - 向量数据库

    Phase 3创新：
    8. 分层检索系统（L0-L3）- 成本优化
    9. Wake-up机制（~170 tokens）
    10. 自动标记关键事实
    """

    def __init__(self, dimension: int = 1536):
        """初始化系统"""
        self.version = "9.2.0-alpha (Phase 3: 分层检索)"
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

        # === NEW: Phase 3 - 分层检索系统 ===

        # L0: Identity（系统身份，~50 tokens）
        self.l0_identity = {
            'system_name': 'SuperMemorySystemV9',
            'system_role': 'AI记忆助手',
            'capabilities': [
                '记忆存储和检索',
                '知识图谱构建',
                '语义搜索',
                '分层检索'
            ],
            'interaction_style': '温暖、专业、细致'
        }

        # L1: Critical Facts（关键事实，~120 tokens）
        self.l1_critical_facts: List[str] = []

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
            'critical_facts': 0,  # NEW
            'l0_tokens': 0,       # NEW
            'l1_tokens': 0,       # NEW
            'wake_up_calls': 0    # NEW
        }

        print(f"[SuperMemorySystemV9] 初始化完成 (v{self.version})")
        print(f"[OK] 记忆宫殿结构已激活")
        print(f"[OK] Closet + Drawer分离已启用")
        print(f"[OK] 向量数据库已就绪")
        print(f"[OK] 分层检索系统（L0-L3）已启用")
        print(f"[OK] Wake-up机制已就绪")

        # 计算L0 tokens
        self._calculate_l0_tokens()

    def _calculate_l0_tokens(self):
        """计算L0层的token数"""
        l0_text = json.dumps(self.l0_identity, ensure_ascii=False)
        self.stats['l0_tokens'] = len(l0_text.split())

    def remember(self, content: str, memory_type: MemoryType = MemoryType.SEMANTIC,
                 tags: List[str] = None, metadata: dict = None,
                 wing: str = None, room: str = None,
                 is_critical: bool = False) -> str:
        """
        记录记忆（Phase 3增强）

        NEW: 自动标记关键事实
        """
        memory_id = f"mem_{datetime.now().timestamp()}_{hash(content) % 10000:04d}"

        # 创建向量
        vector = self._embed(content)

        # === NEW: Phase 3 - 自动判断是否为关键事实 ===
        if is_critical:
            pass  # 用户显式标记
        else:
            # 自动判断
            is_critical = self._auto_detect_critical(content, memory_type, tags)

        # 创建Drawer（原始存储）
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
            is_critical=is_critical  # NEW
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
                'is_critical': is_critical  # NEW
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
            'is_critical': is_critical  # NEW
        }
        self.memories[memory_id] = memory
        self.memory_index[memory_type.value].add(memory_id)
        self.stats['total_memories'] += 1

        # === NEW: Phase 3 - 如果是关键事实，添加到L1 ===
        if is_critical:
            self._add_to_l1_critical(content)
            self.stats['critical_facts'] += 1

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

        # 创建Closet摘要
        closet_id = f"closet_{memory_id}"
        summary, keywords = self._create_smart_summary(content)
        closet = MemoryCloset(
            closet_id=closet_id,
            summary=summary,
            raw_memory_id=memory_id,
            created_at=datetime.now().isoformat(),
            keywords=keywords,
            is_critical=is_critical  # NEW
        )
        self.closets[closet_id] = closet

        self.rooms[room_key].closets.append(closet_id)

        if tags:
            for tag in tags:
                self._update_gravity_source(tag, vector)

        self._trigger_reflection(memory)

        critical_mark = " [关键事实]" if is_critical else ""
        print(f"[记忆{critical_mark}] {memory_type.value}: {content[:50]}...")
        print(f"  → Wing: {wing}, Hall: {hall.value}, Room: {room}")

        return memory_id

    def _auto_detect_critical(self, content: str, memory_type: MemoryType,
                             tags: List[str]) -> bool:
        """
        自动检测关键事实（Phase 3新增）

        Args:
            content: 内容
            memory_type: 记忆类型
            tags: 标签

        Returns:
            是否为关键事实
        """
        # 决策类记忆通常是关键事实
        decision_keywords = ['决定', '选择', '确认', '锁定', '决策']
        if any(kw in content for kw in decision_keywords):
            return True

        # 技术决策可能是关键
        if memory_type == MemoryType.SEMANTIC:
            tech_keywords = ['架构', '技术栈', '框架', '数据库', 'api', '认证']
            if any(kw in content.lower() for kw in tech_keywords):
                # 如果是对比类内容，标记为关键
                if 'vs' in content.lower() or '而非' in content or '不是' in content:
                    return True

        # 标签包含"重要"、"关键"等
        if tags:
            critical_tags = ['重要', '关键', 'critical', 'decision', '决策']
            if any(tag in critical_tags for tag in tags):
                return True

        return False

    def _add_to_l1_critical(self, content: str):
        """
        添加到L1关键事实列表（Phase 3新增）

        Args:
            content: 内容
        """
        # 摘要（如果太长）
        if len(content) > 100:
            summary = content[:97] + "..."
        else:
            summary = content

        self.l1_critical_facts.append(summary)

        # 保持L1在合理大小（目标~120 tokens）
        # 简化：限制条目数
        if len(self.l1_critical_facts) > 20:
            self.l1_critical_facts.pop(0)

        # 更新token统计
        self._calculate_l1_tokens()

    def _calculate_l1_tokens(self):
        """计算L1层的token数"""
        l1_text = " | ".join(self.l1_critical_facts)
        self.stats['l1_tokens'] = len(l1_text.split())

    def wake_up(self, query: str = None,
               auto_search: bool = True,
               search_threshold: float = 0.7) -> dict:
        """
        Wake-up机制（Phase 3核心创新）

        返回~170 tokens的低成本上下文：
        - L0: Identity (~50 tokens)
        - L1: Critical Facts (~120 tokens)

        Args:
            query: 查询（可选）
            auto_search: 是否自动触发L2/L3搜索
            search_threshold: 搜索阈值（相关性高于此值才返回结果）

        Returns:
            {
                'L0': {...},
                'L1': [...],
                'total_tokens': int,
                'query': str,
                'auto_search_triggered': bool,
                'L2_results': [...],  # 如果触发
                'L3_results': [...]   # 如果触发
            }
        """
        self.stats['wake_up_calls'] += 1

        # 构建wake-up上下文
        result = {
            'L0': self.l0_identity.copy(),
            'L1': self.l1_critical_facts.copy(),
            'total_tokens': self.stats['l0_tokens'] + self.stats['l1_tokens'],
            'query': query,
            'auto_search_triggered': False,
            'L2_results': [],
            'L3_results': []
        }

        # 如果有查询且启用自动搜索
        if query and auto_search:
            # 先尝试L2: Room Recall
            l2_results = self.recall_l2_room(query, top_k=3)

            if l2_results['memories'] and l2_results['memories'][0]['similarity'] >= search_threshold:
                # L2找到高质量结果
                result['auto_search_triggered'] = True
                result['L2_results'] = l2_results['memories']
                result['total_tokens'] += sum(len(m['content'].split()) for m in l2_results['memories'][:2])

                print(f"[Wake-up] L2搜索触发，找到{len(l2_results['memories'])}条相关记忆")
            else:
                # L2不够好，尝试L3: Deep Search
                l3_results = self.recall_l3_deep(query, top_k=5)

                if l3_results['memories'] and l3_results['memories'][0]['similarity'] >= search_threshold:
                    result['auto_search_triggered'] = True
                    result['L3_results'] = l3_results['memories']
                    result['total_tokens'] += sum(len(m['content'].split()) for m in l3_results['memories'][:3])

                    print(f"[Wake-up] L3深度搜索触发，找到{len(l3_results['memories'])}条相关记忆")

        return result

    def recall_l0_identity(self) -> dict:
        """
        L0: Identity召回

        Returns:
            系统身份信息（~50 tokens）
        """
        return {
            'identity': self.l0_identity.copy(),
            'tokens': self.stats['l0_tokens']
        }

    def recall_l1_critical(self) -> dict:
        """
        L1: Critical Facts召回

        Returns:
            关键事实列表（~120 tokens）
        """
        return {
            'critical_facts': self.l1_critical_facts.copy(),
            'count': len(self.l1_critical_facts),
            'tokens': self.stats['l1_tokens']
        }

    def recall_l2_room(self, query: str, wing: str = None,
                      hall: HallType = None, room: str = None,
                      top_k: int = 5) -> dict:
        """
        L2: Room Recall（按房间召回）

        按需加载，只搜索特定房间

        Args:
            query: 查询
            wing: 翼（可选）
            hall: 厅（可选）
            room: 房间（可选）
            top_k: 返回数量

        Returns:
            {
                'memories': [...],
                'room': str,
                'count': int
            }
        """
        query_vector = self._embed(query)

        # 如果指定了房间，优先搜索该房间
        if room or (wing and hall):
            # 构建房间过滤
            filter_dict = {}
            if wing:
                filter_dict['wing'] = wing
            if room:
                filter_dict['room'] = room

            # 向量搜索
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

        # 如果没有指定房间，回退到L3
        return self.recall_l3_deep(query, top_k=top_k)

    def recall_l3_deep(self, query: str, top_k: int = 10,
                      use_semantic_search: bool = True) -> dict:
        """
        L3: Deep Search（深度搜索）

        全局搜索，成本最高

        Args:
            query: 查询
            top_k: 返回数量
            use_semantic_search: 是否使用语义搜索

        Returns:
            {
                'memories': [...],
                'count': int,
                'layer': 'L3_deep'
            }
        """
        query_vector = self._embed(query)

        # 使用向量数据库全局搜索
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
            insight = f"已积累{self.stats['total_memories']}条记忆，其中{self.stats['critical_facts']}条关键事实"

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
            tags=tags or ['diary', 'self-reflection']
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
            'critical_facts_count': self.stats['critical_facts'],  # NEW
            'l0_tokens': self.stats['l0_tokens'],  # NEW
            'l1_tokens': self.stats['l1_tokens'],  # NEW
            'wake_up_calls': self.stats['wake_up_calls'],  # NEW
            'top_gravity_sources': sorted(
                [(s['tag_name'], s['gravity_strength'], s['mass'])
                 for s in self.gravity_sources.values()],
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'timestamp': datetime.now().isoformat()
        }


# 便捷函数
def get_sms_v9_phase3() -> SuperMemorySystemV9_Phase3:
    """获取SMSv9 Phase 3单例"""
    return SuperMemorySystemV9_Phase3()


# 测试
if __name__ == "__main__":
    print("="*70)
    print("SuperMemorySystemV9 - Phase 3: 分层检索系统")
    print("L0-L3分层 + Wake-up机制（~170 tokens）")
    print("="*70)

    # 初始化
    sms = get_sms_v9_phase3()

    # 测试1: 记录记忆（自动检测关键事实）
    print("\n[测试1] 记录记忆（自动检测关键事实）")
    memories = [
        ("团队决定使用Clerk而非Auth0，因为定价和开发者体验更好。", "semantic",
         ["认证", "Clerk", "决策"], None, "OAuth"),

        ("选择Postgres而非SQLite，因为需要并发写入支持。", "semantic",
         ["数据库", "Postgres"], None, None),

        ("Kai调试OAuth花了2小时，发现是时区配置错误。", "episodic",
         ["认证", "调试", "Kai"], None, "OAuth"),

        ("我喜欢使用TypeScript，类型安全让我更自信。", "semantic",
         ["偏好", "TypeScript"], None, None),

        ("VCP的TagMemo算法使用语义引力场重塑向量，这是创新方法！", "semantic",
         ["VCP", "TagMemo", "算法"], None, None),
    ]

    memory_ids = []
    for content, mem_type, tags, wing, room in memories:
        mid = sms.remember(content, MemoryType(mem_type), tags, wing=wing, room=room)
        memory_ids.append(mid)
        print()

    # 测试2: Wake-up机制（~170 tokens）
    print("\n[测试2] Wake-up机制")
    wake_result = sms.wake_up("认证")

    print(f"\n=== Wake-up结果 ===")
    print(f"L0 (Identity): {wake_result['L0']['system_name']}")
    print(f"L1 (Critical Facts): {len(wake_result['L1'])}条")
    for i, fact in enumerate(wake_result['L1'][:3], 1):
        print(f"  {i}. {fact}")
    print(f"总Tokens: {wake_result['total_tokens']} (目标: ~170)")

    if wake_result['auto_search_triggered']:
        print(f"\n自动搜索已触发:")
        if wake_result['L2_results']:
            print(f"  L2结果: {len(wake_result['L2_results'])}条")
        if wake_result['L3_results']:
            print(f"  L3结果: {len(wake_result['L3_results'])}条")

    # 测试3: L0单独召回
    print("\n[测试3] L0 Identity召回")
    l0 = sms.recall_l0_identity()
    print(f"L0 Tokens: {l0['tokens']}")
    print(f"系统角色: {l0['identity']['system_role']}")

    # 测试4: L1单独召回
    print("\n[测试4] L1 Critical Facts召回")
    l1 = sms.recall_l1_critical()
    print(f"L1 Tokens: {l1['tokens']}")
    print(f"关键事实数: {l1['count']}")
    print(f"示例:")
    for i, fact in enumerate(l1['critical_facts'][:3], 1):
        print(f"  {i}. {fact}")

    # 测试5: L2 Room Recall
    print("\n[测试5] L2 Room Recall")
    l2 = sms.recall_l2_room("认证", room="OAuth", top_k=3)
    print(f"L2结果 (Room: {l2['room']}): {l2['count']}条")
    for mem in l2['memories']:
        print(f"  - {mem['content'][:50]}... (相似度: {mem['similarity']:.3f})")

    # 测试6: L3 Deep Search
    print("\n[测试6] L3 Deep Search")
    l3 = sms.recall_l3_deep("调试", top_k=3)
    print(f"L3结果: {l3['count']}条")
    for mem in l3['memories']:
        print(f"  - {mem['content'][:50]}... (相似度: {mem['similarity']:.3f})")

    # 测试7: 系统状态
    print("\n[测试7] 系统状态")
    status = sms.get_status()

    print(f"\n版本: {status['version']}")
    print(f"\n统计:")
    for key, value in status['stats'].items():
        print(f"  {key}: {value}")

    print("\n" + "="*70)
    print("SuperMemorySystemV9 Phase 3 测试完成！")
    print("核心创新：分层检索系统（L0-L3）+ Wake-up机制（~170 tokens）")
    print("="*70)
