"""论文质量自动评分器。

对生成的论文进行多维度自动评分，输出质量报告。
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from loguru import logger


@dataclass
class QualityReport:
    """质量评分报告。"""
    total_score: float = 0.0  # 0-100
    dimensions: dict[str, float] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


class PaperQualityScorer:
    """论文质量自动评分器。"""

    WEIGHTS = {
        "structure": 0.15,      # 结构完整性
        "content_depth": 0.20,  # 内容深度
        "math_rigor": 0.20,     # 数学严谨性
        "visualization": 0.10,  # 可视化质量
        "references": 0.10,     # 参考文献
        "language": 0.15,       # 语言质量
        "consistency": 0.10,    # 内容一致性
    }

    def score(self, tex_content: str, charts: list[Path],
              model_type: str = "") -> QualityReport:
        """对论文进行多维度评分。"""
        report = QualityReport()

        scores = {
            "structure": self._score_structure(tex_content),
            "content_depth": self._score_content_depth(tex_content),
            "math_rigor": self._score_math_rigor(tex_content, model_type),
            "visualization": self._score_visualization(charts),
            "references": self._score_references(tex_content),
            "language": self._score_language(tex_content),
            "consistency": self._score_consistency(tex_content, model_type),
        }

        report.dimensions = scores
        report.total_score = sum(
            scores[dim] * self.WEIGHTS[dim] for dim in scores
        )

        # 生成建议
        for dim, score in scores.items():
            if score < 60:
                report.suggestions.append(
                    f"{dim} 维度得分较低 ({score:.0f})，建议重点改进"
                )

        logger.info(f"论文质量评分: {report.total_score:.1f}/100")
        return report

    def _score_structure(self, tex: str) -> float:
        """结构完整性评分。"""
        score = 0.0
        required = [
            ("abstract", r"\\begin\{abstract\}"),
            ("introduction", r"\\section\{引言\}|\\section\{Introduction\}"),
            ("methodology", r"\\section\{方法\}|\\section\{Methodology\}"),
            ("results", r"\\section\{结果|\\section\{Results"),
            ("conclusion", r"\\section\{结论\}|\\section\{Conclusion\}"),
            ("references", r"\\begin\{thebibliography\}"),
            ("figures", r"\\begin\{figure\}"),
            ("tables", r"\\begin\{table\}"),
        ]
        for name, pattern in required:
            if re.search(pattern, tex):
                score += 12.5
        return min(score, 100)

    def _score_content_depth(self, tex: str) -> float:
        """内容深度评分。"""
        score = 0.0
        # 字数
        word_count = len(tex)
        if word_count > 3000:
            score += 30
        elif word_count > 1500:
            score += 20
        else:
            score += 10

        # 数学公式数量
        equations = len(re.findall(r"\\begin\{(equation|align|gather)", tex))
        score += min(equations * 8, 30)

        # 子节数量
        subsections = len(re.findall(r"\\subsection\{", tex))
        score += min(subsections * 5, 20)

        # 列表/枚举
        lists = len(re.findall(r"\\begin\{(itemize|enumerate)", tex))
        score += min(lists * 4, 20)

        return min(score, 100)

    def _score_math_rigor(self, tex: str, model_type: str) -> float:
        """数学严谨性评分。"""
        score = 0.0
        # 数学环境
        math_envs = len(re.findall(r"\\begin\{(equation|align|gather|array)", tex))
        score += min(math_envs * 10, 40)

        # 变量定义
        definitions = len(re.findall(r"\\text\{.*?\}|\\mathrm\{.*?\}", tex))
        score += min(definitions * 2, 20)

        # 数值结果表格
        result_tables = len(re.findall(r"\\begin\{table\}", tex))
        score += min(result_tables * 10, 20)

        # 模型名称匹配
        if model_type and model_type in tex:
            score += 20

        return min(score, 100)

    def _score_visualization(self, charts: list[Path]) -> float:
        """可视化质量评分。"""
        if not charts:
            return 0
        score = 0.0
        n_charts = len(charts)
        score += min(n_charts * 25, 75)  # 最多75分
        # 检查文件大小（非空图表）
        for chart in charts:
            if chart.exists() and chart.stat().st_size > 10000:
                score += 5
        return min(score, 100)

    def _score_references(self, tex: str) -> float:
        """参考文献评分。"""
        bibitems = re.findall(r"\\bibitem\{", tex)
        n_refs = len(bibitems)
        if n_refs >= 8:
            return 100
        elif n_refs >= 5:
            return 80
        elif n_refs >= 3:
            return 60
        else:
            return 30

    def _score_language(self, tex: str) -> float:
        """语言质量评分（启发式检查）。"""
        score = 70  # 基础分

        # 检查是否有LaTeX错误标记
        if "\\textbackslash" in tex:
            score -= 10
        if "???" in tex:
            score -= 15

        # 检查段落长度均匀性
        paragraphs = [p.strip() for p in tex.split("\n\n") if p.strip()]
        if paragraphs:
            avg_len = sum(len(p) for p in paragraphs) / len(paragraphs)
            if avg_len < 50:
                score -= 10  # 段落太短

        # 检查连接词使用
        connectors = ["因此", "然而", "此外", "首先", "其次", "最后", "综上"]
        connector_count = sum(1 for c in connectors if c in tex)
        score += min(connector_count * 3, 15)

        return max(min(score, 100), 0)

    def _score_consistency(self, tex: str, model_type: str) -> float:
        """内容一致性评分。"""
        score = 60  # 基础分

        # 模型类型在正文中被提及
        if model_type:
            type_mentions = tex.count(model_type)
            score += min(type_mentions * 5, 20)

        # 标题和摘要一致性
        title_match = re.search(r"\\title\{(.+?)\}", tex)
        abstract_match = re.search(r"\\begin\{abstract\}(.+?)\\end\{abstract\}", tex, re.DOTALL)
        if title_match and abstract_match:
            title_words = set(title_match.group(1))
            abstract_text = abstract_match.group(1)
            overlap = sum(1 for w in title_words if w in abstract_text and len(w) > 1)
            score += min(overlap * 2, 20)

        return min(score, 100)
