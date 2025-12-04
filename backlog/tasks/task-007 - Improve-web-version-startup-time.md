---
id: task-007
title: Improve web version startup time
status: To Do
assignee: []
created_date: '2025-12-04 17:31'
labels:
  - performance
  - web
  - flet
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Flet web version takes approximately 30 seconds to start each time it's restarted. This significantly impacts development iteration speed and user experience.

**Current behavior:**
- `task flet:web` takes ~30s before the app is accessible
- Various deprecation warnings from websockets library appear during startup

**Investigation areas:**
- Profile startup to identify bottlenecks
- Check if websockets deprecation warnings relate to performance
- Review Flet web compilation/bundling process
- Consider caching strategies for web assets
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Web version starts in under 10 seconds
- [ ] #2 Root cause of slow startup identified and documented
- [ ] #3 Solution does not break existing functionality
<!-- AC:END -->
