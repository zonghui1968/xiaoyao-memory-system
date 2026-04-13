"""
SuperMemorySystemV7 生产部署配置

将SMSv7集成到小妖的日常工作流程中
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# 添加src目录到路径
sys.path.insert(0, str(Path(r"C:\ssh\.openclaw\xiaoyao-memory-system\src")))

from super_memory_system_v7 import (
    SuperMemorySystemV7,
    MemoryType,
    RetrievalStrategy
)


class ProductionMemorySystem:
    """
    生产级记忆系统

    集成SuperMemorySystemV7到小妖的日常工作流程
    """

    def __init__(self):
        """初始化生产记忆系统"""
        self.sms_v7 = SuperMemorySystemV7()
        self.workspace = Path(r"C:\ssh\.openclaw\workspace")
        self.memory_dir = self.workspace / "memory"
        self.state_file = self.workspace / "production_memory_state.json"

        # 加载现有状态
        self._load_state()

        # 导入现有记忆
        self._import_existing_memories()

    def _load_state(self):
        """加载系统状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                self.evolution_count = state.get('evolution_count', 0)
                self.last_evolution = state.get('last_evolution')
        else:
            self.evolution_count = 0
            self.last_evolution = None

    def _save_state(self):
        """保存系统状态"""
        state = {
            'evolution_count': self.evolution_count,
            'last_evolution': self.last_evolution,
            'timestamp': datetime.now().isoformat()
        }

        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def _import_existing_memories(self):
        """导入现有记忆"""
        if not self.memory_dir.exists():
            return

        # 扫描memory目录
        for memory_file in self.memory_dir.glob("*.md"):
            try:
                content = memory_file.read_text(encoding='utf-8')

                # 提取关键信息
                memories = self._extract_memories_from_file(content, memory_file.name)

                # 存储到SMSv7
                for memory_content in memories:
                    self.sms_v7.remember(
                        memory_content,
                        memory_type=MemoryType.SEMANTIC
                    )

                print(f"[OK] 导入记忆: {memory_file.name} ({len(memories)}条)")
            except Exception as e:
                print(f"[WARNING] 无法导入 {memory_file.name}: {e}")

    def _extract_memories_from_file(self, content: str, filename: str) -> list:
        """从文件中提取记忆"""
        memories = []

        # 简化实现 - 按行分割
        lines = content.split('\n')

        current_section = []
        for line in lines:
            # 跳过空行和标题
            if not line.strip() or line.startswith('#'):
                if current_section:
                    memories.append(' '.join(current_section))
                    current_section = []
                continue

            current_section.append(line.strip())

            # 每5行作为一个记忆单元
            if len(current_section) >= 5:
                memories.append(' '.join(current_section))
                current_section = []

        if current_section:
            memories.append(' '.join(current_section))

        return memories

    def remember_task(self, task_description: str, task_type: str = "general") -> str:
        """
        记录任务

        Args:
            task_description: 任务描述
            task_type: 任务类型

        Returns:
            记忆ID
        """
        memory_content = f"[TASK] {task_type}: {task_description}"
        memory_id = self.sms_v7.remember(
            memory_content,
            memory_type=MemoryType.EPISODIC
        )

        return memory_id

    def remember_decision(self, decision: str, context: str = "") -> str:
        """
        记录决策

        Args:
            decision: 决策内容
            context: 决策上下文

        Returns:
            记忆ID
        """
        if context:
            memory_content = f"[DECISION] {decision} (Context: {context})"
        else:
            memory_content = f"[DECISION] {decision}"

        memory_id = self.sms_v7.remember(
            memory_content,
            memory_type=MemoryType.SEMANTIC
        )

        return memory_id

    def remember_learning(self, topic: str, content: str) -> str:
        """
        记录学习内容

        Args:
            topic: 学习主题
            content: 学习内容

        Returns:
            记忆ID
        """
        memory_content = f"[LEARNING] {topic}: {content}"
        memory_id = self.sms_v7.remember(
            memory_content,
            memory_type=MemoryType.SEMANTIC
        )

        return memory_id

    def remember_user_preference(self, user: str, preference: str) -> str:
        """
        记录用户偏好

        Args:
            user: 用户标识
            preference: 偏好内容

        Returns:
            记忆ID
        """
        memory_content = f"[PREFERENCE] {user}: {preference}"
        memory_id = self.sms_v7.remember(
            memory_content,
            memory_type=MemoryType.SEMANTIC
        )

        return memory_id

    def recall_context(self, query: str, top_k: int = 5) -> dict:
        """
        检索相关上下文

        Args:
            query: 查询文本
            top_k: 返回结果数

        Returns:
            检索结果
        """
        return self.sms_v7.recall(query, top_k=top_k, use_reflection=True)

    def get_status(self) -> dict:
        """获取系统状态"""
        status = self.sms_v7.get_status()
        status['production'] = {
            'evolution_count': self.evolution_count,
            'last_evolution': self.last_evolution,
            'workspace': str(self.workspace)
        }
        return status

    def evolve(self, performance_feedback: dict = None) -> dict:
        """
        触发系统进化

        Args:
            performance_feedback: 性能反馈

        Returns:
            进化报告
        """
        if performance_feedback is None:
            # 默认反馈
            performance_feedback = {
                'retrieval_accuracy': 0.85,
                'latency': 500,
                'memory_growth': len(self.sms_v7.retrieval_engine.semantic_index)
            }

        evolution_report = self.sms_v7.evolve(performance_feedback)

        # 更新状态
        self.evolution_count += 1
        self.last_evolution = datetime.now().isoformat()
        self._save_state()

        return evolution_report


