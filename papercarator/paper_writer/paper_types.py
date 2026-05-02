"""论文类型系统 - 定义不同论文类型的结构和规则。

支持: 毕业论文、期刊论文、会议论文、综述论文、实验论文、案例研究。
"""

from typing import Any
from loguru import logger


class PaperType:
    """论文类型基类。"""

    TYPES = {
        "thesis": {
            "name": "毕业论文",
            "description": "本科/硕士/博士学位论文",
            "sections": [
                ("abstract_zh", "中文摘要", True),
                ("abstract_en", "英文摘要", True),
                ("toc", "目录", True),
                ("chapter1_introduction", "第一章 绪论", True),
                ("chapter2_literature", "第二章 文献综述", True),
                ("chapter3_methodology", "第三章 研究方法", True),
                ("chapter4_results", "第四章 结果与分析", True),
                ("chapter5_discussion", "第五章 讨论", True),
                ("chapter6_conclusion", "第六章 结论与展望", True),
                ("references", "参考文献", True),
                ("appendix", "附录", False),
                ("acknowledgements", "致谢", False),
            ],
            "min_pages": 30,
            "max_pages": 100,
            "min_words": 15000,
            "max_words": 50000,
            "citation_format": "gbt7714",
            "language": "zh",
            "requires_real_data": True,
            "requires_literature_review": True,
            "requires_methodology": True,
            "abstract_words": "500-800字",
            "keywords_count": "5-8个",
        },
        "journal": {
            "name": "期刊论文",
            "description": "SCI/EI/核心期刊论文",
            "sections": [
                ("abstract", "摘要", True),
                ("keywords", "关键词", True),
                ("introduction", "引言", True),
                ("methods", "方法", True),
                ("results", "结果", True),
                ("discussion", "讨论", True),
                ("conclusion", "结论", True),
                ("references", "参考文献", True),
            ],
            "min_pages": 6,
            "max_pages": 15,
            "min_words": 4000,
            "max_words": 8000,
            "citation_format": "apa",
            "language": "en",
            "requires_real_data": True,
            "requires_literature_review": True,
            "requires_methodology": True,
            "abstract_words": "200-300 words",
            "keywords_count": "4-6个",
        },
        "conference": {
            "name": "会议论文",
            "description": "学术会议论文",
            "sections": [
                ("abstract", "摘要", True),
                ("introduction", "引言", True),
                ("methodology", "方法", True),
                ("experiments", "实验", True),
                ("results", "结果", True),
                ("conclusion", "结论", True),
                ("references", "参考文献", True),
            ],
            "min_pages": 4,
            "max_pages": 8,
            "min_words": 2000,
            "max_words": 5000,
            "citation_format": "ieee",
            "language": "en",
            "requires_real_data": True,
            "requires_literature_review": False,
            "requires_methodology": True,
            "abstract_words": "150-200 words",
            "keywords_count": "3-5个",
        },
        "review": {
            "name": "综述论文",
            "description": "文献综述/系统综述",
            "sections": [
                ("abstract", "摘要", True),
                ("introduction", "引言", True),
                ("background", "背景", True),
                ("literature_review", "文献综述", True),
                ("taxonomy", "分类体系", True),
                ("comparison", "方法对比", True),
                ("future_directions", "未来方向", True),
                ("conclusion", "结论", True),
                ("references", "参考文献", True),
            ],
            "min_pages": 10,
            "max_pages": 30,
            "min_words": 8000,
            "max_words": 20000,
            "citation_format": "apa",
            "language": "zh",
            "requires_real_data": False,
            "requires_literature_review": True,
            "requires_methodology": False,
            "abstract_words": "300-500字",
            "keywords_count": "5-8个",
        },
        "experiment": {
            "name": "实验论文",
            "description": "实验研究论文",
            "sections": [
                ("abstract", "摘要", True),
                ("introduction", "引言", True),
                ("materials_methods", "材料与方法", True),
                ("results", "结果", True),
                ("discussion", "讨论", True),
                ("conclusion", "结论", True),
                ("references", "参考文献", True),
            ],
            "min_pages": 8,
            "max_pages": 20,
            "min_words": 5000,
            "max_words": 12000,
            "citation_format": "apa",
            "language": "en",
            "requires_real_data": True,
            "requires_literature_review": True,
            "requires_methodology": True,
            "abstract_words": "250-350 words",
            "keywords_count": "4-6个",
        },
        "case_study": {
            "name": "案例研究",
            "description": "案例分析/调研报告",
            "sections": [
                ("abstract", "摘要", True),
                ("introduction", "引言", True),
                ("background", "背景介绍", True),
                ("case_description", "案例描述", True),
                ("analysis", "分析", True),
                ("findings", "发现", True),
                ("conclusion", "结论", True),
                ("references", "参考文献", True),
            ],
            "min_pages": 6,
            "max_pages": 15,
            "min_words": 4000,
            "max_words": 10000,
            "citation_format": "apa",
            "language": "zh",
            "requires_real_data": True,
            "requires_literature_review": False,
            "requires_methodology": False,
            "abstract_words": "200-400字",
            "keywords_count": "3-5个",
        },
        "math_modeling": {
            "name": "数学建模论文",
            "description": "数学建模竞赛/研究论文",
            "sections": [
                ("abstract", "摘要", True),
                ("introduction", "引言", True),
                ("problem_analysis", "问题分析", True),
                ("model_assumptions", "模型假设", True),
                ("model_construction", "模型构建", True),
                ("model_solution", "模型求解", True),
                ("model_evaluation", "模型评价", True),
                ("conclusion", "结论", True),
                ("references", "参考文献", True),
            ],
            "min_pages": 15,
            "max_pages": 30,
            "min_words": 8000,
            "max_words": 20000,
            "citation_format": "gbt7714",
            "language": "zh",
            "requires_real_data": True,
            "requires_literature_review": False,
            "requires_methodology": True,
            "abstract_words": "300-500字",
            "keywords_count": "4-6个",
        },
    }

    @classmethod
    def get_type(cls, type_id: str) -> dict[str, Any]:
        """获取论文类型配置。"""
        if type_id not in cls.TYPES:
            logger.warning(f"未知论文类型: {type_id}，使用 journal")
            type_id = "journal"
        return cls.TYPES[type_id]

    @classmethod
    def list_types(cls) -> list[dict[str, str]]:
        """列出所有论文类型。"""
        return [
            {"id": k, "name": v["name"], "description": v["description"]}
            for k, v in cls.TYPES.items()
        ]

    @classmethod
    def get_sections(cls, type_id: str) -> list[tuple[str, str, bool]]:
        """获取论文类型的章节列表。"""
        return cls.get_type(type_id)["sections"]

    @classmethod
    def detect_type(cls, topic: str, user_hint: str = None) -> str:
        """根据题目和用户提示推断论文类型。"""
        if user_hint:
            hint_lower = user_hint.lower()
            for key in cls.TYPES:
                if key in hint_lower or cls.TYPES[key]["name"] in user_hint:
                    return key

        topic_lower = topic.lower()

        # 综述关键词
        if any(w in topic_lower for w in ["综述", "survey", "review", "回顾", "系统综述"]):
            return "review"

        # 数学建模关键词
        if any(w in topic_lower for w in ["建模", "优化", "排队", "博弈", "微分方程", "modeling"]):
            return "math_modeling"

        # 实验关键词
        if any(w in topic_lower for w in ["实验", "experiment", "测试", "测量", "验证"]):
            return "experiment"

        # 案例研究关键词
        if any(w in topic_lower for w in ["案例", "case study", "调研", "分析报告"]):
            return "case_study"

        # 毕业论文关键词
        if any(w in topic_lower for w in ["毕业论文", "毕业设计", "学位论文", "毕业"]):
            return "thesis"

        # 默认：期刊论文
        return "journal"
