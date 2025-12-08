# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

Use `uv run main.py` to run the application with the virtual environment activated.

### Flet Development Notes

- **Process Management**: Flet processes can accumulate during development. Always kill Flet processes after testing:
  ```bash
  pkill -f flet
  # or
  killall flet
  ```
- **Task Runner**: Use `task flet:run` for development (includes proper cleanup)
- **Background Processes**: When testing code changes, Flet may leave processes running. Check with `ps aux | grep flet` and clean up as needed.

### Flet Platform Builds

| Platform      | Python Runtime     | Package Compatibility           |
|---------------|--------------------|---------------------------------|
| Web (static)  | Pyodide (WASM)     | Very limited - pure Python only |
| Web (dynamic) | Server-side Python | Full compatibility              |
| Android/iOS   | Bundled CPython    | Most packages work              |
| Desktop       | Native Python      | Full compatibility              |

**Mobile caveats:**

- C extensions must be compiled for ARM architecture
- Some packages with native dependencies may need `--source-packages` flag
- SQLite works natively on mobile

**Build commands:**

```bash
task flet:build:web   # Static web (limited packages)
task flet:build:apk   # Android
task flet:build:ipa   # iOS (requires macOS + Xcode)
task flet:build       # macOS (default)
```

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
  - itamarst/eliot
  - pydantic/pydantic-ai
  - taskfile_dev
  - websites/basecoatui_com

<!-- BACKLOG.MD MCP GUIDELINES START -->

<CRITICAL_INSTRUCTION>

## BACKLOG WORKFLOW INSTRUCTIONS

This project uses Backlog.md MCP for all task and project management activities.

**CRITICAL GUIDANCE**

- If your client supports MCP resources, read `backlog://workflow/overview` to understand when and how to use Backlog for this project.
- If your client only supports tools or the above request fails, call `backlog.get_workflow_overview()` tool to load the tool-oriented overview (it lists the matching guide tools).

- **First time working here?** Read the overview resource IMMEDIATELY to learn the workflow
- **Already familiar?** You should have the overview cached ("## Backlog.md Overview (MCP)")
- **When to read it**: BEFORE creating tasks, or when you're unsure whether to track work

These guides cover:
- Decision framework for when to create tasks
- Search-first workflow to avoid duplicates
- Links to detailed guides for task creation, execution, and completion
- MCP tools reference

You MUST read the overview resource to understand the complete workflow. The information is NOT summarized here.

</CRITICAL_INSTRUCTION>

<!-- BACKLOG.MD MCP GUIDELINES END -->