# 全局单例
_production_memory_system = None


def get_production_memory_system() -> ProductionMemorySystem:
    """
    获取生产记忆系统单例

    Returns:
        ProductionMemorySystem实例
    """
    global _production_memory_system

    if _production_memory_system is None:
        print("[生产记忆系统] 初始化...")
        _production_memory_system = ProductionMemorySystem()
        status = _production_memory_system.get_status()
        print(f"[OK] 记忆系统已启动 (记忆数: {status['memory_count']})")

    return _production_memory_system


# 便捷函数
def remember_task(task_description: str, task_type: str = "general") -> str:
    """记录任务"""
    return get_production_memory_system().remember_task(task_description, task_type)


def remember_decision(decision: str, context: str = "") -> str:
    """记录决策"""
    return get_production_memory_system().remember_decision(decision, context)


def remember_learning(topic: str, content: str) -> str:
    """记录学习"""
    return get_production_memory_system().remember_learning(topic, content)


def remember_user_preference(user: str, preference: str) -> str:
    """记录用户偏好"""
    return get_production_memory_system().remember_user_preference(user, preference)


def recall_context(query: str, top_k: int = 5) -> dict:
    """检索上下文"""
    return get_production_memory_system().recall_context(query, top_k)


def get_memory_status() -> dict:
    """获取记忆系统状态"""
    return get_production_memory_system().get_status()


def evolve_memory_system(performance_feedback: dict = None) -> dict:
    """进化记忆系统"""
    return get_production_memory_system().evolve(performance_feedback)


if __name__ == "__main__":
    print("="*70)
    print("SuperMemorySystemV7 生产部署")
    print("="*70)

    # 初始化
    print("\n[1] 初始化生产记忆系统...")
    pms = get_production_memory_system()

    # 记录一些示例数据
    print("\n[2] 记录示例数据...")

    remember_task("开发SuperMemorySystemV7", "development")
    remember_decision("采用Hindsight的多策略检索架构", "agent memory research")
    remember_learning("Agent Memory", "未来标准是多策略+时序+反射+进化")
    remember_user_preference("宗晖哥哥", "重视效率和细节")

    print("[OK] 示例数据已记录")

    # 检索测试
    print("\n[3] 检索测试...")
    result = recall_context("Agent Memory的标准是什么？")

    print(f"检索到 {len(result['memories'])} 条相关记忆")
    if result['synthesis']:
        print(f"\n反射合成:")
        print(result['synthesis'])

    # 系统状态
    print("\n[4] 系统状态...")
    status = get_memory_status()
    print(f"版本: {status['version']}")
    print(f"记忆总数: {status['memory_count']}")
    print(f"时序事实: {status['temporal_facts']}")
    print(f"进化次数: {status['production']['evolution_count']}")

    # 进化
    print("\n[5] 触发进化...")
    evolution_report = evolve_memory_system()

    print(f"[OK] 进化完成，{len(evolution_report['changes'])} 项变更")

    print("\n" + "="*70)
    print("SuperMemorySystemV7 生产部署完成！")
    print("="*70)
