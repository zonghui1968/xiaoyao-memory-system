"""
LLM实体提取器 - WAL协议核心组件
使用LLM从文本中提取实体和关系，自动更新知识图谱
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import threading


class LLMEntityExtractor:
    """
    LLM实体提取器

    功能：
    1. 从文本中提取实体（人名、地名、概念等）
    2. 识别实体间关系
    3. 计算实体重要性
    4. 生成结构化图谱数据
    """

    def __init__(
        self,
        model_name: str = "zai/glm-4.7",  # 使用的LLM模型
        cache_path: str = "data/entity_cache"
    ):
        """
        初始化LLM实体提取器

        Args:
            model_name: LLM模型名称
            cache_path: 缓存路径
        """
        self.model_name = model_name
        self.cache_path = Path(cache_path)
        self.lock = threading.RLock()

        # 创建缓存目录
        self.cache_path.mkdir(parents=True, exist_ok=True)

        # 实体类型模式
        self.entity_patterns = {
            "person": r"[\u4e00-\u9fa5]{2,4}(?=[，。、\s]|$)",  # 中文人名
            "concept": r"[A-Z][a-z]+(?:[A-Z][a-z]+)+",  # 大驼峰（概念名）
            "tech": r"(?:Python|Java|JavaScript|React|Vue|GraphQL|API|REST|SQL|NoSQL)",  # 技术栈
            "project": r"(?:Graphify|SuperMemory|WAL|LanceDB|NetworkX)",  # 项目名
        }

        # 关系词模式
        self.relation_patterns = {
            "is_a": ["是", "属于", "为"],
            "has": ["有", "包含", "具有"],
            "uses": ["使用", "用", "采用"],
            "implements": ["实现", "包含"],
            "related_to": ["相关", "关联"],
        }

        # 统计信息
        self.stats = {
            "extractions": 0,
            "entities_found": 0,
            "relations_found": 0,
            "cache_hits": 0
        }

    def extract_entities(
        self,
        text: str,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        从文本中提取实体和关系

        Args:
            text: 输入文本
            use_llm: 是否使用LLM（False时使用规则匹配）

        Returns:
            提取结果：{entities, relations, metadata}
        """
        with self.lock:
            self.stats["extractions"] += 1

            # 检查缓存
            cache_key = self._get_cache_key(text)
            cached = self._load_from_cache(cache_key)

            if cached:
                self.stats["cache_hits"] += 1
                return cached

            # 执行提取
            if use_llm:
                result = self._extract_with_llm(text)
            else:
                result = self._extract_with_rules(text)

            # 保存到缓存
            self._save_to_cache(cache_key, result)

            # 更新统计
            self.stats["entities_found"] += len(result["entities"])
            self.stats["relations_found"] += len(result["relations"])

            return result

    def _extract_with_llm(self, text: str) -> Dict[str, Any]:
        """
        使用LLM提取实体和关系

        Args:
            text: 输入文本

        Returns:
            提取结果
        """
        # 构建提示词
        prompt = self._build_extraction_prompt(text)

        # 这里应该调用实际的LLM
        # 为了演示，我们使用规则提取作为fallback
        # 在实际应用中，应该：
        # 1. 调用OpenAI API / Anthropic API / 本地LLM
        # 2. 解析LLM返回的JSON
        # 3. 验证提取结果

        # 暂时使用规则提取
        result = self._extract_with_rules(text)

        # 添加LLM标记（实际应用中应该调用真实LLM）
        result["metadata"]["extraction_method"] = "rule_based"  # 改为 "llm_based"
        result["metadata"]["model"] = self.model_name

        return result

    def _build_extraction_prompt(self, text: str) -> str:
        """
        构建LLM提取提示词

        Args:
            text: 输入文本

        Returns:
            提示词
        """
        prompt = f"""请从以下文本中提取实体和关系：

文本：
{text}

请以JSON格式返回：
{{
  "entities": [
    {{"name": "实体名", "type": "类型（person/concept/tech/project等）", "importance": 0.8}}
  ],
  "relations": [
    {{"source": "实体1", "target": "实体2", "type": "关系类型", "weight": 0.9}}
  ]
}}

要求：
1. 只提取明确的实体
2. 关系要有明确的证据
3. 重要性范围0-1
4. 关系权重范围0-1
"""
        return prompt

    def _extract_with_rules(self, text: str) -> Dict[str, Any]:
        """
        使用规则提取实体和关系（fallback方法）

        Args:
            text: 输入文本

        Returns:
            提取结果
        """
        entities = []
        relations = []

        # 提取实体
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.finditer(pattern, text)

            for match in matches:
                entity_name = match.group()

                # 避免重复
                if not any(e["name"] == entity_name for e in entities):
                    entities.append({
                        "name": entity_name,
                        "type": entity_type,
                        "importance": self._calculate_importance(entity_name, text)
                    })

        # 提取关系
        for rel_type, keywords in self.relation_patterns.items():
            for keyword in keywords:
                # 查找关系词模式：实体1 + 关系词 + 实体2
                pattern = rf"({self.entity_patterns['person']}|{self.entity_patterns['concept']})\s*{keyword}\s*({self.entity_patterns['person']}|{self.entity_patterns['concept']})"

                matches = re.finditer(pattern, text)

                for match in matches:
                    source = match.group(1)
                    target = match.group(2)

                    # 避免重复
                    if not any(
                        r["source"] == source and
                        r["target"] == target and
                        r["type"] == rel_type
                        for r in relations
                    ):
                        relations.append({
                            "source": source,
                            "target": target,
                            "type": rel_type,
                            "weight": 0.7
                        })

        return {
            "entities": entities,
            "relations": relations,
            "metadata": {
                "text_length": len(text),
                "extraction_method": "rule_based",
                "timestamp": datetime.now().isoformat()
            }
        }

    def _calculate_importance(self, entity_name: str, text: str) -> float:
        """
        计算实体重要性

        Args:
            entity_name: 实体名
            text: 文本

        Returns:
            重要性分数（0-1）
        """
        # 基于词频
        frequency = text.count(entity_name)

        # 基于位置（首次出现位置）
        first_pos = text.find(entity_name)
        position_score = 1.0 - (first_pos / len(text)) if first_pos >= 0 else 0.5

        # 基于长度（短实体名更重要）
        length_score = 1.0 / (1.0 + len(entity_name) / 10.0)

        # 综合分数
        importance = min(1.0, (frequency * 0.3 + position_score * 0.4 + length_score * 0.3))

        return round(importance, 3)

    def convert_to_graph_format(
        self,
        extraction_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        将提取结果转换为graph.json格式

        Args:
            extraction_result: 提取结果

        Returns:
            graph.json格式数据
        """
        entities = extraction_result["entities"]
        relations = extraction_result["relations"]

        # 生成节点ID
        node_map = {}
        nodes = []

        for entity in entities:
            node_id = entity["name"].lower().replace(" ", "_")
            node_map[entity["name"]] = node_id

            nodes.append({
                "id": node_id,
                "name": entity["name"],
                "type": entity["type"],
                "importance": entity["importance"]
            })

        # 生成边
        edges = []

        for relation in relations:
            source_id = node_map.get(relation["source"])
            target_id = node_map.get(relation["target"])

            if source_id and target_id:
                edges.append({
                    "source": source_id,
                    "target": target_id,
                    "type": relation["type"],
                    "weight": relation["weight"]
                })

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "extraction_method": extraction_result["metadata"]["extraction_method"],
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }
        }

    def _get_cache_key(self, text: str) -> str:
        """生成缓存键"""
        import hashlib
        return hashlib.md5(text.encode()).hexdigest()[:16]

    def _load_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """从缓存加载"""
        cache_file = self.cache_path / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None

        return None

    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]):
        """保存到缓存"""
        cache_file = self.cache_path / f"{cache_key}.json"

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存缓存失败: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()


class WALGraphUpdater:
    """
    WAL图谱更新器
    监控WAL日志，自动更新graph.json
    """

    def __init__(
        self,
        wal_path: str = "data/wal",
        graph_path: str = "knowledge-base/graphify-out/graph.json",
        extractor: Optional[LLMEntityExtractor] = None
    ):
        """
        初始化WAL图谱更新器

        Args:
            wal_path: WAL日志路径
            graph_path: graph.json路径
            extractor: 实体提取器
        """
        self.wal_path = Path(wal_path)
        self.graph_path = Path(graph_path)
        self.extractor = extractor or LLMEntityExtractor()

        # 确保目录存在
        self.wal_path.mkdir(parents=True, exist_ok=True)

    def process_wal_entry(self, entry: Dict[str, Any]) -> bool:
        """
        处理WAL日志条目

        Args:
            entry: WAL条目

        Returns:
            是否成功更新
        """
        try:
            # 提取实体
            text = entry.get("content", "")
            extraction = self.extractor.extract_entities(text)

            # 转换为图谱格式
            graph_data = self.extractor.convert_to_graph_format(extraction)

            # 更新graph.json
            self._update_graph_json(graph_data)

            return True

        except Exception as e:
            print(f"处理WAL条目失败: {e}")
            return False

    def _update_graph_json(self, new_data: Dict[str, Any]):
        """
        更新graph.json

        Args:
            new_data: 新的图谱数据
        """
        # 加载现有图谱
        if self.graph_path.exists():
            with open(self.graph_path, "r", encoding="utf-8") as f:
                existing_graph = json.load(f)
        else:
            existing_graph = {"nodes": [], "edges": []}

        # 合并节点
        existing_nodes = {node["id"]: node for node in existing_graph["nodes"]}

        for node in new_data["nodes"]:
            if node["id"] in existing_nodes:
                # 更新现有节点
                existing_node = existing_nodes[node["id"]]
                existing_node["importance"] = max(
                    existing_node.get("importance", 0),
                    node["importance"]
                )
            else:
                # 添加新节点
                existing_nodes[node["id"]] = node

        # 合并边
        existing_edges = {
            (edge["source"], edge["target"], edge["type"]): edge
            for edge in existing_graph["edges"]
        }

        for edge in new_data["edges"]:
            edge_key = (edge["source"], edge["target"], edge["type"])

            if edge_key in existing_edges:
                # 更新现有边
                existing_edge = existing_edges[edge_key]
                existing_edge["weight"] = max(
                    existing_edge.get("weight", 0),
                    edge["weight"]
                )
            else:
                # 添加新边
                existing_edges[edge_key] = edge

        # 保存更新后的图谱
        updated_graph = {
            "nodes": list(existing_nodes.values()),
            "edges": list(existing_edges.values()),
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "total_nodes": len(existing_nodes),
                "total_edges": len(existing_edges)
            }
        }

        # 确保目录存在
        self.graph_path.parent.mkdir(parents=True, exist_ok=True)

        # 保存
        with open(self.graph_path, "w", encoding="utf-8") as f:
            json.dump(updated_graph, f, ensure_ascii=False, indent=2)

        print(f"图谱已更新: {self.graph_path}")
        print(f"  节点数: {updated_graph['metadata']['total_nodes']}")
        print(f"  边数: {updated_graph['metadata']['total_edges']}")


# 测试代码
if __name__ == "__main__":
    # 创建提取器
    extractor = LLMEntityExtractor()

    # 测试文本
    test_text = """
    小妖是宗晖哥哥的行政助理。Graphify是一个Python知识图谱库，
    使用NetworkX进行网络分析。SuperMemorySystemV6集成了Graphify
    和LanceDB向量数据库，实现了语义搜索功能。
    """

    # 提取实体
    result = extractor.extract_entities(test_text)

    print("提取结果:")
    print(f"  实体数: {len(result['entities'])}")
    print(f"  关系数: {len(result['relations'])}")

    # 转换为图谱格式
    graph_data = extractor.convert_to_graph_format(result)

    print(f"\n图谱数据:")
    print(f"  节点数: {len(graph_data['nodes'])}")
    print(f"  边数: {len(graph_data['edges'])}")

    # 保存图谱
    output_path = Path("data/test_graph.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)

    print(f"\n图谱已保存: {output_path}")
