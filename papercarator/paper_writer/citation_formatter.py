"""引用格式化器 - 支持 GB/T 7714、APA、IEEE 等引用格式。"""

from typing import Any
from loguru import logger


class CitationFormatter:
    """引用格式化器。"""

    FORMATS = {
        "gbt7714": {
            "name": "GB/T 7714",
            "description": "中国国家标准",
            "example": "张三, 李四. 论文标题[J]. 期刊名, 2024, 10(2): 100-110.",
        },
        "apa": {
            "name": "APA 7th",
            "description": "美国心理学会格式",
            "example": "Zhang, S., & Li, S. (2024). Paper title. Journal Name, 10(2), 100-110.",
        },
        "ieee": {
            "name": "IEEE",
            "description": "电气电子工程师学会格式",
            "example": "S. Zhang and S. Li, \"Paper title,\" Journal Name, vol. 10, no. 2, pp. 100-110, 2024.",
        },
        "chicago": {
            "name": "Chicago",
            "description": "芝加哥格式",
            "example": "Zhang, San, and Si Li. \"Paper Title.\" Journal Name 10, no. 2 (2024): 100-110.",
        },
        "mla": {
            "name": "MLA",
            "description": "现代语言协会格式",
            "example": "Zhang, San, and Si Li. \"Paper Title.\" Journal Name, vol. 10, no. 2, 2024, pp. 100-110.",
        },
    }

    def format_citation(self, paper: dict[str, Any], fmt: str = "gbt7714") -> str:
        """格式化单条引用。"""
        formatter = getattr(self, "_format_" + fmt, self._format_gbt7714)
        return formatter(paper)

    def format_bibliography(self, papers, fmt: str = "gbt7714") -> str:
        """格式化参考文献列表。

        接受两种输入：
        - list[dict]: 从文献搜索API返回的论文列表
        - str: 已经是LaTeX \\bibitem格式的字符串，直接包装

        返回 LaTeX thebibliography 环境内的内容。
        """
        if isinstance(papers, str):
            # 已经是 \\bibitem 格式，包裹在 thebibliography 环境中
            return f"\\begin{{thebibliography}}{{99}}\n{papers}\n\\end{{thebibliography}}"

        entries = []
        for i, paper in enumerate(papers, 1):
            entry = self.format_citation(paper, fmt)
            if fmt in ("gbt7714", "ieee"):
                entry = f"[{i}] {entry}"
            entries.append(entry)
        body = "\n\n".join(entries)
        return f"\\begin{{thebibliography}}{{99}}\n{body}\n\\end{{thebibliography}}"

    def _format_gbt7714(self, paper: dict) -> str:
        """GB/T 7714 格式。"""
        authors = paper.get("authors", "Unknown")
        title = paper.get("title", "Unknown")
        journal = paper.get("venue", "")
        year = paper.get("year", "")
        doi = paper.get("doi", "")

        parts = ["{}. {}".format(authors, title)]
        if journal:
            parts[0] += "[J]. {}".format(journal)
        if year:
            parts[0] += ", {}".format(year)
        parts[0] += "."
        if doi:
            parts[0] += " DOI: {}".format(doi)
        return parts[0]

    def _format_apa(self, paper: dict) -> str:
        """APA 7th 格式。"""
        authors = paper.get("authors", "Unknown")
        title = paper.get("title", "Unknown")
        journal = paper.get("venue", "")
        year = paper.get("year", "")
        doi = paper.get("doi", "")

        entry = "{} ({}). {}.".format(authors, year, title)
        if journal:
            entry += " {}.".format(journal)
        if doi:
            entry += " https://doi.org/{}".format(doi)
        return entry

    def _format_ieee(self, paper: dict) -> str:
        """IEEE 格式。"""
        authors = paper.get("authors", "Unknown")
        title = paper.get("title", "Unknown")
        journal = paper.get("venue", "")
        year = paper.get("year", "")
        return '{}, "{}," {} {}.'.format(authors, title, journal, year)

    def _format_chicago(self, paper: dict) -> str:
        authors = paper.get("authors", "Unknown")
        title = paper.get("title", "Unknown")
        journal = paper.get("venue", "")
        year = paper.get("year", "")
        return '{}. "{}." {} ({}).'.format(authors, title, journal, year)

    def _format_mla(self, paper: dict) -> str:
        authors = paper.get("authors", "Unknown")
        title = paper.get("title", "Unknown")
        journal = paper.get("venue", "")
        year = paper.get("year", "")
        return '{}. "{}." {}, {}.'.format(authors, title, journal, year)

    @classmethod
    def list_formats(cls) -> list[dict[str, str]]:
        """列出所有支持的引用格式。"""
        return [
            {"id": k, "name": v["name"], "description": v["description"], "example": v["example"]}
            for k, v in cls.FORMATS.items()
        ]
