---
name: papercarator
description: >
  Academic paper generation skill. Supports thesis, journal, conference, review,
  experiment, case study, and math-modeling papers. Two modes: (A) YOU write using
  math/stat data from scripts, or (B) one-command auto via external LLM. Features:
  16 math models, 7 paper types (full routing), 5 citation formats (integrated),
  statistical analysis (descriptive/t-test/regression/ANOVA/chi-square with LaTeX
  output), automatic thesis structure, charts, PDF generation. NOT for: industrial CAD.
---

# PaperCarator — Academic Paper Skill v0.3

## Prerequisites

```bash
cd <papercarator-root> && pip install -e ".[dev]"
```
Requires: Python 3.10+, xelatex (MiKTeX or TeX Live).

## Paper Types (7) — fully routed

Paper type detection is automatic from topic keywords. The LaTeX generator routes to the correct structure per type:

| ID | Name | Pages | Lang | Citation | Structure |
|----|------|-------|------|----------|-----------|
| thesis | 毕业论文 | 30-100 | zh | GB/T 7714 | ThesisStructure: cover+TOC+abstract_zh/en+chapters+ack |
| journal | 期刊论文 | 6-15 | en | APA | intro→methods→results→discussion→conclusion |
| conference | 会议论文 | 4-8 | en | IEEE | intro→methodology→experiments→results→conclusion |
| review | 综述论文 | 10-30 | zh | APA | background→lit_review→taxonomy→comparison→future |
| experiment | 实验论文 | 8-20 | en | APA | materials_methods→results→discussion→conclusion |
| case_study | 案例研究 | 6-15 | zh | APA | background→case_description→analysis→findings |
| math_modeling | 数学建模 | 15-30 | zh | GB/T 7714 | problem_analysis→assumptions→construction→solution→eval |

## Mode Selection

| Situation | Mode |
|-----------|------|
| Quality paper, you have context | **A** (recommended) |
| User says "快速/一键/自动生成" | **B** |
| Short on context tokens | **B** |

---

## Mode A — YOU Write (3 Steps)

### Step 1: Generate data

```bash
python3 scripts/generate_data.py "TOPIC" --output ./output/my_paper
```

Output: context.json, charts, statistical analysis, literature.

### Step 2: Write sections

Write each section as LaTeX content. Save as `sections.json` in the output directory.

For thesis: also provide `abstract_en`, `keywords_zh`, `acknowledgements`, and cover info (`institution`, `degree`, `advisor`, `student_id`, `major`, `college`).

### Step 3: Assemble PDF

```bash
python3 scripts/assemble_paper.py --context context.json --sections sections.json
```

Auto-detects paper type. Thesis gets full cover page + TOC + bilingual abstract + acknowledgements.
Citations automatically formatted per paper type (GB/T 7714 for Chinese, APA/IEEE for English).
Statistical analysis results auto-injected into the paper.

---

## Mode B — One Command

```bash
python3 scripts/run_paper.py "TOPIC" --output ./output/auto_paper
```

Options: `--data data.csv` `--template ieee` `--type thesis`
Requires: `HIAPI_API_KEY` or `OPENAI_API_KEY` for LLM writing.

Pipeline: analyze topic → build math model → solve → generate charts → statistical analysis → write sections → format citations → compile PDF

---

## Statistical Analysis (integrated into paper output)

```python
from papercarator.statistical_analysis import StatisticalAnalyzer
sa = StatisticalAnalyzer()
sa.descriptive_stats(data)        # 描述统计 (n, mean, std, min, max, Q1, Q3, skewness, kurtosis)
sa.t_test(group1, group2)         # t检验 with Cohen's d effect size
sa.correlation(x, y)              # Pearson相关系数 with strength interpretation
sa.regression(x, y)               # 线性回归 (slope, intercept, R², std error)
sa.anova(g1, g2, g3)              # 单因素方差分析
sa.chi_square(observed)           # 卡方检验
sa.to_latex_table(stats)          # 转LaTeX表格（自动中文标签）
```

Statistics are automatically run on solution values and injected as subsections in the paper.

## Citation Formats (5) — integrated

gbt7714 (中国国标) | apa (APA 7th) | ieee (IEEE) | chicago (Chicago) | mla (MLA)

## Supported Math Models (16)

equation_system, optimization, multi_objective, differential, pde, queueing,
markov_chain, bayesian, statistical, network_flow, time_series, game_theory,
control_theory, clustering, graph_theory, fuzzy_logic

## Templates (6)

custom | ieee | acm | cjm | springer_lncs | thesis

## Quality Scoring (7 dimensions)

Completeness, structure, math rigor, visualization, reference quality, language, format.

## Verification

```bash
python3 scripts/quick_check.py ./output/my_paper
pytest
```