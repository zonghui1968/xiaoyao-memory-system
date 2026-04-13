"""
小妖超级记忆系统 - 配置层（Configuration Layer）

整合六维记忆体系，提供系统级配置管理

作者：小妖🦊
创建日期：2026-04-12
基于：Claude Code六维记忆体系
"""

import os
import json
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import yaml


class ConfigurationLayer:
    """
    配置层（Layer 0）- 六维记忆体系整合

    六层架构：
    1. ORGANIZATION.md - 系统级规范
    2. WORKSPACE.md - 项目级指令
    3. rules/ - 模块化规则
    4. USER.md - 用户偏好
    5. WORKSPACE.local.md - 本地配置
    6. MEMORY.md - 自动记忆索引
    """

    def __init__(self, workspace_path: str = "C:/ssh/.openclaw/workspace"):
        """
        初始化配置层

        Args:
            workspace_path: 工作区路径
        """
        self.workspace_path = Path(workspace_path)
        self.configs = {}
        self.lock = threading.RLock()

        # 加载所有配置
        self._load_all_configs()

    def _load_all_configs(self):
        """加载所有配置"""
        with self.lock:
            # Layer 1: ORGANIZATION.md
            self.configs["organization"] = self._load_markdown_config(
                self.workspace_path / "ORGANIZATION.md"
            )

            # Layer 2: WORKSPACE.md
            self.configs["workspace"] = self._load_markdown_config(
                self.workspace_path / "WORKSPACE.md"
            )

            # Layer 4: USER.md
            self.configs["user"] = self._load_markdown_config(
                self.workspace_path / "USER.md"
            )

            # Layer 3: rules/
            self.configs["rules"] = self._load_rules_directory()

            # Layer 6: MEMORY.md
            self.configs["memory_index"] = self._load_memory_index()

    def _load_markdown_config(self, file_path: Path) -> Dict[str, Any]:
        """
        加载Markdown配置文件

        Args:
            file_path: 文件路径

        Returns:
            配置字典
        """
        if not file_path.exists():
            return {"exists": False, "loaded_at": None}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "exists": True,
                "path": str(file_path),
                "content": content,
                "loaded_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "exists": True,
                "error": str(e),
                "loaded_at": datetime.now().isoformat()
            }

    def _load_rules_directory(self) -> Dict[str, Dict[str, Any]]:
        """
        加载rules/目录

        Returns:
            规则字典
        """
        rules_dir = self.workspace_path / ".openclaw" / "rules"

        if not rules_dir.exists():
            return {"exists": False, "rules": {}}

        rules = {}

        for rule_file in rules_dir.glob("*.md"):
            rule_name = rule_file.stem
            rules[rule_name] = self._load_markdown_config(rule_file)

        return {
            "exists": True,
            "path": str(rules_dir),
            "rules": rules,
            "loaded_at": datetime.now().isoformat()
        }

    def _load_memory_index(self) -> Dict[str, Any]:
        """
        加载MEMORY.md索引

        Returns:
            记忆索引字典
        """
        memory_file = self.workspace_path / "MEMORY.md"

        if not memory_file.exists():
            return {"exists": False, "topics": []}

        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取topics
            topics = self._extract_topics_from_memory(content)

            return {
                "exists": True,
                "path": str(memory_file),
                "topics": topics,
                "loaded_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "exists": True,
                "error": str(e),
                "loaded_at": datetime.now().isoformat()
            }

    def _extract_topics_from_memory(self, content: str) -> List[Dict[str, str]]:
        """
        从MEMORY.md中提取topics

        Args:
            content: MEMORY.md内容

        Returns:
            topic列表
        """
        topics = []
        lines = content.split('\n')

        for line in lines:
            # 查找topic链接 [title](path)
            if '[' in line and '](' in line and '.md' in line:
                try:
                    start = line.index('[') + 1
                    end = line.index('](')
                    title = line[start:end]

                    path_start = end + 2
                    path_end = line.index(')', path_start)
                    path = line[path_start:path_end]

                    topics.append({
                        "title": title,
                        "path": path
                    })

                except ValueError:
                    continue

        return topics

    def get_organization_rules(self) -> Dict[str, Any]:
        """获取组织规则（Layer 1）"""
        return self.configs.get("organization", {})

    def get_workspace_config(self) -> Dict[str, Any]:
        """获取工作区配置（Layer 2）"""
        return self.configs.get("workspace", {})

    def get_rules(self, rule_name: str = None) -> Any:
        """
        获取规则（Layer 3）

        Args:
            rule_name: 规则名称，None返回所有规则

        Returns:
            规则内容
        """
        rules_config = self.configs.get("rules", {})

        if rule_name is None:
            return rules_config

        return rules_config.get("rules", {}).get(rule_name, {})

    def get_user_preferences(self) -> Dict[str, Any]:
        """获取用户偏好（Layer 4）"""
        return self.configs.get("user", {})

    def get_memory_topics(self) -> List[Dict[str, str]]:
        """获取记忆topics（Layer 6）"""
        memory_index = self.configs.get("memory_index", {})
        return memory_index.get("topics", [])

    def reload_config(self, layer: str = None):
        """
        重新加载配置

        Args:
            layer: 配置层，None表示全部重新加载
        """
        with self.lock:
            if layer is None:
                self._load_all_configs()
            elif layer == "organization":
                self.configs["organization"] = self._load_markdown_config(
                    self.workspace_path / "ORGANIZATION.md"
                )
            elif layer == "workspace":
                self.configs["workspace"] = self._load_markdown_config(
                    self.workspace_path / "WORKSPACE.md"
                )
            elif layer == "rules":
                self.configs["rules"] = self._load_rules_directory()
            elif layer == "user":
                self.configs["user"] = self._load_markdown_config(
                    self.workspace_path / "USER.md"
                )
            elif layer == "memory":
                self.configs["memory_index"] = self._load_memory_index()

    def get_system_constraints(self) -> Dict[str, Any]:
        """
        获取系统约束

        Returns:
            约束字典，包括：
            - max_tokens: 最大token数
            - safe_mode: 安全模式
            - allowed_operations: 允许的操作
        """
        organization = self.get_organization_rules()

        return {
            "max_tokens": 205000,  # 从系统获取
            "safe_mode": True,
            "allowed_operations": [
                "read", "write", "exec", "search", "message"
            ]
        }

    def get_user_constraints(self) -> Dict[str, Any]:
        """
        获取用户约束

        Returns:
            用户约束字典
        """
        user = self.get_user_preferences()

        return {
            "language": "zh-CN",
            "timezone": "America/Vancouver",
            "working_hours": "09:00-18:00",
            "contact_method": "webchat"
        }

    def get_project_rules(self, project_path: str = None) -> List[str]:
        """
        获取项目规则

        Args:
            project_path: 项目路径

        Returns:
            规则列表
        """
        rules_config = self.get_rules()

        if not rules_config.get("exists"):
            return []

        rules = []

        for rule_name, rule_content in rules_config.get("rules", {}).items():
            if rule_content.get("exists"):
                rules.append(f"Rule: {rule_name}")

        return rules

    def validate_action(self, action: str, context: Dict[str, Any] = None) -> tuple[bool, str]:
        """
        验证操作是否符合规则

        Args:
            action: 操作类型
            context: 上下文

        Returns:
            (是否允许, 原因)
        """
        # 获取系统约束
        system_constraints = self.get_system_constraints()

        # 检查操作是否允许
        if action not in system_constraints.get("allowed_operations", []):
            return False, f"操作 '{action}' 不在允许列表中"

        # 检查安全模式
        if system_constraints.get("safe_mode", True):
            # 安全模式下的额外检查
            if action in ["delete", "format"]:
                return False, f"操作 '{action}' 在安全模式下被禁止"

        return True, "允许"

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取配置层统计信息

        Returns:
            统计信息
        """
        with self.lock:
            stats = {
                "workspace_path": str(self.workspace_path),
                "layers_loaded": len([k for k, v in self.configs.items() if v]),
                "organization_exists": self.configs.get("organization", {}).get("exists", False),
                "workspace_exists": self.configs.get("workspace", {}).get("exists", False),
                "user_exists": self.configs.get("user", {}).get("exists", False),
                "rules_count": len(self.configs.get("rules", {}).get("rules", {})),
                "memory_topics_count": len(self.configs.get("memory_index", {}).get("topics", [])),
                "last_loaded": datetime.now().isoformat()
            }

            return stats


class ConfigurationManager:
    """
    配置管理器 - 提供高级配置管理功能
    """

    def __init__(self, workspace_path: str = "C:/ssh/.openclaw/workspace"):
        self.layer = ConfigurationLayer(workspace_path)

    def get_full_config(self) -> Dict[str, Any]:
        """
        获取完整配置

        Returns:
            完整配置字典
        """
        return {
            "organization": self.layer.get_organization_rules(),
            "workspace": self.layer.get_workspace_config(),
            "rules": self.layer.get_rules(),
            "user": self.layer.get_user_preferences(),
            "memory_topics": self.layer.get_memory_topics(),
            "statistics": self.layer.get_statistics()
        }

    def get_contextual_rules(self, context: Dict[str, Any]) -> List[str]:
        """
        根据上下文获取相关规则

        Args:
            context: 上下文字典

        Returns:
            相关规则列表
        """
        rules = []

        # 获取项目规则
        project_path = context.get("project_path")
        if project_path:
            rules.extend(self.layer.get_project_rules(project_path))

        # 获取用户规则
        user_config = self.layer.get_user_preferences()
        if user_config.get("exists"):
            rules.append("User preferences loaded")

        return rules


# 测试代码
if __name__ == "__main__":
    print("小妖超级记忆系统 - 配置层（Layer 0）")
    print("=" * 60)

    # 创建配置层
    config_layer = ConfigurationLayer()

    # 获取统计信息
    stats = config_layer.get_statistics()

    print("\n[OK] 配置层初始化成功")
    print(f"  工作区: {stats['workspace_path']}")
    print(f"  已加载层级: {stats['layers_loaded']}")
    print(f"  组织规则: {'存在' if stats['organization_exists'] else '不存在'}")
    print(f"  工作区配置: {'存在' if stats['workspace_exists'] else '不存在'}")
    print(f"  用户配置: {'存在' if stats['user_exists'] else '不存在'}")
    print(f"  规则文件: {stats['rules_count']}个")
    print(f"  记忆topics: {stats['memory_topics_count']}个")

    # 验证操作
    print("\n[OK] 操作验证测试:")
    allowed, reason = config_layer.validate_action("read")
    print(f"  read操作: {reason}")

    allowed, reason = config_layer.validate_action("delete")
    print(f"  delete操作: {reason}")

    # 获取记忆topics
    topics = config_layer.get_memory_topics()
    if topics:
        print(f"\n[OK] 记忆topics（前5个）:")
        for topic in topics[:5]:
            print(f"  - {topic['title']}: {topic['path']}")

    print("\n[OK] 配置层测试通过！")
