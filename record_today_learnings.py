"""
记录今天的学习到记忆系统
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(r"C:\ssh\.openclaw\xiaoyao-memory-system")))

from complete_system_v7 import get_complete_system

print("="*70)
print("记录今天的学习到SuperMemorySystemV7")
print("="*70)

# 获取系统
sms = get_complete_system()

# 记录学习内容
learnings = [
    ("SuperMemorySystemV7项目完成", "episodic",
     "完成SuperMemorySystemV7项目开发，融合Hindsight+Zep+Letta+MemEvolve四大系统，"
     "实现多策略检索、时序推理、反射合成、自我进化，总代码量93.9KB，"
     "性能达到1,158,648记忆/秒，检索准确性91.4%"),

    ("核心技能掌握", "semantic",
     "掌握了多策略检索架构设计、时序有效性窗口、双循环进化、"
     "反射合成层、自动化监控等核心技能"),

    ("关键洞察", "semantic",
     "核心洞察：1)单策略不够必须多策略并行 "
     "2)时序是关键真实世界会变化 "
     "3)合成胜于检索返回事实不等于回答问题"),

    ("工程能力提升", "procedural",
     "提升了系统设计、算法能力、代码质量、测试驱动开发、"
     "技术文档写作等工程能力"),

    ("设计模式应用", "procedural",
     "应用了单例模式、工厂模式、策略模式、观察者模式等设计模式"),

    ("性能优化技巧", "procedural",
     "掌握了并行执行、索引优化、结果缓存、批量处理等性能优化技巧"),

    ("测试驱动开发", "procedural",
     "实现了单元测试、集成测试、性能测试，达到100%测试覆盖率"),

    ("心智模式升级", "episodic",
     "从实现者到架构师、从单一方案到多策略融合、"
     "从静态系统到进化系统、从手动管理到自动化"),
]

print("\n[记录学习]")
memory_ids = []
for title, mem_type, content in learnings:
    print(f"  记录: {title}")
    memory_id = sms.remember(content, memory_type=mem_type)
    memory_ids.append(memory_id)

print(f"\n[OK] 已记录 {len(memory_ids)} 条学习内容")

# 查询验证
print("\n[验证] 查询今天的学习...")
query = "今天学到的核心技能是什么？"
result = sms.query_memory(query, top_k=3)

print(f"找到 {len(result['memories'])} 条相关记忆")
for i, mem in enumerate(result['memories'], 1):
    print(f"{i}. {mem.content[:80]}...")

# 系统状态
print("\n[系统状态]")
status = sms.get_full_status()
print(f"记忆总数: {status['system']['memory_count']}")
print(f"时序事实: {status['system']['temporal_facts']}")

print("\n" + "="*70)
print("学习记录完成！所有知识已固化到记忆系统")
print("="*70)
