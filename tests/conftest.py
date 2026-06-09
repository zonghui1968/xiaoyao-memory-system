"""
测试夹具和共享工具
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import pytest


# =============================================================================
# 路径设置
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))


# =============================================================================
# 夹具
# =============================================================================

@pytest.fixture
def empty_system():
    """返回未初始化的记忆系统"""
    return None  # 调用方自行初始化


@pytest.fixture
def sms():
    """返回已初始化的SuperMemorySystemV9实例"""
    try:
        from super_memory_system_v9 import get_sms_v9
        return get_sms_v9()
    except ImportError as e:
        pytest.skip(f"System not importable: {e}")


@pytest.fixture
def populated_system():
    """返回预填充了测试数据的系统"""
    try:
        from super_memory_system_v9 import get_sms_v9, MemoryType
        system = get_sms_v9()

        test_memories = [
            ("团队决定使用Clerk而非Auth0，因为定价和开发者体验更好。",
             MemoryType.SEMANTIC, ["认证", "Clerk", "决策"]),
            ("Kai调试OAuth花了2小时，发现是时区配置错误。",
             MemoryType.EPISODIC, ["认证", "调试", "Kai"]),
            ("我喜欢使用TypeScript，类型安全让我更自信。",
             MemoryType.SEMANTIC, ["偏好", "TypeScript"]),
            ("选择Postgres而非SQLite，因为需要并发写入和事务支持。",
             MemoryType.SEMANTIC, ["数据库", "Postgres", "决策"]),
            ("OAuth配置步骤：1.创建应用 2.配置回调URL 3.获取client_secret 4.实现token交换",
             MemoryType.PROCEDURAL, ["认证", "OAuth", "配置"]),
        ]

        for content, mem_type, tags in test_memories:
            system.remember(content, memory_type=mem_type, tags=tags)

        return system
    except ImportError as e:
        pytest.skip(f"System not importable: {e}")


@pytest.fixture
def xiaoyao_system():
    """返回XiaoyaoMemorySystem实例"""
    try:
        from xiaoyao_memory_system import get_xiaoyao_memory
        return get_xiaoyao_memory()
    except ImportError as e:
        pytest.skip(f"System not importable: {e}")


@pytest.fixture
def sample_content():
    """返回测试用的示例内容"""
    return {
        "decision": "团队决定迁移到Kubernetes，以提高可扩展性和部署效率。",
        "debugging": "花了3小时调试数据库连接池泄漏，最终发现是忘记在finally中关闭连接。",
        "preference": "我更喜欢使用Rust进行底层系统编程，安全性更高。",
    }


@pytest.fixture
def temp_dir(tmp_path):
    """临时目录"""
    return tmp_path
