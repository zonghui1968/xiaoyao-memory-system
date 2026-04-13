"""
用户反馈收集系统
收集、存储和分析用户反馈
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
from collections import Counter


class FeedbackCollector:
    """
    用户反馈收集器

    功能：
    1. 收集用户反馈
    2. 保存到JSON文件
    3. 生成统计报告
    4. 分析趋势和模式
    """

    def __init__(
        self,
        feedback_path: str = "C:\\ssh\\.openclaw\\xiaoyao-memory-system\\data\\feedbacks.json"
    ):
        """
        初始化反馈收集器

        Args:
            feedback_path: 反馈数据存储路径
        """
        self.feedback_path = Path(feedback_path)
        self.feedback_path.parent.mkdir(parents=True, exist_ok=True)

        # 加载现有反馈
        self.feedbacks = self._load_feedbacks()

    def _load_feedbacks(self) -> List[Dict[str, Any]]:
        """加载现有反馈"""
        if self.feedback_path.exists():
            try:
                with open(self.feedback_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[WARNING] 加载反馈失败: {e}")
                return []

        return []

    def add_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """
        添加反馈

        Args:
            feedback_data: 反馈数据

        Returns:
            是否成功
        """
        try:
            # 添加时间戳
            if 'timestamp' not in feedback_data:
                feedback_data['timestamp'] = datetime.now().isoformat()

            # 添加ID
            feedback_data['id'] = len(self.feedbacks) + 1

            # 添加到列表
            self.feedbacks.append(feedback_data)

            # 保存到文件
            self._save_feedbacks()

            print(f"[OK] 反馈已添加 (ID: {feedback_data['id']})")
            return True

        except Exception as e:
            print(f"[ERROR] 添加反馈失败: {e}")
            return False

    def _save_feedbacks(self):
        """保存反馈到文件"""
        try:
            with open(self.feedback_path, "w", encoding="utf-8") as f:
                json.dump(self.feedbacks, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"[ERROR] 保存反馈失败: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计数据
        """
        if not self.feedbacks:
            return {
                "total_feedbacks": 0,
                "average_rating": 0,
                "use_cases": {},
                "feature_popularity": {},
                "recent_feedbacks": []
            }

        # 计算平均评分
        ratings = [f.get('rating', 0) for f in self.feedbacks if f.get('rating')]
        average_rating = sum(ratings) / len(ratings) if ratings else 0

        # 统计使用场景
        use_cases = Counter([f.get('use_case', 'unknown') for f in self.feedbacks])

        # 统计功能受欢迎程度
        feature_popularity = Counter()
        for f in self.feedbacks:
            for feature in f.get('features', []):
                feature_popularity[feature] += 1

        # 最近反馈（最新10条）
        recent_feedbacks = sorted(
            self.feedbacks,
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )[:10]

        return {
            "total_feedbacks": len(self.feedbacks),
            "average_rating": round(average_rating, 2),
            "use_cases": dict(use_cases),
            "feature_popularity": dict(feature_popularity),
            "recent_feedbacks": recent_feedbacks,
            "rating_distribution": self._get_rating_distribution()
        }

    def _get_rating_distribution(self) -> Dict[int, int]:
        """获取评分分布"""
        distribution = {i: 0 for i in range(1, 6)}

        for f in self.feedbacks:
            rating = f.get('rating', 0)
            if 1 <= rating <= 5:
                distribution[rating] += 1

        return distribution

    def generate_report(
        self,
        output_path: str = "C:\\ssh\\.openclaw\\xiaoyao-memory-system\\data\\feedback_report.md"
    ) -> str:
        """
        生成反馈报告

        Args:
            output_path: 输出路径

        Returns:
            报告内容
        """
        stats = self.get_statistics()

        report = f"""# 用户反馈报告

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**总反馈数:** {stats['total_feedbacks']}
**平均评分:** {stats['average_rating']}/5 ⭐

---

## 📊 评分分布

"""

        for rating, count in stats['rating_distribution'].items():
            percentage = (count / stats['total_feedbacks'] * 100) if stats['total_feedbacks'] > 0 else 0
            bar = '█' * int(percentage / 5)
            report += f"{rating}星: {bar} {count} ({percentage:.1f}%)\n"

        report += "\n## 🎯 使用场景分布\n\n"

        if stats['use_cases']:
            for use_case, count in stats['use_cases'].items():
                report += f"- **{use_case}**: {count}\n"
        else:
            report += "暂无数据\n"

        report += "\n## ⭐ 功能受欢迎程度\n\n"

        if stats['feature_popularity']:
            # 按受欢迎程度排序
            sorted_features = sorted(
                stats['feature_popularity'].items(),
                key=lambda x: x[1],
                reverse=True
            )

            for feature, count in sorted_features:
                feature_name = self._get_feature_name(feature)
                report += f"- **{feature_name}**: {count} 人选择\n"
        else:
            report += "暂无数据\n"

        report += "\n## 💬 最近反馈\n\n"

        if stats['recent_feedbacks']:
            for i, feedback in enumerate(stats['recent_feedbacks'][:5], 1):
                report += f"### 反馈 #{i}\n\n"
                report += f"**用户:** {feedback.get('name', '匿名')}\n"
                report += f"**评分:** {feedback.get('rating', 0)}/5\n"
                report += f"**时间:** {feedback.get('timestamp', 'N/A')}\n"

                if feedback.get('feedback'):
                    report += f"**内容:** {feedback['feedback'][:200]}...\n"

                report += "\n"
        else:
            report += "暂无数据\n"

        report += "\n## 💡 改进建议摘要\n\n"

        # 收集改进建议
        improvements = []
        for f in self.feedbacks:
            if f.get('improvements'):
                improvements.append(f['improvements'])

        if improvements:
            report += f"共收到 {len(improvements)} 条改进建议：\n\n"
            for i, improvement in enumerate(improvements[:10], 1):
                report += f"{i}. {improvement[:150]}...\n"
        else:
            report += "暂无改进建议\n"

        # 保存报告
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"[OK] 报告已生成: {output_path}")

        return report

    def _get_feature_name(self, feature_code: str) -> str:
        """获取功能名称"""
        feature_names = {
            'entity_extraction': '实体提取',
            'graph_viz': '图谱可视化',
            'semantic_search': '语义搜索',
            'wal_protocol': 'WAL协议',
            'performance': '高性能',
            'ease_of_use': '易用性'
        }
        return feature_names.get(feature_code, feature_code)

    def export_feedbacks(
        self,
        output_path: str = "C:\\ssh\\.openclaw\\xiaoyao-memory-system\\data\\feedbacks_export.json"
    ):
        """
        导出反馈数据

        Args:
            output_path: 输出路径
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.feedbacks, f, ensure_ascii=False, indent=2)

        print(f"[OK] 反馈已导出: {output_path}")

    def analyze_trends(self) -> Dict[str, Any]:
        """
        分析趋势

        Returns:
            趋势分析数据
        """
        if not self.feedbacks:
            return {}

        # 按月份统计
        monthly_counts = Counter()

        for feedback in self.feedbacks:
            timestamp = feedback.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    month_key = dt.strftime('%Y-%m')
                    monthly_counts[month_key] += 1
                except:
                    pass

        # 计算满意度趋势
        monthly_ratings = {}

        for feedback in self.feedbacks:
            timestamp = feedback.get('timestamp', '')
            rating = feedback.get('rating', 0)

            if timestamp and rating:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    month_key = dt.strftime('%Y-%m')

                    if month_key not in monthly_ratings:
                        monthly_ratings[month_key] = []

                    monthly_ratings[month_key].append(rating)
                except:
                    pass

        monthly_avg_ratings = {
            month: sum(ratings) / len(ratings)
            for month, ratings in monthly_ratings.items()
        }

        return {
            "monthly_counts": dict(monthly_counts),
            "monthly_avg_ratings": monthly_avg_ratings
        }


# 测试代码
if __name__ == "__main__":
    import sys

    print("="*70)
    print("用户反馈收集系统测试")
    print("="*70)

    # 创建收集器
    collector = FeedbackCollector()

    # 添加测试反馈
    test_feedback = {
        "name": "测试用户",
        "email": "test@example.com",
        "rating": 5,
        "features": ["entity_extraction", "graph_viz"],
        "use_case": "research",
        "feedback": "系统非常棒！实体提取功能很强大。",
        "improvements": "希望添加更多可视化选项"
    }

    print("\n[测试1] 添加反馈...")
    if collector.add_feedback(test_feedback):
        print("[OK] 反馈添加成功")
    else:
        print("[ERROR] 反馈添加失败")

    # 获取统计
    print("\n[测试2] 获取统计信息...")
    stats = collector.get_statistics()
    print(f"[OK] 总反馈数: {stats['total_feedbacks']}")
    print(f"[OK] 平均评分: {stats['average_rating']}")

    # 生成报告
    print("\n[测试3] 生成报告...")
    collector.generate_report()

    # 分析趋势
    print("\n[测试4] 分析趋势...")
    trends = collector.analyze_trends()
    print(f"[OK] 月度统计: {len(trends.get('monthly_counts', {}))} 个月")

    print("\n" + "="*70)
    print("测试完成！")
    print("="*70)
