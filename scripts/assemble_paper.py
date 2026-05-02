#!/usr/bin/env python3
"""Step 3: Assemble AI-written sections into LaTeX and compile PDF.

Supports all 7 paper types: thesis, journal, conference, review, experiment, case_study, math_modeling.

Usage:
    python assemble_paper.py --context context.json --sections sections.json --template custom

sections.json format:
{
    "title": "论文标题",
    "abstract": "摘要内容...",
    "introduction": "引言内容...",
    "related_work": "相关工作...",
    "methodology": "方法...",
    "experiments": "实验...",
    "results": "结果与分析...",
    "conclusion": "结论...",
    "references": "\\bibitem{ref1} Author. Title. Journal, 2024."
}

For thesis type, additional fields:
{
    "author": "作者",
    "student_id": "学号",
    "institution": "学校",
    "college": "学院",
    "major": "专业",
    "advisor": "导师",
    "degree": "硕士",
    "abstract_en": "English abstract...",
    "keywords_zh": ["关键词1", "关键词2"],
    "keywords_en": ["keyword1", "keyword2"],
    "acknowledgements": "致谢内容..."
}
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from papercarator.paper_writer.template_manager import TemplateManager
from papercarator.paper_writer.latex_generator import LaTeXGenerator
from papercarator.paper_writer.paper_types import PaperType
from papercarator.paper_writer.thesis_structure import ThesisStructure


def assemble(context_path: str, sections_path: str, template: str = None) -> dict:
    """Assemble sections into LaTeX and compile PDF."""

    with open(context_path, "r", encoding="utf-8") as f:
        ctx = json.load(f)

    with open(sections_path, "r", encoding="utf-8") as f:
        sections = json.load(f)

    output_dir = Path(ctx["output_dir"]) / "paper"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy charts to paper dir
    import shutil
    for chart_path in ctx.get("charts", []):
        src = Path(chart_path)
        if src.exists():
            dest = output_dir / src.name
            if not dest.exists():
                shutil.copy2(src, dest)

    # Detect paper type
    paper_type = ctx.get("paper_type", "math_modeling")
    type_info = ctx.get("paper_type_info", {})
    if not template:
        template = type_info.get("citation_format", "custom")
        if template in ("gbt7714", "apa", "ieee", "chicago", "mla"):
            template = "custom"

    title = sections.get("title", ctx["topic"])

    # Dispatch based on paper type
    if paper_type == "thesis":
        doc = _assemble_thesis(ctx, sections, title)
    else:
        doc = _assemble_article(ctx, sections, title, template, paper_type)

    # Write tex
    tex_path = output_dir / "paper.tex"
    tex_path.write_text(doc, encoding="utf-8")

    # Compile PDF
    gen = LaTeXGenerator()
    pdf_path = gen._compile_latex(tex_path, output_dir)

    section_order = [
        ("abstract", "摘要"), ("introduction", "引言"),
        ("related_work", "相关工作"), ("methodology", "方法"),
        ("experiments", "实验"), ("results", "结果与分析"),
        ("conclusion", "结论"),
    ]

    return {
        "success": True,
        "paper_type": paper_type,
        "tex": str(tex_path),
        "pdf": str(pdf_path) if pdf_path else None,
        "output_dir": str(output_dir),
        "sections_count": len([k for k, _ in section_order if k in sections and sections[k].strip()]),
    }


def _assemble_thesis(ctx: dict, sections: dict, title: str) -> str:
    """Assemble thesis-format paper with cover, abstract pages, TOC, acknowledgements."""
    ts = ThesisStructure()

    doc = ts.generate_preamble(title=title, author=sections.get("author", ""))
    doc += "\n\\begin{document}\n\n"

    # Cover page
    doc += ts.generate_cover(
        title=title,
        author=sections.get("author", "（作者）"),
        student_id=sections.get("student_id", ""),
        institution=sections.get("institution", "（学校）"),
        college=sections.get("college", ""),
        major=sections.get("major", ""),
        advisor=sections.get("advisor", ""),
        degree=sections.get("degree", "硕士"),
        date=sections.get("date", "\\today"),
    )

    # Abstract pages (zh + en)
    abstract_zh = sections.get("abstract", "（待填写）")
    keywords_zh = sections.get("keywords_zh", ["关键词1", "关键词2"])
    abstract_en = sections.get("abstract_en", "(To be filled)")
    keywords_en = sections.get("keywords_en", ["keyword1", "keyword2"])
    doc += ts.generate_abstract_page(abstract_zh, keywords_zh, abstract_en, keywords_en)

    # Table of contents
    doc += ts.generate_toc()

    # Chapter structure for thesis
    chapter_mapping = [
        ("introduction", "绪论"),
        ("related_work", "文献综述"),
        ("methodology", "研究方法"),
        ("experiments", "实验设计"),
        ("results", "结果与分析"),
        ("discussion", "讨论"),
        ("conclusion", "结论与展望"),
    ]

    for key, ch_title in chapter_mapping:
        if key in sections and sections[key].strip():
            doc += f"\\chapter{{{ch_title}}}\n{sections[key]}\n\n"

    # Algorithm pseudocode
    algorithm = ctx.get("algorithm", "")
    if algorithm:
        doc += "\\chapter{算法描述}\n" + algorithm + "\n\n"

    # Figures
    chart_names = [Path(c).name for c in ctx.get("charts", [])]
    if chart_names:
        doc += "\\chapter{图表}\n\n"
        doc += _build_figures(chart_names)

    # References
    refs = sections.get("references", "")
    if refs.strip():
        doc += "\n\\bibliographystyle{plain}\n"
        doc += "\\begin{thebibliography}{99}\n"
        doc += refs + "\n"
        doc += "\\end{thebibliography}\n\n"

    # Acknowledgements
    ack = sections.get("acknowledgements", "")
    doc += ts.generate_acknowledgements(ack)

    doc += "\\end{document}"
    return doc


def _assemble_article(ctx: dict, sections: dict, title: str,
                      template: str, paper_type: str) -> str:
    """Assemble standard article-format paper."""
    tm = TemplateManager()
    preamble = tm.get_latex_preamble(template)

    doc = preamble + "\n\n"
    doc += "\\title{{{}}}\n".format(title)
    doc += "\\author{PaperCarator}\n"
    doc += "\\date{\\today}\n\n"
    doc += "\\begin{document}\n\n\\maketitle\n\n"

    # Abstract
    if "abstract" in sections:
        doc += "\\begin{abstract}\n" + sections["abstract"] + "\n\\end{abstract}\n\n"

    # Keywords
    kw = sections.get("keywords", ctx.get("plan", {}).get("keywords", []))
    if kw:
        if isinstance(kw, list):
            kw_str = ", ".join(kw)
        else:
            kw_str = kw
        doc += "\\textbf{{Keywords:}} {}\n\n".format(kw_str)

    # Main sections
    section_order = [
        ("introduction", "引言"),
        ("related_work", "相关工作"),
        ("problem_analysis", "问题分析"),
        ("model_assumptions", "模型假设"),
        ("model_construction", "模型构建"),
        ("model_solution", "模型求解"),
        ("model_evaluation", "模型评价"),
        ("methodology", "方法"),
        ("materials_methods", "材料与方法"),
        ("background", "背景"),
        ("case_description", "案例描述"),
        ("analysis", "分析"),
        ("findings", "发现"),
        ("experiments", "实验"),
        ("results", "结果"),
        ("discussion", "讨论"),
        ("conclusion", "结论"),
    ]

    for key, title_zh in section_order:
        if key in sections and sections[key].strip():
            doc += "\\section{{{}}}\n".format(title_zh)
            doc += sections[key] + "\n\n"

    # Algorithm
    algorithm = ctx.get("algorithm", "")
    if algorithm:
        doc += "\\section{算法描述}\n" + algorithm + "\n\n"

    # Figures
    chart_names = [Path(c).name for c in ctx.get("charts", [])]
    if chart_names:
        doc += "\\section{图表}\n\n"
        doc += _build_figures(chart_names)

    # References
    refs = sections.get("references", "")
    if refs.strip():
        doc += "\\bibliographystyle{plain}\n"
        doc += "\\begin{thebibliography}{99}\n"
        doc += refs + "\n"
        doc += "\\end{thebibliography}\n\n"

    doc += "\\end{document}"
    return doc


def _build_figures(chart_names: list) -> str:
    """Build LaTeX figure blocks for all charts."""
    caption_map = {
        "queue_curve": "排队长度随时间演化曲线",
        "queue_metrics": "排队系统关键性能指标",
        "queueing_3d_profile": "排队系统三维可视化",
        "optimization_landscape": "优化目标函数等高线图",
        "optimization_stats": "优化求解统计信息",
        "bayesian_concept": "贝叶斯推断概念图",
        "queueing_concept": "排队系统概念图",
        "math_surface_3d": "数学曲面三维可视化",
        "differential_solution": "微分方程数值解",
        "regression_analysis": "回归分析与残差图",
        "markov_distribution_evolution": "马尔可夫链状态分布演化",
        "markov_probability_heatmap": "状态概率热力图",
        "control_step_response": "控制系统阶跃响应",
        "clustering_result": "聚类分析散点图",
        "game_payoff_matrix": "博弈收益矩阵",
        "game_strategy_distribution": "混合策略分布",
        "network_flow_graph": "网络流路径图",
        "pareto_front": "帕累托前沿",
        "pde_heatmaps": "偏微分方程温度场",
        "time_series_forecast": "时间序列预测",
    }

    doc = ""
    for name in chart_names:
        stem = Path(name).stem
        caption = caption_map.get(stem, "{} 可视化结果".format(stem))
        doc += "\\begin{figure}[H]\n\\centering\n"
        doc += "\\includegraphics[width=0.8\\textwidth]{{{}}}\n".format(name)
        doc += "\\caption{{{}}}\n\\end{figure}\n\n".format(caption)
    return doc


def main():
    parser = argparse.ArgumentParser(description="Assemble paper from AI-written sections")
    parser.add_argument("--context", "-c", required=True, help="Context JSON from generate_data.py")
    parser.add_argument("--sections", "-s", required=True, help="Sections JSON written by AI")
    parser.add_argument("--template", "-t", default=None, help="LaTeX template (auto-detected from paper type)")
    args = parser.parse_args()

    result = assemble(args.context, args.sections, args.template)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
