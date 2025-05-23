# TODO

* Document
  * Fill out [README.md](README.md#further-reading)
* Fix
  * `Error calculating lunch: No restaurants found with option: Normal`
    * Happens when there are no restaurants in the table
* UI/UX
  * Never roll the same option twice in a row
  * Clear last roll output after
    * 0 seconds after deleting a restaurant
    * 10 seconds after roll
  * Move "logo" to top left of container
* Build
  * justfile -> taskfile
* CI/CD
  * Docker
    * Refactor dockerfiles and devcontainer
  * GitHub Actions
    * semver
      * [release-please](https://github.com/marketplace/actions/release-please-action)
    * Lint
    * Format
    * Run tests
    * Build
  * ArgoCD / Flux
* Test
  * Unit tests
  * Integration tests
  * E2E tests
* Package
  * Web
    * Fly.io
    * Self-host
  * Desktop [Tauri](https://v1.tauri.app/) 
    * macOS
    * Linux
    * Windows
  * Mobile (TBD)
    * iOS
    * Android
* Extend
  * sqlite -> ~~postgres~~ [Litestream](https://litestream.io/) / [Turso](https://turso.tech/)
  * Fancy category
  * Images
  * Menus
  * API calls to Yelp, Google, etc.
  * Tinder swipe right/left mechanic hehehe
