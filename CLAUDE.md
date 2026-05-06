# PaperCarator for Claude Code

## What this is

PaperCarator is an AI-driven academic paper generation pipeline. Claude Code should use it as:

- A **two-mode paper generator**: (A) Claude writes using math data, or (B) one-command auto
- Supporting **7 paper types**: thesis, journal, conference, review, experiment, case study, math_modeling
- With **16 mathematical models**, statistical analysis, literature search, and concept diagrams

## Recommended Usage

**Default: Mode A — Claude writes the paper**

```bash
# Step 1: Generate math data + charts + statistics
cd <papercarator-root>
python3 scripts/generate_data.py "TOPIC" --output ./output/my_paper

# Step 2: Read the JSON output. Write sections as LaTeX.
# Save as sections.json in the output directory.

# Step 3: Assemble into PDF
python3 scripts/assemble_paper.py --context context.json --sections sections.json
```

**Fast mode: Mode B — one command auto**

```bash
python3 scripts/run_paper.py "TOPIC" --output ./output/auto_paper
```

Requires HIAPI_API_KEY in env for LLM writing.

## What to Verify

After generating:
- `paper/paper.pdf` exists and renders correctly
- All sections have substantive content (not template filler)
- Figures have descriptive Chinese captions
- References are real publications (5+ entries)
- Keywords are topic-specific, not generic

## Quality Check

```bash
python3 scripts/quick_check.py ./output/my_paper
```

## Boundaries

- Best as a **structured first draft**, not publication-ready final manuscript
- Requires real data for statistical rigor (use `--data data.csv`)
- Not suitable for: pure literature reviews without methodology, experimental papers without real data, industrial CAD design
- Mode B external LLM quality varies; Mode A (Claude writing) gives better results