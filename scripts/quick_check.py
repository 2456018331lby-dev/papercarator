#!/usr/bin/env python3
"""Quick quality check for PaperCarator output.

Usage:
    python quick_check.py /path/to/output/dir

Prints a compact quality report to stdout.
"""

import json
import re
import sys
from pathlib import Path


def check(output_dir: str) -> dict:
    """Check output quality. Returns report dict."""
    root = Path(output_dir)
    paper_dir = root / "paper"
    report = {"dir": str(root), "issues": [], "scores": {}, "files": {}}

    # Check tex
    tex_path = paper_dir / "paper.tex"
    if not tex_path.exists():
        report["issues"].append("CRITICAL: paper.tex not found")
        return report

    tex = tex_path.read_text(encoding="utf-8")
    report["files"]["tex_size"] = len(tex)

    # Check PDF
    pdf_path = paper_dir / "paper.pdf"
    report["files"]["has_pdf"] = pdf_path.exists()
    if pdf_path.exists():
        report["files"]["pdf_size"] = pdf_path.stat().st_size

    # Check charts
    charts = list(paper_dir.glob("*.png")) + list(paper_dir.glob("*.jpg"))
    viz_dir = root / "visualizations" / "charts"
    if viz_dir.exists():
        charts.extend(viz_dir.glob("*.png"))
    report["files"]["chart_count"] = len(charts)

    # Score structure
    sections = {
        "abstract": bool(re.search(r"\\begin\{abstract\}", tex)),
        "introduction": bool(re.search(r"\\section\{引言", tex)),
        "methodology": bool(re.search(r"\\section\{方法", tex)),
        "results": bool(re.search(r"\\section\{结果", tex)),
        "conclusion": bool(re.search(r"\\section\{结论", tex)),
        "references": bool(re.search(r"\\begin\{thebibliography\}", tex)),
        "algorithm": bool(re.search(r"\\begin\{algorithm\}", tex)),
        "figures": bool(re.search(r"\\begin\{figure\}", tex)),
        "tables": bool(re.search(r"\\begin\{table\}", tex)),
    }
    report["scores"]["structure"] = sum(sections.values()) / len(sections) * 100
    report["sections"] = sections

    # Score references
    bibitems = re.findall(r"\\bibitem\{", tex)
    report["scores"]["references"] = min(len(bibitems) / 5 * 100, 100)
    report["files"]["ref_count"] = len(bibitems)

    # Check figure captions
    captions = re.findall(r"\\caption\{(.*?)\}", tex)
    generic = [c for c in captions if "Visualization result" in c or "Figure " in c and ":" in c]
    report["scores"]["captions"] = max(0, 100 - len(generic) * 30)
    report["files"]["caption_count"] = len(captions)
    if generic:
        report["issues"].append(f"INFO: {len(generic)} generic caption(s)")

    # Check keywords
    kw_match = re.search(r"关键词[：:].*?\\textbf", tex, re.DOTALL)
    if kw_match:
        kw_text = kw_match.group(0)
        if "研究" in kw_text and "分析" in kw_text and "优化" in kw_text and "系统" in kw_text:
            report["issues"].append("INFO: Keywords appear generic")

    # Overall
    scores = report["scores"]
    report["overall"] = round(sum(scores.values()) / len(scores), 1) if scores else 0

    # Quick summary
    report["verdict"] = (
        "PASS" if report["overall"] >= 60 and not any("CRITICAL" in i for i in report["issues"])
        else "WARN" if report["overall"] >= 40
        else "FAIL"
    )

    return report


def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_check.py <output_dir>")
        sys.exit(1)

    report = check(sys.argv[1])
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
