"""
小妖日常工作流集成脚本

将SuperMemorySystemV7集成到所有工作中
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(r"C:\ssh\.openclaw\xiaoyao-memory-system")))

from production_memory_system import (
    remember_task,
    remember_decision,
    remember_learning,
    remember_user_preference,
    recall_context,
    get_memory_status,
    evolve_memory_system
)


def on_task_start(task_name: str, task_type: str = "general") -> str:
    """
    任务开始时调用

    记录任务开始，检索相关上下文

    Args:
        task_name: 任务名称
        task_type: 任务类型

    Returns:
        记忆ID
    """
    print(f"\n[工作流] 开始任务: {task_name}")

    # 记录任务
    memory_id = remember_task(f"开始: {task_name}", task_type)

    # 检索相关上下文
    query = f"关于 {task_name} 的相关经验"
    result = recall_context(query, top_k=3)

    if result['memories']:
        print(f"[上下文] 找到 {len(result['memories'])} 条相关记忆:")
        for i, mem in enumerate(result['memories'], 1):
            print(f"  {i}. {mem.content[:60]}...")

    return memory_id


def on_task_complete(task_name: str, outcome: str, lessons: str = "") -> str:
    """
    任务完成时调用

    记录任务结果和经验教训

    Args:
        task_name: 任务名称
        outcome: 任务结果
        lessons: 经验教训

    Returns:
        记忆ID
    """
    print(f"\n[工作流] 任务完成: {task_name}")

    memory_content = f"完成: {task_name} | 结果: {outcome}"
    if lessons:
        memory_content += f" | 经验: {lessons}"

    memory_id = remember_task(memory_content, "completion")

    return memory_id


def on_decision_made(decision: str, context: str = "", reasoning: str = "") -> str:
    """
    做出决策时调用

    记录决策、上下文和推理

    Args:
        decision: 决策内容
        context: 决策上下文
        reasoning: 决策推理

    Returns:
        记忆ID
    """
    print(f"\n[工作流] 记录决策: {decision}")

    full_context = context
    if reasoning:
        full_context += f" | 推理: {reasoning}"

    memory_id = remember_decision(decision, full_context)

    return memory_id


def on_learning(topic: str, content: str, source: str = "") -> str:
    """
    学习新知识时调用

    记录学习内容

    Args:
        topic: 学习主题
        content: 学习内容
        source: 知识来源

    Returns:
        记忆ID
    """
    print(f"\n[工作流] 记录学习: {topic}")

    full_content = content
    if source:
        full_content += f" | 来源: {source}"

    memory_id = remember_learning(topic, full_content)

    return memory_id


def on_user_interaction(user: str, preference: str, interaction_type: str = "preference") -> str:
    """
    用户交互时调用

    记录用户偏好和反馈

    Args:
        user: 用户标识
        preference: 偏好内容
        interaction_type: 交互类型

    Returns:
        记忆ID
    """
    print(f"\n[工作流] 记录用户偏好: {user}")

    memory_id = remember_user_preference(user, preference)

    return memory_id


def query_memory(query: str, top_k: int = 5, show_synthesis: bool = True):
    """
    查询记忆

    Args:
        query: 查询文本
        top_k: 返回结果数
        show_synthesis: 是否显示合成结果
    """
    print(f"\n[查询] {query}")

    result = recall_context(query, top_k=top_k)

    print(f"\n[结果] 找到 {len(result['memories'])} 条相关记忆:")

    for i, mem in enumerate(result['memories'], 1):
        print(f"\n{i}. {mem.content[:80]}...")
        print(f"   得分: {mem.combined_score:.2f} | 策略: {mem.source_strategy.value}")

    if show_synthesis and result['synthesis']:
        print(f"\n[合成分析]")
        print(result['synthesis'])


def check_memory_system():
    """检查记忆系统状态"""
    print("\n[系统状态]")

    status = get_memory_status()

    print(f"版本: {status['version']}")
    print(f"记忆总数: {status['memory_count']}")
    print(f"时序事实: {status['temporal_facts']}")
    print(f"进化次数: {status['production']['evolution_count']}")

    if status['production']['last_evolution']:
        print(f"上次进化: {status['production']['last_evolution']}")


def trigger_evolution():
    """触发系统进化"""
    print("\n[进化] 触发自我进化...")

    evolution_report = evolve_memory_system()

    print(f"[OK] 进化完成，{len(evolution_report['changes'])} 项变更:")

    for change in evolution_report['changes']:
        print(f"  - {change['type']}: {change['reason']}")


# 使用示例
if __name__ == "__main__":
    print("="*70)
    print("小妖日常工作流 - SuperMemorySystemV7集成")
    print("="*70)

    # 示例1: 任务工作流
    print("\n[示例1] 任务工作流")
    task_id = on_task_start("开发SuperMemorySystemV7", "development")

    # ... 执行任务 ...

    on_task_complete(
        "开发SuperMemorySystemV7",
        "完全成功，所有测试通过",
        "多策略检索是关键，时序推理对真实世界很重要"
    )

    # 示例2: 决策记录
    print("\n[示例2] 决策记录")
    on_decision_made(
        "采用Hindsight+Zep+Letta+MemEvolve融合架构",
        "Agent Memory研究",
        "多策略检索保证准确性，时序推理处理真实世界变化"
    )

    # 示例3: 学习记录
    print("\n[示例3] 学习记录")
    on_learning(
        "Agent Memory 2026",
        "未来标准是Hindsight多策略+Zep时序+Letta自我管理+MemEvolve进化",
        "Vectorize.io深度对比研究"
    )

    # 示例4: 用户偏好
    print("\n[示例4] 用户偏好")
    on_user_interaction(
        "宗晖哥哥",
        "重视效率和细节，喜欢简洁明了的汇报",
        "preference"
    )

    # 示例5: 查询记忆
    print("\n[示例5] 查询记忆")
    query_memory("关于Agent Memory的核心洞察是什么？")

    # 示例6: 系统状态
    print("\n[示例6] 系统状态")
    check_memory_system()

    print("\n" + "="*70)
    print("工作流集成示例完成！")
    print("="*70)
