"""
自动图谱更新系统
监控知识库变化，自动更新graph.json，支持增量更新
"""

import json
import time
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class KnowledgeBaseWatcher(FileSystemEventHandler):
    """
    知识库文件监控器

    监控知识库文件变化，触发图谱更新
    """

    def __init__(
        self,
        callback,
        watch_paths: List[str],
        debounce_seconds: float = 2.0
    ):
        """
        初始化监控器

        Args:
            callback: 变化回调函数
            watch_paths: 监控路径列表
            debounce_seconds: 防抖延迟（秒）
        """
        self.callback = callback
        self.watch_paths = watch_paths
        self.debounce_seconds = debounce_seconds

        self.observer = Observer()
        self.last_event_time = None
        self.pending_update = False
        self.lock = threading.Lock()

    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return

        # 只处理markdown和json文件
        if not (event.src_path.endswith('.md') or
                event.src_path.endswith('.json')):
            return

        with self.lock:
            self.last_event_time = time.time()
            self.pending_update = True

    def start(self):
        """启动监控"""
        for path in self.watch_paths:
            self.observer.schedule(self, path, recursive=True)

        self.observer.start()
        print(f"[OK] 知识库监控已启动")
        print(f"  监控路径: {self.watch_paths}")

        # 启动防抖检查线程
        check_thread = threading.Thread(target=self._debounce_check, daemon=True)
        check_thread.start()

    def stop(self):
        """停止监控"""
        self.observer.stop()
        self.observer.join()

    def _debounce_check(self):
        """防抖检查线程"""
        while True:
            time.sleep(0.5)

            with self.lock:
                if self.pending_update:
                    elapsed = time.time() - self.last_event_time

                    if elapsed >= self.debounce_seconds:
                        self.pending_update = False
                        print(f"\n[INFO] 检测到知识库变化，触发更新...")

                        try:
                            self.callback()
                        except Exception as e:
                            print(f"[ERROR] 更新失败: {e}")


