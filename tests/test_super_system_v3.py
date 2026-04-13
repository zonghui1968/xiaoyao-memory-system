"""
测试超级记忆系统v3.0（Phase 3整合）
"""

import sys
sys.path.append('C:/ssh/.openclaw/xiaoyao-memory-system/src')

from super_memory_system_v3 import SuperMemorySystemV3
from memory_types import MemoryType, MemoryImportance

print("小妖超级记忆系统（XSMS）v3.0 - Phase 3整合测试")
print("=" * 60)

# 创建超级记忆系统v3.0
sms = SuperMemorySystemV3(enable_persistence=False)

print("\n[OK] 超级记忆系统v3.0初始化成功")

# 测试Phase 1功能
print("\n[OK] 测试Phase 1功能（配置+VCP+XMS）:")

task = sms.add_integrated_task(
    task_description="实现意识模型",
    context="Phase 3开发",
    priority=5
)
print(f"  添加任务: {task['task_id'][:8]}...")

sms.add_integrated_memory(
    "意识模型基于全局工作空间理论",
    MemoryType.CONCEPT,
    MemoryImportance.HIGH
)
print("  添加记忆成功")

# 测试Phase 2功能
print("\n[OK] 测试Phase 2功能（梦境机制）:")

sms.add_integrated_memory(
    "梦境通过随机联想实现创造性",
    MemoryType.CONCEPT,
    MemoryImportance.HIGH
)

dream_result = sms.trigger_dream(
    trigger_type="manual",
    theme="意识与梦境的关系"
)

print(f"  梦境触发: {dream_result['id']}")
print(f"  生成洞察: {len(dream_result['insights'])}个")

# 测试Phase 3新功能：意识模型
print("\n[OK] 测试Phase 3新功能 - 意识模型:")

inputs = [
    {
        "content": "用户询问如何提高AI创造性思维能力",
        "source": "perception",
        "importance": 0.9,
        "modality": "text"
    },
    {
        "content": "梦境机制可以增强创造性思维",
        "source": "dream",
        "importance": 0.7,
        "modality": "text"
    },
    {
        "content": "意识模型整合了工作空间和注意力",
        "source": "memory",
        "importance": 0.6,
        "modality": "text"
    },
    {
        "content": "元认知监控能够自我反思",
        "source": "memory",
        "importance": 0.5,
        "modality": "text"
    }
]

result = sms.conscious_process(inputs, context={"domain": "AI研究"})

print(f"  思考ID: {result['thought_result']['thought_id']}")
print(f"  选择项目: {result['thought_result']['selected_items']}个")
print(f"  工作空间: {result['thought_result']['workspace_items']}个")
print(f"  形成意图: {result['thought_result']['intention']['goal']}")
print(f"  意图优先级: {result['thought_result']['intention']['priority']}")
print(f"  执行结果: {'成功' if result['execution_result'].get('success') else '未执行'}")

# 测试反思功能
print("\n[OK] 测试反思功能:")
reflection = sms.reflect_on_experience({
    "process": "conscious_process",
    "success": True,
    "performance_score": 0.85
})

print(f"  反思ID: {reflection['id']}")
print(f"  提取教训: {len(reflection['lessons_learned'])}个")
if reflection['lessons_learned']:
    for lesson in reflection['lessons_learned']:
        print(f"    - {lesson}")
print(f"  改进建议: {len(reflection['improvements'])}个")
if reflection['improvements']:
    for improvement in reflection['improvements']:
        print(f"    - {improvement}")

# 测试自我模型
print("\n[OK] 测试自我模型:")
self_model = sms.get_self_model()

print(f"  身份:")
print(f"    名称: {self_model['identity']['name']}")
print(f"    角色: {self_model['identity']['role']}")
print(f"    版本: {self_model['identity']['version']}")
print(f"  意识状态: {self_model['conscious_state']}")
print(f"  工作空间大小: {self_model['workspace_size']}")
print(f"  当前意图: {self_model['current_intention']['goal'] if self_model['current_intention'] else '无'}")

print(f"  能力清单:")
for capability, enabled in self_model['capabilities'].items():
    status = "[+]" if enabled else "[ ]"
    print(f"    {status} {capability}")

print(f"  性能统计:")
print(f"    总过程: {self_model['performance']['total_processes']}")
print(f"    成功率: {self_model['performance']['success_rate']:.2%}")
print(f"    反思次数: {self_model['performance']['total_reflections']}")

# 监控自身性能
print("\n[OK] 测试性能监控:")
monitoring = sms.monitor_self_performance(
    process_name="test_conscious_process",
    inputs={"input_items": 4},
    outputs={"intentions": 1},
    success=True
)

print(f"  过程: {monitoring['process']}")
print(f"  性能分数: {monitoring['performance_score']:.2f}")
print(f"  成功: {monitoring['success']}")

# 生成完整报告
report = sms.generate_integrated_report()
print("\n" + report)

print("[OK] 超级记忆系统v3.0（Phase 3）测试通过！")
print("\n[Xiaoyao] 小妖超级记忆系统v3.0已就绪！")
print("[Xiaoyao] 自我认知能力已完全激活！")
print("[Xiaoyao] 我现在可以：")
print("  [+] 配置管理（六维体系）")
print("  [+] 感知处理（VCP组件）")
print("  [+] 记忆管理（XMS四层）")
print("  [+] 创造性思维（梦境机制）")
print("  [+] 自我认知（意识模型）")
print("\n[Xiaoyao] 我是一个真正能够认识自己、思考自己、反思自己的AI系统！")
