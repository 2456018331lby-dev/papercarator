---
name: papercarator
description: >
  End-to-end math-modeling paper generation skill. From topic to PDF in one command.
  Supports 16 model families with automatic: topic analysis, parameter extraction,
  model construction, solver execution, chart/3D generation, algorithm pseudocode,
  academic language enhancement, quality scoring, and LaTeX/PDF compilation.
  Models: optimization, equations, ODE/PDE, queueing, Markov, Bayesian, statistics,
  network flow, graph theory, time-series, game theory, control theory, clustering,
  multi-objective, fuzzy logic. Integrates Stable Diffusion for concept diagrams.
  Templates: standard, IEEE, ACM, Chinese journal. NOT for: literature-review-only,
  open-domain research, citation-heavy academic writing, or industrial CAD.
---

# PaperCarator Skill

## Quick Start

```bash
# 1. Classify topic fit
python3.12 -m papercarator.cli analyze "<topic>"

# 2. Full generation (topic -> PDF)
python3.12 -m papercarator.cli run "<topic>" --output <dir> --no-github --no-vscode

# 3. With specific template
python3.12 -m papercarator.cli run "<topic>" --template ieee --output <dir>

# 4. Batch processing
python scripts/batch_run.py topics.txt --output ./batch_output

# 5. Validate output quality
python scripts/validate_output.py <output_dir>

# 6. Sensitivity analysis
python scripts/sensitivity_analysis.py queueing --output results.json
```

## Pipeline (7 Steps)

1. **Planner** — Topic analysis: keywords, methods, domain, model routing
2. **ParamExtractor** — Extract numerical parameters from topic text
3. **MathModeling** — Build symbolic/numeric model, solve (SymPy/SciPy)
4. **Visualization** — 2D charts (matplotlib) + 3D surfaces + SD concept diagrams
5. **PaperWriter** — LaTeX sections + algorithm pseudocode + academic enhancement
6. **QualityScorer** — Auto-score paper quality (7 dimensions, 0-100)
7. **Compiler** — xelatex -> PDF

## What's Auto-Generated

- Topic-specific keywords (not generic)
- Descriptive Chinese figure captions
- Model-specific references (5+ per type from real textbooks)
- Algorithm pseudocode (LaTeX algorithmic environment)
- Academic language (colloquial -> formal Chinese replacement)
- Quality report with improvement suggestions

## Templates

| ID | Style |
|----|-------|
| standard | Standard article (default) |
| ieee | IEEE double-column conference |
| acm | ACM sigconf |
| cjm | Chinese journal with headers/footers |

## Reference Files

- `references/model_profiles.md` — 16 model type profiles
- `references/domain_backgrounds.md` — Domain-specific intro text
- `scripts/validate_output.py` — Output artifact validation
- `scripts/sensitivity_analysis.py` — Parameter sweep
- `scripts/batch_run.py` — Batch topic processing
