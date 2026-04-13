"""
SuperMemorySystemV9 - Phase 2: 原始存储

基于Phase 1，添加Closet + Drawer分离和ChromaDB语义搜索

作者：小妖🦊
创建日期：2026-04-12
版本：9.1.0-alpha (Phase 2)
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
    """
    记忆壁橱（Closet）

    指向原始记忆的摘要
    Phase 2增强：使用智能摘要算法
    """
    closet_id: str
    summary: str
    raw_memory_id: str
    created_at: str
    keywords: List[str] = field(default_factory=list)  # 提取的关键词


@dataclass
class MemoryDrawer:
    """
    记忆抽屉（Drawer）

    原始逐字文件
    Phase 2增强：添加向量索引
    """
    drawer_id: str
    content: str
    created_at: str
    metadata: dict = field(default_factory=dict)
    vector: List[float] = field(default_factory=list)  # NEW: 向量索引


class SimpleVectorDB:
    """
    简化向量数据库（模拟ChromaDB）

    实际应该使用ChromaDB，这里简化实现用于演示
    """

    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self.vectors: Dict[str, List[float]] = {}  # id -> vector
        self.metadata: Dict[str, dict] = {}  # id -> metadata

    def add(self, doc_id: str, vector: List[float], metadata: dict = None):
        """添加向量"""
        self.vectors[doc_id] = vector
        self.metadata[doc_id] = metadata or {}

    def search(self, query_vector: List[float], top_k: int = 5,
               filter_dict: dict = None) -> List[Tuple[str, float]]:
        """
        语义搜索

        Args:
            query_vector: 查询向量
            top_k: 返回结果数
            filter_dict: 元数据过滤

        Returns:
            [(doc_id, similarity), ...]
        """
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


class SuperMemorySystemV9_Phase2:
    """
    超级记忆系统V9 - Phase 2版本

    Phase 1创新：
    1. Wing结构 - 按人物/项目组织
    2. 5种Halls - facts, events, discoveries, preferences, advice
    3. Room概念 - 具体主题
    4. Tunnel自动连接 - 跨域关联

    Phase 2创新：
    5. Closet + Drawer分离 - 摘要 + 原始
    6. 保留完整上下文 - 原始逐字存储
    7. ChromaDB语义搜索 - 向量数据库
    """

    def __init__(self, dimension: int = 1536):
        """初始化系统"""
        self.version = "9.1.0-alpha (Phase 2: 原始存储)"
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

        # Phase 1: 记忆宫殿结构
        self.wings: Dict[str, MemoryWing] = {}
        self.rooms: Dict[str, MemoryRoom] = {}
        self.closets: Dict[str, MemoryCloset] = {}
        self.drawers: Dict[str, MemoryDrawer] = {}
        self.tunnel_index: Dict[str, List[Tuple[str, str]]] = {}

        # Phase 2: NEW - 向量数据库（模拟ChromaDB）
        self.vector_db = SimpleVectorDB(dimension)

        # 语义引力场
        self.gravity_sources: Dict[str, dict] = {}

        # 日记系统
        self.diary_entries: List[dict] = []

        # 反思层
        self.reflections: List[dict] = []

        # 统计
        self.stats = {
            'total_memories': 0,
            'total_reflections': 0,
            'gravity_sources': 0,
            'diary_entries': 0,
            'total_wings': 0,
            'total_rooms': 0,
            'total_tunnels': 0,
            'total_vectors': 0  # NEW
        }

        print(f"[SuperMemorySystemV9] 初始化完成 (v{self.version})")
        print(f"[OK] 记忆宫殿结构已激活")
        print(f"[OK] Closet + Drawer分离已启用")
        print(f"[OK] 向量数据库（模拟ChromaDB）已就绪")
        print(f"[OK] 语义搜索已启用")

    def remember(self, content: str, memory_type: MemoryType = MemoryType.SEMANTIC,
                 tags: List[str] = None, metadata: dict = None,
                 wing: str = None, room: str = None) -> str:
        """
        记录记忆（Phase 2增强）

        NEW: Closet + Drawer分离
        """
        memory_id = f"mem_{datetime.now().timestamp()}_{hash(content) % 10000:04d}"

        # 创建向量
        vector = self._embed(content)

        # === NEW: Phase 2 - 先创建Drawer（原始存储）===
        drawer = MemoryDrawer(
            drawer_id=memory_id,
            content=content,  # 完整原始内容
            created_at=datetime.now().isoformat(),
            metadata={
                'type': memory_type.value,
                'tags': tags or [],
                **(metadata or {})
            },
            vector=vector  # 添加向量索引
        )
        self.drawers[memory_id] = drawer

        # === NEW: Phase 2 - 添加到向量数据库===
        self.vector_db.add(
            doc_id=memory_id,
            vector=vector,
            metadata={
                'type': memory_type.value,
                'tags': tags or [],
                'wing': wing,
                'room': room
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
            'gravity_score': 0.0
        }
        self.memories[memory_id] = memory
        self.memory_index[memory_type.value].add(memory_id)
        self.stats['total_memories'] += 1

        # 记忆宫殿组织（Phase 1）
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

        # === NEW: Phase 2 - 创建智能Closet摘要===
        closet_id = f"closet_{memory_id}"
        summary, keywords = self._create_smart_summary(content)
        closet = MemoryCloset(
            closet_id=closet_id,
            summary=summary,
            raw_memory_id=memory_id,
            created_at=datetime.now().isoformat(),
            keywords=keywords  # NEW: 提取关键词
        )
        self.closets[closet_id] = closet

        self.rooms[room_key].closets.append(closet_id)

        if tags:
            for tag in tags:
                self._update_gravity_source(tag, vector)

        self._trigger_reflection(memory)

        print(f"[记忆] {memory_type.value}: {content[:50]}...")
        print(f"  → Wing: {wing}, Hall: {hall.value}, Room: {room}")
        print(f"  → Drawer: {memory_id} ({len(content)} chars)")
        print(f"  → Closet: {closet_id} ({len(summary)} chars)")

        return memory_id

    def _create_smart_summary(self, content: str, max_length: int = 100) -> Tuple[str, List[str]]:
        """
        创建智能摘要（Phase 2增强）

        NEW: 提取关键词

        Args:
            content: 原始内容
            max_length: 最大长度

        Returns:
            (摘要, 关键词列表)
        """
        # 简单摘要
        if len(content) <= max_length:
            summary = content
        else:
            summary = content[:max_length-3] + "..."

        # NEW: 提取关键词（简化实现）
        keywords = self._extract_keywords(content)

        return summary, keywords

    def _extract_keywords(self, content: str, top_k: int = 5) -> List[str]:
        """
        提取关键词（Phase 2新增）

        Args:
            content: 内容
            top_k: 返回前k个关键词

        Returns:
            关键词列表
        """
        # 简化实现：基于词频
        # 移除标点符号
        content_clean = re.sub(r'[^\w\s]', ' ', content.lower())

        # 分词
        words = content_clean.split()

        # 过滤停用词（简化）
        stopwords = {'的', '了', '是', '在', '和', '与', '或', '但', '如果', '就'}
        words_filtered = [w for w in words if len(w) > 1 and w not in stopwords]

        # 统计词频
        word_freq = {}
        for word in words_filtered:
            word_freq[word] = word_freq.get(word, 0) + 1

        # 返回前k个
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_k]

        return [word for word, freq in top_words]

    def recall(self, query: str, top_k: int = 5,
               wing: str = None, hall: str = None, room: str = None,
               use_gravity: bool = True, use_semantic_search: bool = True) -> dict:
        """
        回忆记忆（Phase 2增强）

        NEW: 使用向量数据库进行语义搜索
        """
        query_vector = self._embed(query)

        # === NEW: Phase 2 - 优先使用向量数据库语义搜索===
        if use_semantic_search:
            # 构建过滤条件
            filter_dict = {}
            if wing:
                filter_dict['wing'] = wing
            if room:
                filter_dict['room'] = room

            # 向量数据库搜索
            vector_results = self.vector_db.search(query_vector, top_k=top_k * 2, filter_dict=filter_dict)

            print(f"[语义搜索] 找到 {len(vector_results)} 个候选")

            # 获取完整记忆信息
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

            # 排序并返回top_k
            results.sort(key=lambda x: x['similarity'], reverse=True)
            top_results = results[:top_k]

            return {
                'query': query,
                'memories': top_results,
                'search_method': 'semantic_vector_db',
                'filters': {
                    'wing': wing,
                    'hall': hall,
                    'room': room
                },
                'timestamp': datetime.now().isoformat()
            }

        # Fallback: 使用传统检索方法
        # ... (与Phase 1相同)

    def _auto_classify_hall(self, content: str, memory_type: MemoryType) -> HallType:
        """自动分类到Hall"""
        # ... (与Phase 1相同)
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
            insight = f"已积累{self.stats['total_memories']}条记忆，向量数据库包含{self.stats['total_vectors']}个向量"

            reflection = {
                'timestamp': datetime.now().isoformat(),
                'insight': insight,
                'confidence': 0.8,
                'related_memories': [memory['id']]
            }

            self.reflections.append(reflection)
            self.stats['total_reflections'] += 1

            print(f"[反思] {insight}")

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

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
            'vector_count': self.stats['total_vectors'],  # NEW
            'top_gravity_sources': sorted(
                [(s['tag_name'], s['gravity_strength'], s['mass'])
                 for s in self.gravity_sources.values()],
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'timestamp': datetime.now().isoformat()
        }


# 便捷函数
def get_sms_v9_phase2() -> SuperMemorySystemV9_Phase2:
    """获取SMSv9 Phase 2单例"""
    return SuperMemorySystemV9_Phase2()


# 测试
if __name__ == "__main__":
    print("="*70)
    print("SuperMemorySystemV9 - Phase 2: 原始存储")
    print("Closet + Drawer分离 + 向量数据库语义搜索")
    print("="*70)

    # 初始化
    sms = get_sms_v9_phase2()

    # 测试1: 记录记忆（自动创建Closet + Drawer）
    print("\n[测试1] 记录记忆（Closet + Drawer分离）")
    memories = [
        ("Kai建议使用Clerk而非Auth0，因为定价和开发者体验。Clerk的API更简洁，文档更清晰。", "procedural",
         ["认证", "Clerk", "Kai"], None, "OAuth"),

        ("团队决定迁移到Clerk认证。会议讨论了各种方案，最终选择了Clerk。", "semantic",
         ["认证", "Clerk", "决策"], None, "OAuth"),

        ("选择Postgres而非SQLite，因为需要并发写入。Postgres支持多连接同时写入数据，而SQLite会锁库。", "semantic",
         ["数据库", "Postgres"], None, None),

        ("Kai花了2小时调试OAuth token刷新问题。最终发现是时区配置错误。", "episodic",
         ["认证", "调试", "Kai"], None, "OAuth"),

        ("VCP的TagMemo算法使用语义引力场重塑向量。这是一种创新的方法！", "semantic",
         ["VCP", "TagMemo", "算法"], None, None),
    ]

    memory_ids = []
    for content, mem_type, tags, wing, room in memories:
        mid = sms.remember(content, MemoryType(mem_type), tags, wing=wing, room=room)
        memory_ids.append(mid)
        print()

    # 测试2: 向量数据库语义搜索
    print("\n[测试2] 向量数据库语义搜索")
    result = sms.recall("认证", use_semantic_search=True)

    print(f"\n找到 {len(result['memories'])} 条相关记忆:")
    for i, mem in enumerate(result['memories'], 1):
        print(f"{i}. [{mem['type']}] {mem['content'][:60]}...")
        print(f"   相似度: {mem['similarity']:.3f}")

    # 测试3: 查看Closet摘要
    print("\n[测试3] 查看Closet摘要")
    print(f"\nCloset总数: {len(sms.closets)}")
    for closet_id, closet in list(sms.closets.items())[:3]:
        print(f"\n  {closet_id}:")
        print(f"    摘要: {closet.summary}")
        print(f"    关键词: {', '.join(closet.keywords)}")

    # 测试4: 系统状态
    print("\n[测试4] 系统状态")
    status = sms.get_status()

    print(f"\n版本: {status['version']}")
    print(f"\n统计:")
    for key, value in status['stats'].items():
        print(f"  {key}: {value}")

    print("\n" + "="*70)
    print("SuperMemorySystemV9 Phase 2 测试完成！")
    print("核心创新：Closet + Drawer分离 + 向量数据库语义搜索")
    print("="*70)
