---
id: task-010
title: Refactor frontend to use Basecoat UI component library
status: To Do
assignee: []
created_date: '2025-12-04 17:58'
updated_date: '2025-12-04 18:01'
labels:
  - frontend
  - refactor
  - ui
  - basecoat
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refactor the Flet-based frontend (app/frontend/gui.py) to adopt Basecoat UI design language using Flet's theming system, maintaining cross-platform compatibility (desktop, web, mobile).

## Approach
Use Flet's theming and styling capabilities to implement Basecoat's design tokens:
- Color schemes and semantic colors
- Typography scale and font weights
- Spacing and padding conventions
- Border radius and shadow styles
- Component-specific styling (buttons, cards, inputs)

## Current State
- Frontend uses Flet (Flutter for Python) with native components
- LunchGUI class (~300 lines) with components: Image, Text, RadioGroup, BottomSheet, Buttons
- Methods: create_controls, setup_layout, set_callbacks, and various event handlers

## Basecoat Design Tokens to Adopt
- Colors: primary, secondary, muted, accent, destructive, border, background, foreground
- Button variants: btn (primary), btn-outline, btn-sm-outline
- Card structure: header, section, footer with consistent padding
- Form inputs: consistent border, focus ring styles
- Spacing: gap-2, gap-4, gap-6 equivalents

## Components to Restyle
- Banner image container → Card-like container
- Title and result text → Typography hierarchy
- Radio group → Styled radio/segmented control
- Action buttons → Basecoat button variants
- Bottom sheets → Card-styled dialogs
- Form inputs → Consistent input styling
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create Flet theme with Basecoat color palette and design tokens
- [ ] #2 Style buttons to match Basecoat btn/btn-outline variants
- [ ] #3 Update containers and layouts to match Basecoat card/spacing conventions
- [ ] #4 Maintain existing functionality (roll, add, delete, list restaurants)
- [ ] #5 Ensure consistent appearance across desktop, web, and mobile

- [ ] #6 Preserve dark/light theme support using Basecoat color semantics
<!-- AC:END -->
