---
id: task-006
title: Fix AI agent executor conflict in Flet desktop mode
status: Done
assignee: []
created_date: '2025-12-04 00:09'
updated_date: '2025-12-04 16:45'
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
- ✅ FIXED: Both web mode and desktop mode now work correctly

**Root Cause:**
httpx (used by pydantic-ai and duckduckgo_search_tool) uses Python's global ThreadPoolExecutor. Flet's desktop mode marks this executor as "shutting down" during its event loop management, causing the error.

**Solution Implemented:**
Created synchronous API integrations for both Ollama and OpenRouter providers that bypass pydantic-ai's async httpx usage entirely. The system now uses direct synchronous HTTP requests to the respective APIs instead of going through pydantic-ai's async framework, avoiding ThreadPoolExecutor conflicts in Flet desktop mode.

**Changes Made:**
1. Updated `app/backend/agent.py`:
   - Modified `lookup_restaurant_info()` to use synchronous requests for both Ollama and OpenRouter providers
   - Improved synchronous DuckDuckGo search tool using DuckDuckGo instant answers API
   - Falls back to pydantic-ai approach only for unsupported providers
2. Maintained backward compatibility with existing async interfaces

**Provider Support:**
- ✅ Ollama: Synchronous HTTP requests to `/api/generate` endpoint
- ✅ OpenRouter: Synchronous HTTP requests to `/api/v1/chat/completions` endpoint
- ✅ Fallback: pydantic-ai for any other providers (may have issues in Flet desktop mode)

**Relevant Files:**
- `app/backend/agent.py` - RestaurantSearchAgent with search() method
- `app/backend/service.py` - lookup_info_sync() called via page.run_thread()
- `app/main.py` - Flet app entry point
<!-- SECTION:DESCRIPTION:END -->
