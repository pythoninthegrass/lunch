---
id: task-011
title: Fix restaurant list view scroll indicator and dynamic resizing
status: To Do
assignee: []
created_date: '2025-12-09 00:26'
labels:
  - bug
  - frontend
  - flet
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The "All Restaurants" list view has issues with the scroll indicator (down arrow) and dynamic resizing:

1. **Scroll indicator not showing**: The down arrow should appear when there are more than 12 items, but it's not consistently visible. The indicator is placed inside a Stack overlay but may not be rendering correctly.

2. **List doesn't resize after deletions**: When items are deleted, the list container doesn't properly resize to fit the remaining content.

3. **Arrow visibility threshold**: Currently set to `> 12` items, but the actual number of visible items varies based on viewport size.

**Current implementation** (gui.py ~lines 499-560):
- Uses `ft.Column` with `scroll=ft.ScrollMode.AUTO` and `expand=True`
- Scroll indicator is positioned via `ft.Stack` overlay at bottom
- Threshold check: `self.list_scroll_indicator.visible = len(items) > 12`

**Attempted solutions**:
- Tried Column vs ListView approaches
- Tried different expand settings
- Used Stack to overlay indicator at bottom

**Desired behavior**:
- Show down arrow only when list content exceeds viewport
- Arrow should be fixed at bottom of list container (not scroll with content)
- List container should shrink to fit content when all items visible
- List should properly resize after item deletions
<!-- SECTION:DESCRIPTION:END -->
