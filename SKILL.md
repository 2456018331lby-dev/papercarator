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

| ID | Name | Pages | Lang | Use Case |
|----|------|-------|------|----------|
| thesis | 毕业论文 | 30-100 | zh | 本科/硕士/博士 |
| journal | 期刊论文 | 6-15 | en | SCI/EI/核心期刊 |
| conference | 会议论文 | 4-8 | en | 学术会议 |
| review | 综述论文 | 10-30 | zh | 文献综述 |
| experiment | 实验论文 | 8-20 | en | 实验研究 |
| case_study | 案例研究 | 6-15 | zh | 案例分析 |
| math_modeling | 数学建模 | 15-30 | zh | 建模竞赛 |

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
cd <papercarator-root>
python3 scripts/generate_data.py "TOPIC" --output ./output/my_paper
```

Output: context.json. Key fields:
- `solution.values` — 实际数值，写论文时必须引用
- `statistical_analysis` — 描述统计/回归/相关分析结果
- `literature` — 从 Semantic Scholar 抓的真实文献
- `charts` — 图表文件路径
- `algorithm` — 算法伪代码（LaTeX 格式）
- `paper_type` — 自动推断的论文类型

### Step 2: Write sections

Write each section as LaTeX content. Save as `sections.json` in the output directory.

**Section writing guidelines:**

| Section | Content | Word Count | Key Rules |
|---------|---------|-----------|-----------|
| abstract | 研究问题+方法+关键数值+结论 | 200-500 | 必须引用 solution.values 中的数字 |
| introduction | 背景→问题→贡献→结构 | 400-800 | 具体场景，不泛泛而谈 |
| related_work | 按方法分类综述 | 500-1000 | 引用 literature 字段，讨论优缺点 |
| methodology | 问题形式化+模型+求解 | 600-1200 | 必须有 LaTeX 公式，引用参数 |
| experiments | 目标+设置+指标 | 200-400 | 说明数据来源和评价指标 |
| results | 引用数值+含义+对比 | 400-800 | 引用 statistical_analysis 结果 |
| conclusion | 总结+局限+展望 | 200-400 | 列出 3-4 条具体结论 |
| references | \\bibitem 格式 | - | 引用 literature 字段的真实论文 |

**Thesis-specific sections (毕业论文额外章节):**

| Field | Content |
|-------|---------|
| abstract_en | English abstract (200-300 words) |
| keywords_zh | ["关键词1", "关键词2", ...] |
| keywords_en | ["keyword1", "keyword2", ...] |
| acknowledgements | 致谢内容 |
| author, student_id, institution, college, major, advisor | 封面信息 |

### Step 3: Assemble PDF

```bash
python3 scripts/assemble_paper.py --context context.json --sections sections.json
```

Auto-detects paper type from context. Thesis gets cover page + TOC + acknowledgements.

---

## Mode B — One Command

```bash
python3 scripts/run_paper.py "TOPIC" --output ./output/auto_paper
```

Options: `--data data.csv` `--template ieee`
Requires: `HIAPI_API_KEY` or `OPENAI_API_KEY` for LLM writing.

---

## Statistical Analysis

```python
from papercarator.statistical_analysis import StatisticalAnalyzer
sa = StatisticalAnalyzer()
sa.descriptive_stats(data)        # 描述统计
sa.t_test(group1, group2)         # t检验
sa.correlation(x, y)              # 相关分析
sa.regression(x, y)               # 回归分析
sa.anova(g1, g2, g3)              # 方差分析
sa.chi_square(observed)           # 卡方检验
sa.to_latex_table(stats)          # 转LaTeX表格
```

## Citation Formats (5)

gbt7714 | apa | ieee | chicago | mla

## Supported Math Models (16)

equation_system, optimization, multi_objective, differential, pde, queueing,
markov_chain, bayesian, statistical, network_flow, time_series, game_theory,
control_theory, clustering, graph_theory, fuzzy_logic

## Templates

custom | ieee | acm | cjm | springer_lncs | thesis

## Verification

```bash
python3 scripts/quick_check.py ./output/my_paper
```
