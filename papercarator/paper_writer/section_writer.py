"""章节写作器 - 生成论文各章节内容。

当前版本坚持规则驱动，不依赖额外 LLM。
重点针对数学建模类题目输出更贴近模型类型的论文内容。
"""

from typing import Any

from loguru import logger


class SectionWriter:
    """论文章节写作器。"""

    DOMAIN_LABELS = {
        "computer_vision": "计算机视觉",
        "signal_processing": "信号处理",
        "communication": "通信系统",
        "mechanical_engineering": "机械工程",
        "materials_science": "材料科学",
        "energy_systems": "能源系统",
        "transportation": "交通运输",
        "medical": "医疗健康",
        "finance": "金融分析",
        "environmental": "环境系统",
        "general": "综合建模",
    }

    MODEL_PROFILES = {
        "equation_system": {
            "label": "方程组模型",
            "focus": "多个变量之间的平衡关系与约束一致性",
            "workflow": "建立变量关系、整理等式约束、采用符号或数值方法求解",
            "evaluation": "残差大小、解的唯一性与变量解释性",
            "benchmarks": ["解析求解", "数值根搜索", "迭代修正法"],
            "future": "可进一步扩展到非线性、多层级耦合方程组。",
        },
        "optimization": {
            "label": "优化模型",
            "focus": "目标函数、约束条件与资源配置效率",
            "workflow": "定义决策变量、构造目标函数、描述约束并执行优化求解",
            "evaluation": "目标值、迭代效率、约束满足度与稳定性",
            "benchmarks": ["梯度法", "二次规划", "启发式搜索"],
            "future": "可进一步扩展到多目标、鲁棒与动态优化场景。",
        },
        "differential": {
            "label": "微分方程模型",
            "focus": "系统状态随时间或空间的连续演化规律",
            "workflow": "建立状态方程、设置初始条件、进行数值积分与轨迹分析",
            "evaluation": "轨迹合理性、相图特征、数值稳定性与收敛精度",
            "benchmarks": ["解析近似", "数值积分", "相空间分析"],
            "future": "可进一步扩展到偏微分与多尺度动力系统。",
        },
        "statistical": {
            "label": "统计回归模型",
            "focus": "数据关系识别、参数估计与预测解释",
            "workflow": "整理样本数据、建立回归关系、估计参数并分析误差",
            "evaluation": "拟合优度、均方误差、残差结构与泛化稳定性",
            "benchmarks": ["最小二乘法", "稳健回归", "正则化回归"],
            "future": "可进一步扩展到非线性统计与时间序列建模。",
        },
        "network_flow": {
            "label": "网络流模型",
            "focus": "节点连接关系、路径代价与流量分配效率",
            "workflow": "构建网络节点与边、定义容量或代价、执行路径或流量求解",
            "evaluation": "路径代价、流量可行性、边利用率与网络解释性",
            "benchmarks": ["最短路径法", "最大流方法", "最小费用流"],
            "future": "可进一步扩展到更大规模的动态交通与物流网络。",
        },
        "time_series": {
            "label": "时间序列模型",
            "focus": "趋势项、季节项与未来时刻预测能力",
            "workflow": "整理时序观测、拟合趋势与季节结构、执行未来预测",
            "evaluation": "预测误差、趋势拟合质量、季节性解释与稳定性",
            "benchmarks": ["移动平均", "指数平滑", "季节趋势回归"],
            "future": "可进一步扩展到 ARIMA、状态空间与多变量时序模型。",
        },
        "multi_objective": {
            "label": "多目标优化模型",
            "focus": "多个目标之间的权衡关系与帕累托最优结构",
            "workflow": "构造多个目标函数、设计权重或偏好、搜索折中解与帕累托前沿",
            "evaluation": "目标权衡效果、帕累托分布、折中解稳定性与可解释性",
            "benchmarks": ["加权和法", "约束法", "帕累托前沿采样"],
            "future": "可进一步扩展到 NSGA-II 等更复杂的多目标算法。",
        },
        "pde": {
            "label": "偏微分方程模型",
            "focus": "时空分布、边界条件与连续介质演化规律",
            "workflow": "建立 PDE、设置边界与初值、采用离散化方法进行数值求解",
            "evaluation": "数值稳定性、场分布合理性、边界满足情况与时空解释性",
            "benchmarks": ["有限差分法", "有限元法", "解析近似"],
            "future": "可进一步扩展到更高维、更复杂边界条件的 PDE 系统。",
        },
        "queueing": {
            "label": "排队系统模型",
            "focus": "到达率、服务率、等待时间与系统利用率",
            "workflow": "定义到达过程与服务过程、构造稳态指标、分析排队性能",
            "evaluation": "平均等待时间、平均队长、系统稳定性与服务效率",
            "benchmarks": ["M/M/1", "M/M/c", "离散事件仿真"],
            "future": "可进一步扩展到更复杂的优先级排队与网络排队系统。",
        },
        "markov_chain": {
            "label": "马尔可夫链模型",
            "focus": "状态转移、稳态分布与长期演化规律",
            "workflow": "构造转移矩阵、定义初始分布、分析多步转移与稳态行为",
            "evaluation": "分布收敛性、稳态误差、状态解释性与转移合理性",
            "benchmarks": ["矩阵幂法", "稳态分布求解", "状态转移图分析"],
            "future": "可进一步扩展到隐马尔可夫模型与连续时间马尔可夫过程。",
        },
        "game_theory": {
            "label": "博弈论模型",
            "focus": "参与者策略、收益矩阵、均衡结构与最优响应关系",
            "workflow": "构造策略集合与收益矩阵、分析最优响应、求解均衡或博弈值",
            "evaluation": "均衡稳定性、策略概率分布、博弈值与最优响应差距",
            "benchmarks": ["纯策略枚举", "混合策略线性规划", "最小最大分析"],
            "future": "可进一步扩展到非零和博弈、演化博弈与多主体动态博弈。",
        },
        "control_theory": {
            "label": "控制理论模型",
            "focus": "反馈结构、控制参数、系统稳定性与动态响应特征",
            "workflow": "建立闭环系统方程、设置控制参数、分析特征根与阶跃响应",
            "evaluation": "稳定性、阻尼比、自然频率、响应速度与超调风险",
            "benchmarks": ["Routh-Hurwitz 判据", "PID 参数整定", "阶跃响应分析"],
            "future": "可进一步扩展到状态空间控制、LQR 与鲁棒控制系统。",
        },
        "clustering": {
            "label": "聚类分析模型",
            "focus": "样本分布、簇中心、类内距离与无监督结构发现",
            "workflow": "构造样本特征空间、初始化聚类中心、迭代分配样本并更新中心",
            "evaluation": "簇内误差、聚类中心稳定性、类别分离度与可解释性",
            "benchmarks": ["K-means", "层次聚类", "密度聚类"],
            "future": "可进一步扩展到自动选簇、谱聚类与高维特征降维分析。",
        },
        "bayesian": {
            "label": "贝叶斯推断模型",
            "focus": "先验分布、似然函数、后验推断与不确定性量化",
            "workflow": "设定先验、构造似然、执行共轭更新或采样、分析后验分布",
            "evaluation": "后验均值、可信区间、先验敏感性与收敛诊断",
            "benchmarks": ["Beta-Binomial共轭", "正态-逆Gamma", "MCMC采样"],
            "future": "可进一步扩展到变分推断与层次贝叶斯模型。",
        },
        "graph_theory": {
            "label": "图论模型",
            "focus": "节点连通性、路径优化、最小生成树与网络结构分析",
            "workflow": "构建邻接矩阵、选择图算法、分析结构特征与优化路径",
            "evaluation": "最小代价、连通分量、图密度与算法复杂度",
            "benchmarks": ["Kruskal MST", "Dijkstra最短路径", "Ford-Fulkerson最大流"],
            "future": "可进一步扩展到有向图、加权超图与动态网络分析。",
        },
        "fuzzy_logic": {
            "label": "模糊逻辑模型",
            "focus": "隶属函数、模糊规则、推理机制与去模糊化",
            "workflow": "定义模糊集合与隶属函数、建立规则库、执行模糊推理、去模糊化",
            "evaluation": "去模糊化输出、规则覆盖度、隶属函数合理性与推理一致性",
            "benchmarks": ["Mamdani推理", "Sugeno推理", "重心法去模糊化"],
            "future": "可进一步扩展到自适应模糊系统与神经模糊混合模型。",
        },
    }

    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm
        logger.info(f"初始化 SectionWriter (LLM={use_llm})")

    def write_all_sections(
        self,
        topic: str,
        plan: dict[str, Any],
        math_model: dict[str, Any],
        solution: dict[str, Any],
    ) -> dict[str, str]:
        """生成所有章节内容。"""
        logger.info("开始生成论文章节...")

        sections = {
            "title": topic,
            "abstract": self._write_abstract(topic, plan, math_model, solution),
            "introduction": self._write_introduction(topic, plan, math_model),
            "related_work": self._write_related_work(topic, plan, math_model),
            "methodology": self._write_methodology(topic, plan, math_model, solution),
            "experiments": self._write_experiments(topic, plan, math_model, solution),
            "results": self._write_results(topic, plan, math_model, solution),
            "conclusion": self._write_conclusion(topic, plan, math_model, solution),
            "references": self._write_references(topic, math_model),
        }

        logger.info(f"论文章节生成完成 - 共 {len(sections)} 个章节")
        return sections

    def _write_abstract(
        self,
        topic: str,
        plan: dict[str, Any],
        math_model: dict[str, Any],
        solution: dict[str, Any],
    ) -> str:
        """生成摘要。"""
        profile = self._get_model_profile(math_model)
        domain = self._humanize_domain(plan.get("application_domain", "general"))
        methods = [self._latex_text(method) for method in (plan.get("research_methods") or ["mathematical_modeling"])]
        keywords = [self._latex_text(keyword) for keyword in (plan.get("keywords") or ["数学建模", "数值分析"])]
        model_name = math_model.get("name", profile["label"])
        success = solution.get("success", False)
        message = solution.get("message", "完成了求解分析")
        value_summary = self._format_value_sentence(solution.get("values", {}))

        abstract = f"""本文围绕\\textbf{{{topic}}}展开研究，面向{domain}场景构建了一套可执行的数学建模求解流程。

针对问题中涉及的{profile["focus"]}，本文基于{', '.join(methods)}进行题目分析与形式化描述，
并建立了\\textbf{{{model_name}}}。在求解阶段，围绕“{profile["workflow"]}”这一主线完成模型计算与结果验证。

实验与分析结果表明，模型求解{'成功' if success else '完成但仍需进一步校验'}，
{message}。{value_summary}
从结果表现看，该方法能够较好地支撑题目求解、结果解释与论文表达的一体化输出。

本文工作说明，针对数学建模类题目，规则驱动的自动化流程能够稳定完成
“题目分析-建模求解-图表生成-论文写作”闭环，为后续扩展到更复杂题目提供了基础。

\\textbf{{关键词：}}{', '.join(keywords)}"""

        return abstract

    def _write_introduction(
        self,
        topic: str,
        plan: dict[str, Any],
        math_model: dict[str, Any],
    ) -> str:
        """生成引言。"""
        domain = self._humanize_domain(plan.get("application_domain", "general"))
        methods = [self._latex_text(method) for method in (plan.get("research_methods") or ["mathematical_modeling"])]
        profile = self._get_model_profile(math_model)

        background = {
            "计算机视觉": "随着数据规模与算力条件的提升，复杂系统中可量化问题越来越适合通过数学建模方式进行分析与优化。",
            "交通运输": "交通网络中的资源配置、路径选择与系统调度问题具有典型的建模与求解需求。",
            "能源系统": "能源系统普遍具有多变量耦合、强约束和高稳定性要求，是数学建模的重要应用场景。",
            "环境系统": "环境治理问题往往同时包含动态变化、约束协调和效果评估，适合通过模型化手段进行系统分析。",
            "综合建模": "数学建模能够将复杂问题抽象为可分析、可求解、可验证的形式化对象，是连接问题理解与决策支持的重要桥梁。",
        }.get(domain, f"{domain}中的复杂决策与分析任务通常需要借助数学建模方法来提升问题刻画能力与求解效率。")

        return f"""\\subsection{{研究背景}}

{background}
对于\\textbf{{{topic}}}这类题目，研究者需要同时完成问题抽象、模型建立、求解验证和结果表达，
这使其成为检验一体化自动论文生成流程能力的典型场景。

\\subsection{{问题挑战}}

围绕该题目，主要挑战体现在以下几个方面：

\\begin{{itemize}}
    \\item 需要将自然语言题目转换为可执行的数学对象，并明确变量、目标与约束；
    \\item 需要根据题目特征选择合理的{profile["label"]}表达方式；
    \\item 需要在有限信息下完成求解、可视化和结果解释，保证输出具有基本学术结构；
    \\item 需要让最终论文内容与模型类型一致，而不是停留在通用模板层面。
\\end{{itemize}}

\\subsection{{本文思路}}

本文采用规则驱动的自动化流程完成研究：
首先根据题目进行分析，提取关键词、研究方法和应用领域；
随后利用{', '.join(methods)}建立模型并完成求解；
最后将数值结果、图表和文字说明组织为完整论文。

\\subsection{{本文贡献}}

本文的主要贡献包括：

\\begin{{enumerate}}
    \\item 构建了面向数学建模题目的自动化论文生成流程；
    \\item 将{profile["label"]}与论文章节生成逻辑对齐，提升内容一致性；
    \\item 实现了从模型结果到图表、再到 LaTeX 论文的统一输出；
    \\item 为后续扩展到更复杂题目类型提供了明确的维护边界与验证基础。
\\end{{enumerate}}"""

    def _write_related_work(
        self,
        topic: str,
        plan: dict[str, Any],
        math_model: dict[str, Any],
    ) -> str:
        """生成相关工作。"""
        profile = self._get_model_profile(math_model)
        methods = [self._latex_text(method) for method in (plan.get("research_methods") or ["mathematical_modeling"])]
        benchmarks = [self._latex_text(benchmark) for benchmark in profile["benchmarks"]]

        return f"""\\subsection{{建模研究脉络}}

围绕{topic}这类问题，现有研究通常遵循“问题抽象-模型构建-算法求解-结果验证”的基本路径。
在具体方法上，研究者常结合{', '.join(methods)}与领域先验知识，
将实际问题转化为{profile["label"]}或与其相近的形式。

\\subsection{{典型方法}}

现有相关方法可概括为以下几类：

\\begin{{itemize}}
    \\item \\textbf{{解析或结构化方法}}：强调问题结构利用，适合规模较小且约束清晰的任务；
    \\item \\textbf{{数值求解方法}}：通过迭代或离散化处理复杂模型，是自动化系统中的主流路线；
    \\item \\textbf{{混合方法}}：结合规则、经验和数值策略，在精度与效率之间寻求平衡。
\\end{{itemize}}

对于当前模型类型，常见对比思路包括：{', '.join(benchmarks)}。

\\subsection{{现有工作的不足}}

尽管已有方法能够覆盖部分问题，但在自动化论文生成场景中仍存在不足：

\\begin{{itemize}}
    \\item 模型生成与论文写作往往割裂，导致结果解释与建模形式不一致；
    \\item 通用模板容易忽略不同模型类型的叙事差异；
    \\item 可视化和文字说明缺少对求解结果的联动，难以形成完整研究闭环。
\\end{{itemize}}

\\subsection{{本文定位}}

本文不追求覆盖所有开放域题目，而是聚焦数学建模类任务，
强调在有限规则体系内实现稳定的一体化输出，
即让模型、结果、图表与章节内容保持同一叙事主线。"""

    def _write_methodology(
        self,
        topic: str,
        plan: dict[str, Any],
        math_model: dict[str, Any],
        solution: dict[str, Any],
    ) -> str:
        """生成方法章节。"""
        profile = self._get_model_profile(math_model)
        model_name = math_model.get("name", profile["label"])
        model_type = self._latex_text(math_model.get("model_type", "equation_system"))
        equations = math_model.get("equations") or []
        objective = math_model.get("objective")
        objective_type = math_model.get("objective_type", "minimize")
        methods = [self._latex_text(method) for method in (plan.get("research_methods") or ["mathematical_modeling"])]

        sections = [
            "\\subsection{问题形式化}",
            f"针对{topic}，本文首先明确研究对象、决策变量与约束条件，",
            f"并将问题抽象为{profile['label']}。该模型重点关注{profile['focus']}。",
            "",
            "\\subsection{模型构建}",
            f"本文建立的核心模型为\\textbf{{{model_name}}}，模型类型为\\textbf{{{model_type}}}。",
            f"在建模过程中，主要采用{', '.join(methods)}完成变量关系整理与求解路径设计。",
        ]

        if equations:
            sections.extend([
                "",
                "模型中的主要数学表达如下：",
                "",
                "\\begin{align}",
                self._format_equation_block(equations),
                "\\end{align}",
            ])

        if objective:
            direction = "最小化" if objective_type == "minimize" else "最大化"
            sections.extend([
                "",
                "\\paragraph{目标函数}",
                f"对于该模型，核心优化目标可写为 {direction}：",
                "",
                "\\begin{equation}",
                objective,
                "\\end{equation}",
            ])

        sections.extend([
            "",
            "\\subsection{求解策略}",
            f"围绕“{profile['workflow']}”这一思路，本文采用分阶段求解策略：",
            "\\begin{enumerate}",
            "    \\item 根据题目和模型结构确定求解变量与初始条件；",
            "    \\item 调用与模型类型匹配的数值或符号求解器得到候选解；",
            "    \\item 对求解结果进行有效性检查，并提取可用于论文展示的统计量；",
            "    \\item 将结果进一步传递给图表生成与 LaTeX 写作模块，完成一体化输出。",
            "\\end{enumerate}",
            "",
            "\\subsection{评价指标}",
            f"本文重点关注{profile['evaluation']}，并以此评估自动化流程输出的有效性与稳定性。",
        ])

        if solution.get("statistics"):
            sections.extend([
                "",
                "\\paragraph{求解器返回统计}",
                self._summarize_statistics(solution["statistics"]),
            ])

        return "\n".join(sections)

    def _write_experiments(
        self,
        topic: str,
        plan: dict[str, Any],
        math_model: dict[str, Any],
        solution: dict[str, Any],
    ) -> str:
        """生成实验章节。"""
        profile = self._get_model_profile(math_model)
        model_type = self._latex_text(math_model.get("model_type", "equation_system"))

        return f"""\\subsection{{实验目标}}

实验部分重点验证以下问题：

\\begin{{itemize}}
    \\item 当前自动化流程是否能够稳定完成{profile["label"]}的建模与求解；
    \\item 输出结果是否能够支撑论文中的表格、图形与文字分析；
    \\item 针对{model_type}类型题目，论文内容是否与模型特征保持一致。
\\end{{itemize}}

\\subsection{{实验环境}}

\\begin{{table}}[H]
\\centering
\\caption{{实验环境配置}}
\\begin{{tabular}}{{ll}}
\\toprule
\\textbf{{配置项}} & \\textbf{{说明}} \\\\
\\midrule
Python & 3.12 \\\\
数学计算 & NumPy / SciPy / SymPy \\\\
图表生成 & Matplotlib \\\\
论文编译 & XeLaTeX \\\\
工作模式 & 规则驱动，无额外 LLM 依赖 \\\\
\\bottomrule
\\end{{tabular}}
\\end{{table}}

\\subsection{{实验流程}}

实验按照以下步骤执行：

\\begin{{enumerate}}
    \\item 输入题目并完成规则化分析；
    \\item 自动构建{profile["label"]}并调用对应求解器；
    \\item 根据求解结果生成二维图表和可用的三维示意；
    \\item 组织摘要、方法、实验、结果和结论，输出 LaTeX 论文与 PDF。
\\end{{enumerate}}

\\subsection{{评价维度}}

实验从以下维度评估该 skill 的表现：

\\begin{{itemize}}
    \\item 建模合理性：模型类型与题目是否匹配；
    \\item 求解有效性：是否获得可解释的结果或统计量；
    \\item 输出完整性：图表、LaTeX 与 PDF 是否能够联动生成；
    \\item 文本一致性：论文章节是否围绕同一模型叙事展开。
\\end{{itemize}}"""

    def _write_results(
        self,
        topic: str,
        plan: dict[str, Any],
        math_model: dict[str, Any],
        solution: dict[str, Any],
    ) -> str:
        """生成结果章节。"""
        profile = self._get_model_profile(math_model)
        values = solution.get("values", {})
        statistics = solution.get("statistics", {})
        success = solution.get("success", False)
        message = solution.get("message", "未返回额外说明")
        numerical = solution.get("numerical_data", {})

        blocks = [
            "\\subsection{求解结果概览}",
            f"针对{topic}，系统{'成功' if success else '未完全成功'}完成了{profile['label']}求解。",
            f"求解器返回信息为：{message}",
        ]

        if values:
            blocks.extend([
                "",
                "\\begin{table}[H]",
                "\\centering",
                "\\caption{关键变量结果}",
                "\\begin{tabular}{lc}",
                "\\toprule",
                "\\textbf{变量} & \\textbf{数值} \\\\",
                "\\midrule",
                self._format_value_rows(values),
                "\\bottomrule",
                "\\end{tabular}",
                "\\end{table}",
            ])

        if statistics:
            blocks.extend([
                "",
                "\\begin{table}[H]",
                "\\centering",
                "\\caption{统计指标汇总}",
                "\\begin{tabular}{lc}",
                "\\toprule",
                "\\textbf{指标} & \\textbf{数值} \\\\",
                "\\midrule",
                self._format_statistics_rows(statistics),
                "\\bottomrule",
                "\\end{tabular}",
                "\\end{table}",
            ])

        blocks.extend([
            "",
            "\\subsection{结果分析}",
            f"从结果可以看出，该流程已经能够围绕{profile['label']}形成完整的自动化闭环。",
            f"分析重点落在{profile['evaluation']}，这与当前模型类型保持一致。",
        ])

        if numerical:
            available_keys = ", ".join(sorted(numerical.keys()))
            blocks.append(
                f"数值结果中已返回时序或样本级数据（字段包括：{self._latex_text(available_keys)}），可直接用于二维图表或三维示意生成。"
            )

        blocks.extend([
            "",
            "\\subsection{能力边界}",
            "需要说明的是，当前结果更适合数学建模类题目，",
            "即变量、约束、状态演化或统计关系能够被明确抽象的场景。",
            "对于开放域研究题目、强文献依赖题目或工业级 CAD 设计任务，",
            "仍需要进一步扩展模型库、检索能力与专业几何建模能力。",
        ])

        return "\n".join(blocks)

    def _write_conclusion(
        self,
        topic: str,
        plan: dict[str, Any],
        math_model: dict[str, Any],
        solution: dict[str, Any],
    ) -> str:
        """生成结论。"""
        profile = self._get_model_profile(math_model)
        domain = self._humanize_domain(plan.get("application_domain", "general"))
        success = solution.get("success", False)

        return f"""\\subsection{{工作总结}}

本文围绕\\textbf{{{topic}}}完成了从题目分析、数学建模、结果可视化到论文生成的自动化流程验证。
在当前版本中，系统能够稳定处理{profile["label"]}相关题目，
并在{domain}等场景下输出结构完整的学术论文草稿。

\\subsection{{主要结论}}

本文得到以下结论：

\\begin{{itemize}}
    \\item 当前规则驱动流程已经能够支撑数学建模类题目的端到端演示与验证；
    \\item 论文内容与模型类型的一致性比早期通用模板方案更强；
    \\item 求解器、图表和 LaTeX 输出已形成稳定联动，求解{'成功并可复用' if success else '流程打通但仍需进一步增强鲁棒性'}；
    \\item 项目更适合作为“给 LLM 使用的数学建模 skill”，而不是宣称覆盖任意开放域题目。
\\end{{itemize}}

\\subsection{{后续方向}}

在保持无额外 LLM 依赖的前提下，后续可继续沿以下方向改进：

\\begin{{enumerate}}
    \\item 扩展更多数学模型类型与更细粒度的题目路由规则；
    \\item 加强结果后处理，使图表、表格和叙事内容更加贴近真实解的特征；
    \\item 继续提升三维建模表达能力，区分数学可视化与工程 CAD 建模边界；
    \\item 在进入更广泛题目类型之前，先完善数学建模专用场景的验证基线。
\\end{{enumerate}}

\\subsection{{维护结论}}

当前版本已经具备较好的维护基础：
核心链路可运行、测试可回归、输出边界可描述。
下一阶段的重点不是盲目追求“任何题目全自动”，而是继续把数学建模专用能力做深做稳。
{profile["future"]}"""

    def _write_references(self, topic: str, math_model: dict[str, Any]) -> str:
        """生成参考文献 - 按模型类型动态生成。"""
        model_type = math_model.get("model_type", "equation_system")

        common_refs = [
            "\\bibitem{ref1} Boyd S, Vandenberghe L. Convex Optimization. Cambridge University Press, 2004.",
            "\\bibitem{ref2} Nocedal J, Wright S J. Numerical Optimization. Springer, 2nd edition, 2006.",
            "\\bibitem{ref3} Quarteroni A, Sacco R, Saleri F. Numerical Mathematics. Springer, 2007.",
        ]

        model_refs = {
            "equation_system": [
                "\\bibitem{ref4} Kelley C T. Iterative Methods for Linear and Nonlinear Equations. SIAM, 1995.",
                "\\bibitem{ref5} Ortega J M, Rheinboldt W C. Iterative Solution of Nonlinear Equations in Several Variables. SIAM, 2000.",
            ],
            "optimization": [
                "\\bibitem{ref4} Bertsekas D P. Nonlinear Programming. Athena Scientific, 1999.",
                "\\bibitem{ref5} Fletcher R. Practical Methods of Optimization. Wiley, 1987.",
            ],
            "multi_objective": [
                "\\bibitem{ref4} Deb K. Multi-Objective Optimization Using Evolutionary Algorithms. Wiley, 2001.",
                "\\bibitem{ref5} Coello Coello C A. Evolutionary Algorithms for Solving Multi-Objective Problems. Springer, 2007.",
            ],
            "differential": [
                "\\bibitem{ref4} Butcher J C. Numerical Methods for Ordinary Differential Equations. Wiley, 2008.",
                "\\bibitem{ref5} Hairer E, Wanner G. Solving Ordinary Differential Equations II. Springer, 1996.",
            ],
            "pde": [
                "\\bibitem{ref4} LeVeque R J. Finite Difference Methods for Ordinary and Partial Differential Equations. SIAM, 2007.",
                "\\bibitem{ref5} Strikwerda J C. Finite Difference Schemes and Partial Differential Equations. SIAM, 2004.",
            ],
            "statistical": [
                "\\bibitem{ref4} Hastie T, Tibshirani R, Friedman J. The Elements of Statistical Learning. Springer, 2009.",
                "\\bibitem{ref5} Draper N R, Smith H. Applied Regression Analysis. Wiley, 1998.",
            ],
            "network_flow": [
                "\\bibitem{ref4} Ahuja R K, Magnanti T L, Orlin J B. Network Flows. Prentice Hall, 1993.",
                "\\bibitem{ref5} Cormen T H, et al. Introduction to Algorithms. MIT Press, 3rd edition, 2009.",
            ],
            "time_series": [
                "\\bibitem{ref4} Box G E P, Jenkins G M, Reinsel G C. Time Series Analysis. Wiley, 2015.",
                "\\bibitem{ref5} Hyndman R J, Athanasopoulos G. Forecasting: Principles and Practice. OTexts, 2018.",
            ],
            "queueing": [
                "\\bibitem{ref4} Gross D, Harris C M. Fundamentals of Queueing Theory. Wiley, 1998.",
                "\\bibitem{ref5} Kleinrock L. Queueing Systems, Volume 1: Theory. Wiley, 1975.",
            ],
            "markov_chain": [
                "\\bibitem{ref4} Norris J R. Markov Chains. Cambridge University Press, 1997.",
                "\\bibitem{ref5} Bremaud P. Markov Chains: Gibbs Fields, Monte Carlo Simulation, and Queues. Springer, 2020.",
            ],
            "game_theory": [
                "\\bibitem{ref4} Osborne M J, Rubinstein A. A Course in Game Theory. MIT Press, 1994.",
                "\\bibitem{ref5} Fudenberg D, Tirole J. Game Theory. MIT Press, 1991.",
            ],
            "control_theory": [
                "\\bibitem{ref4} Ogata K. Modern Control Engineering. Prentice Hall, 5th edition, 2010.",
                "\\bibitem{ref5} Franklin G F, Powell J D, Emami-Naeini A. Feedback Control of Dynamic Systems. Pearson, 2014.",
            ],
            "clustering": [
                "\\bibitem{ref4} Hastie T, Tibshirani R, Friedman J. The Elements of Statistical Learning. Springer, 2009.",
                "\\bibitem{ref5} Jain A K. Data clustering: 50 years beyond K-means. Pattern Recognition Letters, 2010.",
            ],
        }

        refs = common_refs + model_refs.get(model_type, [])
        refs.append(f"\\bibitem{{ref-topic}} PaperCarator project artifacts for topic: {topic}.")
        return "\n\n".join(refs)

    def _get_model_profile(self, math_model: dict[str, Any]) -> dict[str, str]:
        """根据模型类型获取写作画像。"""
        model_type = math_model.get("model_type", "equation_system")
        return self.MODEL_PROFILES.get(model_type, self.MODEL_PROFILES["equation_system"])

    def _humanize_domain(self, domain: str) -> str:
        """将领域标识转换为可读文本。"""
        return self.DOMAIN_LABELS.get(domain, domain.replace("_", " "))

    def _format_value_sentence(self, values: dict[str, Any]) -> str:
        """将少量求解变量格式化为摘要句子。"""
        if not values:
            return "当前结果主要以模型结构和求解流程验证为主。"

        formatted = []
        for key, value in list(values.items())[:3]:
            if isinstance(value, float):
                formatted.append(f"\\texttt{{{self._latex_text(key)}}}={value:.4f}")
            else:
                formatted.append(
                    f"\\texttt{{{self._latex_text(key)}}}={self._latex_text(str(value))}"
                )

        return f"关键结果包括 {', '.join(formatted)}。"

    def _format_equation_block(self, equations: list[Any]) -> str:
        """将模型方程整理为 align 环境内容。"""
        lines = []
        for index, equation in enumerate(equations[:5], start=1):
            if hasattr(equation, "lhs") and hasattr(equation, "rhs"):
                line = f"{equation.lhs} = {equation.rhs}"
            else:
                line = str(equation)
                if line.startswith("Eq(") and line.endswith(")"):
                    content = line[3:-1]
                    lhs, rhs = content.split(",", 1)
                    line = f"{lhs.strip()} = {rhs.strip()}"

            line = line.replace(">=", "\\geq ").replace("<=", "\\leq ")
            suffix = r" \\" if index < min(len(equations), 5) else ""
            lines.append(f"    {line}{suffix}")
        return "\n".join(lines)

    def _format_value_rows(self, values: dict[str, Any]) -> str:
        """生成结果表格行。"""
        rows = []
        for key, value in values.items():
            if isinstance(value, float):
                rendered = f"{value:.6f}"
            else:
                rendered = self._latex_text(str(value))
            rows.append(f"\\texttt{{{self._latex_text(key)}}} & {rendered} \\\\")
        return "\n".join(rows)

    def _format_statistics_rows(self, statistics: dict[str, Any]) -> str:
        """生成统计表格行。"""
        rows = []
        for key, value in statistics.items():
            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    rendered = f"{nested_value:.6f}" if isinstance(nested_value, float) else self._latex_text(str(nested_value))
                    label = self._latex_text(f"{key}-{nested_key}")
                    rows.append(f"{label} & {rendered} \\\\")
            else:
                rendered = f"{value:.6f}" if isinstance(value, float) else self._latex_text(str(value))
                rows.append(f"{self._latex_text(key)} & {rendered} \\\\")
        return "\n".join(rows)

    def _summarize_statistics(self, statistics: dict[str, Any]) -> str:
        """将统计信息转为简短叙述。"""
        parts = []
        for key, value in statistics.items():
            if isinstance(value, dict):
                nested = ", ".join(
                    f"{self._latex_text(nested_key)}={nested_value:.4f}" if isinstance(nested_value, float)
                    else f"{self._latex_text(nested_key)}={self._latex_text(str(nested_value))}"
                    for nested_key, nested_value in value.items()
                )
                parts.append(f"{self._latex_text(key)}({nested})")
            else:
                if isinstance(value, float):
                    parts.append(f"{self._latex_text(key)}={value:.4f}")
                else:
                    parts.append(f"{self._latex_text(key)}={self._latex_text(str(value))}")
        return "求解器返回的关键统计量包括：" + "；".join(parts) + "。"

    def _latex_text(self, value: str) -> str:
        """转义普通文本中的 LaTeX 特殊字符。"""
        return (
            value.replace("\\", "\\textbackslash ")
            .replace("_", "\\_")
            .replace("%", "\\%")
            .replace("&", "\\&")
            .replace("#", "\\#")
        )
