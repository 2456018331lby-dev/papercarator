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
        """调用 LLM 生成所有章节。"""
        if not self.is_available():
            logger.warning("LLM API 不可用，返回空（将由规则模板兜底）")
            return {}

        logger.info("开始 LLM 深度写作...")
        start = time.time()

        # 构建研究上下文
        context = self._build_context(topic, plan, math_model, solution)

        # 系统提示：学术论文写作专家
        system = self._get_system_prompt()

        sections = {}

        # 逐章节生成（每章节独立prompt，保证深度）
        section_tasks = [
            ("abstract", "摘要", 600),
            ("introduction", "引言", 1200),
            ("related_work", "相关工作", 1500),
            ("methodology", "方法", 2000),
            ("experiments", "实验", 1200),
            ("results", "结果与分析", 1500),
            ("conclusion", "结论", 800),
        ]

        for key, name, max_tokens in section_tasks:
            prompt = self._build_section_prompt(name, context, key)
            logger.info(f"  LLM 生成: {name}...")
            content = self._call_llm(system, prompt, max_tokens=max_tokens)
            if content:
                # 清理LLM输出中的markdown标记
                content = self._clean_latex_content(content)
                sections[key] = content
                logger.info(f"  {name}: {len(content)} 字符")
            else:
                logger.warning(f"  {name}: LLM 生成失败，跳过")

        # 参考文献
        refs_prompt = self._build_section_prompt("参考文献", context, "references")
        refs_content = self._call_llm(system, refs_prompt, max_tokens=1000)
        if refs_content:
            sections["references"] = self._clean_latex_content(refs_content)

        elapsed = time.time() - start
        logger.info(f"LLM 写作完成: {len(sections)} 章节, 耗时 {elapsed:.1f}s")
        return sections

    def _get_system_prompt(self) -> str:
        """学术论文写作专家系统提示。"""
        return """你是一位资深的数学建模论文写作专家。你的任务是为自动生成的数学建模论文撰写高质量的学术内容。

写作要求：
1. 使用规范的中文学术表达，避免口语化
2. 每个章节要有实质性内容，不能空洞或重复
3. 数学公式使用 LaTeX 格式（行内用 $...$，独立公式用 \\begin{equation}...\\end{equation}）
4. 结果分析要具体，引用实际数值
5. 相关工作要真实可信，不能编造文献
6. 方法描述要清晰说明建模思路、假设条件和求解策略
7. 不要使用 markdown 格式（如 #、**），直接输出 LaTeX 格式
8. 每个章节开头不需要写 \\section{}，由外层框架添加

输出格式：纯 LaTeX 内容，可直接嵌入论文。"""

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
                              section_key: str) -> str:
        """为特定章节构建写作提示。"""
        prompts = {
            "abstract": f"""请为以下数学建模论文撰写摘要（200-300字）。

要求：
- 概述研究问题和背景
- 说明采用的数学模型和方法
- 列出关键数值结果（必须引用具体数字）
- 总结主要结论和意义
- 最后给出3-5个关键词

{context}""",

            "introduction": f"""请为以下数学建模论文撰写引言（800-1200字）。

要求：
- 研究背景：该领域的实际需求和研究意义（具体场景，不要泛泛而谈）
- 问题提出：现有方法的不足，为什么需要新的建模方法
- 本文工作：明确说明做了什么、用了什么方法、解决了什么问题
- 文章结构：简述各章节内容安排

{context}""",

            "related_work": f"""请为以下数学建模论文撰写相关工作（800-1200字）。

要求：
- 按研究方向分类综述（不要按时间流水账）
- 每类工作要说明具体方法、优缺点
- 指出现有工作的不足和本文的切入点
- 引用的文献必须是该领域真实存在的经典文献

{context}""",

            "methodology": f"""请为以下数学建模论文撰写方法章节（1200-1800字）。

要求：
- 问题形式化：用数学语言定义研究对象、变量、约束
- 模型假设：明确列出建模假设条件及其合理性
- 模型构建：详细推导数学模型，给出完整的方程和公式
- 求解策略：说明求解算法的原理和步骤
- 参数估计：说明参数如何确定（从数据拟合/文献/经验）

必须包含 LaTeX 数学公式。引用求解结果中的具体数值。

{context}""",

            "experiments": f"""请为以下数学建模论文撰写实验章节（600-1000字）。

要求：
- 实验目标：明确要验证什么
- 实验设置：数据来源、参数配置、运行环境
- 评价指标：使用什么指标评估结果
- 实验流程：具体步骤

{context}""",

            "results": f"""请为以下数学建模论文撰写结果与分析章节（800-1200字）。

要求：
- 呈现求解结果（必须引用具体数值，如 ρ=0.703, Lq=1.375）
- 分析结果的物理/实际含义
- 讨论参数敏感性（改变参数会怎样）
- 与理论预期或已有方法对比
- 指出模型的局限性

必须引用求解结果中的具体数字。

{context}""",

            "conclusion": f"""请为以下数学建模论文撰写结论（400-600字）。

要求：
- 总结本文工作和主要发现（具体数字）
- 列出3-4条主要结论
- 讨论实际应用价值
- 指出局限性和未来改进方向

{context}""",

            "references": f"""请为以下数学建模论文生成参考文献列表。

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

        return prompts.get(section_key, f"请为{section_name}章节撰写内容。\n\n{context}")

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
