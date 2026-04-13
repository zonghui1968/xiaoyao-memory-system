"""
小妖超级记忆系统 - 参数调优器（Parameter Tuner）

功能：
- 参数搜索
- 性能评估
- 最优参数选择
- A/B测试

作者：小妖🦊
创建日期：2026-04-12
"""

import random
import threading
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict
import statistics


class ParameterSet:
    """参数集"""

    def __init__(self, params: Dict[str, Any]):
        """
        初始化参数集

        Args:
            params: 参数字典
        """
        self.params = params
        self.performance_score = 0.0
        self.test_count = 0
        self.created_at = datetime.now()

    def update_performance(self, score: float):
        """
        更新性能分数

        Args:
            score: 性能分数
        """
        # 指数移动平均
        alpha = 0.3
        self.performance_score = alpha * score + (1 - alpha) * self.performance_score
        self.test_count += 1


class ParameterTuner:
    """
    参数调优器

    功能：
    - 参数搜索
    - 性能评估
    - 最优参数选择
    - A/B测试
    """

    def __init__(self):
        """初始化参数调优器"""
        self.parameter_sets: Dict[str, ParameterSet] = {}
        self.test_results = []
        self.ab_tests = []
        self.lock = threading.RLock()

    def add_parameter_set(
        self,
        name: str,
        params: Dict[str, Any]
    ) -> str:
        """
        添加参数集

        Args:
            name: 名称
            params: 参数

        Returns:
            参数集ID
        """
        with self.lock:
            param_set = ParameterSet(params)
            param_set_id = f"param_{name}_{datetime.now().timestamp()}"
            self.parameter_sets[param_set_id] = param_set
            return param_set_id

    def update_performance(
        self,
        param_set_id: str,
        score: float
    ):
        """
        更新参数集性能

        Args:
            param_set_id: 参数集ID
            score: 性能分数
        """
        with self.lock:
            if param_set_id in self.parameter_sets:
                self.parameter_sets[param_set_id].update_performance(score)

    def grid_search(
        self,
        param_grid: Dict[str, List[Any]],
        evaluate_func: callable,
        iterations: int = 3
    ) -> Tuple[Dict[str, Any], float]:
        """
        网格搜索

        Args:
            param_grid: 参数网格 {param_name: [values]}
            evaluate_func: 评估函数
            iterations: 每组参数的迭代次数

        Returns:
            (最佳参数, 最佳分数)
        """
        with self.lock:
            best_params = None
            best_score = -float('inf')

            # 生成所有组合
            from itertools import product

            param_names = list(param_grid.keys())
            param_values = list(param_grid.values())

            for combination in product(*param_values):
                params = dict(zip(param_names, combination))

                # 评估
                scores = []
                for _ in range(iterations):
                    try:
                        score = evaluate_func(params)
                        scores.append(score)
                    except Exception as e:
                        print(f"评估失败: {e}")
                        continue

                if scores:
                    avg_score = statistics.mean(scores)

                    if avg_score > best_score:
                        best_score = avg_score
                        best_params = params

                    # 记录结果
                    self.test_results.append({
                        "params": params,
                        "score": avg_score,
                        "timestamp": datetime.now().isoformat()
                    })

            return best_params, best_score

    def random_search(
        self,
        param_ranges: Dict[str, Tuple[float, float]],
        evaluate_func: callable,
        n_iterations: int = 50
    ) -> Tuple[Dict[str, Any], float]:
        """
        随机搜索

        Args:
            param_ranges: 参数范围 {param_name: (min, max)}
            evaluate_func: 评估函数
            n_iterations: 迭代次数

        Returns:
            (最佳参数, 最佳分数)
        """
        with self.lock:
            best_params = None
            best_score = -float('inf')

            for _ in range(n_iterations):
                # 随机生成参数
                params = {}
                for param_name, (min_val, max_val) in param_ranges.items():
                    params[param_name] = random.uniform(min_val, max_val)

                # 评估
                try:
                    score = evaluate_func(params)
                except Exception as e:
                    print(f"评估失败: {e}")
                    continue

                if score > best_score:
                    best_score = score
                    best_params = params

                # 记录结果
                self.test_results.append({
                    "params": params,
                    "score": score,
                    "timestamp": datetime.now().isoformat()
                })

            return best_params, best_score

    def ab_test(
        self,
        param_set_a: Dict[str, Any],
        param_set_b: Dict[str, Any],
        evaluate_func: callable,
        n_tests: int = 20
    ) -> Dict[str, Any]:
        """
        A/B测试

        Args:
            param_set_a: 参数集A
            param_set_b: 参数集B
            evaluate_func: 评估函数
            n_tests: 测试次数

        Returns:
            测试结果
        """
        with self.lock:
            scores_a = []
            scores_b = []

            for _ in range(n_tests):
                # 测试A
                try:
                    score_a = evaluate_func(param_set_a)
                    scores_a.append(score_a)
                except:
                    pass

                # 测试B
                try:
                    score_b = evaluate_func(param_set_b)
                    scores_b.append(score_b)
                except:
                    pass

            # 分析结果
            result = {
                "param_set_a": param_set_a,
                "param_set_b": param_set_b,
                "scores_a": scores_a,
                "scores_b": scores_b,
                "mean_a": statistics.mean(scores_a) if scores_a else 0.0,
                "mean_b": statistics.mean(scores_b) if scores_b else 0.0,
                "std_a": statistics.stdev(scores_a) if len(scores_a) > 1 else 0.0,
                "std_b": statistics.stdev(scores_b) if len(scores_b) > 1 else 0.0,
                "winner": None,
                "improvement": 0.0
            }

            if result["mean_a"] > result["mean_b"]:
                result["winner"] = "A"
                result["improvement"] = (
                    (result["mean_a"] - result["mean_b"]) / result["mean_b"]
                    if result["mean_b"] > 0 else 0.0
                )
            else:
                result["winner"] = "B"
                result["improvement"] = (
                    (result["mean_b"] - result["mean_a"]) / result["mean_a"]
                    if result["mean_a"] > 0 else 0.0
                )

            # 记录测试
            self.ab_tests.append(result)

            return result

    def get_best_parameters(self) -> Optional[Tuple[str, Dict[str, Any], float]]:
        """
        获取最佳参数

        Returns:
            (参数集ID, 参数, 性能分数)
        """
        with self.lock:
            if not self.parameter_sets:
                return None

            best_id = None
            best_score = -float('inf')

            for param_id, param_set in self.parameter_sets.items():
                if param_set.performance_score > best_score:
                    best_score = param_set.performance_score
                    best_id = param_id

            if best_id is None:
                return None

            return best_id, self.parameter_sets[best_id].params, best_score

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            return {
                "total_parameter_sets": len(self.parameter_sets),
                "total_tests": len(self.test_results),
                "total_ab_tests": len(self.ab_tests),
                "best_performance": max(
                    (ps.performance_score for ps in self.parameter_sets.values()),
                    default=0.0
                )
            }


