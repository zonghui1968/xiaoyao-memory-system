"""
测试小妖超级记忆系统（XSMS）
"""

import sys
sys.path.append('C:/ssh/.openclaw/xiaoyao-memory-system/src')

from super_memory_system import SuperMemorySystem
from memory_types import MemoryType, MemoryImportance

print("小妖超级记忆系统（XSMS）- 整合系统")
print("=" * 60)

# 创建超级记忆系统
sms = SuperMemorySystem(enable_persistence=False)

print("\n[OK] 超级记忆系统初始化成功")

# 测试Layer 0: 配置层
print("\n[OK] 测试配置层:")
rules = sms.get_system_rules()
print(f"  组织规则存在: {rules['organization'].get('exists', False)}")

# 测试Layer 2: 工作记忆层
print("\n[OK] 测试工作记忆层:")
task = sms.add_integrated_task(
    task_description="实现梦境处理器",
    context="VCP开发",
    priority=5
)
print(f"  添加任务: {task['task_id']}")

# 测试Layer 3: 短期记忆层
print("\n[OK] 测试短期记忆层:")
sms.record_integrated_conversation(
    session_id="test-session",
    user_input="什么是VCP系统？",
    assistant_response="VCP是一个创造性思维系统..."
)
print(f"  对话记录成功")

# 测试Layer 4: 长期记忆层
print("\n[OK] 测试长期记忆层:")
memory = sms.add_integrated_memory(
    content="VCP系统通过梦境机制实现创造性思维",
    memory_type=MemoryType.CONCEPT,
    importance=MemoryImportance.HIGH
)
print(f"  添加记忆: {memory['memory_id']}")

# 测试Layer 5: 元认知层
print("\n[OK] 测试元认知层:")
sms.add_integrated_strategy(
    name="dream_trigger",
    content="定期触发梦境周期以发现新关联",
    effectiveness=0.8
)
print(f"  添加策略成功")

# 生成报告
report = sms.generate_integrated_report()
print("\n" + report)

print("[OK] 超级记忆系统测试通过！")
print("\n[Xiaoyao] 小妖超级记忆系统（XSMS）已就绪！")
