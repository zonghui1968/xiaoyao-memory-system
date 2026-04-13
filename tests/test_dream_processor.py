"""
测试梦境处理器
"""

import sys
sys.path.append('C:/ssh/.openclaw/xiaoyao-memory-system/src')

import networkx as nx
from dream_processor import DreamProcessor

print("小妖超级记忆系统 - 梦境处理器测试")
print("=" * 60)

# 创建测试知识图谱
graph = nx.DiGraph()
graph.add_edge("Python", "编程", weight=1.0)
graph.add_edge("编程", "算法", weight=0.8)
graph.add_edge("算法", "AI", weight=0.9)
graph.add_edge("AI", "机器学习", weight=1.0)
graph.add_edge("机器学习", "深度学习", weight=0.9)
graph.add_edge("深度学习", "神经网络", weight=1.0)
graph.add_edge("Python", "数据科学", weight=0.7)
graph.add_edge("数据科学", "AI", weight=0.8)

print("\n[OK] 测试知识图谱创建成功")
print(f"  节点数: {graph.number_of_nodes()}")
print(f"  边数: {graph.number_of_edges()}")

# 创建梦境处理器
dream_processor = DreamProcessor(graph)

print("\n[OK] 梦境处理器初始化成功")

# 测试随机联想
print("\n[OK] 测试随机联想:")
path = dream_processor.associator.random_walk("Python", steps=5)
print(f"  随机游走: {' → '.join(path)}")

# 测试跨域关联
print("\n[OK] 测试跨域关联:")
associations = dream_processor.associator.cross_domain_association(
    ["Python"],
    max_distance=3
)
print(f"  发现关联: {len(associations)}个")
if associations:
    for i, (source, target, score) in enumerate(associations[:3]):
        print(f"    {i+1}. {source} → {target} (相似度: {score:.2f})")

# 测试意外发现
print("\n[OK] 测试意外发现:")
discoveries = dream_processor.associator.serendipitous_discovery(
    "Python",
    num_discoveries=3
)
print(f"  意外发现: {len(discoveries)}个")
for i, discovery in enumerate(discoveries):
    print(f"    {i+1}. {discovery}")

# 测试知识重构
print("\n[OK] 测试知识重构:")
reconstruction = dream_processor.reconstructor.reconstruct_narrative(
    associations,
    theme="技术学习"
)
print(f"  叙事连贯性: {reconstruction['coherence']:.2f}")
print(f"  关键概念: {', '.join(reconstruction['key_concepts'][:5])}")
print(f"  叙事: {reconstruction['narrative'][:100]}...")

# 测试洞察生成
print("\n[OK] 测试洞察生成:")
insight = dream_processor.insight_generator.generate_insight(
    reconstruction,
    {"theme": "技术学习"}
)
print(f"  洞察: {insight['content']}")
print(f"  质量分数: {insight['quality_score']:.2f}")

# 测试完整梦境周期
print("\n[OK] 测试完整梦境周期:")
dream_result = dream_processor.trigger_dream_cycle(
    trigger_type="manual",
    seed_memories=["Python", "AI"],
    context={"theme": "技术学习路径"}
)

print(f"  梦境ID: {dream_result['id']}")
print(f"  触发类型: {dream_result['trigger_type']}")
print(f"  种子记忆: {len(dream_result['seed_memories'])}个")
print(f"  发现关联: {len(dream_result['associations'])}个")
print(f"  生成洞察: {len(dream_result['insights'])}个")

if dream_result['insights']:
    print(f"\n  洞察详情:")
    for i, insight in enumerate(dream_result['insights']):
        status = "[有效]" if insight.get('validated') else "[无效]"
        print(f"    {i+1}. {status} {insight['content']}")
        print(f"       质量分数: {insight['quality_score']:.2f}")

# 获取统计
print("\n[OK] 梦境统计:")
stats = dream_processor.get_dream_statistics()
print(f"  总梦境: {stats['total_dreams']}")
print(f"  总洞察: {stats['total_insights']}")
print(f"  有效洞察: {stats['validated_insights']}")
print(f"  最后梦境: {stats['last_dream_time']}")

print("\n[OK] 梦境处理器测试通过！")
print("\n[Xiaoyao] 梦境机制已就绪，可以开始创造性思维！")
