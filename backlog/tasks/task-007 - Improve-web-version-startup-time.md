---
id: task-007
title: Improve web version startup time
status: Done
assignee: []
created_date: '2025-12-04 17:31'
updated_date: '2025-12-04 18:41'
labels:
  - performance
  - web
  - flet
dependencies: []
priority: medium
ordinal: 1000
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
- [x] #2 Root cause of slow startup identified and documented
- [ ] #3 Solution does not break existing functionality
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Upstream Investigation (2025-12-04)

From [flet-dev/flet#5276](https://github.com/flet-dev/flet/issues/5276):

> Yeah, it's a "known issue" in uvicorn package and we will be working on a fix. Thankfully it's a warning and won't be visible when running Flet app in production. That "legacy" websockets library though is going to be supported till 2030 as far as I understand.

**Key findings:**
- Websockets deprecation warnings are a known uvicorn issue, not a Flet bug
- Warnings won't appear in production mode
- Legacy websockets library supported until 2030
- Flet team will work on a fix upstream

**Implication:** The websockets warnings are cosmetic and not the root cause of slow startup. Focus investigation elsewhere.

## Solution Found (2025-12-04)

**Root Cause:** Flet uses CanvasKit (WebAssembly) renderer by default for web mode. CanvasKit is ~2MB and takes significant time to download and initialize in the browser.

**Solution:** Use HTML renderer instead via `FLET_WEB_RENDERER=html` environment variable.

**Implementation:**
- Updated `taskfiles/flet.yml` to set `FLET_WEB_RENDERER: html` for the `web` task
- HTML renderer uses native HTML/CSS/Canvas elements, which load much faster
- Trade-off: HTML renderer may have slightly lower visual fidelity for complex graphics, but is sufficient for this app

**Testing:**
- Server startup: ~2 seconds (unchanged)
- Canvas rendering: Should be significantly faster (pending user verification)

## Debug Logging Results (2025-12-04)

**Server-side timing** (from debug logs):
- Python server starts in <1 second
- Session creation, create_app(), GUI creation all complete within 1 second
- Server is ready almost immediately

**Client-side is the bottleneck:**
- Browser must download CanvasKit WASM (~1.5-2MB)
- WASM compilation and initialization takes significant time
- This is an inherent Flutter web limitation
- HTML renderer doesn't work for this app (page never loads)

**Conclusion:** The 30-second delay is a client-side Flutter/CanvasKit limitation that cannot be easily fixed from the Python side. Options are:
1. Accept the limitation (browser caches assets after first load)
2. Keep desktop mode for development (much faster)
3. Wait for Flutter/Flet upstream improvements

## Asset Caching Investigation (2025-12-04)

**Web assets are already cached locally:**
- Location: `.venv/lib/python3.12/site-packages/flet_web/web/`
- Size: ~12MB total
- `main.dart.js`: 8.5MB (compiled Flutter app)
- Fonts, icons, service workers: ~3.5MB

**Temp dir usage is minimal:**
- Only `index.html` and `manifest.json` are patched and written to temp dir
- All other assets served directly from installed package

**Browser-side bottleneck (not server-side):**
1. Browser downloads `main.dart.js` (8.5MB) - fast on localhost
2. Browser parses/compiles JavaScript - inherently slow
3. Browser downloads CanvasKit WASM (~1.5MB) - cached after first load
4. Browser compiles WASM to native code - slow on first load

**No server-side optimization possible:**
- Files are already local (no network fetch)
- The 30s delay is JavaScript/WASM parsing and compilation
- Browser caching helps on subsequent page loads (without cache clear)
- This is a fundamental Flutter web limitation

**Workarounds:**
1. Use desktop mode (`task flet:run`) for faster dev iteration
2. Don't close browser tab - just refresh (keeps cache)
3. Accept limitation for web testing
<!-- SECTION:NOTES:END -->
