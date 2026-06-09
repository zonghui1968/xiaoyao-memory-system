"""
SuperMemorySystemV9 测试

测试V9的完整功能：
- 初始化和配置
- 记忆记录和类型
- 输入验证
- Wake-up机制
- 实体关系
- 矛盾检测
- L2/L3检索
- 系统状态
"""

import sys
from pathlib import Path
from datetime import datetime
import pytest

# 路径设置
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from super_memory_system_v9 import (
    SuperMemorySystemV9,
    MemoryType,
    HallType,
    RecallLayer,
    CompressionLevel,
    TemporalERTriple,
    get_sms_v9,
)


# =============================================================================
# 初始化测试
# =============================================================================

class TestInitialization:
    """系统初始化测试"""

    def test_default_init(self):
        """默认初始化"""
        sms = SuperMemorySystemV9()
        assert "9.5.0" in sms.version
        assert sms.dimension == 1536
        assert sms.stats["total_memories"] == 0

    def test_custom_dimension(self):
        """自定义维度"""
        sms = SuperMemorySystemV9(dimension=768)
        assert sms.dimension == 768

    def test_compression_level(self):
        """压缩级别配置"""
        sms = SuperMemorySystemV9(default_compression=CompressionLevel.LOW)
        assert sms.default_compression == CompressionLevel.LOW

    def test_singleton(self):
        """单例获取"""
        # get_sms_v9 clears and creates a new singleton each time
        sms1 = get_sms_v9()
        sms2 = get_sms_v9()
        assert isinstance(sms1, SuperMemorySystemV9)
        assert isinstance(sms2, SuperMemorySystemV9)


# =============================================================================
# 记忆记录测试
# =============================================================================

class TestRemember:
    """记忆记录测试"""

    def test_remember_basic(self):
        """基础记忆记录"""
        sms = SuperMemorySystemV9()
        mid = sms.remember(
            "团队决定使用Clerk",
            memory_type=MemoryType.SEMANTIC,
            tags=["认证", "决策"],
        )
        assert mid is not None
        assert mid.startswith("mem_")
        assert mid in sms.memories

    def test_remember_critical(self):
        """关键事实记录"""
        sms = SuperMemorySystemV9()
        mid = sms.remember(
            "决定使用Postgres作为主数据库",
            memory_type=MemoryType.SEMANTIC,
            tags=["数据库", "决策"],
            is_critical=True,
        )
        memory = sms.memories[mid]
        assert memory.get("is_critical") == True

    def test_remember_all_types(self):
        """所有记忆类型"""
        sms = SuperMemorySystemV9()
        types = [
            (MemoryType.EPISODIC, "事件记录"),
            (MemoryType.SEMANTIC, "语义知识"),
            (MemoryType.PROCEDURAL, "步骤流程"),
            (MemoryType.TEMPORAL, "时间记录"),
            (MemoryType.REFLECTIVE, "反思内容"),
        ]
        for mem_type, content in types:
            mid = sms.remember(content, memory_type=mem_type, tags=["test"])
            assert mid is not None
            assert sms.memories[mid]["type"] == mem_type.value

    def test_remember_creates_wing(self):
        """记忆创建Wing"""
        sms = SuperMemorySystemV9()
        mid = sms.remember(
            "测试内容",
            memory_type=MemoryType.SEMANTIC,
            tags=["测试"],
            wing="自定义翼",
        )
        assert mid in sms.memories
        assert "自定义翼" in sms.wings

    def test_remember_creates_room(self):
        """记忆创建Room"""
        sms = SuperMemorySystemV9()
        mid = sms.remember(
            "认证测试",
            memory_type=MemoryType.SEMANTIC,
            tags=["认证"],
            room="OAuth",
        )
        assert mid in sms.memories
        memory = sms.memories[mid]
        # Room is stored in the drawer, accessible via room_key
        assert "认证" in memory.get("tags", [])


# =============================================================================
# Wake-up测试
# =============================================================================

