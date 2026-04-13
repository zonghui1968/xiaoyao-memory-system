"""
测试小妖AI原生知识记忆系统
"""

import sys
sys.path.append('C:/ssh/.openclaw/xiaoyao-memory-system/src')

from xiaoyao_memory_system import XiaoyaoMemorySystem
from memory_types import MemoryType, MemoryImportance

print("小妖AI原生知识记忆系统 - 统一接口")
print("=" * 60)

# 创建系统
system = XiaoyaoMemorySystem(enable_persistence=False)

# 添加一些任务
task1 = system.add_task(
    task_description="实现知识图谱构建",
    context="XMS开发",
    priority=5
)

task2 = system.add_task(
    task_description="编写单元测试",
    context="XMS开发",
    priority=3
)

print("\n[OK] 任务添加成功")

# 记录对话
system.record_conversation(
    session_id="test-session",
    user_input="你好，我是小妖",
    assistant_response="你好！很高兴认识你"
)

print("[OK] 对话记录成功")

# 添加长期记忆
memory1 = system.add_long_term_memory(
    content="Python是一种高级编程语言",
    memory_type=MemoryType.FACT,
    importance=MemoryImportance.HIGH,
    verified=True
)

memory2 = system.add_long_term_memory(
    content="知识图谱用于表示实体和关系",
    memory_type=MemoryType.CONCEPT,
    importance=MemoryImportance.HIGH
)

print("[OK] 长期记忆添加成功")

# 添加策略
system.add_strategy(
    name="semantic_search",
    content="使用语义向量检索相关记忆",
    effectiveness=0.85
)

print("[OK] 策略添加成功")

# 记录洞察
system.record_insight(
    name="first_insight",
    content="四层记忆架构能够有效组织知识",
    effectiveness=0.8
)

print("[OK] 洞察记录成功")

# 生成报告
report = system.generate_summary_report()
print("\n" + report)

print("[OK] 系统测试通过！")
print("\n[Xiaoyao] 小妖AI原生知识记忆系统已就绪！")
