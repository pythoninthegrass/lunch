---
id: task-006
title: Fix AI agent executor conflict in Flet desktop mode
status: In Progress
assignee: []
created_date: '2025-12-04 00:09'
updated_date: '2025-12-04 00:13'
labels:
  - bug
  - flet
  - pydantic-ai
  - async
dependencies: []
priority: medium
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Background AI restaurant lookups using pydantic-ai fail in Flet desktop mode with "cannot schedule new futures after interpreter shutdown" error.

**Current Status:**
- Web mode (`flet run --web`): Works with nest_asyncio
- Desktop mode (`ft.app()`): Still fails

**Root Cause:**
httpx (used by pydantic-ai and duckduckgo_search_tool) uses Python's global ThreadPoolExecutor. Flet's desktop mode marks this executor as "shutting down" during its event loop management, causing the error.

**Attempted Solutions:**
1. Custom event loop with dedicated ThreadPoolExecutor - didn't work
2. nest_asyncio - works in web mode only

**Potential Solutions to Try:**
1. HTTP microservice (FastAPI) - run AI agent in separate process, call via HTTP
2. Subprocess isolation - spawn separate Python process for AI lookups
3. Custom httpx client injection - if pydantic-ai supports it
4. Investigate Flet desktop vs web threading differences

**Relevant Files:**
- `app/backend/agent.py` - RestaurantSearchAgent with search() method
- `app/backend/service.py` - lookup_info_sync() called via page.run_thread()
- `app/main.py` - Flet app entry point
<!-- SECTION:DESCRIPTION:END -->