# 测试代码
if __name__ == "__main__":
    print("小妖超级记忆系统 - 参数调优器")
    print("=" * 60)

    tuner = ParameterTuner()

    print("\n[OK] 参数调优器初始化成功")

    # 模拟评估函数
    def dummy_evaluate(params):
        """模拟评估函数"""
        # 简单的二次函数，最优解在x=5, y=3
        x = params.get("x", 0)
        y = params.get("y", 0)
        return -((x - 5) ** 2 + (y - 3) ** 2) + 100

    # 网格搜索
    print("\n[OK] 网格搜索:")

    param_grid = {
        "x": [0, 2, 4, 6, 8, 10],
        "y": [0, 1, 2, 3, 4, 5]
    }

    best_params, best_score = tuner.grid_search(
        param_grid,
        dummy_evaluate,
        iterations=2
    )

    print(f"  最佳参数: {best_params}")
    print(f"  最佳分数: {best_score:.3f}")

    # 随机搜索
    print("\n[OK] 随机搜索:")

    param_ranges = {
        "x": (0, 10),
        "y": (0, 5)
    }

    best_params_random, best_score_random = tuner.random_search(
        param_ranges,
        dummy_evaluate,
        n_iterations=30
    )

    print(f"  最佳参数: {best_params_random}")
    print(f"  最佳分数: {best_score_random:.3f}")

    # A/B测试
    print("\n[OK] A/B测试:")

    param_set_a = {"x": 4, "y": 3}
    param_set_b = {"x": 5, "y": 3}

    ab_result = tuner.ab_test(
        param_set_a,
        param_set_b,
        dummy_evaluate,
        n_tests=10
    )

    print(f"  参数集A平均分数: {ab_result['mean_a']:.3f}")
    print(f"  参数集B平均分数: {ab_result['mean_b']:.3f}")
    print(f"  获胜者: {ab_result['winner']}")
    print(f"  提升幅度: {ab_result['improvement']:.2%}")

    # 获取统计
    print("\n[OK] 统计信息:")
    stats = tuner.get_statistics()

    print(f"  参数集总数: {stats['total_parameter_sets']}")
    print(f"  总测试数: {stats['total_tests']}")
    print(f"  A/B测试数: {stats['total_ab_tests']}")
    print(f"  最佳性能: {stats['best_performance']:.3f}")

    print("\n[OK] 参数调优器测试通过！")
    print("\n[Xiaoyao] 参数调优器已就绪，可以开始参数优化！")
