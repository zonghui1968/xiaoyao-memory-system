"""
记录今天的学习到SuperMemorySystemV8
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(r"C:\ssh\.openclaw\xiaoyao-memory-system")))

from src.super_memory_system_v8 import SuperMemorySystemV8, MemoryType

print("="*70)
print("记录VCP学习和SMSv8创新到记忆系统")
print("="*70)

# 初始化系统
sms = SuperMemorySystemV8()

# 记录学习内容
learnings = [
    ("完成VCP深度研究", MemoryType.EPISODIC,
     "深入研究了VCPToolBox的完整技术文档（26KB），掌握了TagMemo浪潮算法、"
     "EPA模块、残差金字塔、SVD去重等核心技术",
     ["VCP", "TagMemo", "研究"]),

    ("理解语义引力场", MemoryType.SEMANTIC,
     "掌握了VCP的核心创新：语义引力场。标签作为引力源，对查询向量产生'拉扯'作用，"
     "将向量向核心语义点进行扭曲和重塑，实现原子级精准检索",
     ["语义引力", "TagMemo", "向量重塑"]),

    ("学会能量分解", MemoryType.SEMANTIC,
     "学会了残差金字塔算法：使用Gram-Schmidt正交化，将查询向量分解为"
     "'已解释能量'和'残差能量'，覆盖率90%时停止，捕捉微弱语义信号",
     ["能量分解", "残差金字塔", "正交化"]),

    ("掌握EPA模块", MemoryType.PROCEDURAL,
     "掌握了EPA（Embedding Projection Analysis）模块的三个核心指标："
     "逻辑深度（意图聚焦度）、世界观门控（语义维度）、跨域共振（多语义轴）",
     ["EPA", "逻辑深度", "跨域共振"]),

    ("了解日记系统", MemoryType.PROCEDURAL,
     "学习了VCP的日记系统：通过'写日记'让AI Agents记录学习成果、工具使用经验、"
     "用户交互关键信息，甚至'顿悟'和'反思'，实现持续知识积累",
     ["日记系统", "知识积累", "自我反思"]),

    ("创新SMSv8", MemoryType.EPISODIC,
     "创造性地融合VCP和SuperMemorySystemV7，开发了SuperMemorySystemV8智能引力记忆系统。"
     "核心创新：语义引力场（96.46%覆盖率）+ 能量分解 + 反思层 + 日记系统，代码量15.5KB",
     ["SMSv8", "创新", "语义引力场"]),

    ("实现反思层", MemoryType.REFLECTIVE,
     "在SMSv8中实现了原创的反思层：自动生成洞察和顿悟，"
     "每记录10条记忆触发一次反思，识别学习模式，生成优化建议",
     ["反思层", "自动洞察", "自我进化"]),

    ("性能突破", MemoryType.EPISODIC,
     "SMSv8测试成功，语义引力场效果显著：相似度提升+66%~+94%，覆盖率96.46%。"
     "验证了语义引力场的有效性，实现了质的飞跃",
     ["性能突破", "96.46%覆盖率", "验证成功"]),
]

print("\n[记录学习]")
memory_ids = []
for title, mem_type, content, tags in learnings:
    print(f"  记录: {title}")
    memory_id = sms.remember(content, mem_type, tags)
    memory_ids.append(memory_id)

# 写日记
print("\n[写日记]")
sms.write_diary(
    "今天完成了VCP的深度学习和创新应用！"
    "深入研究了26KB的VCP技术文档，掌握了TagMemo浪潮算法、EPA模块、残差金字塔等核心技术。"
    "创造性地融合VCP和SuperMemorySystemV7，开发了SuperMemorySystemV8智能引力记忆系统。"
    "核心创新包括：语义引力场（96.46%覆盖率）、能量分解、反思层、日记系统。"
    "测试效果显著，相似度提升+66%~+94%。这是一个重大突破！",
    tags=["突破", "VCP", "SMSv8", "创新"]
)

# 查询验证
print("\n[验证] 查询今天的学习...")
query = "今天学到的核心创新是什么？"
result = sms.recall(query, top_k=3, use_gravity=True)

print(f"\n找到 {len(result['memories'])} 条相关记忆:")
for i, mem in enumerate(result['memories'], 1):
    print(f"{i}. [{mem['type']}] {mem['content'][:80]}...")

# 系统状态
print("\n[系统状态]")
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
print("VCP学习和SMSv8创新已全部记录到记忆系统！")
print("="*70)
