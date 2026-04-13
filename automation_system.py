"""
自动化监控系统

自动监控工作流并提取关键信息
"""

import sys
from pathlib import Path
from datetime import datetime
import json
import re
from typing import Dict, List, Optional, Tuple

# 添加路径
sys.path.insert(0, str(Path(r"C:\ssh\.openclaw\xiaoyao-memory-system")))

from production_memory_system import get_production_memory_system
from super_memory_system_v7 import MemoryType


class AutoTaskMonitor:
    """
    自动任务监控器

    监控工作流并自动记录任务
    """

    def __init__(self):
        """初始化监控器"""
        self.pms = get_production_memory_system()
        self.active_tasks = {}
        self.task_patterns = {
            'development': [r'开发', r'实现', r'编写', r'构建', r'develop', r'implement', r'build'],
            'testing': [r'测试', r'test', r'验证', r'verify'],
            'documentation': [r'文档', r'记录', r'document', r'record'],
            'optimization': [r'优化', r'改进', r'optimize', r'improve'],
            'debugging': [r'调试', r'修复', r'debug', r'fix'],
            'research': [r'研究', r'分析', r'学习', r'research', r'analyze', r'learn'],
        }

    def detect_task_type(self, text: str) -> str:
        """检测任务类型"""
        for task_type, patterns in self.task_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return task_type
        return 'general'

    def extract_task_info(self, text: str) -> Optional[Dict[str, str]]:
        """
        从文本中提取任务信息

        Args:
            text: 输入文本

        Returns:
            任务信息字典或None
        """
        # 检测任务开始
        task_start_patterns = [
            r'(开始|启动|Starting|Begin) (.+)',
            r'(我要|我将|I will|I am going to) (.+)',
            r'正在(.+)',
        ]

        for pattern in task_start_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                task_desc = match.group(2) if match.lastindex >= 2 else match.group(1)
                task_type = self.detect_task_type(task_desc)

                return {
                    'action': 'start',
                    'description': task_desc.strip(),
                    'type': task_type,
                    'timestamp': datetime.now().isoformat()
                }

        # 检测任务完成
        task_complete_patterns = [
            r'(完成|Finished|Completed|Done) (.+)',
            r'(.+)(完成|成功|succeeded|completed)',
        ]

        for pattern in task_complete_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                task_desc = match.group(1) if '完成' in match.group(0) or '完成' in text else match.group(2)
                task_type = self.detect_task_type(task_desc)

                return {
                    'action': 'complete',
                    'description': task_desc.strip(),
                    'type': task_type,
                    'timestamp': datetime.now().isoformat()
                }

        return None

    def monitor_text(self, text: str) -> List[str]:
        """
        监控文本并自动记录任务

        Args:
            text: 输入文本

        Returns:
            记忆ID列表
        """
        task_info = self.extract_task_info(text)
        memory_ids = []

        if task_info:
            if task_info['action'] == 'start':
                # 记录任务开始
                memory_content = f"[TASK_START] {task_info['type']}: {task_info['description']}"
                memory_id = self.pms.sms_v7.remember(
                    memory_content,
                    memory_type=MemoryType.EPISODIC
                )
                memory_ids.append(memory_id)

                # 追踪活动任务
                self.active_tasks[task_info['description']] = {
                    'start_time': datetime.now(),
                    'type': task_info['type'],
                    'memory_id': memory_id
                }

                print(f"[AutoMonitor] 检测到任务开始: {task_info['description']}")

            elif task_info['action'] == 'complete':
                # 记录任务完成
                memory_content = f"[TASK_COMPLETE] {task_info['type']}: {task_info['description']}"
                memory_id = self.pms.sms_v7.remember(
                    memory_content,
                    memory_type=MemoryType.EPISODIC
                )
                memory_ids.append(memory_id)

                # 更新活动任务
                if task_info['description'] in self.active_tasks:
                    task = self.active_tasks[task_info['description']]
                    duration = datetime.now() - task['start_time']

                    # 记录任务时长
                    duration_content = f"[TASK_DURATION] {task_info['description']}: {duration.total_seconds():.0f}秒"
                    duration_id = self.pms.sms_v7.remember(
                        duration_content,
                        memory_type=MemoryType.EPISODIC
                    )
                    memory_ids.append(duration_id)

                    del self.active_tasks[task_info['description']]

                print(f"[AutoMonitor] 检测到任务完成: {task_info['description']}")

        return memory_ids


