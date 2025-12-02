---
id: task-003
title: Integrate pydantic-ai duckduckgo_search_tool for restaurant info lookup
status: To Do
assignee: []
created_date: '2025-12-02 23:53'
labels:
  - feature
  - ai
  - database
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use pydantic-ai's common tools implementation of duckduckgo_search_tool to look up restaurant information:
- Add pydantic-ai dependency if not present
- Implement restaurant info lookup using duckduckgo_search_tool
- Hardcode zip code to 73107 as stopgap
- Search for restaurant closest to zip code
- Create new database table for restaurant info with foreign key to restaurant name
- Store fetched info (address, phone, hours, etc.) in the new table
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 pydantic-ai duckduckgo_search_tool integrated
- [ ] #2 Restaurant lookup uses zip code 73107
- [ ] #3 New database table created with FK to restaurant name
- [ ] #4 Restaurant info stored in database after lookup
<!-- AC:END -->
