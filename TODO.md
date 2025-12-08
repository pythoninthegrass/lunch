# TODO

* General
  * Reinstate the roll rotation logic
    * Keep track of rolls with timestamp
    * Skip already rolled restaurants until the total of outstanding restaurants have been shown
    * Choices reset after n days (14 is the default via env var)
  * Tighten ddg search
    * restaurant_name doesn't match address/description etc
* UI/UX
  * Move "logo" to top left of container
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
  * ~~Integration tests~~
  * E2E tests
* Package
  * Desktop
    * macOS
    * Linux
    * Windows
  * Web
    * Self-host
  * Mobile
    * iOS
    * Android
* Extend
  * Fancy category
  * Images
  * Menus
  * API calls to Yelp, Google, etc.
    * Maybe just cache info after scraping once
  * sqlite -> ~~postgres~~ [Litestream](https://litestream.io/) / [Turso](https://turso.tech/)
  * Tinder swipe right/left mechanic hehehe
