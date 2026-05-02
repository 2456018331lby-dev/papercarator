---
name: papercarator
description: >
  Math-modeling paper generator. Two modes: (A) YOU write the paper using math data
  from scripts, or (B) one-command auto via external LLM. Use when user wants a
  math-modeling paper with equations, charts, and PDF output. Supports 16 model types:
  optimization, equations, ODE/PDE, queueing, Markov, Bayesian, statistics, network flow,
  graph theory, time-series, game theory, control theory, clustering, multi-objective,
  fuzzy logic. NOT for: literature-review-only, open-domain research, industrial CAD.
---

# PaperCarator — Math-Modeling Paper Skill

## Prerequisites (one-time setup)

```bash
cd <papercarator-root>
pip install -e ".[dev]"
```

Requires: Python 3.10+, xelatex (MiKTeX or TeX Live).

## Mode Selection

| Situation | Mode | Why |
|-----------|------|-----|
| User wants quality paper, you have context | **A** | You write with your own intelligence |
| User says "快速/一键/自动生成" | **B** | One command, external LLM writes |
| You're short on context tokens | **B** | Don't have room for 6 sections |
| User provides CSV/Excel data file | **A** | Better data integration |

**Default: Mode A.** Only use B if user explicitly asks for speed.

---

## Mode A — YOU Write the Paper

### Step 1: Generate math data

```bash
cd <papercarator-root>
python3 scripts/generate_data.py "基于排队论的医院门诊流程优化研究" --output ./output/my_paper
```

This outputs JSON to stdout. Save it. Key fields you will use:

```json
{
  "topic": "基于排队论的医院门诊流程优化研究",
  "plan": {"paper_type": "queueing", "keywords": ["排队", "优化"], "difficulty": "medium"},
  "model": {"name": "M/M/c 排队系统模型", "type": "queueing", "parameters": {"arrival_rate": 4.5}},
  "solution": {"values": {"rho": 0.7031, "Lq": 1.375, "Wq": 0.3056}, "statistics": {...}},
  "charts": ["./output/my_paper/visualizations/charts/queue_curve.png", ...],
  "algorithm": "\\begin{algorithm}[H]\\caption{M/M/c 排队系统稳态分析}...",
  "literature": [{"title": "...", "authors": "...", "year": "2024", "doi": "..."}]
}
```

### Step 2: YOU write 6 sections

Save as `sections.json` in the output directory. Structure:

```json
{
  "abstract": "200-300字。引用 solution.values 中的具体数字。",
  "introduction": "400-600字。研究背景+问题提出+本文工作。",
  "related_work": "400-600字。按方法分类综述，引用 literature 字段。",
  "methodology": "500-800字。问题形式化+模型构建+求解策略。必须有LaTeX公式。",
  "experiments": "200-400字。实验目标+设置+评价指标。",
  "results": "400-600字。引用具体数值，分析物理含义。",
  "conclusion": "200-300字。主要结论+局限性+未来方向。",
  "references": "\\bibitem{ref1} Author. Title. Journal, Year.\n\\bibitem{ref2} ..."
}
```

**Writing rules:**
- Use REAL numbers: "ρ=0.7031" not "求解成功"
- Cite from `literature` field: "Green (2006) 分析了急诊排队系统..."
- LaTeX math: inline `$x$`, display `$$\sum_{i=1}^{n}$$`
- Related work: categorize by method, discuss pros/cons
- Results: interpret numbers physically ("利用率70.3%表明系统负载适中")

### Step 3: Assemble PDF

```bash
python3 scripts/assemble_paper.py \
  --context ./output/my_paper/context.json \
  --sections ./output/my_paper/sections.json \
  --template custom
```

Output: `./output/my_paper/paper/paper.pdf`

---

## Mode B — One-Command Auto

```bash
cd <papercarator-root>
python3 scripts/run_paper.py "基于贝叶斯推断的药物疗效评估研究" --output ./output/auto_paper
```

Options:
- `--data data.csv` — import real data
- `--template ieee` — IEEE format (custom/ieee/acm/cjm/springer_lncs/thesis)
- Requires: `HIAPI_API_KEY` or `OPENAI_API_KEY` in environment for LLM writing

Output: JSON summary with `success`, `pdf`, `quality_score`, `charts`, `suggestions`.

---

## Supported Models (16)

equation_system, optimization, multi_objective, differential, pde, queueing,
markov_chain, bayesian, statistical, network_flow, time_series, game_theory,
control_theory, clustering, graph_theory, fuzzy_logic

## Verification

After generating, run:
```bash
python3 scripts/quick_check.py ./output/my_paper
```

Checks: structure (9 sections), references (≥5), figures, captions, PDF existence.
Output: `PASS` / `WARN` / `FAIL` with scores.
