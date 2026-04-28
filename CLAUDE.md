# PaperCarator for Claude Code

## What this repo is

PaperCarator is a math-modeling paper generation pipeline.

Claude Code should treat it as:
- a structured modeling-and-writing toolchain
- not a general-purpose autonomous research system

## Safe usage pattern

Prefer topics that map cleanly to:
- optimization / multi-objective optimization
- equation systems
- ODE / PDE
- queueing systems
- Markov chains
- statistical regression
- network flow / shortest path
- time-series forecasting

## Recommended command

```bash
python3.12 -m papercarator.cli run "<topic>" --output <target_dir> --no-github --no-vscode
```

If using a config preset:

```bash
python3.12 -m papercarator.cli --config configs/skill_claude.yaml run "<topic>" --output <target_dir> --no-github --no-vscode
```

## What Claude Code should verify

After running, check:
- `paper/paper.pdf` exists
- `paper/paper.tex` exists
- at least one chart exists
- at least one 3D visualization exists when the topic calls for it

## Known boundary

Claude Code should not present outputs from this repo as publication-ready academic truth without extra review.

The generated paper is best treated as:
- a strong structured first draft
- a math-modeling report artifact
- a demonstration of a model-selection and generation pipeline
