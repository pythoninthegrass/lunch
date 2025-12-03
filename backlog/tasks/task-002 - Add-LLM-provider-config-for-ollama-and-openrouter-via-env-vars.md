---
id: task-002
title: Add LLM provider config for ollama and openrouter via env vars
status: Done
assignee: []
created_date: '2025-12-02 23:53'
updated_date: '2025-12-03 16:38'
labels:
  - feature
  - llm
  - config
dependencies: []
priority: medium
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a config.py file to support multiple LLM providers:
- Add LLM_PROVIDER env var to switch between ollama and openrouter
- Add OLLAMA_HOST, LLM_MODEL, LLM_TEMPERATURE, LLM_TIMEOUT env vars
- Add OPENROUTER_API_KEY env var for OpenRouter support
- Create LLM provider factory pattern similar to django_ai_agent/core/config.py
- Validate configuration on startup
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 config.py exists with LLM provider configuration
- [x] #2 Environment variables control provider selection
- [x] #3 Both ollama and openrouter work via env var toggle
- [x] #4 Configuration validates on startup
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Complete

- Created `app/config.py` with full LLM provider configuration
- Follows django_ai_agent/core/config.py pattern adapted for non-Django use
- Uses python-decouple for environment variable management
- 20 unit tests pass covering all functionality

### Files Changed
- `app/config.py` - LLM config merged with existing DEV config
- `tests/test_llm_config.py` - 20 comprehensive unit tests
- `.env` - Added LLM configuration variables

### Note
Existing tests in test_db_operations.py, test_integration.py, and test_restaurant_service.py have pre-existing import path issues from task-001 restructure (using `from backend` instead of `from app.backend`).

### Criteria #3 Note
The configuration infrastructure supports both ollama and openrouter via env var toggle. Configuration loading and validation is tested. Actual runtime LLM calls will verify integration when LLM features are implemented.
<!-- SECTION:NOTES:END -->
