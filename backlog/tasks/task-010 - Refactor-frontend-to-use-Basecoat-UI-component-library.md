---
id: task-010
title: Refactor frontend to use Basecoat UI component library
status: In Progress
assignee: []
created_date: '2025-12-04 17:58'
updated_date: '2025-12-04 21:38'
labels:
  - frontend
  - refactor
  - ui
  - basecoat
dependencies: []
priority: medium
ordinal: 1000
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Mobile UI Reference Analysis (Dec 4, 2025)

Analyzed three production mobile apps for design patterns:

### Common Navigation Patterns
- **Bottom tab bar**: 4-5 icons, selected state uses pill-shaped highlight/background
- **Back navigation**: "< Back" text with chevron (not iOS back arrow)
- **Modal dismissal**: "Done" text button in top-right corner (blue/accent color)
- **Drill-down**: Chevron (>) on right side of list items
- **Horizontal tabs**: Scrollable tab bar for account/section switching

### Visual Design Tokens
- **Icons**: Flat, monochrome or single-accent-color, no 3D effects or gradients
- **Buttons**: Pill-shaped with rounded corners; outlined for secondary actions
- **Colors for meaning**: Green = positive/success, Red = negative/destructive/danger
- **Section headers**: Muted gray text, uppercase or sentence case
- **Separators**: Thin 1px lines between list items, not full-width
- **Whitespace**: Generous padding, especially on light themes

### Layout Patterns
- **Card-based**: White cards on colored backgrounds for focused content
- **List items**: Icon/avatar + text + optional right accessory (chevron, value, badge)
- **Sections**: Clear grouping with headers, consistent internal padding
- **Typography hierarchy**: Large bold for key data, regular for body, muted for secondary

### Theme Considerations
- Light theme: White/off-white background, dark text, subtle gray accents
- Dark theme: Pure black background (#000), white text, vibrant accent colors
- Both themes use same semantic color meanings (green/red)

### Viewport-Aware Behavior
- Full-width layouts on mobile
- Content should adapt to screen size
- Bottom navigation only on mobile; desktop could use sidebar or top nav
- Touch targets sized appropriately (44pt minimum)

### Actionable for Lunch App
1. Add bottom tab bar for mobile viewport (Roll, List, Settings)
2. Use "< Back" text pattern for detail/edit views
3. Style action buttons as pills with rounded corners
4. Use outlined style for secondary actions, filled for primary
5. "Cancel"/destructive actions as plain red text (no button chrome)
6. Detect viewport and switch navigation style (bottom tabs vs sidebar)
<!-- SECTION:NOTES:END -->
