# Repository Guidelines

## Project Overview
AI File Renamer is an intelligent file renaming tool that uses OpenAI's API to analyze file content and suggest descriptive filenames. The project keeps a small footprint with all logic contained in a single `main.py` file.

## Project Structure & Module Organization
Application entry point and core logic live in `main.py`. Shared modules should be grouped into a package named `ai_file_renamer/` (create the folder when you add the first module) and imported from `main.py`. Configuration and automation live at the repo root: `pyproject.toml` defines metadata, dependencies, and tool configuration (ruff, ty), `Makefile` wraps common tasks. Place automated tests under `tests/` mirroring the package structure. Keep generated artifacts (e.g., `.venv`, caches) and sensitive data (API keys) out of version control; the existing `.gitignore` already covers the standard entries.

## Build, Test, and Development Commands
- `make setup` — provisions Python 3.14 via `uv`, creates `.venv`, installs and locks dependencies. Run after cloning or whenever dependencies change.
- `make run` — executes `main.py` inside the managed virtualenv; use for manual smoke checks.
- `make lint` — runs `ruff` autofixes then `ty` for type checking; address warnings immediately.
- `make tidy` — formats Python, shell, and JSON files; prefer before commits to avoid noisy diffs.
- `make clean` — removes virtualenv, lockfiles, caches; run before packaging or when state drifts.

## Coding Style & Naming Conventions
Follow `ruff` defaults: 4-space indentation, 120-character lines, double quotes, import sorting via isort rules. Use snake_case for modules, functions, and variables; UpperCamelCase for classes; constants in UPPER_SNAKE. Prefer explicit relative imports within the project package. Type annotations are encouraged; `ty` validates them during linting.

## Testing Guidelines
Add a `tests/` package with `__init__.py` and mirror the module layout (`tests/test_main.py`, etc.). Leverage the standard library `unittest` or add `pytest` to `pyproject.toml` and the Makefile when test coverage grows. Name test functions with `test_<behavior>` and keep fixtures short. Run the suite via `uv run python -m unittest` (or `uv run pytest` if adopted) before pushing. Target line coverage above 80% for new modules.

## Commit & Pull Request Guidelines
Keep commits focused and in the imperative mood (`Add run target`, `Refactor setup workflow`) as seen in the log. Reference linked issues in the commit body when applicable. Pull requests should include: a concise summary of changes, testing evidence (commands or screenshots), any follow-up tasks, and mention of breaking changes. Request review once linting and tests pass and CI (when available) is green.
