# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

Use `uv run main.py` to run the application with the virtual environment activated.

## Common Development Commands

### Package Management & Environment

- `uv sync` - Sync dependencies from pyproject.toml and uv.lock
- `uv add <package>` - Add new dependency
- `uv add --optional dev <package>` - Add development dependency
- `uv pip freeze > requirements.txt` - Export requirements
- Always prefix commands with `uv run` or `source .venv/bin/activate` at the beginning of a session

### Code Quality & Formatting

- `ruff check .` - Run linter on entire codebase
- `ruff check --fix .` - Run linter and auto-fix issues
- `ruff format .` - Format code according to project style
- `mypy .` - Run type checking
- When editing markdown files, always follow `markdownlint -c .markdownlint.jsonc <markdown_file>` linting rules.

### Testing

- `pytest` - Run tests (once test suite is implemented)
- `pytest --cov` - Run tests with coverage
- `coverage report` - Show coverage report

### Pre-commit Hooks

- `pre-commit install` - Install pre-commit hooks
- `pre-commit run --all-files` - Run all pre-commit checks manually
- `pre-commit autoupdate` - Update hook versions

## Project Architecture

This is a Python desktop application built with Flet (Flutter for Python) for restaurant selection.

### Core Components

- **main.py**: Main application entry point containing the Flet GUI
- **utils/db.py**: Database operations using SQLite with manual SQL queries
- **data/**: Contains SQLite database and CSV data files
- **static/**: Application assets (icons, images)

### Database Schema

- **lunch_list table**: Stores restaurants with their categories (cheap/Normal)
- **recent_lunch table**: Tracks the last 14 restaurant selections for round-robin logic

### Application Logic

- Round-robin restaurant selection to avoid repetition
- Category-based filtering (cheap vs Normal restaurants)
- GUI allows adding/deleting restaurants dynamically
- Recent selection tracking prevents same restaurant appearing too frequently

### Configuration

- Python 3.12.11 required (specified in .tool-versions)
- Line length: 130 characters (ruff configuration)
- Uses uv for package management instead of pip
- Pre-commit hooks enforce code quality

### Development Tools

- **Ruff**: Linting and formatting (replaces black, isort, flake8)
- **Pytest**: Testing framework (tests directory not yet implemented)
- **Pre-commit**: Git hooks for code quality
- **mise**: Tool version management

### Key Dependencies

- **flet[all]**: GUI framework (Flutter for Python)
- **sqlmodel**: Database ORM (though currently using raw SQL)

## Testing Strategy

The project is configured for pytest with markers for unit, integration, e2e, and benchmark tests. Test files should be placed in a `tests/` directory following the pattern `test_*.py`.

## Context

- Context7 mcp libraries
  - astral-sh/uv
  - astral-sh/ruff
  - flet-dev/flet
  - taskfile_dev
