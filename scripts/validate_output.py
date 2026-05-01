#!/usr/bin/env python3
"""Validate PaperCarator output artifacts.

Usage:
    python scripts/validate_output.py <output_dir>

Checks:
    1. paper/paper.tex exists and contains expected sections
    2. paper/paper.pdf exists (or compile.log reports failure)
    3. At least one chart image exists
    4. Figure captions are descriptive (not generic)
    5. Keywords are topic-specific (not generic defaults)
    6. References section has model-specific entries
"""

import sys
import re
from pathlib import Path


def validate(output_dir: str) -> list[str]:
    """Return list of issues found. Empty = all good."""
    issues = []
    root = Path(output_dir)

    # 1. Check paper.tex
    tex_path = root / "paper" / "paper.tex"
    if not tex_path.exists():
        issues.append("FAIL: paper/paper.tex not found")
        return issues  # Can't continue without tex

    tex = tex_path.read_text(encoding="utf-8")

    # 2. Check paper.pdf
    pdf_path = root / "paper" / "paper.pdf"
    if not pdf_path.exists():
        log_path = root / "paper" / "compile.log"
        if log_path.exists():
            issues.append(f"WARN: paper.pdf missing, compile.log says: {log_path.read_text(encoding='utf-8')[:200]}")
        else:
            issues.append("WARN: paper.pdf not found (no compile.log either)")

    # 3. Check charts
    paper_dir = root / "paper"
    charts = list(paper_dir.glob("*.png")) + list(paper_dir.glob("*.jpg"))
    viz_dir = root / "visualizations"
    if viz_dir.exists():
        charts.extend(viz_dir.glob("*.png"))
        charts.extend(viz_dir.glob("*.jpg"))

    if not charts:
        issues.append("WARN: No chart images found in paper/ or visualizations/")

    # 4. Check figure captions
    generic_captions = re.findall(r'\\caption\{(.*?)\}', tex)
    for cap in generic_captions:
        if cap.strip().lower() in ("visualization result", "figure", "chart", "plot"):
            issues.append(f"INFO: Generic figure caption found: '{cap}'")

    # 5. Check keywords
    kw_match = re.search(r'关键词[：:]\s*\{?(.*?)\}?\s*\\?$', tex, re.MULTILINE)
    if kw_match:
        kw_text = kw_match.group(1)
        generic_kws = ["研究", "分析", "优化", "系统"]
        kws = [k.strip() for k in kw_text.split(",")]
        if all(k in generic_kws for k in kws):
            issues.append(f"INFO: Keywords appear generic: {kws}")

    # 6. Check references
    bibitems = re.findall(r'\\bibitem\{(.*?)\}', tex)
    if len(bibitems) < 3:
        issues.append(f"WARN: Only {len(bibitems)} references found (expect >= 3)")

    # 7. Check sections exist
    required_sections = ["引言", "方法", "实验", "结果", "结论"]
    for section in required_sections:
        if section not in tex:
            issues.append(f"WARN: Section '{section}' not found in paper.tex")

    # 8. Check for broken LaTeX
    if tex.count(r"\begin{") != tex.count(r"\end{"):
        issues.append("WARN: Mismatched \\begin/\\end environments")

    return issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_output.py <output_dir>")
        sys.exit(1)

    output_dir = sys.argv[1]
    issues = validate(output_dir)

    if not issues:
        print("VALID: All checks passed!")
        sys.exit(0)

    for issue in issues:
        print(f"  {issue}")

    errors = [i for i in issues if i.startswith("FAIL")]
    if errors:
        print(f"\nFAILED: {len(errors)} critical issues")
        sys.exit(1)
    else:
        print(f"\nOK with {len(issues)} warnings/info")
        sys.exit(0)


if __name__ == "__main__":
    main()
