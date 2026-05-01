"""中文学术用语增强器。

将口语化/通用表述替换为更规范的学术用语，提升论文语言质量。
"""

import re
from typing import Any

from loguru import logger


class AcademicEnhancer:
    """中文学术用语增强器。"""

    # 口语 -> 学术用语替换表
    REPLACEMENTS = [
        # 动词
        ("用了", "采用"),
        ("做了", "完成了"),
        ("得到了", "获得了"),
        ("看出来", "可以看出"),
        ("说清楚", "明确阐述"),
        ("弄明白", "深入理解"),
        ("搞定", "解决"),
        ("跑通", "成功运行"),
        # 连接词
        ("然后呢", "随后"),
        ("但是", "然而"),
        ("所以", "因此"),
        ("而且", "此外"),
        ("不过", "然而"),
        ("就是说", "即"),
        ("总的来说", "综上所述"),
        ("其实", "实际上"),
        # 形容词
        ("特别好", "显著优于"),
        ("很差", "表现不佳"),
        ("很厉害", "具有显著优势"),
        ("差不多", "相近"),
        # 量化
        ("大概", "约"),
        ("差不多", "约为"),
        ("可能", "有较大可能"),
    ]

    # 学术句式模板
    SENTENCE_TEMPLATES = {
        "result": [
            "实验结果表明，{content}",
            "数值分析结果显示，{content}",
            "求解结果表明，{content}",
        ],
        "comparison": [
            "与{baseline}相比，{method}在{metric}方面提升了{value}",
            "相较{baseline}，{method}表现出更优的{metric}性能",
        ],
        "contribution": [
            "本文的主要贡献包括：{items}",
            "本文工作的创新点体现在以下几个方面：{items}",
        ],
    }

    def enhance(self, text: str) -> str:
        """增强文本的学术性。

        Args:
            text: 原始文本

        Returns:
            增强后的文本
        """
        enhanced = text

        # 应用替换表
        for colloquial, academic in self.REPLACEMENTS:
            enhanced = enhanced.replace(colloquial, academic)

        # 检查并标记可能需要改进的表述
        weak_starters = ["我觉得", "我认为", "我们发现"]
        for starter in weak_starters:
            if starter in enhanced:
                logger.warning(f"检测到弱学术表述: '{starter}'，建议改写")

        return enhanced

    def enhance_sections(self, sections: dict[str, str]) -> dict[str, str]:
        """增强所有章节的学术用语。"""
        enhanced = {}
        for key, content in sections.items():
            if key in ("title", "references"):
                enhanced[key] = content
            else:
                enhanced[key] = self.enhance(content)
        return enhanced
