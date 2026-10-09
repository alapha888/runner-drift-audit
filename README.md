# runner-drift-audit

Scans GitHub Actions workflows for floating runner labels, unpinned action refs, and tool-version drift ahead of the ubuntu-latest 24.04→26.04 migration.

GitHub moves the `ubuntu-latest` label from Ubuntu 24.04 to Ubuntu 26.04 between **October 19 and November 19, 2026**. Nothing in your repository changes — the machine underneath your CI does. This tool scans your workflow files and reports, line by line, what is likely to break or silently change.

Free, MIT, single-file Python (stdlib only, no dependencies).

## Usage

```bash
python3 runner_drift_audit.py [path-to-repo]   # default: current directory
```

Exit code is 1 when any HIGH finding exists, so it can gate a CI job. Sample workflows live in `samples/bad` and `samples/clean`.

## What it checks

Rules are grounded in a diff of the official `actions/runner-images` toolsets (`toolset-2404.json` vs `toolset-2604.json`, compared 2026-10-10 — 22 differences):

| Rule | Severity | Examples from the official toolset diff |
|---|---|---|
| Floating runner label | HIGH | `runs-on: ubuntu-latest` (also quoted / list forms) |
| Removed tool invoked in a run step | HIGH | `hg` (mercurial removed), `mediainfo`, `sphinxsearch`, `haveged`, `fastlane` gem, globally preinstalled `webpack`/`gulp`/`grunt`/`parcel`/`lerna`/`newman`/`tsc` (only `n` and `yarn` remain), `gcc-12`, `clang-16/17`, `p7zip` |
| Default version drift (no setup action pins it) | WARN | Java 17→25 (Java 8 removed), Node 22→24, PHP 8.3→8.5 only, PostgreSQL 16→18, clang 18→21, Go 1.24→1.26, CMake unpinned (was held at 3.31.6 to avoid CMake 4.0 issues), Docker 28→29 / Compose 2.38→5.1 |
| Action referenced by mutable tag instead of a full SHA | WARN | `uses: actions/checkout@v4` |

## Limits

- This is a line scanner with shell-aware heuristics (quotes, `sudo`/`env`/`VAR=val` prefixes, multi-line `run:` blocks), not a full YAML/shell parser. Treat findings as a review checklist, not a proof.
- It checks invocations in `run:` steps and labels in `runs-on:`; it does not execute anything and does not phone home.

## Planned paid option (validation only — not built, not for sale yet)

A one-time **fleet audit**: one report across every repo in your GitHub account or org, priced at **$29 one-time** if built. It will only be built if at least 20 people ask for it before the migration window closes on November 19, 2026. To register interest, [email the maintainer](mailto:alapha888@gmail.com?subject=%5BRunnerDrift%20Fleet%5D%20interest) with subject `[RunnerDrift Fleet] interest` and say how many repos you would scan. No payment, no newsletter — one reply if it ships, one if it doesn't.
