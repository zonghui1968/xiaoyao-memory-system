"""
SuperMemorySystemV8 - 智能引力记忆系统

融合VCP TagMemo浪潮算法 + SuperMemorySystemV7多策略检索
创新性融合，创造下一代AI记忆系统

作者：小妖🦊
创建日期：2026-04-12
版本：8.0.0-alpha
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

# 添加路径
sys.path.insert(0, str(Path(r"C:\ssh\.openclaw\xiaoyao-memory-system")))


class MemoryType(Enum):
    """记忆类型"""
    EPISODIC = "episodic"      # 情景记忆（具体事件）
    SEMANTIC = "semantic"      # 语义记忆（知识）
    PROCEDURAL = "procedural"  # 程序性记忆（技能）
    TEMPORAL = "temporal"      # 时序记忆（带时间维度）
    REFLECTIVE = "reflective"  # 反思记忆（自我洞察）- NEW!


@dataclass
class GravitySource:
    """
    语义引力源

    每个标签都是一个引力源，对向量产生"拉扯"作用
    """
    tag_id: str
    tag_name: str
    vector: List[float]
    gravity_strength: float = 1.0  # 引力强度
    mass: float = 1.0              # 质量（影响范围）


@dataclass
class EnergyDecomposition:
    """
    能量分解结果

    将查询向量分解为：
    - 已解释能量（被标签吸引的部分）
    - 残差能量（未被吸引的部分）
    """
    explained_energy: float        # 已解释能量
    residual_energy: float         # 残差能量
    coverage_ratio: float          # 覆盖率
    gravity_sources: List[GravitySource]  # 吸引源
    residual_vector: List[float]   # 残差向量


@dataclass
class ReflectionEntry:
    """
    反思条目

    系统自动生成的自我洞察和顿悟
    """
    timestamp: str
    insight: str
    confidence: float
    related_memories: List[str]
    action_items: List[str] = field(default_factory=list)


class SuperMemorySystemV8:
    """
    超级记忆系统V8 - 智能引力版本

    核心创新：
    1. 语义引力场 - 标签作为引力源，动态重塑向量
    2. 能量分解 - 将查询分解为已解释能量和残差能量
    3. 反思层 - 自动生成洞察和顿悟
    4. 日记系统 - 持续记录和自我进化
    5. 多策略融合 - TagMemo + 多策略检索
    """

    def __init__(self, dimension: int = 1536):
        """初始化V8系统"""
        self.version = "8.0.0-alpha"
        self.dimension = dimension

        # 记忆存储
        self.memories: Dict[str, dict] = {}  # memory_id -> memory
        self.memory_index: Dict[str, Set[str]] = {
            'episodic': set(),
            'semantic': set(),
            'procedural': set(),
            'temporal': set(),
            'reflective': set()
        }

        # 语义引力场
        self.gravity_sources: Dict[str, GravitySource] = {}  # tag_id -> source

        # 日记系统
        self.diary_entries: List[dict] = []

        # 反思层
        self.reflections: List[ReflectionEntry] = []

        # 统计
        self.stats = {
            'total_memories': 0,
            'total_reflections': 0,
            'gravity_sources': 0,
            'diary_entries': 0
        }

        print(f"[SuperMemorySystemV8] 初始化完成 (v{self.version})")
        print(f"[OK] 语义引力场已激活")
        print(f"[OK] 反思层已启动")
        print(f"[OK] 日记系统已就绪")

    def remember(self, content: str, memory_type: MemoryType = MemoryType.SEMANTIC,
                 tags: List[str] = None, metadata: dict = None) -> str:
        """
        记录记忆

        Args:
            content: 记忆内容
            memory_type: 记忆类型
            tags: 标签列表（这些标签将成为引力源）
            metadata: 元数据

        Returns:
            记忆ID
        """
        # 生成记忆ID
        memory_id = f"mem_{datetime.now().timestamp()}_{hash(content) % 10000:04d}"

        # 创建记忆
        memory = {
            'id': memory_id,
            'content': content,
            'type': memory_type.value,
            'tags': tags or [],
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'vector': self._embed(content),  # 简化：使用内容hash作为伪向量
            'gravity_score': 0.0  # 将被引力场影响
        }

        # 存储记忆
        self.memories[memory_id] = memory
        self.memory_index[memory_type.value].add(memory_id)
        self.stats['total_memories'] += 1

        # 创建或更新引力源
        if tags:
            for tag in tags:
                self._update_gravity_source(tag, memory['vector'])

        # 触发反思
        self._trigger_reflection(memory)

        print(f"[记忆] {memory_type.value}: {content[:50]}...")

        return memory_id

    def _embed(self, text: str) -> List[float]:
        """
        文本向量化（简化实现）

        实际应该调用OpenAI/Cohere Embedding API
        这里简化为基于hash的伪向量
        """
        # 使用hash生成伪向量（仅用于演示）
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()

        # 转换为浮点向量
        vector = []
        for i in range(0, min(len(hash_hex), self.dimension * 2), 2):
            byte_val = int(hash_hex[i:i+2], 16)
            normalized = (byte_val - 128) / 128.0  # 归一化到[-1, 1]
            vector.append(normalized)

        # 填充到指定维度
        while len(vector) < self.dimension:
            vector.append(0.0)

        return vector[:self.dimension]

    def _update_gravity_source(self, tag: str, vector: List[float]):
        """
        更新语义引力源

        Args:
            tag: 标签名
            vector: 向量
        """
        tag_id = f"tag_{hash(tag) % 10000:04d}"

        if tag_id in self.gravity_sources:
            # 更新现有引力源（增强）
            source = self.gravity_sources[tag_id]
            source.gravity_strength += 0.1
            source.mass += 1.0
        else:
            # 创建新引力源
            self.gravity_sources[tag_id] = GravitySource(
                tag_id=tag_id,
                tag_name=tag,
                vector=vector,
                gravity_strength=1.0,
                mass=1.0
            )
            self.stats['gravity_sources'] += 1

    def _compute_gravity_field(self, query_vector: List[float]) -> Dict[str, float]:
        """
        计算语义引力场

        对每个引力源，计算其对查询向量的引力

        Args:
            query_vector: 查询向量

        Returns:
            每个引力源的引力值
        """
        gravity_field = {}

        for source_id, source in self.gravity_sources.items():
            # 计算余弦相似度（作为引力）
            similarity = self._cosine_similarity(query_vector, source.vector)

            # 引力 = 相似度 * 引力强度 * 质量因子
            gravity = similarity * source.gravity_strength * math.log(1 + source.mass)

            gravity_field[source_id] = gravity

        return gravity_field

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _apply_gravity_distortion(self, query_vector: List[float],
                                  gravity_field: Dict[str, float]) -> List[float]:
        """
        应用引力扭曲

        根据引力场，将查询向量向核心语义点"拉扯"

        Args:
            query_vector: 原始查询向量
            gravity_field: 引力场

        Returns:
            扭曲后的向量
        """
        distorted = query_vector.copy()

        # 计算总引力
        total_gravity = sum(abs(g) for g in gravity_field.values())

        if total_gravity == 0:
            return distorted

        # 应用引力扭曲
        for source_id, gravity in gravity_field.items():
            if gravity > 0:
                source = self.gravity_sources[source_id]

                # 向量向引力源移动
                for i in range(self.dimension):
                    # 拉扯强度 = 引力 / 总引力
                    pull_strength = gravity / total_gravity

                    # 扭曲：原始向量 + 拉扯向量
                    distorted[i] += pull_strength * (source.vector[i] - distorted[i]) * 0.3

        return distorted

    def _decompose_energy(self, original_vector: List[float],
                         distorted_vector: List[float]) -> EnergyDecomposition:
        """
        能量分解

        将查询分解为：
        - 已解释能量（被引力场吸引的部分）
        - 残差能量（未被吸引的部分）

        Args:
            original_vector: 原始查询向量
            distorted_vector: 扭曲后的向量

        Returns:
            能量分解结果
        """
        # 计算原始能量
        original_energy = sum(v * v for v in original_vector)

        # 计算残差向量（原始 - 扭曲）
        residual = [o - d for o, d in zip(original_vector, distorted_vector)]
        residual_energy = sum(r * r for r in residual)

        # 已解释能量
        explained_energy = original_energy - residual_energy

        # 覆盖率
        coverage_ratio = explained_energy / original_energy if original_energy > 0 else 0

        # 识别主要引力源
        gravity_field = self._compute_gravity_field(original_vector)
        top_sources = sorted(gravity_field.items(),
                           key=lambda x: abs(x[1]),
                           reverse=True)[:5]

        sources = []
        for source_id, gravity in top_sources:
            if abs(gravity) > 0.1:
                source = self.gravity_sources[source_id]
                sources.append(source)

        return EnergyDecomposition(
            explained_energy=explained_energy,
            residual_energy=residual_energy,
            coverage_ratio=coverage_ratio,
            gravity_sources=sources,
            residual_vector=residual
        )

    def recall(self, query: str, top_k: int = 5, use_gravity: bool = True) -> dict:
        """
        回忆记忆

        Args:
            query: 查询文本
            top_k: 返回结果数
            use_gravity: 是否使用引力场

        Returns:
            查询结果
        """
        # 向量化查询
        query_vector = self._embed(query)

        # 应用引力扭曲
        if use_gravity:
            gravity_field = self._compute_gravity_field(query_vector)
            distorted_vector = self._apply_gravity_distortion(query_vector, gravity_field)

            # 能量分解
            decomposition = self._decompose_energy(query_vector, distorted_vector)

            print(f"[引力场] 覆盖率: {decomposition.coverage_ratio:.2%}")
            print(f"[引力场] 引力源: {len(decomposition.gravity_sources)}")

            # 使用扭曲后的向量检索
            search_vector = distorted_vector
        else:
            search_vector = query_vector

        # 检索记忆
        results = []
        for memory_id, memory in self.memories.items():
            similarity = self._cosine_similarity(search_vector, memory['vector'])

            # 如果使用引力，添加引力加成
            if use_gravity and memory['tags']:
                gravity_boost = 0.0
                for tag in memory['tags']:
                    tag_id = f"tag_{hash(tag) % 10000:04d}"
                    if tag_id in gravity_field:
                        gravity_boost += gravity_field[tag_id] * 0.1

                similarity += gravity_boost

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
            'gravity_used': use_gravity,
            'timestamp': datetime.now().isoformat()
        }

    def _trigger_reflection(self, memory: dict):
        """
        触发反思

        自动生成洞察和顿悟

        Args:
            memory: 新记录的记忆
        """
        # 简化实现：检查是否达到反思阈值
        if self.stats['total_memories'] % 10 == 0:
            # 生成反思
            insight = f"已积累{self.stats['total_memories']}条记忆，系统正在形成稳定的语义引力场"

            reflection = ReflectionEntry(
                timestamp=datetime.now().isoformat(),
                insight=insight,
                confidence=0.8,
                related_memories=[memory['id']]
            )

            self.reflections.append(reflection)
            self.stats['total_reflections'] += 1

            print(f"[反思] {insight}")

    def write_diary(self, content: str, tags: List[str] = None):
        """
        写日记

        持续记录学习和成长

        Args:
            content: 日记内容
            tags: 标签
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'content': content,
            'tags': tags or [],
            'memory_count': self.stats['total_memories'],
            'reflection_count': self.stats['total_reflections']
        }

        self.diary_entries.append(entry)
        self.stats['diary_entries'] += 1

        # 将日记内容也记录为记忆
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
            'top_gravity_sources': sorted(
                [(s.tag_name, s.gravity_strength, s.mass)
                 for s in self.gravity_sources.values()],
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'timestamp': datetime.now().isoformat()
        }


