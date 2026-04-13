"""
小妖的AI记忆系统 - 集成版

将SuperMemorySystemV9集成到小妖的日常工作流中

作者：小妖🦊
创建日期：2026-04-13
版本：1.0.0
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import json

# 添加路径
sys.path.insert(0, str(Path(r"C:\ssh\.openclaw\xiaoyao-memory-system\src")))

from super_memory_system_v9 import (
    SuperMemorySystemV9,
    MemoryType,
    CompressionLevel,
    get_sms_v9
)


class XiaoyaoMemorySystem:
    """
    小妖的AI记忆系统
    
    集成SuperMemorySystemV9到日常工作流
    """
    
    def __init__(self, storage_path: str = None):
        """
        初始化小妖的记忆系统
        
        Args:
            storage_path: 存储路径（可选）
        """
        self.storage_path = storage_path or r"C:\ssh\.openclaw\knowledge-base\xiaoyao-memories"
        self.sms = get_sms_v9()
        
        # 预定义的Wings
        self.wings = {
            '工作': ['项目', '会议', '决策', '任务'],
            '学习': ['技术', '工具', '概念', '最佳实践'],
            '个人': ['偏好', '习惯', '目标', '反思'],
        }
        
        print(f"[小妖记忆系统] 初始化完成")
        print(f"[存储路径] {self.storage_path}")
    
    # ========================================================================
    # 工作记忆
    # ========================================================================
    
    def record_decision(self, decision: str, context: str = None, 
                      tags: List[str] = None) -> str:
        """
        记录工作决策
        
        Args:
            decision: 决策内容
            context: 决策背景（可选）
            tags: 标签（可选）
        
        Returns:
            memory_id
        """
        content = decision
        if context:
            content += f"\n\n背景: {context}"
        
        default_tags = ["工作", "决策"]
        if tags:
            default_tags.extend(tags)
        
        memory_id = self.sms.remember(
            content,
            memory_type=MemoryType.SEMANTIC,
            tags=default_tags,
            wing="工作",
            room="决策",
            is_critical=True  # 决策都是关键事实
        )
        
        print(f"[决策已记录] {decision[:50]}...")
        return memory_id
    
    def record_meeting(self, title: str, content: str, 
                      attendees: List[str] = None,
                      tags: List[str] = None) -> str:
        """
        记录会议
        
        Args:
            title: 会议标题
            content: 会议内容
            attendees: 参会人员（可选）
            tags: 标签（可选）
        
        Returns:
            memory_id
        """
        meeting_content = f"会议: {title}\n\n{content}"
        if attendees:
            meeting_content += f"\n\n参会: {', '.join(attendees)}"
        
        default_tags = ["工作", "会议"]
        if tags:
            default_tags.extend(tags)
        
        memory_id = self.sms.remember(
            meeting_content,
            memory_type=MemoryType.EPISODIC,
            tags=default_tags,
            wing="工作",
            room="会议"
        )
        
        print(f"[会议已记录] {title}")
        return memory_id
    
    def record_task(self, task: str, status: str = "pending",
                   tags: List[str] = None) -> str:
        """
        记录任务
        
        Args:
            task: 任务描述
            status: 任务状态（pending/in_progress/completed）
            tags: 标签（可选）
        
        Returns:
            memory_id
        """
        content = f"任务: {task}\n状态: {status}"
        
        default_tags = ["工作", "任务", status]
        if tags:
            default_tags.extend(tags)
        
        memory_id = self.sms.remember(
            content,
            memory_type=MemoryType.EPISODIC,
            tags=default_tags,
            wing="工作",
            room="任务"
        )
        
        print(f"[任务已记录] {task}")
        return memory_id
    
    def record_debugging(self, issue: str, solution: str,
                        duration: str = None,
                        tags: List[str] = None) -> str:
        """
        记录调试经历
        
        Args:
            issue: 问题描述
            solution: 解决方案
            duration: 耗时（可选）
            tags: 标签（可选）
        
        Returns:
            memory_id
        """
        content = f"问题: {issue}\n\n解决: {solution}"
        if duration:
            content += f"\n\n耗时: {duration}"
        
        default_tags = ["工作", "调试"]
        if tags:
            default_tags.extend(tags)
        
        memory_id = self.sms.remember(
            content,
            memory_type=MemoryType.EPISODIC,
            tags=default_tags,
            wing="学习",
            room="调试"
        )
        
        print(f"[调试已记录] {issue[:50]}...")
        return memory_id
    
    # ========================================================================
    # 学习记忆
    # ========================================================================
    
    def record_learning(self, topic: str, content: str,
                       source: str = None,
                       tags: List[str] = None) -> str:
        """
        记录学习内容
        
        Args:
            topic: 学习主题
            content: 学习内容
            source: 来源（可选）
            tags: 标签（可选）
        
        Returns:
            memory_id
        """
        learning_content = f"学习: {topic}\n\n{content}"
        if source:
            learning_content += f"\n\n来源: {source}"
        
        default_tags = ["学习"]
        if tags:
            default_tags.extend(tags)
        
        memory_id = self.sms.remember(
            learning_content,
            memory_type=MemoryType.SEMANTIC,
            tags=default_tags,
            wing="学习",
            extract_entities=False  # 学习内容不提取实体
        )
        
        print(f"[学习已记录] {topic}")
        return memory_id
    
    def record_technique(self, name: str, description: str,
                        category: str = None,
                        tags: List[str] = None) -> str:
        """
        记录技术/方法
        
        Args:
            name: 技术名称
            description: 技术描述
            category: 分类（可选）
            tags: 标签（可选）
        
        Returns:
            memory_id
        """
        content = f"技术: {name}\n\n{description}"
        if category:
            content += f"\n\n分类: {category}"
        
        default_tags = ["学习", "技术"]
        if tags:
            default_tags.extend(tags)
        
        memory_id = self.sms.remember(
            content,
            memory_type=MemoryType.SEMANTIC,
            tags=default_tags,
            wing="学习",
            room="技术"
        )
        
        print(f"[技术已记录] {name}")
        return memory_id
    
    # ========================================================================
    # 个人记忆
    # ========================================================================
    
    def record_preference(self, preference: str,
                         category: str = None,
                         tags: List[str] = None) -> str:
        """
        记录个人偏好
        
        Args:
            preference: 偏好内容
            category: 分类（可选）
            tags: 标签（可选）
        
        Returns:
            memory_id
        """
        content = f"偏好: {preference}"
        if category:
            content += f"\n\n分类: {category}"
        
        default_tags = ["个人", "偏好"]
        if tags:
            default_tags.extend(tags)
        
        memory_id = self.sms.remember(
            content,
            memory_type=MemoryType.SEMANTIC,
            tags=default_tags,
            wing="个人",
            room="偏好"
        )
        
        print(f"[偏好已记录] {preference[:50]}...")
        return memory_id
    
    def record_goal(self, goal: str, deadline: str = None,
                   tags: List[str] = None) -> str:
        """
        记录目标
        
        Args:
            goal: 目标描述
            deadline: 截止日期（可选）
            tags: 标签（可选）
        
        Returns:
            memory_id
        """
        content = f"目标: {goal}"
        if deadline:
            content += f"\n\n截止: {deadline}"
        
        default_tags = ["个人", "目标"]
        if tags:
            default_tags.extend(tags)
        
        memory_id = self.sms.remember(
            content,
            memory_type=MemoryType.SEMANTIC,
            tags=default_tags,
            wing="个人",
            room="目标"
        )
        
        print(f"[目标已记录] {goal[:50]}...")
        return memory_id
    
    def record_reflection(self, reflection: str,
                         context: str = None,
                         tags: List[str] = None) -> str:
        """
        记录反思
        
        Args:
            reflection: 反思内容
            context: 反思背景（可选）
            tags: 标签（可选）
        
        Returns:
            memory_id
        """
        content = f"反思: {reflection}"
        if context:
            content += f"\n\n背景: {context}"
        
        default_tags = ["个人", "反思"]
        if tags:
            default_tags.extend(tags)
        
        memory_id = self.sms.remember(
            content,
            memory_type=MemoryType.REFLECTIVE,
            tags=default_tags,
            wing="个人",
            room="反思"
        )
        
        print(f"[反思已记录] {reflection[:50]}...")
        return memory_id
    
    # ========================================================================
    # 查询API
    # ========================================================================
    
    def wake_up(self, query: str = None) -> dict:
        """
        Wake-up记忆
        
        Args:
            query: 查询（可选）
        
        Returns:
            Wake-up结果
        """
        return self.sms.wake_up(query)
    
    def search_work(self, query: str) -> dict:
        """搜索工作记忆"""
        return self.sms.recall_l2_room(query, wing="工作")
    
    def search_learning(self, query: str) -> dict:
        """搜索学习记忆"""
        return self.sms.recall_l2_room(query, wing="学习")
    
    def search_personal(self, query: str) -> dict:
        """搜索个人记忆"""
        return self.sms.recall_l2_room(query, wing="个人")
    
    def get_status(self) -> dict:
        """获取系统状态"""
        return self.sms.get_status()
    
    def check_contradictions(self) -> List[dict]:
        """检查矛盾"""
        return self.sms.check_contradictions()
    
    # ========================================================================
    # 实用工具
    # ========================================================================
    
    def daily_summary(self) -> str:
        """
        生成每日总结
        
        Returns:
            总结文本
        """
        status = self.sms.get_status()
        
        summary = f"""=== 小妖每日总结 ===
