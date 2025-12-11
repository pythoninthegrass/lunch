---
id: task-012
title: Optimize uv/PyInstaller and Tauri build times
status: In Progress
assignee: []
created_date: '2025-12-09 23:19'
updated_date: '2025-12-10 17:20'
labels: []
dependencies: []
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Current build times:
- PyInstaller sidecar build: ~18 seconds
- Tauri build: ~37 seconds (36.54s compile + bundling)

Potential optimizations to investigate:

**PyInstaller:**
- Use --onedir instead of --onefile (faster builds, but larger distribution)
- Exclude unused modules (IPython, pytest, black, jedi, pygments detected in build)
- Use PyInstaller cache more effectively
- Consider alternatives:
  - ~~cosmofy~~ - REJECTED: `fastcore` (fasthtml dep) uses `os.sched_getaffinity()` which Cosmopolitan Python doesn't implement. Also 228MB binary vs 45MB.
  - [PEX](https://docs.pex-tool.org/scie.html#)
  - ~~[cx_freeze](https://github.com/marcelotduarte/cx_Freeze)~~
  - ~~[shiv](https://shiv.readthedocs.io/en/latest/)~~
  - ~~Nuitka~~
     
**Tauri:**
- Enable incremental compilation in Cargo
- Use lld or mold linker for faster linking
- Optimize Cargo.toml release profile
- Consider split-debuginfo for smaller binaries
- ~~Use sccache for Rust compilation caching~~
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## PEX SCIE Evaluation (2025-12-10)

**Results:**
- Build time: ~5 seconds (vs ~21s PyInstaller) - 4x faster
- Binary size: 31MB (vs 37MB PyInstaller) - 16% smaller
- Tauri integration: Works as drop-in replacement

**Build command:**
```bash
pex python-fasthtml uvicorn python-decouple sqlmodel httpx eliot pydantic pydantic-ai-slim certifi \
  -P app -e app.main --scie eager --scie-only --scie-pbs-stripped --scie-python-version 3.12 \
  -o lunch-pex
```

**Required code change:**
- Updated `is_frozen()` in `app/main.py` to detect PEX via `os.environ.get('PEX')` environment variable

**Caveats:**
- Need to stage app files separately (exclude build/, __pycache__, etc.)
- First run extracts Python to `~/.cache/nce` (~15MB)

**Recommendation:** PEX SCIE is a viable PyInstaller replacement with faster builds and smaller binaries.

## Rust Compile Time Optimizations (from corrode.dev)

**Linker Configuration (.cargo/config.toml):**
```toml
[build]
rustflags = ["-C", "link-arg=-fuse-ld=lld"]
```

**macOS-Specific (Cargo.toml):**
```toml
[profile.dev]
opt-level = 1
debug = 0
split-debuginfo = "unpacked"  # Can reduce compile time by 70%
strip = "debuginfo"
```

**Profiling & Dependency Cleanup:**
- `cargo build --timings` - visualize compilation bottlenecks and parallelism
- `cargo machete` - remove unused dependencies
- `cargo features prune` - disable unused crate features
- `cargo tree --duplicate` - consolidate multiple dependency versions

**macOS Tips:**
- Add terminal to Developer Tools (System Preferences → Security & Privacy) to exclude from Gatekeeper checks
- Use `lld` linker (or `mold` on Linux)

**Nightly Options:**
- Parallel frontend: `RUSTFLAGS="-Z threads=8" cargo +nightly build` (50% potential improvement)
- `rustc_codegen_cranelift` - faster compilation without optimization for local dev

**Source:** https://corrode.dev/blog/tips-for-faster-rust-compile-times/
<!-- SECTION:NOTES:END -->
