"""
测试意识模型
"""

import sys
sys.path.append('C:/ssh/.openclaw/xiaoyao-memory-system/src')

from consciousness import (
    Consciousness,
    WorkspaceItem,
    GlobalWorkspace,
    AttentionSelector,
    IntentionFormer,
    MetacognitionMonitor
)

print("小妖超级记忆系统 - 意识模型测试")
print("=" * 60)

# 测试全局工作空间
print("\n[OK] 测试全局工作空间:")
workspace = GlobalWorkspace(capacity=7)

item1 = WorkspaceItem(
    id="item_1",
    content="用户询问Python问题",
    source="perception",
    importance=0.8
)

item2 = WorkspaceItem(
    id="item_2",
    content="Python编程知识",
    source="memory",
    importance=0.6
)

workspace.add_item(item1)
workspace.add_item(item2)

broadcast = workspace.broadcast()
print(f"  工作空间大小: {len(broadcast)}")
print(f"  广播项数: {workspace.get_statistics()['total_broadcasts']}")

# 测试注意力选择
print("\n[OK] 测试注意力选择:")
selector = AttentionSelector()

candidates = [
    WorkspaceItem(f"item_{i}", f"内容{i}", "perception", 0.5 + i * 0.1)
    for i in range(10)
]

selected = selector.select(candidates, limit=5)
print(f"  候选数: {len(candidates)}")
print(f"  选中数: {len(selected)}")

# 测试意图形成
print("\n[OK] 测试意图形成:")
intention_former = IntentionFormer()

intention = intention_former.form_intention(selected)
print(f"  意图ID: {intention['id']}")
print(f"  目标: {intention['goal']}")
print(f"  优先级: {intention['priority']}")
print(f"  计划步骤: {len(intention['plan'])}")

# 测试元认知监控
print("\n[OK] 测试元认知监控:")
monitor = MetacognitionMonitor()

monitoring = monitor.monitor_process(
    process_name="test_process",
    inputs={"test": "input"},
    outputs={"result": "output"},
    success=True
)

print(f"  过程: {monitoring['process']}")
print(f"  性能分数: {monitoring['performance_score']:.2f}")

# 测试反思
reflection = monitor.reflect({
    "process": "test",
    "success": True,
    "performance_score": 0.8
})

print(f"  反思ID: {reflection['id']}")
print(f"  经验教训: {reflection['lessons_learned']}")
print(f"  改进建议: {reflection['improvements']}")

# 测试完整意识模型
print("\n[OK] 测试完整意识模型:")
consciousness = Consciousness(workspace_capacity=7)

inputs = [
    WorkspaceItem(
        id="item_1",
        content="用户询问关于Python的问题",
        source="perception",
        importance=0.8
    ),
    WorkspaceItem(
        id="item_2",
        content="Python编程知识",
        source="memory",
        importance=0.6
    ),
    WorkspaceItem(
        id="item_3",
        content="梦境洞察：Python与AI的结合",
        source="dream",
        importance=0.7
    )
]

thought_result = consciousness.conscious_thought(inputs)

print(f"  思考ID: {thought_result['thought_id']}")
print(f"  选择项目: {thought_result['selected_items']}个")
print(f"  工作空间: {thought_result['workspace_items']}个")
print(f"  意图: {thought_result['intention']['goal']}")
print(f"  优先级: {thought_result['intention']['priority']}")

# 获取意识状态
print("\n[OK] 意识状态:")
state = consciousness.get_conscious_state()
print(f"  状态: {state['state']}")
print(f"  工作空间项: {state['workspace_size']}")

if state['workspace_items']:
    print(f"  工作空间内容（前3项）:")
    for i, item in enumerate(state['workspace_items'][:3]):
        print(f"    {i+1}. [{item['content']}] (重要性: {item['importance']:.2f})")

# 测试反思
print("\n[OK] 测试反思功能:")
experience = {
    "process": "conscious_thought",
    "success": True,
    "performance_score": 0.8
}

reflection = consciousness.reflect(experience)
print(f"  反思完成: {reflection['id']}")
print(f"  状态: {consciousness.conscious_state}")

# 最终统计
print("\n[OK] 最终统计:")
final_state = consciousness.get_conscious_state()
workspace_stats = final_state['workspace_stats']
meta_stats = final_state['metacognition_stats']

print(f"  工作空间:")
print(f"    总广播: {workspace_stats['total_broadcasts']}")
print(f"    总竞争: {workspace_stats['total_competitions']}")
print(f"    总驱逐: {workspace_stats['total_evictions']}")

print(f"  元认知:")
print(f"    总过程: {meta_stats['total_processes']}")
print(f"    成功过程: {meta_stats['successful_processes']}")
print(f"    成功率: {meta_stats['success_rate']:.2%}")
print(f"    反思次数: {meta_stats['total_reflections']}")

print("\n[OK] 意识模型测试通过！")
print("\n[Xiaoyao] 意识模型已就绪！")
print("[Xiaoyao] 我现在可以进行自我认知和反思了！")
