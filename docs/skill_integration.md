# Skill Integration Guide

## Goal

This document explains how to call PaperCarator as a reusable skill from Codex-like and Claude Code-like agents.

## Supported workflow

1. Provide a topic that fits a supported math-model family.
2. Run `python3.12 -m papercarator.cli analyze "<topic>"` when fit is uncertain.
3. Run the CLI with GitHub and VS Code side effects disabled unless explicitly needed.
4. Collect:
   - topic classification
   - model type
   - solver result
   - charts
   - 3D visualization
   - LaTeX and PDF

## Recommended presets

- `configs/skill_codex.yaml`
- `configs/skill_claude.yaml`

These presets keep the run focused on local artifact generation instead of external integrations.

## Suggested agent contract

### Inputs

- topic
- optional output directory
- optional template
- optional depth

### Outputs

- `paper/paper.tex`
- `paper/paper.pdf`
- supporting figures

### Success criteria

- model type is recognized
- solver succeeds
- PDF is generated
- artifact set is coherent with the selected model family
- generated sections reference the selected model and solver output, not only generic paper text

### Degraded mode

If classification returns `review`, `experimental`, `theoretical`, or generic `modeling`, treat the run as a modeling approximation. State the limitation before execution and prefer a narrower topic that names a model family, such as queueing, optimization, network flow, PDE, game theory, control theory, clustering, or time series.

## Current high-confidence model families

- equation systems
- optimization
- multi-objective optimization
- differential equations
- PDE heat-style problems
- queueing systems
- Markov chains
- regression/statistical analysis
- network flow / shortest path
- time-series forecasting
- game theory / Nash equilibrium
- control theory / PID stability
- clustering / K-means analysis

## Remaining integration gaps

- no citation retrieval pipeline
- no academic source-grounding layer
- no universal open-domain reasoning coverage
- 3D output is illustrative, not production CAD