class AutoDecisionExtractor:
    """
    自动决策提取器

    从文本中自动提取决策
    """

    def __init__(self):
        """初始化提取器"""
        self.pms = get_production_memory_system()
        self.decision_patterns = [
            r'(决定|选择|采用|使用|Decision:|Choose|Adopt) (.+)',
            r'(我将|I will|We will) (.+)',
            r'(.+)(是最佳选择|是最好的|is the best)',
        ]

    def extract_decision(self, text: str) -> Optional[Dict[str, str]]:
        """
        从文本中提取决策

        Args:
            text: 输入文本

        Returns:
            决策信息字典或None
        """
        for pattern in self.decision_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                decision = match.group(2) if match.lastindex >= 2 else match.group(1)

                return {
                    'decision': decision.strip(),
                    'context': text[:200],  # 保存上下文
                    'timestamp': datetime.now().isoformat()
                }

        return None

    def monitor_text(self, text: str) -> Optional[str]:
        """
        监控文本并自动记录决策

        Args:
            text: 输入文本

        Returns:
            记忆ID或None
        """
        decision_info = self.extract_decision(text)

        if decision_info:
            memory_content = f"[DECISION] {decision_info['decision']} | Context: {decision_info['context']}"
            memory_id = self.pms.sms_v7.remember(
                memory_content,
                memory_type=MemoryType.SEMANTIC
            )

            print(f"[AutoExtractor] 检测到决策: {decision_info['decision'][:50]}...")

            return memory_id

        return None


class AutoLearningArchiver:
    """
    自动学习归档器

    识别和归档学习内容
    """

    def __init__(self):
        """初始化归档器"""
        self.pms = get_production_memory_system()
        self.learning_patterns = [
            r'(学到了|学会了|发现|意识到|Learned|Discovered|Realized) (.+)',
            r'(新的洞察|新的理解|New insight|Understanding) (.+)',
            r'(.+)(是关键|很重要|is key|is important)',
        ]

        self.technical_keywords = [
            'API', '算法', 'algorithm', '架构', 'architecture',
            '框架', 'framework', '库', 'library',
            '性能', 'performance', '优化', 'optimization',
            '安全', 'security', '测试', 'testing'
        ]

    def extract_learning(self, text: str) -> Optional[Dict[str, str]]:
        """
        从文本中提取学习内容

        Args:
            text: 输入文本

        Returns:
            学习信息字典或None
        """
        # 检测学习模式
        for pattern in self.learning_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                learning = match.group(2) if match.lastindex >= 2 else match.group(1)

                return {
                    'topic': self._infer_topic(learning),
                    'content': learning.strip(),
                    'timestamp': datetime.now().isoformat()
                }

        # 检测技术关键词
        if any(keyword in text for keyword in self.technical_keywords):
            return {
                'topic': 'Technical',
                'content': text.strip(),
                'timestamp': datetime.now().isoformat()
            }

        return None

    def _infer_topic(self, content: str) -> str:
        """推断学习主题"""
        # 简化实现 - 根据关键词推断
        if 'Agent' in content or 'Memory' in content:
            return 'AI System'
        elif 'API' in content or '代码' in content:
            return 'Development'
        elif '性能' in content or '优化' in content:
            return 'Optimization'
        else:
            return 'General'

    def monitor_text(self, text: str) -> Optional[str]:
        """
        监控文本并自动归档学习内容

        Args:
            text: 输入文本

        Returns:
            记忆ID或None
        """
        learning_info = self.extract_learning(text)

        if learning_info:
            memory_content = f"[LEARNING] {learning_info['topic']}: {learning_info['content']}"
            memory_id = self.pms.sms_v7.remember(
                memory_content,
                memory_type=MemoryType.SEMANTIC
            )

            print(f"[AutoArchiver] 检测到学习: {learning_info['topic']} - {learning_info['content'][:50]}...")

            return memory_id

        return None


