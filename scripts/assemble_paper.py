#!/usr/bin/env python3
"""Step 3: Assemble AI-written sections into LaTeX and compile PDF.

Delegates to LaTeXGenerator.generate() which handles all 7 paper types,
citation formatting, statistical analysis injection, and thesis structure.

Usage:
    python assemble_paper.py --context context.json --sections sections.json

sections.json format:
{
    "title": "论文标题",
    "abstract": "摘要内容...",
    "introduction": "引言内容...",
    ...
    "references": "\\bibitem{ref1} Author. Title. Journal, 2024."
}

For thesis type, extra fields: author, student_id, institution, college, major,
advisor, degree, abstract_en, keywords_zh, acknowledgements.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from papercarator.paper_writer.latex_generator import LaTeXGenerator


def assemble(context_path: str, sections_path: str) -> dict:
    """Assemble sections into LaTeX and compile PDF via LaTeXGenerator."""

    with open(context_path, "r", encoding="utf-8") as f:
        ctx = json.load(f)

    with open(sections_path, "r", encoding="utf-8") as f:
        sections = json.load(f)

    output_dir = Path(ctx["output_dir"])
    paper_dir = output_dir / "paper"
    paper_dir.mkdir(parents=True, exist_ok=True)

    # Build plan dict from context
    paper_type = ctx.get("paper_type", "math_modeling")
    plan = {
        "paper_type": paper_type,
        "keywords": sections.get("keywords_zh",
                   ctx.get("plan", {}).get("keywords", [])),
        "topic": ctx.get("topic", ""),
        "template": ctx.get("paper_type_info", {}).get("citation_format", "custom"),
    }

    # Add thesis-specific info from sections
    for field in ("institution", "degree", "advisor", "student_id", "major", "college"):
        if field in sections:
            plan[field] = sections[field]

    # Inject stat results from context
    stat_results = ctx.get("statistical_analysis") or None

    # Build model/solution stubs for LaTeXGenerator
    math_model = ctx.get("model", {})
    solution = ctx.get("solution", {})

    # Collect visualization paths
    visualizations = [Path(p) for p in ctx.get("charts", []) if Path(p).exists()]

    # Copy charts to paper dir
    import shutil
    for viz_path in visualizations:
        dest = paper_dir / viz_path.name
        if not dest.exists():
            shutil.copy2(viz_path, dest)

    # Add title to sections
    title = sections.get("title", ctx["topic"])
    sections["title"] = title

    # Delegate to LaTeXGenerator
    gen = LaTeXGenerator()
    secs, pdf_path = gen.generate(
        topic=ctx["topic"],
        plan=plan,
        math_model=math_model,
        solution=solution,
        visualizations=visualizations,
        output_dir=paper_dir,
        stat_results=stat_results,
    )

    tex_path = paper_dir / "paper.tex"
    return {
        "success": True,
        "paper_type": paper_type,
        "tex": str(tex_path) if tex_path.exists() else None,
        "pdf": str(pdf_path) if pdf_path else None,
        "output_dir": str(paper_dir),
        "sections_count": sum(1 for v in secs.values() if isinstance(v, str) and v.strip()),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Assemble paper from AI-written sections")
    parser.add_argument("--context", "-c", required=True,
                        help="Context JSON from generate_data.py")
    parser.add_argument("--sections", "-s", required=True,
                        help="Sections JSON written by AI")
    args = parser.parse_args()

    result = assemble(args.context, args.sections)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()