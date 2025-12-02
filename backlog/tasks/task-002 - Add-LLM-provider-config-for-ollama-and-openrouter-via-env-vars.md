---
id: task-002
title: Add LLM provider config for ollama and openrouter via env vars
status: To Do
assignee: []
created_date: '2025-12-02 23:53'
labels:
  - feature
  - llm
  - config
dependencies: []
priority: medium
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
- [ ] #1 config.py exists with LLM provider configuration
- [ ] #2 Environment variables control provider selection
- [ ] #3 Both ollama and openrouter work via env var toggle
- [ ] #4 Configuration validates on startup
<!-- AC:END -->
