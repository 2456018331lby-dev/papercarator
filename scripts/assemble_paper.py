#!/usr/bin/env python3
"""Step 3: Assemble AI-written sections into LaTeX and compile PDF.

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
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from papercarator.paper_writer.template_manager import TemplateManager
from papercarator.paper_writer.latex_generator import LaTeXGenerator


def assemble(context_path: str, sections_path: str, template: str = "custom") -> dict:
    """Assemble sections into LaTeX and compile PDF."""

    # Load context
    with open(context_path, "r", encoding="utf-8") as f:
        ctx = json.load(f)

    # Load sections
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

    # Generate LaTeX
    tm = TemplateManager()
    preamble = tm.get_latex_preamble(template)

    title = sections.get("title", ctx["topic"])
    doc = preamble + "\n\n"
    doc += f"\\title{{{title}}}\n"
    doc += "\\author{PaperCarator}\n"
    doc += "\\date{\\today}\n\n"
    doc += "\\begin{document}\n\n\\maketitle\n\n"

    # Abstract
    if "abstract" in sections:
        doc += "\\begin{abstract}\n" + sections["abstract"] + "\n\\end{abstract}\n\n"

    # Main sections
    section_order = [
        ("introduction", "引言"),
        ("related_work", "相关工作"),
        ("methodology", "方法"),
        ("experiments", "实验"),
        ("results", "结果与分析"),
        ("conclusion", "结论"),
    ]

    # Chart filenames for figure insertion
    chart_names = [Path(c).name for c in ctx.get("charts", [])]

    for key, title_zh in section_order:
        if key in sections and sections[key].strip():
            doc += f"\\section{{{title_zh}}}\n"
            doc += sections[key] + "\n\n"

    # Figures section
    if chart_names:
        doc += "\\section{图表}\n\n"
        for i, name in enumerate(chart_names):
            caption_map = {
                "queue_curve": "排队长度随时间演化曲线",
                "queue_metrics": "排队系统关键性能指标",
                "queueing_3d_profile": "排队系统三维可视化",
                "optimization_landscape": "优化目标函数等高线图",
                "bayesian_concept": "贝叶斯推断概念图",
                "queueing_concept": "排队系统概念图",
                "math_surface_3d": "数学曲面三维可视化",
            }
            stem = Path(name).stem
            caption = caption_map.get(stem, f"{stem} 可视化结果")
            doc += f"\\begin{{figure}}[H]\n\\centering\n"
            doc += f"\\includegraphics[width=0.8\\textwidth]{{{name}}}\n"
            doc += f"\\caption{{{caption}}}\n\\end{{figure}}\n\n"

    # References
    if "references" in sections and sections["references"].strip():
        doc += "\\bibliographystyle{plain}\n"
        doc += "\\begin{thebibliography}{99}\n"
        doc += sections["references"] + "\n"
        doc += "\\end{thebibliography}\n\n"

    doc += "\\end{document}\n"

    # Write tex
    tex_path = output_dir / "paper.tex"
    tex_path.write_text(doc, encoding="utf-8")

    # Compile PDF
    gen = LaTeXGenerator()
    pdf_path = gen._compile_latex(tex_path, output_dir)

    return {
        "success": True,
        "tex": str(tex_path),
        "pdf": str(pdf_path) if pdf_path else None,
        "output_dir": str(output_dir),
        "sections_count": len([k for k, _ in section_order if k in sections and sections[k].strip()]),
    }


def main():
    parser = argparse.ArgumentParser(description="Assemble paper from AI-written sections")
    parser.add_argument("--context", "-c", required=True, help="Context JSON from generate_data.py")
    parser.add_argument("--sections", "-s", required=True, help="Sections JSON written by AI")
    parser.add_argument("--template", "-t", default="custom", help="LaTeX template")
    args = parser.parse_args()

    result = assemble(args.context, args.sections, args.template)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
