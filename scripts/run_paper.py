#!/usr/bin/env python3
"""PaperCarator — One-command paper generation.

Usage:
    python run_paper.py "基于排队论的医院门诊流程优化研究"
    python run_paper.py "基于贝叶斯推断的药物疗效评估" --output ./my_paper
    python run_paper.py "基于PID控制的自动驾驶" --template ieee

Output: JSON summary to stdout with paths, quality score, and suggestions.
"""

import argparse
import json
import sys
import time
from pathlib import Path

# Ensure papercarator is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from papercarator.core.config import Config
from papercarator.core.pipeline import Pipeline
from papercarator.core.utils import sanitize_filename
from papercarator.planner import TopicAnalyzer
from papercarator.math_modeling import ModelBuilder, ModelSolver, ModelValidator
from papercarator.visualization import ChartGenerator, Model3DGenerator
from papercarator.paper_writer import LaTeXGenerator
from papercarator.github_publisher import GitHubPublisher


def run(topic: str, output_dir: str = None, template: str = "custom",
        data_file: str = None, paper_type_hint: str = None) -> dict:
    """Run the full paper generation pipeline. Returns summary dict."""

    start_time = time.time()

    # Auto-detect paper type
    from papercarator.paper_writer.paper_types import PaperType
    paper_type = PaperType.detect_type(topic, paper_type_hint)
    type_info = PaperType.get_type(paper_type)

    # Auto-select template from paper type
    if template == "custom":
        cite_fmt = type_info.get("citation_format", "custom")
        if paper_type == "thesis":
            template = "custom"  # thesis uses ThesisStructure, not template
        elif cite_fmt == "ieee":
            template = "ieee"
        elif cite_fmt == "gbt7714":
            template = "custom"

    # Load external data if provided
    imported_data = None
    if data_file:
        from papercarator.data_importer import DataImporter
        importer = DataImporter()
        try:
            imported_data = importer.load(data_file)
            logger.info(f"已导入数据: {imported_data['n_rows']}行 x {imported_data['n_cols']}列")
        except Exception as e:
            logger.warning(f"数据导入失败: {e}")

    # Setup config
    config = Config()
    config.planner.analysis_depth = "standard"
    config.paper_writer.template = template
    config.vscode.enabled = False
    config.github_publisher.enabled = False

    if output_dir:
        config.system.output_dir = Path(output_dir)
    else:
        safe_name = sanitize_filename(topic)[:40]
        config.system.output_dir = Path(f"./output/{safe_name}")

    # Build pipeline
    pipeline = Pipeline(config)

    pipeline.register_module("planner", TopicAnalyzer())
    pipeline.register_module("math_modeling", {
        "builder": ModelBuilder(),
        "solver": ModelSolver(),
        "validator": ModelValidator(),
        "build_and_solve": lambda topic, plan, matlab_bridge=None: _build_and_solve(topic, plan, imported_data),
    })
    pipeline.register_module("visualization", {
        "chart": ChartGenerator(),
        "model3d": Model3DGenerator(),
        "generate": lambda topic, math_model, plan, output_dir, solidworks_bridge=None: _visualize(
            topic, math_model, plan, output_dir
        ),
    })
    pipeline.register_module("paper_writer", {
        "generator": LaTeXGenerator(),
        "write": lambda topic, plan, math_model, visualizations, output_dir: _write_paper(
            topic, plan, math_model, visualizations, output_dir
        ),
    })

    # Execute
    try:
        result = pipeline.run(topic)
    except Exception as e:
        return {"success": False, "error": str(e), "topic": topic}

    # Run statistical analysis on pipeline results, then regenerate paper
    stat_results = _run_statistical_analysis(topic, plan, result)
    if stat_results:
        from papercarator.paper_writer.latex_generator import LaTeXGenerator
        gen = LaTeXGenerator()
        paper_dir = config.system.output_dir / "paper"
        model = result.math_model.get("model", {})
        sol = result.math_model.get("solution", {})
        viz = result.visualizations
        sections, new_pdf = gen.generate(
            topic, plan, model, sol, viz, paper_dir, stat_results
        )
        if new_pdf:
            result.paper_pdf = new_pdf
            result.paper_content = sections

    elapsed = time.time() - start_time

    # Gather output info
    out = config.system.output_dir
    paper_dir = out / "paper"
    pdf_path = paper_dir / "paper.pdf"
    tex_path = paper_dir / "paper.tex"
    charts = list((out / "visualizations" / "charts").glob("*.png")) if (out / "visualizations" / "charts").exists() else []
    charts += list(paper_dir.glob("*.png"))

    # Quality check
    from papercarator.paper_writer.quality_scorer import PaperQualityScorer
    scorer = PaperQualityScorer()
    if tex_path.exists():
        tex_content = tex_path.read_text(encoding="utf-8")
        model_type = result.math_model.get("model", {}).get("model_type", "")
        report = scorer.score(tex_content, charts, model_type)
        quality_score = round(report.total_score, 1)
        suggestions = report.suggestions[:3]
    else:
        quality_score = 0
        suggestions = ["paper.tex not found"]

    # Build summary
    plan = result.plan or {}
    model_info = result.math_model.get("model", {})
    solution_info = result.math_model.get("solution", {})

    summary = {
        "success": True,
        "topic": topic,
        "paper_type": paper_type,
        "paper_type_name": type_info.get("name", ""),
        "model_type": model_info.get("model_type", "unknown"),
        "model_name": model_info.get("name", ""),
        "keywords": plan.get("keywords", []),
        "difficulty": plan.get("difficulty", "unknown"),
        "quality_score": quality_score,
        "pdf": str(pdf_path) if pdf_path.exists() else None,
        "tex": str(tex_path) if tex_path.exists() else None,
        "charts": [str(c) for c in charts],
        "chart_count": len(charts),
        "has_algorithm": "\\begin{algorithm}" in (tex_path.read_text(encoding="utf-8") if tex_path.exists() else ""),
        "solution_success": solution_info.get("success", False),
        "solution_message": solution_info.get("message", ""),
        "suggestions": suggestions,
        "elapsed_seconds": round(elapsed, 1),
        "output_dir": str(out),
    }

    return summary


