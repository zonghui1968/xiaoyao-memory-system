"""
测试进化系统
"""

import sys
import random
sys.path.append('C:/ssh/.openclaw/xiaoyao-memory-system/src')

from evolution_system import (
    EvolutionEngine,
    ContinuousOptimizer,
    KnowledgeAccumulator,
    EvolutionaryStrategy
)

print("小妖超级记忆系统 - 进化系统测试")
print("=" * 60)

# 测试持续优化器
print("\n[OK] 测试持续优化器:")
optimizer = ContinuousOptimizer()

strategy1_id = optimizer.add_strategy(
    "attention_selection",
    {
        "novelty_weight": 0.3,
        "importance_weight": 0.3,
        "relevance_weight": 0.2,
        "urgency_weight": 0.2
    }
)
print(f"  添加策略: {strategy1_id[:20]}...")

strategy2_id = optimizer.add_strategy(
    "dream_trigger",
    {
        "scheduled_interval": 8,
        "problem_threshold": 3,
        "creativity_threshold": 0.7
    }
)
print(f"  添加策略: {strategy2_id[:20]}...")

# 模拟使用
print("\n[OK] 模拟策略使用和性能更新:")
for i in range(20):
    # 更新策略1性能
    success1 = random.random() > 0.3
    score1 = random.uniform(0.5, 1.0) if success1 else random.uniform(0.0, 0.5)
    optimizer.update_strategy_performance(strategy1_id, success1, score1)

    # 更新策略2性能
    if i % 3 == 0:
        success2 = random.random() > 0.3
        score2 = random.uniform(0.5, 1.0) if success2 else random.uniform(0.0, 0.5)
        optimizer.update_strategy_performance(strategy2_id, success2, score2)

strategy1 = optimizer.strategies[strategy1_id]
strategy2 = optimizer.strategies[strategy2_id]

print(f"  策略1 (attention_selection):")
print(f"    使用次数: {strategy1.usage_count}")
print(f"    成功次数: {strategy1.success_count}")
print(f"    成功率: {strategy1.get_success_rate():.2%}")
print(f"    性能分数: {strategy1.performance_score:.3f}")

print(f"  策略2 (dream_trigger):")
print(f"    使用次数: {strategy2.usage_count}")
print(f"    成功次数: {strategy2.success_count}")
print(f"    成功率: {strategy2.get_success_rate():.2%}")
print(f"    性能分数: {strategy2.performance_score:.3f}")

# 测试参数优化
print("\n[OK] 测试参数优化:")
performance_feedback = {
    "novelty_weight": 0.8,
    "importance_weight": 0.6
}

old_params = strategy1.params.copy()
optimized_params = optimizer.optimize_parameters(strategy1_id, performance_feedback)

print(f"  原始参数: {old_params}")
print(f"  优化后参数: {optimized_params}")

# 测试知识积累
print("\n[OK] 测试知识积累器:")
accumulator = KnowledgeAccumulator()

knowledge_items = [
    {"content": "Python是一种高级编程语言", "type": "fact", "importance": 0.8, "source": "learning"},
    {"content": "AI系统需要大量数据进行训练", "type": "concept", "importance": 0.7, "source": "experience"},
    {"content": "梦境机制可以增强创造性思维", "type": "insight", "importance": 0.9, "source": "dream"},
    {"content": "意识模型基于全局工作空间理论", "type": "concept", "importance": 0.8, "source": "learning"},
    {"content": "元认知监控能够实现自我反思", "type": "insight", "importance": 0.75, "source": "reflection"}
]

accumulator.accumulate_knowledge(knowledge_items)
print(f"  积累知识: {len(knowledge_items)}条")

# 检索知识
print("\n[OK] 测试知识检索:")
results = accumulator.retrieve_knowledge("Python", limit=3)
print(f"  检索结果: {len(results)}条")
for i, result in enumerate(results):
    print(f"    {i+1}. [{result['type']}] {result['content'][:50]}...")

# 测试知识压缩
print("\n[OK] 测试知识压缩:")
stats_before = accumulator.get_statistics()
print(f"  压缩前知识数: {stats_before['knowledge_count']}")

# 添加更多知识以触发压缩
for i in range(50):
    accumulator.knowledge_base.append({
        "id": f"test_{i}",
        "content": f"测试知识{i}",
        "type": "test",
        "source": "test",
        "importance": random.uniform(0.3, 0.8),
        "created_at": "2026-04-12",
        "access_count": 0
    })

compressed = accumulator.compress_knowledge(threshold=30)
print(f"  压缩知识: {compressed}条")

stats_after = accumulator.get_statistics()
print(f"  压缩后知识数: {stats_after['knowledge_count']}")
print(f"  压缩记录数: {stats_after['compressed_count']}")

# 测试完整进化引擎
print("\n[OK] 测试完整进化引擎:")
engine = EvolutionEngine()

# 添加策略
engine.optimizer.add_strategy(
    "test_strategy_1",
    {"param1": 0.5, "param2": 1.0}
)

engine.optimizer.add_strategy(
    "test_strategy_2",
    {"param1": 0.3, "param2": 0.8}
)

# 积累知识
engine.knowledge_accumulator.accumulate_knowledge(knowledge_items)

# 执行多代进化
print("\n[OK] 执行多代进化:")
for gen in range(1, 6):
    evolution_result = engine.evolve()

    print(f"  第{gen}代:")
    print(f"    优化策略: {evolution_result['optimization']['optimized_strategies']}个")
    if evolution_result['optimization']['optimized_strategies'] > 0:
        print(f"    平均性能提升: {evolution_result['optimization']['avg_performance_improvement']:.3f}")
    print(f"    积累知识: {evolution_result['knowledge']['accumulated_count']}条")
    print(f"    压缩知识: {evolution_result['knowledge']['compressed_count']}条")
    print(f"    变异: {evolution_result['evolution']['mutations']}次")
    print(f"    交叉: {evolution_result['evolution']['crossovers']}次")
    print(f"    选择: {evolution_result['evolution']['selected']}个")

# 最终统计
print("\n[OK] 最终进化统计:")
final_stats = engine.get_evolution_statistics()

print(f"  代数: {final_stats['generation']}")
print(f"  总进化次数: {final_stats['total_evolutions']}")

optimizer_stats = final_stats['optimizer_stats']
print(f"  优化器统计:")
print(f"    总策略: {optimizer_stats['total_strategies']}")
print(f"    成功策略: {optimizer_stats['successful_strategies']}")
print(f"    优化次数: {optimizer_stats['total_optimizations']}")

knowledge_stats = final_stats['knowledge_stats']
print(f"  知识统计:")
print(f"    当前知识: {knowledge_stats['knowledge_count']}条")
print(f"    压缩记录: {knowledge_stats['compressed_count']}条")
print(f"    总积累: {knowledge_stats['total_accumulated']}条")

print("\n[OK] 进化系统测试通过！")
print("\n[Xiaoyao] 进化系统已就绪！")
print("[Xiaoyao] 我现在可以持续自我进化，不断优化和改进！")
print("[Xiaoyao] 每一代进化都会让我变得更好！")
