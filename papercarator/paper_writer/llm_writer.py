"""LLM 论文写作引擎 - 调用大模型逐章节深度写作。

与 SectionWriter 的规则模板不同，本模块调用真实 LLM API，
根据完整的数学建模上下文生成有深度的学术内容。

用法:
    writer = LLMWriter(api_base="https://hiapi.work/v1", api_key="...", model="...")
    sections = writer.write_all_sections(topic, plan, math_model, solution)

环境变量 (自动读取):
    HIAPI_API_KEY / OPENAI_API_KEY / OPENAI_API_BASE
"""

import json
import os
import time
from typing import Any, Optional

import httpx
from loguru import logger


class LLMWriter:
    """调用 LLM 逐章节深度写作。"""

    def __init__(self, api_base: str = None, api_key: str = None,
                 model: str = None, timeout: int = 120):
        self.api_base = api_base or os.environ.get(
            "HIAPI_API_BASE",
            os.environ.get("OPENAI_API_BASE", "https://hiapi.work/v1")
        )
        self.api_key = api_key or os.environ.get(
            "HIAPI_API_KEY",
            os.environ.get("OPENAI_API_KEY", "")
        )
        self.model = model or "MiniMax-M2.7"
        self.timeout = timeout
        self._available = None
        logger.info(f"初始化 LLMWriter (model={self.model}, base={self.api_base[:30]}...)")

    def is_available(self) -> bool:
        """检查 LLM API 是否可用。"""
        if self._available is not None:
            return self._available
        try:
            resp = httpx.get(
                f"{self.api_base}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            self._available = resp.status_code == 200
        except Exception:
            self._available = False
        logger.info(f"LLM API 可用: {self._available}")
        return self._available

    def _call_llm(self, system_prompt: str, user_prompt: str,
                  temperature: float = 0.4, max_tokens: int = 2000) -> str:
        """调用 LLM API 生成文本。"""
        try:
            resp = httpx.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=self.timeout,
            )

            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                return content.strip()
            else:
                logger.warning(f"LLM API 返回 {resp.status_code}: {resp.text[:200]}")
                return ""

        except Exception as e:
            logger.warning(f"LLM 调用失败: {e}")
            return ""

    def write_all_sections(self, topic: str, plan: dict[str, Any],
                           math_model: dict[str, Any],
                           solution: dict[str, Any]) -> dict[str, str]:
        """调用 LLM 生成所有章节。根据论文类型调整章节结构和写作风格。"""
        if not self.is_available():
            logger.warning("LLM API 不可用，返回空（将由规则模板兜底）")
            return {}

        logger.info("开始 LLM 深度写作...")
        start = time.time()

        # Detect paper type from plan or metadata
        paper_type = plan.get("paper_type", "math_modeling")

        # Build research context
        context = self._build_context(topic, plan, math_model, solution)

        # System prompt tailored to paper type
        system = self._get_system_prompt(paper_type)

        sections = {}

        # Section tasks vary by paper type
        section_tasks = self._get_section_tasks(paper_type)

        for key, name, max_tokens in section_tasks:
            prompt = self._build_section_prompt(name, context, key, paper_type)
            logger.info(f"  LLM 生成: {name}...")
            content = self._call_llm(system, prompt, max_tokens=max_tokens)
            if content:
                content = self._clean_latex_content(content)
                sections[key] = content
                logger.info(f"  {name}: {len(content)} 字符")
            else:
                logger.warning(f"  {name}: LLM 生成失败，跳过")

        # References
        refs_prompt = self._build_section_prompt("参考文献", context, "references", paper_type)
        refs_content = self._call_llm(system, refs_prompt, max_tokens=1000)
        if refs_content:
            sections["references"] = self._clean_latex_content(refs_content)

        # Thesis-specific: English abstract
        if paper_type == "thesis":
            en_prompt = self._build_section_prompt("英文摘要", context, "abstract_en", paper_type)
            en_content = self._call_llm(system, en_prompt, max_tokens=600)
            if en_content:
                sections["abstract_en"] = self._clean_latex_content(en_content)

            ack_prompt = self._build_section_prompt("致谢", context, "acknowledgements", paper_type)
            ack_content = self._call_llm(system, ack_prompt, max_tokens=400)
            if ack_content:
                sections["acknowledgements"] = self._clean_latex_content(ack_content)

        elapsed = time.time() - start
        logger.info(f"LLM 写作完成: {len(sections)} 章节, 耗时 {elapsed:.1f}s")
        return sections

    def _get_system_prompt(self, paper_type: str = "math_modeling") -> str:
        """学术论文写作专家系统提示 - 根据论文类型调整。"""

        type_descriptions = {
            "thesis": "毕业论文（学位论文）写作专家。要求：结构完整、论证充分、每章有实质性内容、中文学术表达规范、有文献综述深度、有研究方法论。",
            "journal": "SCI/EI期刊论文写作专家。要求：精炼、逻辑严密、英文学术表达规范、创新点突出、实验结果可复现。",
            "conference": "学术会议论文写作专家。要求：简洁精炼、重点突出创新贡献、英文表达规范、篇幅控制严格。",
            "review": "文献综述论文写作专家。要求：覆盖面广、分类体系清晰、方法对比有深度、指出现有不足和未来方向。",
            "experiment": "实验研究论文写作专家。要求：实验设计严谨、变量控制清晰、结果分析透彻、讨论有深度。",
            "case_study": "案例研究论文写作专家。要求：案例描述详实、分析框架明确、发现有实践意义。",
            "math_modeling": "数学建模论文写作专家。要求：问题分析清晰、模型构建合理、求解过程完整、结果验证充分。",
        }

        desc = type_descriptions.get(paper_type, type_descriptions["math_modeling"])

        return f"""你是一位资深的{desc}

写作要求：
1. 使用规范的中文学术表达，避免口语化（毕业论文和中文期刊用中文，国际期刊/会议用英文）
2. 每个章节要有实质性内容，不能空洞或重复
3. 数学公式使用 LaTeX 格式（行内用 $...$，独立公式用 \\begin{{equation}}...\\end{{equation}}）
4. 结果分析要具体，引用实际数值
5. 相关工作要真实可信，不能编造文献
6. 方法描述要清晰说明建模思路、假设条件和求解策略
7. 不要使用 markdown 格式（如 #、**），直接输出 LaTeX 格式
8. 每个章节开头不需要写 \\section{{}} 或 \\chapter{{}}，由外层框架添加

输出格式：纯 LaTeX 内容，可直接嵌入论文。"""

    def _get_section_tasks(self, paper_type: str) -> list[tuple]:
        """根据论文类型返回章节任务列表 (key, name, max_tokens)。"""
        tasks = {
            "thesis": [
                ("abstract", "中文摘要", 800),
                ("introduction", "绪论", 1500),
                ("related_work", "文献综述", 2000),
                ("methodology", "研究方法", 2500),
                ("experiments", "实验设计", 1200),
                ("results", "结果与分析", 2000),
                ("discussion", "讨论", 1500),
                ("conclusion", "结论与展望", 1000),
            ],
            "journal": [
                ("abstract", "Abstract", 300),
                ("introduction", "Introduction", 800),
                ("methods", "Methods", 1200),
                ("results", "Results", 1000),
                ("discussion", "Discussion", 1200),
                ("conclusion", "Conclusion", 400),
            ],
            "conference": [
                ("abstract", "Abstract", 200),
                ("introduction", "Introduction", 600),
                ("methodology", "Methodology", 800),
                ("experiments", "Experiments", 600),
                ("results", "Results", 600),
                ("conclusion", "Conclusion", 300),
            ],
            "review": [
                ("abstract", "摘要", 500),
                ("introduction", "引言", 800),
                ("background", "背景", 1000),
                ("literature_review", "文献综述", 3000),
                ("comparison", "方法对比", 1500),
                ("future_directions", "未来方向", 800),
                ("conclusion", "结论", 400),
            ],
            "experiment": [
                ("abstract", "Abstract", 350),
                ("introduction", "Introduction", 800),
                ("materials_methods", "Materials and Methods", 1500),
                ("results", "Results", 1200),
                ("discussion", "Discussion", 1200),
                ("conclusion", "Conclusion", 400),
            ],
            "case_study": [
                ("abstract", "摘要", 400),
                ("introduction", "引言", 600),
                ("background", "背景介绍", 800),
                ("case_description", "案例描述", 1200),
                ("analysis", "分析", 1000),
                ("findings", "发现", 800),
                ("conclusion", "结论", 400),
            ],
            "math_modeling": [
                ("abstract", "摘要", 600),
                ("introduction", "引言", 1200),
                ("problem_analysis", "问题分析", 1000),
                ("model_assumptions", "模型假设", 600),
                ("model_construction", "模型构建", 1500),
                ("model_solution", "模型求解", 1200),
                ("model_evaluation", "模型评价", 800),
                ("conclusion", "结论", 600),
            ],
        }
        return tasks.get(paper_type, tasks["math_modeling"])

    def _build_context(self, topic: str, plan: dict, math_model: dict,
                       solution: dict) -> str:
        """构建完整的研究上下文。"""
        model_info = math_model if "model" not in math_model else math_model["model"]
        sol_info = math_model.get("solution", solution)

        # 关键数值结果
        values = sol_info.get("values", {})
        stats = sol_info.get("statistics", {})
        numerical = sol_info.get("numerical_data", {})
        equations = model_info.get("equations", [])
        parameters = model_info.get("parameters", {})
        metadata = model_info.get("metadata", {})

        values_str = "\n".join(f"  - {k} = {v}" for k, v in values.items()) if values else "  无"
        stats_str = "\n".join(f"  - {k} = {v}" for k, v in stats.items() if not isinstance(v, dict)) if stats else "  无"
        eq_str = "\n".join(f"  - {eq}" for eq in equations[:5]) if equations else "  无"
        params_str = "\n".join(f"  - {k} = {v}" for k, v in parameters.items()) if parameters else "  无"

        # 数值数据摘要
        data_summary = ""
        if numerical:
            for key, val in numerical.items():
                if isinstance(val, list) and len(val) > 0:
                    data_summary += f"  - {key}: {len(val)} 个数据点, 范围 [{min(val[:100]):.4f}, {max(val[:100]):.4f}]\n"

        context = f"""## 研究题目
{topic}

## 题目分析
- 论文类型: {plan.get('paper_type', '未知')}
- 研究方法: {', '.join(plan.get('research_methods', []))}
- 应用领域: {plan.get('application_domain', '未知')}
- 难度评估: {plan.get('difficulty', '未知')}
- 关键词: {', '.join(plan.get('keywords', []))}

## 数学模型
- 模型名称: {model_info.get('name', '未知')}
- 模型类型: {model_info.get('model_type', '未知')}
- 模型描述: {model_info.get('description', '无')}
- 方程:
{eq_str}
- 参数:
{params_str}

## 求解结果
- 成功: {sol_info.get('success', False)}
- 消息: {sol_info.get('message', '无')}
- 关键变量:
{values_str}
- 统计量:
{stats_str}

## 数值数据
{data_summary if data_summary else '  无数值数据\n'}

## 元数据
{json.dumps(metadata, ensure_ascii=False, indent=2)[:500]}
"""
        return context

    def _build_section_prompt(self, section_name: str, context: str,
                              section_key: str, paper_type: str = "math_modeling") -> str:
        """为特定章节构建写作提示。根据论文类型调整。"""
        # Add paper type hint to context
        type_hint = f"\n## 论文类型\n{paper_type}\n\n"
        # Paper type specific prompts
        is_thesis = paper_type == "thesis"
        is_english = paper_type in ("journal", "conference", "experiment")
        lang = "英文" if is_english else "中文"

        prompts = {
            "abstract": f"""请为以下论文撰写{lang}摘要（{('500-800字' if is_thesis else '200-300字')}）。

要求：
- 概述研究问题和背景
- 说明采用的方法和模型
- 列出关键数值结果（必须引用具体数字）
- 总结主要结论和意义
- 最后给出3-5个关键词
{type_hint}{context}""",

            "abstract_en": f"""Write an English abstract (200-300 words) for the following thesis.

Requirements:
- Summarize the research problem and background
- Describe the methodology used
- List key numerical results with specific numbers
- Conclude with main findings and significance
- Provide 3-5 keywords

{context}""",

            "introduction": f"""请为以下论文撰写{lang}{('绪论' if is_thesis else '引言')}（{'1500-2500字' if is_thesis else '800-1200字'}）。

要求：
- 研究背景：该领域的实际需求和研究意义（具体场景，不要泛泛而谈）
- 国内外研究现状：概述已有工作和不足
- 问题提出：现有方法的不足，为什么需要新方法
- 本文工作：明确说明做了什么、用了什么方法、解决了什么问题
{'- 研究意义：理论意义和实践价值' if is_thesis else ''}
- 文章结构：简述各章节内容安排
{type_hint}{context}""",

            "related_work": f"""请为以下论文撰写{lang}相关工作（{'2000-3000字' if is_thesis else '800-1200字'}）。

要求：
- 按研究方向分类综述（不要按时间流水账）
- 每类工作要说明具体方法、优缺点
- 指出现有工作的不足和本文的切入点
- 引用的文献必须是该领域真实存在的经典文献
{'- 综述要全面、有深度，体现对领域的理解' if is_thesis else ''}
{type_hint}{context}""",

            "methodology": f"""请为以下论文撰写{lang}{'研究方法' if is_thesis else '方法'}章节（{'2000-3000字' if is_thesis else '1200-1800字'}）。

要求：
- 问题形式化：用数学语言定义研究对象、变量、约束
- 模型假设：明确列出建模假设条件及其合理性
- 模型构建：详细推导数学模型，给出完整的方程和公式
- 求解策略：说明求解算法的原理和步骤
- 参数估计：说明参数如何确定（从数据拟合/文献/经验）
必须包含 LaTeX 数学公式。引用求解结果中的具体数值。
{type_hint}{context}""",

            "methods": f"""请为以下期刊论文撰写 Methods 章节（800-1200 words）。

Requirements:
- Clearly describe the research design
- Detail data collection and preprocessing
- Explain the mathematical model with LaTeX formulas
- Describe evaluation metrics
- Ensure reproducibility with specific parameters

{context}""",

            "experiments": f"""请为以下论文撰写{lang}{'实验设计' if is_thesis else '实验'}章节（{'1200-1500字' if is_thesis else '600-1000字'}）。

要求：
- 实验目标：明确要验证什么
- 实验设置：数据来源、参数配置、运行环境
- 评价指标：使用什么指标评估结果
- 实验流程：具体步骤
{'- 对比实验设计：选择哪些baseline方法对比' if is_thesis else ''}
{type_hint}{context}""",

            "results": f"""请为以下论文撰写{lang}{'结果与分析' if is_thesis else '结果'}章节（{'1500-2500字' if is_thesis else '800-1200字'}）。

要求：
- 呈现求解结果（必须引用具体数值）
- 分析结果的物理/实际含义
{'- 与baseline方法对比分析' if is_thesis else '- 讨论参数敏感性'}
- 指出模型的局限性
必须引用求解结果中的具体数字。
{type_hint}{context}""",

            "results_en": """Write a Results section (800-1200 words) for the following paper.

Requirements:
- Present numerical results with specific values
- Analyze physical/practical meaning of results
- Compare with baseline methods or theoretical expectations
- Include statistical significance where applicable

{context}""",

            "discussion": f"""请为以下论文撰写{lang}讨论章节（{'1500-2000字' if is_thesis else '800-1200字'}）。

要求：
- 对结果进行深入解读和讨论
- 与已有研究进行对比
- 讨论研究的理论贡献和实践意义
- 分析研究的局限性
- 提出未来研究方向
{type_hint}{context}""",

            "conclusion": f"""请为以下论文撰写{lang}结论（{'600-1000字' if is_thesis else '400-600字'}）。

要求：
- 总结本文工作和主要发现（具体数字）
- 列出3-4条主要结论
{'- 讨论理论意义和实践价值' if is_thesis else '- 讨论实际应用价值'}
- 指出局限性和未来改进方向
{type_hint}{context}""",

            "acknowledgements": """请为毕业论文撰写致谢（300-500字）。

要求：
- 感谢导师的指导
- 感谢实验室同学的帮助
- 感谢家人的支持
- 语言真诚、得体
- 不要过于模板化

{context}""",

            "problem_analysis": f"""请为以下数学建模论文撰写问题分析章节（600-1000字）。

要求：
- 对题目进行深入分析
- 识别关键变量和约束条件
- 分析问题的数学结构
- 提出解题思路

{context}""",

            "model_assumptions": f"""请为以下数学建模论文撰写模型假设章节（300-600字）。

要求：
- 列出所有建模假设
- 说明每条假设的合理性
- 分析假设对结果的影响

{context}""",

            "model_construction": f"""请为以下数学建模论文撰写模型构建章节（800-1500字）。

要求：
- 定义决策变量和参数
- 建立目标函数
- 列出约束条件
- 给出完整的数学模型
必须包含 LaTeX 数学公式。

{context}""",

            "model_solution": f"""请为以下数学建模论文撰写模型求解章节（600-1200字）。

要求：
- 说明求解算法的选择理由
- 描述算法步骤
- 给出求解结果（引用具体数值）
- 分析收敛性

{context}""",

            "model_evaluation": f"""请为以下数学建模论文撰写模型评价章节（400-800字）。

要求：
- 评估模型的合理性
- 分析灵敏度
- 讨论模型优缺点
- 提出改进方向

{context}""",

            "literature_review": f"""请为以下综述论文撰写文献综述主体（2000-3000字）。

要求：
- 按研究方向/方法分类综述
- 每类工作要说明具体方法、优缺点
- 引用真实文献
- 分类清晰、逻辑严密

{context}""",

            "comparison": f"""请为以下综述论文撰写方法对比章节（1000-1500字）。

要求：
- 列出不同方法的对比维度
- 用表格或结构化方式对比
- 分析各方法的适用场景
- 总结方法发展的趋势

{context}""",

            "future_directions": f"""请为以下综述论文撰写未来方向章节（500-800字）。

要求：
- 基于现有不足提出未来研究方向
- 分析可能的技术突破点
- 讨论潜在的应用场景

{context}""",

            "materials_methods": """Write a Materials and Methods section (1000-1500 words).

Requirements:
- Describe materials/equipment used
- Detail experimental procedures
- Explain data collection methods
- Describe statistical analysis methods
- Ensure reproducibility

{context}""",

            "background": f"""请为以下论文撰写背景介绍（500-800字）。

要求：
- 介绍研究领域的背景知识
- 说明研究问题的实际场景
- 引用相关数据和事实

{context}""",

            "case_description": f"""请为以下案例研究撰写案例描述（800-1200字）。

要求：
- 详细描述案例背景和场景
- 说明数据来源和收集方法
- 呈现关键数据和观察

{context}""",

            "analysis": f"""请为以下案例研究撰写分析章节（600-1000字）。

要求：
- 使用合适的分析框架
- 深入分析案例中的关键问题
- 引用数据支撑分析

{context}""",

            "findings": f"""请为以下案例研究撰写发现章节（500-800字）。

要求：
- 总结分析中的主要发现
- 讨论发现的理论和实践意义
- 与已有研究对比

{context}""",

            "references": f"""请为以下论文生成参考文献列表。

要求：
- 8-12篇参考文献
- 必须是该领域真实存在的经典论文和教材
- 使用 \\bibitem{{}} 格式
- 包含作者、标题、期刊/出版社、年份
- 按引用顺序排列

输出格式示例：
\\bibitem{{ref1}} Boyd S, Vandenberghe L. Convex Optimization. Cambridge University Press, 2004.

{context}""",
        }

        return prompts.get(section_key, f"请为{section_name}章节撰写内容。\n\n{type_hint}{context}")

    def _clean_latex_content(self, content: str) -> str:
        """清理 LLM 输出中的非 LaTeX 标记。"""
        import re

        # 移除 markdown 代码块
        content = re.sub(r'```latex\s*', '', content)
        content = re.sub(r'```\s*', '', content)

        # 移除 markdown 标题（# ## ###）
        content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)

        # 移除 markdown 加粗
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)

        # 移除开头的章节命令（由外层框架添加）
        content = re.sub(r'^\\section\{.*?\}\s*', '', content, flags=re.MULTILINE)
        content = re.sub(r'^\\subsection\{.*?\}\s*', '', content, flags=re.MULTILINE)

        return content.strip()
