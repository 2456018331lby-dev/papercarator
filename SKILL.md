# PaperCarator Skill

## Purpose

PaperCarator is a math-modeling-first paper generation skill for Codex-style agents.

It is designed for prompts where the user wants:
- topic analysis
- mathematical modeling
- solver output
- charts and a simple 3D visualization
- a LaTeX paper and PDF

## Best-fit tasks

Use this skill when the topic can be abstracted into one of the currently supported model families:
- `equation_system`
- `optimization`
- `multi_objective`
- `differential`
- `pde`
- `queueing`
- `markov_chain`
- `statistical`
- `network_flow`
- `time_series`

## Do not overclaim

This skill is not a universal research agent.

It works best for structured math-modeling topics.
It is not yet a reliable choice for:
- literature-review-only papers
- open-domain science research
- citation-heavy academic writing
- industrial CAD-grade 3D modeling

## Recommended invocation

```bash
python3.12 -m papercarator.cli run "<topic>" --output <target_dir> --no-github --no-vscode
```

Recommended config presets:
- Codex-oriented: `configs/skill_codex.yaml`
- Claude Code-oriented: `configs/skill_claude.yaml`

## Expected outputs

Typical generated files:
- `paper/paper.tex`
- `paper/paper.pdf`
- chart images in `paper/`
- chart/3D source images in `visualizations/`

## Prompt pattern

Good prompt shape:

```text
Generate a math-modeling paper for:
<topic>

Constraints:
- prioritize internal modeling over literature claims
- produce charts and one 3D visualization
- export LaTeX and PDF
```

## Operational notes

- On Windows, use `python3.12 -m papercarator.cli`, not `python3.12 -m papercarator`
- The CLI is already adjusted to avoid common `gbk` terminal crashes
- PDF generation requires `xelatex`
