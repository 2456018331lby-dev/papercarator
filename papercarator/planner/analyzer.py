"""题目分析器 - 解析论文题目，提取关键信息"""

import json
from dataclasses import dataclass, field
from typing import Any

from loguru import logger


@dataclass
class TopicAnalysis:
    """题目分析结果"""
    topic: str
    # 研究主题
    research_subject: str = ""
    # 研究方法
    research_methods: list[str] = field(default_factory=list)
    # 应用领域
    application_domain: str = ""
    # 关键词
    keywords: list[str] = field(default_factory=list)
    # 论文类型: theoretical | experimental | review | modeling
    paper_type: str = "modeling"
    # 需要的数学工具
    required_math_tools: list[str] = field(default_factory=list)
    # 需要的可视化类型
    required_visualizations: list[str] = field(default_factory=list)
    # 建议的章节结构
    suggested_sections: list[str] = field(default_factory=list)
    # 难度评估: easy | medium | hard
    difficulty: str = "medium"
    # 元数据
    metadata: dict[str, Any] = field(default_factory=dict)


class TopicAnalyzer:
    """论文题目分析器

    分析论文题目，提取关键要素，为后续模块提供指导。
    """

    # 常见研究方法关键词映射
    METHOD_KEYWORDS = {
        "深度学习": ["neural_network", "deep_learning"],
        "机器学习": ["machine_learning", "supervised_learning"],
        "优化": ["optimization", "gradient_descent"],
        "多目标": ["multi_objective_optimization", "pareto_analysis"],
        "帕累托": ["multi_objective_optimization", "pareto_analysis"],
        "排队": ["queueing_analysis", "stochastic_service"],
        "服务台": ["queueing_analysis", "stochastic_service"],
        "马尔可夫": ["markov_chain_analysis", "state_transition"],
        "转移概率": ["markov_chain_analysis", "state_transition"],
        "仿真": ["simulation", "monte_carlo"],
        "建模": ["mathematical_modeling", "differential_equations"],
        "数值": ["numerical_analysis", "finite_element"],
        "统计": ["statistics", "regression"],
        "预测": ["time_series_analysis", "forecasting"],
        "时间序列": ["time_series_analysis", "forecasting"],
        "偏微分": ["pde_modeling", "finite_difference"],
        "热传导": ["pde_modeling", "finite_difference"],
        "扩散方程": ["pde_modeling", "finite_difference"],
        "网络": ["network_optimization", "graph_analysis"],
        "物流": ["network_flow", "resource_allocation"],
        "图像": ["image_processing", "computer_vision"],
        "控制": ["control_theory", "pid_control"],
    }

    # 应用领域关键词映射
    DOMAIN_KEYWORDS = {
        "图像": "computer_vision",
        "信号": "signal_processing",
        "通信": "communication",
        "机械": "mechanical_engineering",
        "材料": "materials_science",
        "能源": "energy_systems",
        "交通": "transportation",
        "物流": "transportation",
        "供应链": "transportation",
        "排队": "transportation",
        "服务": "transportation",
        "医疗": "medical",
        "金融": "finance",
        "环境": "environmental",
    }

    PAPER_TYPE_RULES = [
        ("review", ["综述", "回顾", "survey", "review"]),
        ("queueing", ["排队", "服务台", "排队系统", "到达率", "queueing", "queueing system", "service queue"]),
        ("markov_chain", ["马尔可夫", "状态转移", "转移概率", "markov chain", "state transition"]),
        ("multi_objective", ["多目标", "帕累托", "pareto", "multi-objective"]),
        ("pde", ["偏微分", "热方程", "扩散方程", "二维热传导", "pde", "partial differential"]),
        ("network_flow", ["最短路径", "网络流", "物流网络", "配送网络", "路径规划", "network flow", "shortest path"]),
        ("time_series", ["时间序列", "时序", "预测", "forecast", "demand forecasting", "trend"]),
        ("optimization", ["优化", "optimization", "最优", "调度", "分配", "资源配置"]),
        ("differential", ["微分方程", "differential", "热传导", "扩散", "波动"]),
        ("equation_system", ["方程组", "equation system", "线性方程组", "非线性方程组"]),
        ("experimental", ["实验", "experimental", "empirical"]),
        ("theoretical", ["理论", "theoretical", "证明"]),
    ]

    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm
        logger.info(f"初始化 TopicAnalyzer (LLM={use_llm})")

    def analyze(self, topic: str) -> dict[str, Any]:
        """分析论文题目

        Args:
            topic: 论文题目

        Returns:
            分析结果字典
        """
        logger.info(f"分析题目: {topic}")

        analysis = TopicAnalysis(topic=topic)

        # 基于规则的分析
        self._extract_keywords(analysis)
        self._identify_methods(analysis)
        self._identify_domain(analysis)
        self._determine_paper_type(analysis)
        self._suggest_math_tools(analysis)
        self._suggest_visualizations(analysis)
        self._suggest_sections(analysis)
        self._assess_difficulty(analysis)

        # 如果使用LLM，进行增强分析
        if self.use_llm:
            analysis = self._llm_enhance(analysis)

        result = {
            "topic": analysis.topic,
            "research_subject": analysis.research_subject,
            "research_methods": analysis.research_methods,
            "application_domain": analysis.application_domain,
            "keywords": analysis.keywords,
            "paper_type": analysis.paper_type,
            "required_math_tools": analysis.required_math_tools,
            "required_visualizations": analysis.required_visualizations,
            "suggested_sections": analysis.suggested_sections,
            "difficulty": analysis.difficulty,
            "metadata": analysis.metadata,
        }

        logger.info(f"题目分析完成 - 类型: {analysis.paper_type}, 难度: {analysis.difficulty}")
        return result

    def _extract_keywords(self, analysis: TopicAnalysis) -> None:
        """提取关键词"""
        # 简单分词提取（实际项目中可使用jieba等中文分词库）
        topic = analysis.topic
        # 基于常见学术词汇提取
        common_keywords = [
            "算法", "模型", "系统", "方法", "优化", "设计", "分析",
            "基于", "研究", "应用", "实现", "改进", "创新",
        ]
        keywords = [kw for kw in common_keywords if kw in topic]
        # 添加题目中的名词性短语（简化版）
        analysis.keywords = list(set(keywords))
        if not analysis.keywords:
            analysis.keywords = ["建模", "分析"]

    def _identify_methods(self, analysis: TopicAnalysis) -> None:
        """识别研究方法"""
        topic = analysis.topic
        methods = []
        for keyword, method_list in self.METHOD_KEYWORDS.items():
            if keyword in topic:
                methods.extend(method_list)
        analysis.research_methods = list(set(methods)) if methods else ["mathematical_modeling"]

    def _identify_domain(self, analysis: TopicAnalysis) -> None:
        """识别应用领域"""
        topic = analysis.topic
        for keyword, domain in self.DOMAIN_KEYWORDS.items():
            if keyword in topic:
                analysis.application_domain = domain
                return
        analysis.application_domain = "general"

    def _determine_paper_type(self, analysis: TopicAnalysis) -> None:
        """确定论文类型"""
        topic = analysis.topic
        for paper_type, keywords in self.PAPER_TYPE_RULES:
            if any(keyword in topic for keyword in keywords):
                analysis.paper_type = paper_type
                return

        analysis.paper_type = "modeling"

    def _suggest_math_tools(self, analysis: TopicAnalysis) -> None:
        """建议数学工具"""
        tools = set()
        # 基于论文类型
        if analysis.paper_type == "modeling":
            tools.update(["sympy", "scipy", "numpy"])
        if analysis.paper_type == "optimization":
            tools.update(["scipy.optimize", "cvxpy"])
        if analysis.paper_type == "multi_objective":
            tools.update(["scipy.optimize", "numpy"])
        if analysis.paper_type == "pde":
            tools.update(["numpy", "scipy", "finite_difference"])
        if analysis.paper_type == "queueing":
            tools.update(["numpy", "statistics"])
        if analysis.paper_type == "markov_chain":
            tools.update(["numpy", "linear_algebra"])
        if analysis.paper_type == "network_flow":
            tools.update(["numpy", "scipy.optimize"])
        if analysis.paper_type == "time_series":
            tools.update(["numpy", "scipy", "statistics"])
        # 基于方法
        for method in analysis.research_methods:
            if "neural" in method:
                tools.add("pytorch/tensorflow")
            if "optimization" in method:
                tools.add("scipy.optimize")
            if "simulation" in method:
                tools.add("monte_carlo")
            if "forecast" in method or "time_series" in method:
                tools.add("numpy")
        analysis.required_math_tools = list(tools) if tools else ["sympy", "numpy"]

    def _suggest_visualizations(self, analysis: TopicAnalysis) -> None:
        """建议可视化类型"""
        viz = ["line_chart", "bar_chart", "scatter_plot"]
        if "3D" in analysis.topic or "三维" in analysis.topic:
            viz.append("3d_model")
        if analysis.paper_type == "network_flow":
            viz.extend(["network_graph", "3d_model"])
        if analysis.paper_type == "time_series":
            viz.extend(["forecast_curve", "heatmap"])
        if analysis.paper_type == "multi_objective":
            viz.extend(["pareto_front", "3d_model"])
        if analysis.paper_type == "pde":
            viz.extend(["heatmap", "surface_plot", "3d_model"])
        if analysis.paper_type == "queueing":
            viz.extend(["queue_curve", "heatmap"])
        if analysis.paper_type == "markov_chain":
            viz.extend(["state_graph", "heatmap", "3d_model"])
        if any(m in analysis.research_methods for m in ["neural_network", "deep_learning"]):
            viz.append("network_graph")
        if analysis.application_domain == "mechanical_engineering":
            viz.append("cad_model")
        analysis.required_visualizations = list(dict.fromkeys(viz))

    def _suggest_sections(self, analysis: TopicAnalysis) -> None:
        """建议论文章节"""
        base_sections = [
            "abstract",
            "introduction",
            "related_work",
            "methodology",
            "experiments",
            "results",
            "conclusion",
            "references",
        ]
        if analysis.paper_type == "review":
            base_sections = [
                "abstract",
                "introduction",
                "background",
                "literature_review",
                "discussion",
                "future_work",
                "conclusion",
                "references",
            ]
        analysis.suggested_sections = base_sections

    def _assess_difficulty(self, analysis: TopicAnalysis) -> None:
        """评估难度"""
        topic = analysis.topic
        hard_indicators = ["深度学习", "神经网络", "多目标优化", "非线性", "偏微分方程"]
        easy_indicators = ["综述", "介绍", "概述", "survey"]
        if any(w in topic for w in hard_indicators):
            analysis.difficulty = "hard"
        elif any(w in topic for w in easy_indicators):
            analysis.difficulty = "easy"
        else:
            analysis.difficulty = "medium"

    def _llm_enhance(self, analysis: TopicAnalysis) -> TopicAnalysis:
        """使用LLM增强分析结果"""
        # TODO: 集成LLM API进行更智能的分析
        logger.info("LLM增强分析 (待实现)")
        return analysis