def _build_and_solve(topic, plan, imported_data=None):
    builder = ModelBuilder()
    solver = ModelSolver()
    validator = ModelValidator()

    model = builder.build(topic, plan)

    # If we have imported data, apply it to model parameters
    if imported_data:
        from papercarator.data_importer import DataImporter
        importer = DataImporter()
        data_params = importer.to_model_params(imported_data, model.model_type)
        if data_params:
            model.parameters.update(data_params)
            model.metadata["data_source"] = imported_data.get("source", "")
            model.metadata["data_rows"] = imported_data.get("n_rows", 0)

    solution = solver.solve(model)
    validation = validator.validate(model, solution)
    return {
        "model": builder.to_dict(model),
        "solution": {
            "success": solution.success,
            "values": solution.values,
            "message": solution.message,
            "statistics": solution.statistics,
            "numerical_data": solution.numerical_data,
        },
        "validation": {
            "is_valid": validation.is_valid,
            "score": validation.score,
            "checks": validation.checks,
        },
    }


def _visualize(topic, math_model, plan, output_dir):
    chart_gen = ChartGenerator()
    model3d_gen = Model3DGenerator()
    all_files = []
    if "solution" in math_model:
        chart_files = chart_gen.generate(
            math_model["model"], math_model["solution"], output_dir / "charts"
        )
        all_files.extend(chart_files)
    model3d_files = model3d_gen.generate(
        topic, math_model.get("model", {}), output_dir / "3d_models"
    )
    all_files.extend(model3d_files)

    # Generate concept diagram (pure matplotlib, no GPU needed)
    from papercarator.visualization.concept_diagrams import ConceptDiagramGenerator
    concept_gen = ConceptDiagramGenerator()
    model_type = math_model.get("model", {}).get("model_type", "")
    concept = concept_gen.generate(model_type, topic, output_dir / "concepts")
    if concept:
        all_files.append(concept)

    return all_files


def _write_paper(topic, plan, math_model, visualizations, output_dir):
    generator = LaTeXGenerator()
    sections, pdf_path = generator.generate(
        topic=topic,
        plan=plan,
        math_model=math_model.get("model", {}),
        solution=math_model.get("solution", {}),
        visualizations=visualizations,
        output_dir=output_dir,
    )
    return sections, pdf_path


def _run_statistical_analysis(topic: str, plan: dict,
                              result) -> dict | None:
    """Run statistical analysis on pipeline results. Returns stat dict or None."""
    try:
        from papercarator.statistical_analysis import StatisticalAnalyzer
        analyzer = StatisticalAnalyzer()
        stat_results = {}

        solution = result.math_model.get("solution", {})
        numeric_vals = {k: v for k, v in solution.get("values", {}).items()
                        if isinstance(v, (int, float))}
        if numeric_vals:
            vals_list = list(numeric_vals.values())
            if len(vals_list) >= 2:
                stat_results["descriptive"] = analyzer.descriptive_stats(vals_list)

        # Try t-test with synthetic groups if we have enough values
        if len(vals_list) >= 6:
            half = len(vals_list) // 2
            try:
                stat_results["t_test"] = analyzer.t_test(
                    vals_list[:half], vals_list[half:], test_type="independent"
                )
            except Exception:
                pass

        # Add numerical data stats from solution
        numerical_data = solution.get("numerical_data", {})
        if numerical_data:
            for key, arr in numerical_data.items():
                if isinstance(arr, (list, tuple)) and len(arr) >= 3:
                    try:
                        stat_results[f"regression_{key}"] = analyzer.regression(
                            list(range(len(arr))), list(arr))
                    except Exception:
                        pass

        if stat_results:
            from loguru import logger
            logger.info(f"统计分析完成: {list(stat_results.keys())}")
            return stat_results

    except Exception as e:
        from loguru import logger
        logger.warning(f"统计分析跳过: {e}")

    return None


def main():
    parser = argparse.ArgumentParser(description="PaperCarator — One-command paper generation")
    parser.add_argument("topic", help="Paper topic / title")
    parser.add_argument("--output", "-o", help="Output directory (default: ./output/<topic>/)")
    parser.add_argument("--template", "-t", default="custom",
                        choices=["custom", "ieee", "acm", "cjm", "springer_lncs", "thesis"],
                        help="LaTeX template (default: custom)")
    parser.add_argument("--data", "-d", help="Data file path (CSV/Excel/JSON) for real data modeling")
    parser.add_argument("--type", help="Paper type hint: thesis/journal/conference/review/experiment/case_study/math_modeling")
    args = parser.parse_args()

    summary = run(args.topic, args.output, args.template, args.data, args.type)

    # Print JSON summary to stdout
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    # Exit code
    sys.exit(0 if summary.get("success") else 1)


if __name__ == "__main__":
    main()