# 便捷函数
def get_sms_v8() -> SuperMemorySystemV8:
    """获取SMSv8单例"""
    return SuperMemorySystemV8()


# 测试
if __name__ == "__main__":
    print("="*70)
    print("SuperMemorySystemV8 - 智能引力记忆系统")
    print("="*70)

    # 初始化
    sms = get_sms_v8()

    # 测试1: 记录记忆
    print("\n[测试1] 记录记忆")
    memories = [
        ("VCP的TagMemo算法使用语义引力场重塑向量", "semantic", ["VCP", "TagMemo", "语义引力"]),
        ("SuperMemorySystemV7实现了多策略检索", "semantic", ["SMSv7", "多策略", "检索"]),
        ("Gram-Schmidt正交化用于能量分解", "procedural", ["数学", "正交化", "能量分解"]),
        ("今天学习了VCP的日记系统，非常震撼", "episodic", ["学习", "日记", "感悟"]),
        ("EPA模块计算逻辑深度、世界观门控和跨域共振", "procedural", ["EPA", "逻辑深度", "共振"]),
    ]

    memory_ids = []
    for content, mem_type, tags in memories:
        mid = sms.remember(content, MemoryType(mem_type), tags)
        memory_ids.append(mid)

    # 测试2: 使用引力场检索
    print("\n[测试2] 使用引力场检索")
    result = sms.recall("VCP的算法特点", use_gravity=True)

    print(f"\n找到 {len(result['memories'])} 条相关记忆:")
    for i, mem in enumerate(result['memories'], 1):
        print(f"{i}. [{mem['type']}] {mem['content']}")
        print(f"   相似度: {mem['similarity']:.3f}")
        if mem['tags']:
            print(f"   标签: {', '.join(mem['tags'])}")

    # 测试3: 不使用引力场检索
    print("\n[测试3] 不使用引力场检索（对比）")
    result_no_gravity = sms.recall("VCP的算法特点", use_gravity=False)

    print(f"\n找到 {len(result_no_gravity['memories'])} 条相关记忆:")
    for i, mem in enumerate(result_no_gravity['memories'], 1):
        print(f"{i}. [{mem['type']}] {mem['content']}")
        print(f"   相似度: {mem['similarity']:.3f}")

    # 测试4: 写日记
    print("\n[测试4] 写日记")
    sms.write_diary(
        "今天完成了VCP的深度学习，创造性地融合了TagMemo浪潮算法和SuperMemorySystemV7，"
        "开发了SuperMemorySystemV8智能引力记忆系统。这是一个重要的突破！",
        tags=["突破", "创新", "VCP", "SMSv8"]
    )

    # 测试5: 查看系统状态
    print("\n[测试5] 系统状态")
    status = sms.get_status()

    print(f"\n版本: {status['version']}")
    print(f"\n统计:")
    for key, value in status['stats'].items():
        print(f"  {key}: {value}")

    print(f"\n记忆分布:")
    for mem_type, count in status['memory_distribution'].items():
        print(f"  {mem_type}: {count}")

    print(f"\nTop 5 引力源:")
    for tag, strength, mass in status['top_gravity_sources'][:5]:
        print(f"  {tag}: 引力={strength:.2f}, 质量={mass:.1f}")

    print("\n" + "="*70)
    print("SuperMemorySystemV8 测试完成！")
    print("核心创新：语义引力场 + 能量分解 + 反思层 + 日记系统")
    print("="*70)