日期: {datetime.now().strftime("%Y-%m-%d")}

系统状态:
- 总记忆数: {status['stats']['total_memories']}
- 关键事实: {status['stats']['critical_facts']}
- Wake-up调用: {status['stats']['wake_up_calls']}

记忆分布:
"""
        for mem_type, count in status['memory_distribution'].items():
            summary += f"- {mem_type}: {count}\n"
        
        # 检查矛盾
        contradictions = self.sms.check_contradictions()
        if contradictions:
            summary += f"\n⚠️  发现 {len(contradictions)} 个矛盾\n"
        
        return summary
    
    def export_memories(self, output_path: str = None) -> str:
        """
        导出所有记忆
        
        Args:
            output_path: 输出路径（可选）
        
        Returns:
            导出文件路径
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{self.storage_path}/xiaoyao_memories_{timestamp}.json"
        
        # 创建目录
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 导出
        status = self.sms.get_status()
        export_data = {
            'version': self.sms.version,
            'export_date': datetime.now().isoformat(),
            'stats': status['stats'],
            'memories': []
        }
        
        # 添加所有记忆
        for memory_id, memory in self.sms.memories.items():
            export_data['memories'].append({
                'id': memory_id,
                'content': memory['content'],
                'type': memory['type'],
                'tags': memory['tags'],
                'created_at': memory['created_at'],
                'is_critical': memory.get('is_critical', False)
            })
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"[记忆已导出] {output_path}")
        return output_path


