# Repository Guidelines

## Project Overview
AI File Renamer is an intelligent file renaming tool that uses OpenAI's API to analyze file content and suggest descriptive filenames. The project keeps a small footprint with all logic contained in a single `main.py` file.

## Project Structure & Module Organization
Application entry point and core logic live in `main.py`. Shared modules should be grouped into a package named `ai_file_renamer/` (create the folder when you add the first module) and imported from `main.py`. Configuration and automation live at the repo root: `pyproject.toml` defines metadata, dependencies, and tool configuration (ruff, ty), `Makefile` wraps common tasks. 

## Build, Test, and Development Commands
- `make setup` — provisions Python 3.14 via `uv`, creates `.venv`, installs and locks dependencies. Run after cloning or whenever dependencies change.
- `make run` — executes `main.py` inside the managed virtualenv; use for manual smoke checks.
- `make lint` — runs `ruff` autofixes then `ty` for type checking; address warnings immediately.
- `make tidy` — formats Python, shell, and JSON files; prefer before commits to avoid noisy diffs.
- `make clean` — removes virtualenv, lockfiles, caches; run before packaging or when state drifts.

## Development Workflow
After making code edits, run `make tidy` followed by `make lint` to ensure code quality and consistency:
1. `make tidy` — formats code and sorts imports
2. `make lint` — fixes remaining linting issues and performs type checking

This ensures code is properly formatted before linting checks catch any remaining issues.

## Coding Style & Naming Conventions
Follow `ruff` defaults: 4-space indentation, 120-character lines, double quotes, import sorting via isort rules. Use snake_case for modules, functions, and variables; UpperCamelCase for classes; constants in UPPER_SNAKE. Prefer explicit relative imports within the project package. Type annotations are encouraged; `ty` validates them during linting.