class AutoMonitoringSystem:
    """
    自动化监控系统

    整合所有自动化功能
    """

    def __init__(self):
        """初始化监控系统"""
        self.task_monitor = AutoTaskMonitor()
        self.decision_extractor = AutoDecisionExtractor()
        self.learning_archiver = AutoLearningArchiver()

        self.stats = {
            'tasks_recorded': 0,
            'decisions_extracted': 0,
            'learning_archived': 0,
            'start_time': datetime.now().isoformat()
        }

    def monitor_text(self, text: str) -> Dict[str, List[str]]:
        """
        监控文本并自动提取所有类型的信息

        Args:
            text: 输入文本

        Returns:
            各类信息的记忆ID字典
        """
        results = {
            'tasks': [],
            'decisions': [],
            'learning': []
        }

        # 监控任务
        task_ids = self.task_monitor.monitor_text(text)
        results['tasks'].extend(task_ids)
        if task_ids:
            self.stats['tasks_recorded'] += len(task_ids)

        # 提取决策
        decision_id = self.decision_extractor.monitor_text(text)
        if decision_id:
            results['decisions'].append(decision_id)
            self.stats['decisions_extracted'] += 1

        # 归档学习
        learning_id = self.learning_archiver.monitor_text(text)
        if learning_id:
            results['learning'].append(learning_id)
            self.stats['learning_archived'] += 1

        return results

    def get_stats(self) -> Dict[str, int]:
        """获取监控统计"""
        return self.stats.copy()

    def save_stats(self, filepath: str):
        """保存统计信息"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)


# 全局单例
_auto_monitoring_system = None


def get_auto_monitoring_system() -> AutoMonitoringSystem:
    """获取监控系统单例"""
    global _auto_monitoring_system

    if _auto_monitoring_system is None:
        print("[自动化系统] 初始化监控系统...")
        _auto_monitoring_system = AutoMonitoringSystem()
        print("[OK] 监控系统已启动")

    return _auto_monitoring_system


# 便捷函数
def auto_monitor(text: str) -> Dict[str, List[str]]:
    """自动监控文本"""
    return get_auto_monitoring_system().monitor_text(text)


def get_monitoring_stats() -> Dict[str, int]:
    """获取监控统计"""
    return get_auto_monitoring_system().get_stats()


# 测试
if __name__ == "__main__":
    print("="*70)
    print("自动化监控系统测试")
    print("="*70)

    # 初始化
    monitor = get_auto_monitoring_system()

    # 测试文本
    test_texts = [
        "我开始开发SuperMemorySystemV7系统",
        "经过研究，我发现多策略检索是关键",
        "我决定采用Hindsight+Zep+Letta+MemEvolve的融合架构",
        "SuperMemorySystemV7开发完成！",
        "性能优化是关键，存储吞吐量达到1,158,648记忆/秒",
        "测试完成，所有功能正常工作",
    ]

    print("\n[测试] 监控文本...")
    for text in test_texts:
        print(f"\n输入: {text}")
        results = monitor.monitor_text(text)

        if any(results.values()):
            print("检测结果:")
            if results['tasks']:
                print(f"  - 任务: {len(results['tasks'])}条")
            if results['decisions']:
                print(f"  - 决策: {len(results['decisions'])}条")
            if results['learning']:
                print(f"  - 学习: {len(results['learning'])}条")

    # 统计
    print("\n[统计] 监控统计:")
    stats = monitor.get_stats()
    print(f"  任务记录: {stats['tasks_recorded']}")
    print(f"  决策提取: {stats['decisions_extracted']}")
    print(f"  学习归档: {stats['learning_archived']}")

    print("\n" + "="*70)
    print("自动化监控系统测试完成！")
    print("="*70)
