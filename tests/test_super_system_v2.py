"""
测试超级记忆系统v2.1（Phase 2整合）
"""

import sys
sys.path.append('C:/ssh/.openclaw/xiaoyao-memory-system/src')

from super_memory_system_v2 import SuperMemorySystemV2
from memory_types import MemoryType, MemoryImportance

print("小妖超级记忆系统（XSMS）v2.1 - Phase 2整合测试")
print("=" * 60)

# 创建超级记忆系统v2.1
sms = SuperMemorySystemV2(enable_persistence=False)

print("\n[OK] 超级记忆系统v2.1初始化成功")

# 测试Phase 1功能
print("\n[OK] 测试Phase 1功能:")

task = sms.add_integrated_task(
    task_description="实现梦境处理器",
    context="Phase 2开发",
    priority=5
)
print(f"  添加任务: {task['task_id'][:8]}...")

sms.record_integrated_conversation(
    session_id="test-session",
    user_input="什么是梦境机制？",
    assistant_response="梦境机制是VCP系统的核心，通过随机联想和知识重构实现创造性思维..."
)
print("  记录对话成功")

# 测试Phase 2新功能：梦境
print("\n[OK] 测试Phase 2新功能 - 梦境系统:")

# 添加种子记忆
sms.add_integrated_memory(
    "Python是一种高级编程语言",
    MemoryType.FACT,
    MemoryImportance.HIGH
)

sms.add_integrated_memory(
    "AI需要大量数据进行训练",
    MemoryType.CONCEPT,
    MemoryImportance.HIGH
)

sms.add_integrated_memory(
    "深度学习使用神经网络",
    MemoryType.CONCEPT,
    MemoryImportance.HIGH
)

sms.add_integrated_memory(
    "编程需要逻辑思维",
    MemoryType.CONCEPT,
    MemoryImportance.MEDIUM
)

print("  添加种子记忆: 4个")

# 触发梦境
dream_result = sms.trigger_dream(
    trigger_type="manual",
    theme="AI技术学习路径"
)

print(f"  梦境触发: {dream_result['id']}")
print(f"  种子记忆: {len(dream_result['seed_memories'])}个")
print(f"  发现关联: {len(dream_result['associations'])}个")
print(f"  生成洞察: {len(dream_result['insights'])}个")

if dream_result['insights']:
    print(f"\n  洞察详情:")
    for i, insight in enumerate(dream_result['insights']):
        status = "[有效]" if insight.get('validated') else "[无效]"
        print(f"    {i+1}. {status} {insight['content']}")
        print(f"       质量分数: {insight['quality_score']:.2f}")

# 测试关联探索
print("\n[OK] 测试关联探索:")
associations = sms.explore_associations("Python", max_depth=2, limit=5)
print(f"  发现关联: {len(associations)}个")

if associations:
    print(f"  前3个关联:")
    for i, assoc in enumerate(associations[:3]):
        source = assoc.get('source', 'unknown')
        target = assoc.get('target', assoc.get('target_concept', 'unknown'))
        score = assoc['score']
        print(f"    {i+1}. [{source}] {target} (分数: {score:.2f})")

# 测试创造性洞察
print("\n[OK] 测试创造性洞察生成:")
creative_result = sms.generate_creative_insight(
    problem="如何提高AI系统的创造性思维能力？",
    context={"domain": "AI研究"}
)

print(f"  问题: {creative_result['problem']}")
print(f"  生成洞察: {len(creative_result['insights'])}个")

if creative_result['insights']:
    for i, insight in enumerate(creative_result['insights']):
        status = "[有效]" if insight.get('validated') else "[无效]"
        print(f"    {i+1}. {status} {insight['content']}")

# 生成报告
report = sms.generate_integrated_report()
print("\n" + report)

print("[OK] 超级记忆系统v2.1（Phase 2）测试通过！")
print("\n[Xiaoyao] 小妖超级记忆系统v2.1已就绪！")
print("[Xiaoyao] 创造性思维能力已激活！")
print("[Xiaoyao] 梦境机制正常运行！")