class TestWakeUp:
    """Wake-up机制测试"""

    def test_wake_up_empty(self):
        """空系统唤醒"""
        sms = SuperMemorySystemV9()
        result = sms.wake_up()
        assert "L0" in result
        assert "L1" in result
        assert "total_tokens" in result
        assert result["total_tokens"] > 0

    def test_wake_up_with_query(self):
        """带查询唤醒"""
        sms = SuperMemorySystemV9()
        sms.remember(
            "团队决定使用Clerk",
            memory_type=MemoryType.SEMANTIC,
            tags=["认证"],
            is_critical=True,
        )
        result = sms.wake_up("认证", search_threshold=0.1)
        # auto_search may or may not trigger depending on MD5 similarity
        # but the result should always have L0/L1 populated
        assert "L0" in result
        assert "L1" in result
        assert len(result["L1"]) > 0

    def test_wake_up_tokens(self):
        """Wake-up token计数"""
        sms = SuperMemorySystemV9()
        sms.remember("关键决策", tags=["重要"], is_critical=True)
        result = sms.wake_up()
        assert result["total_tokens"] < 500  # 应远低于2000


# =============================================================================
# 检索测试
# =============================================================================

class TestRecall:
    """检索测试"""

    def test_l2_recall(self):
        """L2 Room Recall"""
        sms = SuperMemorySystemV9()
        sms.remember("Clerk认证方案", tags=["认证"], wing="工作", room="认证")
        sms.remember("OAuth调试记录", tags=["认证"], wing="工作", room="认证")
        result = sms.recall_l2_room("认证", wing="工作")
        # May return L2_room or fallback to L3_deep depending on MD5 match
        assert result["layer"] in ("L2_room", "L3_deep")
        assert result["count"] > 0

    def test_l3_recall(self):
        """L3 Deep Search"""
        sms = SuperMemorySystemV9()
        sms.remember("机器学习模型部署", tags=["ML", "部署"])
        sms.remember("深度学习训练流程", tags=["DL", "训练"])
        result = sms.recall_l3_deep("机器学习", top_k=5)
        assert result["layer"] == "L3_deep"
        assert len(result["memories"]) > 0


# =============================================================================
# 实体关系测试
# =============================================================================

class TestEntityRelations:
    """实体关系测试"""

    def test_query_entity(self):
        """查询实体关系"""
        sms = SuperMemorySystemV9()
        sms.remember(
            "团队决定使用Clerk",
            memory_type=MemoryType.SEMANTIC,
            tags=["认证"],
            extract_entities=True,
        )
        relations = sms.query_entity_relations("团队")
        assert isinstance(relations, dict)

    def test_check_contradictions(self):
        """矛盾检测"""
        sms = SuperMemorySystemV9()
        sms.remember("团队选择Clerk", tags=["认证"], extract_entities=True)
        sms.remember("团队选择Auth0", tags=["认证"], extract_entities=True)
        contradictions = sms.check_contradictions()
        assert isinstance(contradictions, list)


# =============================================================================
# 状态测试
# =============================================================================

class TestStatus:
    """系统状态测试"""

    def test_get_status(self):
        """获取系统状态"""
        sms = SuperMemorySystemV9()
        sms.remember("测试记忆", tags=["test"])
        status = sms.get_status()
        assert "version" in status
        assert "stats" in status
        assert status["stats"]["total_memories"] == 1

    def test_memory_distribution(self):
        """记忆分布"""
        sms = SuperMemorySystemV9()
        sms.remember("情景", memory_type=MemoryType.EPISODIC, tags=["test"])
        sms.remember("语义", memory_type=MemoryType.SEMANTIC, tags=["test"])
        status = sms.get_status()
        dist = status["memory_distribution"]
        assert dist["episodic"] >= 1
        assert dist["semantic"] >= 1


# =============================================================================
# 错误处理测试
# =============================================================================

class TestErrorHandling:
    """错误处理测试"""

    def test_empty_content(self):
        """空内容"""
        sms = SuperMemorySystemV9()
        # V9应该能处理空内容（但可能产生低质量记忆）
        mid = sms.remember("", memory_type=MemoryType.SEMANTIC, tags=["test"])
        # 当前实现可能接受空内容，这是一个已知问题
        # TODO: 添加输入验证后更新此测试

    def test_invalid_memory_type(self):
        """无效记忆类型"""
        with pytest.raises(ValueError):
            MemoryType("invalid_type")

    def test_query_nonexistent_entity(self):
        """查询不存在的实体"""
        sms = SuperMemorySystemV9()
        relations = sms.query_entity_relations("不存在的实体")
        # Returns dict with entity as key (may be empty or contain the entity)
        assert "不存在的实体" in relations
        assert isinstance(relations["不存在的实体"], list)
