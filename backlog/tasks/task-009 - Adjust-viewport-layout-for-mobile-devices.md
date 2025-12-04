---
id: task-009
title: Adjust viewport layout for mobile devices
status: Done
assignee: []
created_date: '2025-12-04 17:53'
updated_date: '2025-12-04 18:04'
labels:
  - ui
  - responsive
  - mobile
dependencies: []
priority: medium
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The current layout doesn't fit properly on mobile viewports. On iPhone 13 mini (375x812 logical pixels - the smallest supported viewport), the button row is cut off and the "List All" button is not visible.

**Current Issues:**
- Button row extends beyond viewport width on mobile
- "List All" button is completely cut off on iPhone 13 mini
- No responsive layout adjustments for narrow screens

**Reference Screenshots:**
- Mobile: `/Users/lance/Downloads/http10.5.4.1098551appmain.py.jpeg`
- Desktop: `/Users/lance/Desktop/Screenshot 2025-12-04 at 11-52-49 Lunch.png`

**Target Viewport:**
- Minimum supported: iPhone 13 mini (375x812 points)
- Must also work on larger phones and desktop
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 All buttons visible on iPhone 13 mini viewport (375px width)
- [x] #2 Buttons remain accessible and tappable on mobile
- [x] #3 Layout adapts gracefully to different screen sizes
- [x] #4 Desktop layout still works correctly
- [x] #5 ASCII art banner scales or adjusts for narrow screens
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation

Changes made to `app/frontend/gui.py`:

1. **Button row**: Added `wrap=True` and `spacing=10`, `run_spacing=10` to allow buttons to wrap on narrow viewports. Removed unnecessary Container wrappers around buttons.

2. **Banner image**: Reduced width from 500px to 350px to fit within iPhone 13 mini viewport (375px).

## Testing

Verified via Playwright at:
- 375x812 (iPhone 13 mini): Buttons wrap - 3 on first row, 1 on second row
- 1024x768 (desktop): All 4 buttons fit on single row

All 96 unit tests pass.
<!-- SECTION:NOTES:END -->