# =============================================================================
# 便捷函数
# =============================================================================

def get_xiaoyao_memory() -> XiaoyaoMemorySystem:
    """获取小妖记忆系统单例"""
    return XiaoyaoMemorySystem()


# =============================================================================
# 测试
# =============================================================================

if __name__ == "__main__":
    print("="*70)
    print("小妖的AI记忆系统 - 集成测试")
    print("="*70)
    
    # 初始化
    xiaoyao = get_xiaoyao_memory()
    
    # 测试：记录决策
    print("\n[测试] 记录工作决策")
    xiaoyao.record_decision(
        "团队决定使用Clerk而非Auth0，因为定价和开发者体验更好。",
        context="项目启动阶段，评估了多个认证方案",
        tags=["认证", "Clerk"]
    )
    
    # 测试：记录学习
    print("\n[测试] 记录学习内容")
    xiaoyao.record_learning(
        "MemPalace记忆系统",
        "核心是原始存储优先，不预先过滤内容。Wing/Room/Hall组织。",
        source="https://github.com/MemPalace/mempalace",
        tags=["MemPalace", "记忆系统"]
    )
    
    # 测试：记录偏好
    print("\n[测试] 记录个人偏好")
    xiaoyao.record_preference(
        "我喜欢使用TypeScript，类型安全让我更自信。",
        category="技术偏好",
        tags=["TypeScript"]
    )
    
    # 测试：Wake-up
    print("\n[测试] Wake-up")
    wake_result = xiaoyao.wake_up("决策")
    print(f"Wake-up tokens: {wake_result['total_tokens']}")
    
    # 测试：搜索
    print("\n[测试] 搜索工作记忆")
    work_result = xiaoyao.search_work("认证")
    print(f"找到 {work_result['count']} 条工作记忆")
    
    # 测试：每日总结
    print("\n[测试] 每日总结")
    print(xiaoyao.daily_summary())
    
    # 测试：导出
    print("\n[测试] 导出记忆")
    export_path = xiaoyao.export_memories()
    print(f"已导出到: {export_path}")
    
    print("\n" + "="*70)
    print("小妖的AI记忆系统测试完成！")
    print("="*70)
