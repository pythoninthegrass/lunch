---
id: task-001
title: 'Restructure project: move backend, frontend, static to app directory'
status: Done
assignee: []
created_date: '2025-12-02 23:53'
updated_date: '2025-12-09 23:22'
labels:
  - refactor
  - architecture
dependencies: []
priority: high
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Reorganize the lunch project to follow the django_ai_agent structure:
- Create top-level `app/` directory
- Move `backend/` (if exists) or create `app/backend/` for Python code
- Move frontend assets to `app/frontend/`
- Move static assets to `app/static/`
- Refactor all import paths and file references for new relative paths
- Update any configuration files (settings, etc.) to reflect new structure
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All source files moved to app/ directory structure
- [ ] #2 All imports and relative paths updated
- [ ] #3 Application runs successfully after restructure
- [ ] #4 No broken file references
<!-- AC:END -->
