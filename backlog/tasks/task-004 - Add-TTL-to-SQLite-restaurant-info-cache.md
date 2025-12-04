---
id: task-004
title: Add TTL to SQLite restaurant info cache
status: Done
assignee: []
created_date: '2025-12-02 23:53'
updated_date: '2025-12-04 17:22'
labels:
  - feature
  - caching
dependencies:
  - task-003
priority: medium
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement cache expiration for restaurant info using the existing SQLite `restaurant_info` table:
- Add TTL check to `get_restaurant_info()` using the existing `last_updated` column
- Return None for stale entries (configurable max age, default 7 days)
- Caller triggers fresh lookup when cache miss or stale
- No new infrastructure required - uses existing SQLite storage
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 get_restaurant_info() checks last_updated against configurable TTL
- [x] #2 Stale entries trigger fresh LLM/search lookup
- [x] #3 TTL configurable via environment variable or config
- [x] #4 Existing restaurant_info table schema unchanged
<!-- AC:END -->
