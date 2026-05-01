---
name: papercarator
description: >
  Math-modeling paper generator. From topic to PDF in one command.
  Use when user wants to generate an academic paper with mathematical modeling,
  equations, solver results, charts, algorithm pseudocode, and LaTeX/PDF output.
  Supports 16 model types: optimization, equations, ODE/PDE, queueing, Markov,
  Bayesian, statistics, network flow, graph theory, time-series, game theory,
  control theory, clustering, multi-objective, fuzzy logic.
  NOT for: literature-review-only, open-domain research, industrial CAD.
---

# PaperCarator — One-Command Paper Generation

## Usage (copy-paste for Claude Code / Hermes)

```bash
cd /path/to/papercarator && python3.12 scripts/run_paper.py "YOUR_TOPIC_HERE"
```

That's it. The script handles everything: analysis → modeling → solving → charts → pseudocode → academic enhancement → LaTeX → PDF → quality report.

## Options

```bash
# Default: output to ./output/<topic>/
python3.12 scripts/run_paper.py "基于排队论的医院门诊流程优化研究"

# Custom output directory
python3.12 scripts/run_paper.py "基于贝叶斯推断的药物疗效评估" --output /path/to/dir

# Specific template (standard/ieee/acm/cjm)
python3.12 scripts/run_paper.py "基于PID控制的自动驾驶" --template ieee

# Check existing output quality
python3.12 scripts/quick_check.py /path/to/output/dir
```

## What You Get

After running, the script prints a JSON summary:

```json
{
  "topic": "...",
  "model_type": "queueing",
  "keywords": ["排队", "服务台", "优化"],
  "quality_score": 77.4,
  "pdf": "/path/to/paper.pdf",
  "charts": ["queue_curve.png", "queue_metrics.png"],
  "has_algorithm": true,
  "suggestions": ["math_rigor 维度得分较低 (52)"]
}
```

If PDF compilation fails (no xelatex), the .tex file is still generated and valid.

## Supported Models (16)

equation_system | optimization | multi_objective | differential | pde |
queueing | markov_chain | bayesian | statistical | network_flow |
time_series | game_theory | control_theory | clustering | graph_theory | fuzzy_logic

## Troubleshooting

- **No xelatex**: Install MiKTeX or TeX Live. Script auto-detects Windows MiKTeX in WSL.
- **Missing deps**: `pip install -e ".[dev]"` in the papercarator directory.
- **Low quality score**: Run `python3.12 scripts/quick_check.py <dir>` for details.
