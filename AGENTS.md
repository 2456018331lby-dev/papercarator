# Repository Guidelines

## Project Structure & Module Organization
`papercarator/` is the main Python package. Core orchestration lives in `papercarator/core/`, topic analysis in `papercarator/planner/`, model construction and solving in `papercarator/math_modeling/`, charting and 3D output in `papercarator/visualization/`, and LaTeX generation in `papercarator/paper_writer/`. The CLI entry point is [papercarator/cli.py](papercarator/cli.py). Tests live under `tests/`, example usage under `examples/`, configuration presets under `configs/`, and deeper design notes under `docs/`. Scripts for end-to-end workflows in `scripts/`.

## Build, Test, and Development Commands
Install the editable dev environment with `python -m pip install -e ".[dev]"`. Run `python examples/basic_usage.py` for a simple end-to-end demo.

Quality commands:
- `pytest` runs the full test suite.
- `pytest tests/test_cli.py -v` targets one module during iteration.
- `pytest --cov=papercarator --cov-report=html` generates coverage output.
- `black papercarator tests` formats code.
- `ruff check papercarator tests` runs lint checks.
- `mypy papercarator` enforces typed module boundaries.

## Scripts (end-to-end)
- `python scripts/run_paper.py "题目"` — 一键生成论文（模式B）
- `python scripts/generate_data.py "题目"` — 生成建模数据+统计（模式A步骤1）
- `python scripts/assemble_paper.py` — 组装LaTeX→PDF（模式A步骤3）
- `python scripts/quick_check.py ./output` — 输出质量检查

## Coding Style & Naming Conventions
Target Python 3.10+ and keep formatting compatible with `black` and `ruff` at a 100-character line length. 4-space indent, `snake_case` for functions/modules, `PascalCase` for classes. Explicit type hints required; `mypy` configured with `disallow_untyped_defs = true`.

## Testing Guidelines
Pytest discovers files named `test_*.py`, classes named `Test*`, functions named `test_*`. Add regression tests beside the closest existing module. New behavior: at least one positive-path test and one failure/edge-case assertion.

## Commit & Pull Request Guidelines
Use Conventional Commit prefixes: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `style:`, `chore:`. PRs should explain the user-visible change, list verification commands, link related issues.

## Configuration & Environment Notes
LaTeX compilation requires a local TeX distribution (MiKTeX or TeX Live). Optional Windows-only integrations may need `pywin32`.