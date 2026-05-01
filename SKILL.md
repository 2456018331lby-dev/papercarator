---
name: papercarator
description: >
  Math-modeling paper generator. Two modes: (A) YOU write the paper using math data from scripts, or (B) one-command auto via external LLM. Use when user wants a math-modeling paper with equations, charts, and PDF. Supports 16 model types.
---

# PaperCarator Skill

## Decision: Which Mode?

**Mode A — You (the AI) write the paper** (default, recommended):
Use when: user wants a quality paper, you have context budget, user doesn't mind a few steps.
Benefit: YOU write with your own intelligence. Better quality, no external API cost.

**Mode B — One-command auto** (fallback):
Use when: user wants it fast, or you don't have context to write 6 sections.
Requirement: HIAPI_API_KEY or OPENAI_API_KEY in environment.

## Mode A: YOU Write (3 Steps)

**Step 1** — Run this command to get modeling data:
```bash
cd <papercarator-dir> && python3 scripts/generate_data.py "TOPIC" --output <output-dir>
```
Save the JSON output. It contains: model type, equations, solution values, statistics, chart paths, algorithm pseudocode, and real literature.

**Step 2** — Write each section as LaTeX. Create a JSON file with this structure:
```json
{
  "abstract": "Your abstract here with actual numbers from the solution...",
  "introduction": "Your introduction with research background...",
  "related_work": "Your literature review citing papers from the JSON...",
  "methodology": "Your method description with LaTeX equations...",
  "experiments": "Your experimental setup...",
  "results": "Your analysis with specific numbers from solution.values...",
  "conclusion": "Your conclusions...",
  "references": "\\bibitem{ref1} Author. Title. Journal, Year."
}
```

Writing rules:
- Use REAL numbers from `solution.values` (e.g., "ρ=0.7031" not "求解成功")
- Cite literature from the JSON's `literature` field
- Each section: 200-600 words, substantive analysis
- Include LaTeX math: inline `$...$`, display `$$...$$`
- Related work: categorize by method, discuss pros/cons
- Results: interpret what numbers mean physically

**Step 3** — Assemble into PDF:
```bash
python3 scripts/assemble_paper.py --context <context.json> --sections <your-sections.json> --template custom
```

## Mode B: One Command

```bash
cd <papercarator-dir> && python3 scripts/run_paper.py "TOPIC" --output <dir>
```
Optional: `--data data.csv` for real data, `--template ieee` for IEEE format.

## Supported Models (16)

equation_system | optimization | multi_objective | differential | pde |
queueing | markov_chain | bayesian | statistical | network_flow |
time_series | game_theory | control_theory | clustering | graph_theory | fuzzy_logic

## Templates

custom | ieee | acm | cjm | springer_lncs | thesis
