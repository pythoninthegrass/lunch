# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

### FastHTML (Web UI - Primary)

Use `uv run app/main.py` to run the FastHTML web application on `localhost:8080`.

### Tauri Desktop App

The application can be packaged as a native macOS desktop app using Tauri v2 with the FastHTML backend bundled as a PyInstaller sidecar.

```bash
task tauri:build:arm64   # Build for Apple Silicon
task tauri:build:x64     # Build for Intel
task tauri:dev           # Development mode
task tauri:test-app      # Launch built app
```

**Architecture:**

```text
Tauri Shell
├── Native Window (WebView) ◄──► Python Sidecar (FastHTML Server)
│                            HTTP   localhost:8080
```

- Tauri spawns PyInstaller-bundled Python executable as sidecar
- WebView loads FastHTML UI from `localhost:8080`
- Graceful shutdown via POST to `/shutdown` endpoint

**Build outputs:**

- `.app`: `src-tauri/target/aarch64-apple-darwin/release/bundle/macos/Lunch.app`
- `.dmg`: `src-tauri/target/aarch64-apple-darwin/release/bundle/dmg/Lunch_*.dmg`

**Data storage:**

- Development: `app/data/lunch.db`
- Production (bundled): `~/Library/Application Support/Lunch/lunch.db`

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

This is a Python web application built with FastHTML for restaurant selection.

### Core Components

- **main.py**: Main application entry point containing FastHTML routes and UI
- **backend/db.py**: Database operations using SQLite with manual SQL queries
- **backend/service.py**: Business logic layer for restaurant management
- **backend/agent.py**: AI agent for restaurant info lookup using pydantic-ai
- **data/**: Contains SQLite database and CSV data files
- **static/**: Application assets (icons, images)

### Database Schema

- **lunch_list table**: Stores restaurants with their categories (cheap/Normal)
- **recent_lunch table**: Tracks the last 14 restaurant selections for round-robin logic
- **restaurant_info table**: Caches AI-fetched restaurant details

### Application Logic

- Round-robin restaurant selection to avoid repetition
- Category-based filtering (cheap vs Normal restaurants)
- Web UI allows adding/deleting restaurants dynamically
- Recent selection tracking prevents same restaurant appearing too frequently

### Configuration

- Python 3.12.11 required (specified in .tool-versions)
- Line length: 130 characters (ruff configuration)
- Uses uv for package management instead of pip
- Pre-commit hooks enforce code quality

### Development Tools

- **Ruff**: Linting and formatting (replaces black, isort, flake8)
- **Pytest**: Testing framework
- **Pre-commit**: Git hooks for code quality
- **mise**: Tool version management
- **Tauri v2**: Desktop app framework (Rust + WebView)
- **PyInstaller**: Python bundler for sidecar executable

### Key Dependencies

- **fasthtml**: Server-side HTML framework (primary UI)
- **uvicorn**: ASGI server for FastHTML
- **pydantic-ai**: LLM agent framework
- **sqlmodel**: Database ORM (though currently using raw SQL)
- **pyinstaller**: Bundles Python app for Tauri sidecar

### Project Structure

```text
lunch/
├── app/                    # Python application
│   ├── main.py             # FastHTML entry point
│   ├── backend/            # Database, services, agent
│   ├── static/             # Assets (logo, CSS)
│   └── data/               # SQLite DB, seed CSV
├── src-tauri/              # Tauri desktop wrapper
│   ├── src/                # Rust source
│   ├── bin/                # Sidecar binaries
│   ├── icons/              # App icons
│   └── tauri.conf.json     # Tauri config
├── pyinstaller/            # PyInstaller config
│   └── lunch.spec          # Build specification
├── taskfiles/              # Task runner configs
│   ├── tauri.yml           # Tauri/sidecar tasks
│   ├── npm.yml             # npm tasks
│   └── uv.yml              # uv/Python tasks
└── Taskfile.yml            # Main task entry point
```

## Testing Strategy

The project is configured for pytest with markers for unit, integration, e2e, and benchmark tests. Test files should be placed in a `tests/` directory following the pattern `test_*.py`.

## Context

- Context7 mcp libraries
  - astral-sh/uv
  - astral-sh/ruff
  - itamarst/eliot
  - pydantic/pydantic-ai
  - rohanadwankar/oxdraw
  - taskfile_dev
  - websites/basecoatui_com
  - websites/v2_tauri_app

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
