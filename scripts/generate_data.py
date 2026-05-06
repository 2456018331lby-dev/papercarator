#!/usr/bin/env python3
"""Step 1: Generate modeling data, charts, and context for AI to write about.

Usage:
    python generate_data.py "基于排队论的医院门诊流程优化研究"

Output: JSON with all math results, stats, and context. AI reads this and writes sections.
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from papercarator.core.config import Config
from papercarator.planner import TopicAnalyzer
from papercarator.math_modeling import ModelBuilder, ModelSolver, ModelValidator
from papercarator.visualization import ChartGenerator, Model3DGenerator
from papercarator.core.utils import sanitize_filename


def generate(topic: str, output_dir: str = None, data_file: str = None) -> dict:
    """Run analysis + modeling + visualization. Returns full context for AI writing."""

    start = time.time()

    config = Config()
    if output_dir:
        config.system.output_dir = Path(output_dir)
    else:
        safe_name = sanitize_filename(topic)[:40]
        config.system.output_dir = Path(f"./output/{safe_name}")

    out = config.system.output_dir
    out.mkdir(parents=True, exist_ok=True)
    viz_dir = out / "visualizations"
    viz_dir.mkdir(exist_ok=True)

    # 1. Topic analysis
    analyzer = TopicAnalyzer()
    plan = analyzer.analyze(topic)

    # 2. Build and solve model
    builder = ModelBuilder()
    solver = ModelSolver()
    validator = ModelValidator()

    model = builder.build(topic, plan)

    # Import external data if provided
    imported_data = None
    if data_file:
        from papercarator.data_importer import DataImporter
        importer = DataImporter()
        try:
            imported_data = importer.load(data_file)
            params = importer.to_model_params(imported_data, model.model_type)
            if params:
                model.parameters.update(params)
        except Exception as e:
            print(f"Warning: data import failed: {e}", file=sys.stderr)

    solution = solver.solve(model)
    validation = validator.validate(model, solution)

    # 3. Generate charts
    chart_gen = ChartGenerator()
    model3d_gen = Model3DGenerator()

    math_dict = {
        "model": builder.to_dict(model),
        "solution": {
            "success": solution.success,
            "values": solution.values,
            "message": solution.message,
            "statistics": solution.statistics,
            "numerical_data": {k: v[:50] if isinstance(v, list) else v
                              for k, v in solution.numerical_data.items()},
        },
        "validation": {
            "is_valid": validation.is_valid,
            "score": validation.score,
        },
    }

    chart_files = chart_gen.generate(
        math_dict["model"], math_dict["solution"], viz_dir / "charts"
    )
    model3d_files = model3d_gen.generate(
        topic, math_dict["model"], viz_dir / "3d_models"
    )

    # 4. Concept diagram
    from papercarator.visualization.concept_diagrams import ConceptDiagramGenerator
    concept_gen = ConceptDiagramGenerator()
    concept_file = concept_gen.generate(model.model_type, topic, viz_dir / "concepts")

    all_charts = [str(f) for f in chart_files + model3d_files]
    if concept_file:
        all_charts.append(str(concept_file))

    # 5. Algorithm pseudocode
    from papercarator.paper_writer.algorithm_writer import AlgorithmWriter
    algo = AlgorithmWriter()
    algorithm_code = algo.generate(model.model_type)

    # 6. Literature search
    from papercarator.literature_search import LiteratureSearcher
    searcher = LiteratureSearcher()
    papers = searcher.search(topic + " " + model.model_type, limit=5)

    # 7. Statistical analysis (if numeric data available)
    from papercarator.statistical_analysis import StatisticalAnalyzer
    stat_analyzer = StatisticalAnalyzer()
    stat_results = {}

    # Extract numeric data from solution for analysis
    numeric_values = {k: v for k, v in solution.values.items() if isinstance(v, (int, float))}
    if numeric_values:
        values_list = list(numeric_values.values())
        stat_results["descriptive"] = stat_analyzer.descriptive_stats(values_list)

    # If imported data has numeric columns, run regression/correlation
    if imported_data:
        numeric_cols = imported_data.get("numeric_columns", [])
        if len(numeric_cols) >= 2:
            col1, col2 = numeric_cols[0], numeric_cols[1]
            idx1 = imported_data["columns"].index(col1)
            idx2 = imported_data["columns"].index(col2)
            x_vals = [row[idx1] for row in imported_data["data"]
                      if row[idx1] is not None and row[idx2] is not None]
            y_vals = [row[idx2] for row in imported_data["data"]
                      if row[idx1] is not None and row[idx2] is not None]
            if len(x_vals) >= 3:
                try:
                    stat_results["regression"] = stat_analyzer.regression(x_vals, y_vals)
                    stat_results["correlation"] = stat_analyzer.correlation(x_vals, y_vals)
                except Exception:
                    pass

    elapsed = time.time() - start

    # Detect paper type
    from papercarator.paper_writer.paper_types import PaperType
    paper_type = PaperType.detect_type(topic)
    type_info = PaperType.get_type(paper_type)

    # Build output
    result = {
        "topic": topic,
        "paper_type": paper_type,
        "paper_type_info": {
            "name": type_info["name"],
            "sections": [s[0] for s in type_info["sections"]],
            "citation_format": type_info["citation_format"],
            "language": type_info["language"],
            "min_pages": type_info["min_pages"],
        },
        "plan": {
            "paper_type": plan.get("paper_type"),
            "keywords": plan.get("keywords", []),
            "difficulty": plan.get("difficulty"),
            "application_domain": plan.get("application_domain"),
            "research_methods": plan.get("research_methods", []),
        },
        "model": {
            "name": model.name,
            "type": model.model_type,
            "description": model.description,
            "equations": [str(eq) for eq in model.equations[:5]],
            "parameters": model.parameters,
            "metadata": {k: v for k, v in model.metadata.items()
                        if not isinstance(v, (list, dict)) or len(str(v)) < 200},
        },
        "solution": {
            "success": solution.success,
            "message": solution.message,
            "values": {k: round(v, 6) if isinstance(v, float) else v
                      for k, v in solution.values.items()},
            "statistics": {k: round(v, 4) if isinstance(v, float) else v
                          for k, v in solution.statistics.items()
                          if not isinstance(v, dict)},
        },
        "statistical_analysis": stat_results,
        "charts": all_charts,
        "algorithm": algorithm_code,
        "literature": papers,
        "output_dir": str(out),
        "elapsed_seconds": round(elapsed, 1),
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="Generate modeling data for AI writing")
    parser.add_argument("topic", help="Paper topic")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--data", "-d", help="Data file (CSV/Excel/JSON)")
    args = parser.parse_args()

    result = generate(args.topic, args.output, args.data)

    # Auto-save context.json to output dir
    out_dir = Path(result["output_dir"])
    ctx_path = out_dir / "context.json"
    ctx_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    # Also print to stdout
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n# Context saved to: {ctx_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
