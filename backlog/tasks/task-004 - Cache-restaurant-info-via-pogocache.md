---
id: task-004
title: Cache restaurant info via pogocache
status: To Do
assignee: []
created_date: '2025-12-02 23:53'
labels:
  - feature
  - caching
  - performance
dependencies:
  - task-003
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement caching for restaurant info lookups using pogocache:
- Add pogocache dependency
- Configure POGOCACHE_HOST and POGOCACHE_PORT env vars
- Cache restaurant info to avoid repeated API calls
- Set appropriate TTL for cached data
- Implement cache invalidation strategy
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 pogocache integrated and configured
- [ ] #2 Restaurant info cached after first lookup
- [ ] #3 Subsequent lookups hit cache
- [ ] #4 Cache TTL configured appropriately
<!-- AC:END -->
