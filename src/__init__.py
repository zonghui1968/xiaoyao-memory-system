"""
小妖记忆系统 (Xiaoyao Memory System)

SuperMemorySystemV9 - 基于MemPalace系统（LongMemEval 96.6% R@5）设计的AI记忆系统。

核心功能:
- 记忆宫殿架构 (Wing/Room/Hall/Tunnel)
- 原始存储优先 (Closet + Drawer分离)
- 分层检索系统 (L0-L3 + Wake-up机制)
- 知识图谱 (Temporal ER Triples + Fact Checker)
- AAAK压缩 (可选，默认禁用)

使用:
    from xiaoyao_memory_system import SuperMemorySystemV9, MemoryType

    sms = SuperMemorySystemV9()
    sms.remember("团队决定使用Clerk。", memory_type=MemoryType.SEMANTIC,
                 tags=["认证", "决策"])
    wake_result = sms.wake_up("认证")
"""

__version__ = "9.5.0"
__author__ = "小妖🦊 (Zonghui Yang)"
__email__ = "hizonghui@gmail.com"

# 核心系统
from .super_memory_system_v9 import (
    SuperMemorySystemV9,
    get_sms_v9,
)

# 枚举类型
from .super_memory_system_v9 import (
    MemoryType,
    HallType,
    RecallLayer,
    CompressionLevel,
)

# 数据结构
from .super_memory_system_v9 import (
    TemporalERTriple,
)

# 小妖集成系统
from .xiaoyao_memory_system import (
    XiaoyaoMemorySystem,
    get_xiaoyao_memory,
)

# 向量存储 (可选)
try:
    from .vector_store import (
        VectorStore,
        SimpleVectorStore,
        LanceDBVectorStore,
    )
except ImportError:
    pass

__all__ = [
    # 核心
    "SuperMemorySystemV9",
    "get_sms_v9",
    "XiaoyaoMemorySystem",
    "get_xiaoyao_memory",
    # 枚举
    "MemoryType",
    "HallType",
    "RecallLayer",
    "CompressionLevel",
    # 数据结构
    "TemporalERTriple",
    # 版本
    "__version__",
    "__author__",
]
