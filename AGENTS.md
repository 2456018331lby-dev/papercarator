# Repository Guidelines

## Project Structure & Module Organization
`papercarator/` is the main Python package. Core orchestration lives in `papercarator/core/`, topic analysis in `papercarator/planner/`, model construction and solving in `papercarator/math_modeling/`, charting and 3D output in `papercarator/visualization/`, and LaTeX generation in `papercarator/paper_writer/`. The CLI entry point is [papercarator/cli.py](/C:/Users/24560/Desktop/study/opendemo/papercarator/papercarator/cli.py). Tests live under `tests/`, example usage under `examples/`, configuration presets under `configs/`, and deeper design notes under `docs/`.

## Build, Test, and Development Commands
Install the editable dev environment with `python -m pip install -e ".[dev]"`. Use `python -m papercarator.cli --help` to inspect CLI options and `python -m papercarator.cli run "题目"` to run the pipeline locally. Run `python examples/basic_usage.py` for a simple end-to-end demo.

Quality commands:

- `pytest` runs the full test suite.
- `pytest tests/test_cli.py -v` targets one module during iteration.
- `pytest --cov=papercarator --cov-report=html` generates coverage output.
- `black papercarator tests` formats code.
- `ruff check papercarator tests` runs lint checks.
- `mypy papercarator` enforces typed module boundaries.

## Coding Style & Naming Conventions
Target Python 3.10+ and keep formatting compatible with `black` and `ruff` at a 100-character line length. Use 4-space indentation, `snake_case` for functions and modules, `PascalCase` for classes, and clear package names that match existing domains such as `planner`, `visualization`, or `paper_writer`. Prefer explicit type hints; `mypy` is configured with `disallow_untyped_defs = true`.

## Testing Guidelines
Pytest discovers files named `test_*.py`, classes named `Test*`, and functions named `test_*`. Add regression tests beside the closest existing module, for example `tests/test_pipeline.py` for pipeline changes. New behavior should include at least one positive-path test and one failure or edge-case assertion when practical.

## Commit & Pull Request Guidelines
Current history uses Conventional Commit prefixes such as `feat:`; continue with `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `style:`, or `chore:`. Keep commits focused and reviewable. Pull requests should explain the user-visible change, list verification commands run, link related issues, and include sample output or screenshots when CLI, visualization, or generated-paper behavior changes.

## Configuration & Environment Notes
LaTeX compilation requires a local TeX distribution such as MiKTeX or TeX Live. Optional Windows-only integrations may need `pywin32`; broader local setups can use `pip install -e ".[all]"`.