class IncrementalGraphUpdater:
    """
    增量图谱更新器

    功能：
    1. 监控知识库文件变化
    2. 增量更新graph.json
    3. 合并新旧图谱数据
    4. 自动优化和清理
    """

    def __init__(
        self,
        knowledge_base_path: str = "C:\\ssh\\.openclaw\\knowledge-base",
        graph_output_path: str = "C:\\ssh\\.openclaw\\knowledge-base\\graphify-out\\graph.json",
        extractor=None
    ):
        """
        初始化增量图谱更新器

        Args:
            knowledge_base_path: 知识库路径
            graph_output_path: graph.json输出路径
            extractor: 实体提取器
        """
        self.kb_path = Path(knowledge_base_path)
        self.graph_path = Path(graph_output_path)
        self.extractor = extractor

        # 监控路径
        self.watch_paths = [
            str(self.kb_path / "raw"),
            str(self.kb_path / "wiki")
        ]

        # 统计信息
        self.stats = {
            "total_updates": 0,
            "files_processed": 0,
            "nodes_added": 0,
            "edges_added": 0,
            "last_update": None
        }

    def update_graph(self) -> bool:
        """
        更新图谱（增量更新）

        Returns:
            是否成功
        """
        try:
            print(f"\n[INFO] 开始增量更新图谱...")

            # 1. 加载现有图谱
            existing_graph = self._load_existing_graph()

            # 2. 扫描知识库文件
            new_data = self._scan_knowledge_base()

            # 3. 合并图谱数据
            merged_graph = self._merge_graphs(existing_graph, new_data)

            # 4. 优化图谱
            optimized_graph = self._optimize_graph(merged_graph)

            # 5. 保存图谱
            self._save_graph(optimized_graph)

            # 6. 更新统计
            self.stats["total_updates"] += 1
            self.stats["last_update"] = datetime.now().isoformat()

            print(f"[OK] 图谱更新完成")
            print(f"  节点数: {len(optimized_graph['nodes'])}")
            print(f"  边数: {len(optimized_graph['edges'])}")

            return True

        except Exception as e:
            print(f"[ERROR] 图谱更新失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _load_existing_graph(self) -> Dict[str, Any]:
        """加载现有图谱"""
        if self.graph_path.exists():
            try:
                with open(self.graph_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[WARNING] 加载现有图谱失败: {e}")

        return {
            "nodes": [],
            "edges": [],
            "metadata": {}
        }

    def _scan_knowledge_base(self) -> Dict[str, Any]:
        """扫描知识库文件"""
        nodes = []
        edges = []

        # 扫描raw目录
        raw_path = self.kb_path / "raw"
        if raw_path.exists():
            for file_path in raw_path.rglob("*.md"):
                file_nodes, file_edges = self._process_file(file_path)
                nodes.extend(file_nodes)
                edges.extend(file_edges)
                self.stats["files_processed"] += 1

        # 扫描wiki目录
        wiki_path = self.kb_path / "wiki"
        if wiki_path.exists():
            for file_path in wiki_path.rglob("*.md"):
                file_nodes, file_edges = self._process_file(file_path)
                nodes.extend(file_nodes)
                edges.extend(file_edges)
                self.stats["files_processed"] += 1

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "source": "knowledge_base_scan",
                "timestamp": datetime.now().isoformat()
            }
        }

    def _process_file(self, file_path: Path) -> tuple:
        """处理单个文件"""
        try:
            # 读取文件
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 提取实体
            if self.extractor:
                extraction = self.extractor.extract_entities(content)
                graph_data = self.extractor.convert_to_graph_format(extraction)
            else:
                # 简单提取：文件名作为节点
                graph_data = {
                    "nodes": [{
                        "id": file_path.stem,
                        "name": file_path.stem,
                        "type": "file",
                        "importance": 0.5
                    }],
                    "edges": []
                }

            return graph_data["nodes"], graph_data["edges"]

        except Exception as e:
            print(f"[WARNING] 处理文件失败 {file_path}: {e}")
            return [], []

    def _merge_graphs(
        self,
        existing: Dict[str, Any],
        new: Dict[str, Any]
    ) -> Dict[str, Any]:
        """合并图谱数据"""
        # 合并节点
        existing_nodes = {node["id"]: node for node in existing.get("nodes", [])}

        for node in new.get("nodes", []):
            if node["id"] in existing_nodes:
                # 更新现有节点
                existing_node = existing_nodes[node["id"]]
                existing_node["importance"] = max(
                    existing_node.get("importance", 0),
                    node.get("importance", 0)
                )
            else:
                # 添加新节点
                existing_nodes[node["id"]] = node
                self.stats["nodes_added"] += 1

        # 合并边
        existing_edges = {}
        for edge in existing.get("edges", []):
            edge_key = self._get_edge_key(edge)
            existing_edges[edge_key] = edge

        for edge in new.get("edges", []):
            edge_key = self._get_edge_key(edge)

            if edge_key in existing_edges:
                # 更新现有边
                existing_edge = existing_edges[edge_key]
                existing_edge["weight"] = max(
                    existing_edge.get("weight", 0),
                    edge.get("weight", 0)
                )
            else:
                # 添加新边
                existing_edges[edge_key] = edge
                self.stats["edges_added"] += 1

        return {
            "nodes": list(existing_nodes.values()),
            "edges": list(existing_edges.values()),
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "total_nodes": len(existing_nodes),
                "total_edges": len(existing_edges)
            }
        }

    def _get_edge_key(self, edge: Dict[str, Any]) -> tuple:
        """获取边的唯一键"""
        return (
            edge["source"],
            edge["target"],
            edge.get("type", "related_to")
        )

    def _optimize_graph(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """优化图谱"""
        # 移除低重要性节点
        min_importance = 0.1

        filtered_nodes = [
            node for node in graph["nodes"]
            if node.get("importance", 0) >= min_importance
        ]

        node_ids = {node["id"] for node in filtered_nodes}

        # 移除指向不存在节点的边
        filtered_edges = [
            edge for edge in graph["edges"]
            if edge["source"] in node_ids and edge["target"] in node_ids
        ]

        return {
            "nodes": filtered_nodes,
            "edges": filtered_edges,
            "metadata": {
                **graph.get("metadata", {}),
                "optimized": True,
                "min_importance": min_importance
            }
        }

    def _save_graph(self, graph: Dict[str, Any]):
        """保存图谱"""
        # 确保目录存在
        self.graph_path.parent.mkdir(parents=True, exist_ok=True)

        # 保存
        with open(self.graph_path, "w", encoding="utf-8") as f:
            json.dump(graph, f, ensure_ascii=False, indent=2)

        print(f"[OK] 图谱已保存: {self.graph_path}")

    def start_auto_update(self):
        """启动自动更新"""
        watcher = KnowledgeBaseWatcher(
            callback=self.update_graph,
            watch_paths=self.watch_paths
        )

        watcher.start()

        return watcher

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()


# 测试代码
if __name__ == "__main__":
    # 导入实体提取器
    import sys
    sys.path.insert(0, str(Path(r"C:\ssh\.openclaw\xiaoyao-memory-system\src")))
    from llm_entity_extractor import LLMEntityExtractor

    # 创建提取器
    extractor = LLMEntityExtractor()

    # 创建更新器
    updater = IncrementalGraphUpdater(
        knowledge_base_path=r"C:\ssh\.openclaw\knowledge-base",
        graph_output_path=r"C:\ssh\.openclaw\knowledge-base\graphify-out\graph_auto.json",
        extractor=extractor
    )

    # 手动触发更新
    print("执行手动更新...")
    updater.update_graph()

    # 显示统计
    stats = updater.get_statistics()
    print(f"\n统计信息: {json.dumps(stats, indent=2, ensure_ascii=False)}")
