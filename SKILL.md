---
name: papercarator
description: >
  Math-modeling paper generator. You (the AI) write the paper, scripts handle math and formatting.
  Use when user wants to generate an academic paper with mathematical modeling.
  Supports 16 model types. NOT for: literature-review-only, open-domain research, industrial CAD.
---

# PaperCarator — AI-Written Paper Generation

## How It Works (3 Steps)

### Step 1: Generate modeling data (you run this)
```bash
cd <papercarator-dir> && python3 scripts/generate_data.py "TOPIC" --output <dir>
```
This outputs JSON with: model type, equations, solution values, statistics, charts, algorithm pseudocode, and real literature from Semantic Scholar.

### Step 2: YOU write the paper (you do this)
Read the JSON from Step 1. Write each section as LaTeX content. Use the actual numbers from the solution. Cite the literature from the JSON. Write with depth — real analysis, not templates.

Save your written sections as a JSON file:
```json
{
  "abstract": "...",
  "introduction": "...",
  "related_work": "...",
  "methodology": "...",
  "experiments": "...",
  "results": "...",
  "conclusion": "...",
  "references": "\\bibitem{ref1} Author. Title. Journal, 2024."
}
```

### Step 3: Assemble into PDF (you run this)
```bash
python3 scripts/assemble_paper.py --context <context.json> --sections <sections.json> --template custom
```

## Quick Alternative (one command, uses external LLM)
```bash
python3 scripts/run_paper.py "TOPIC" --output <dir>
```
This calls MiniMax-M2.7 via API to write sections automatically. Set HIAPI_API_KEY in env.

## Writing Guidelines for Step 2

- Use actual numbers: "系统利用率 ρ=0.7031" not "求解成功"
- Cite real literature from the JSON's `literature` field
- Each section should be substantive (300-800 words)
- Include LaTeX math formulas for key equations
- Related work: categorize by method, discuss pros/cons
- Results: interpret what the numbers mean physically
- Use `\cite{ref1}` for citations, `\bibitem{ref1}` in references section

## Supported Models (16)

equation_system | optimization | multi_objective | differential | pde |
queueing | markov_chain | bayesian | statistical | network_flow |
time_series | game_theory | control_theory | clustering | graph_theory | fuzzy_logic

## Templates

custom (default) | ieee | acm | cjm | springer_lncs | thesis
