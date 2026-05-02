---
name: papercarator
description: >
  Academic paper generation skill. Supports thesis, journal, conference, review,
  experiment, case study, and math modeling papers. Two modes: (A) YOU write using
  math/stat data from scripts, or (B) one-command auto via external LLM. Features:
  16 math models, 7 paper types, 5 citation formats, statistical analysis, charts,
  PDF generation. NOT for: industrial CAD.
---

# PaperCarator — Academic Paper Skill

## Prerequisites

```bash
cd <papercarator-root> && pip install -e ".[dev]"
```
Requires: Python 3.10+, xelatex (MiKTeX or TeX Live).

## Paper Types (7)

| ID | Name | Pages | Language | Use Case |
|----|------|-------|----------|----------|
| thesis | 毕业论文 | 30-100 | zh | 本科/硕士/博士 |
| journal | 期刊论文 | 6-15 | en | SCI/EI/核心期刊 |
| conference | 会议论文 | 4-8 | en | 学术会议 |
| review | 综述论文 | 10-30 | zh | 文献综述/系统综述 |
| experiment | 实验论文 | 8-20 | en | 实验研究 |
| case_study | 案例研究 | 6-15 | zh | 案例分析/调研 |
| math_modeling | 数学建模 | 15-30 | zh | 建模竞赛/研究 |

## Citation Formats (5)

gbt7714 (中国国标) | apa (APA 7th) | ieee | chicago | mla

## Mode Selection

| Situation | Mode |
|-----------|------|
| Quality paper, you have context | **A** |
| User says "快速/一键" | **B** |
| Short on context tokens | **B** |

## Mode A — YOU Write (3 Steps)

**Step 1** — Generate data:
```bash
cd <papercarator-root>
python3 scripts/generate_data.py "TOPIC" --output ./output/my_paper
```
Output: context.json with model type, equations, solution values, charts, literature, paper type.

**Step 2** — Write sections as JSON:
```json
{
  "abstract": "200-500字，引用具体数值",
  "introduction": "研究背景+问题+贡献",
  "related_work": "文献综述，引用literature字段",
  "methodology": "方法描述，LaTeX公式",
  "experiments": "实验设置",
  "results": "结果分析，引用solution.values",
  "conclusion": "结论+局限性",
  "references": "\\bibitem{ref1} Author. Title. Journal, Year."
}
```

**Step 3** — Assemble PDF:
```bash
python3 scripts/assemble_paper.py --context context.json --sections sections.json
```

## Mode B — One Command

```bash
python3 scripts/run_paper.py "TOPIC" --output ./output/auto_paper
```

## Statistical Analysis

For experiment/thesis papers with data:
```python
from papercarator.statistical_analysis import StatisticalAnalyzer
sa = StatisticalAnalyzer()
stats = sa.descriptive_stats(data)        # 描述统计
t = sa.t_test(group1, group2)             # t检验
r = sa.correlation(x, y)                  # 相关分析
reg = sa.regression(x, y)                 # 回归分析
anova = sa.anova(group1, group2, group3)  # 方差分析
chi = sa.chi_square(observed)             # 卡方检验
latex = sa.to_latex_table(stats)          # 转LaTeX表格
```

## Supported Math Models (16)

equation_system | optimization | multi_objective | differential | pde |
queueing | markov_chain | bayesian | statistical | network_flow |
time_series | game_theory | control_theory | clustering | graph_theory | fuzzy_logic

## Templates

custom | ieee | acm | cjm | springer_lncs | thesis

## Verification

```bash
python3 scripts/quick_check.py ./output/my_paper
```
