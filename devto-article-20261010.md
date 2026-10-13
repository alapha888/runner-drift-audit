---
title: ubuntu-latest moves to Ubuntu 26.04 on October 19 — 22 toolset differences that can break your CI
published: true
description: GitHub moves ubuntu-latest from 24.04 to 26.04 between Oct 19 and Nov 19, 2026. I diffed the official runner-images toolsets: Java 17→25, mercurial and global webpack removed, CMake unpinned, and more.
tags: githubactions, ci, devops, opensource
---

Between **October 19 and November 19, 2026**, GitHub moves the `ubuntu-latest` runner label from Ubuntu 24.04 to Ubuntu 26.04. Nothing in your repository changes — the machine underneath your CI does.

I diffed the official `actions/runner-images` toolsets (`toolset-2404.json` vs `toolset-2604.json`) on 2026-10-10 and found **22 differences**. These are the ones most likely to break or silently change a build:

## Removed outright

- **mercurial (`hg`)**, `mediainfo`, `sphinxsearch`, `haveged` — removed from the image
- **Globally preinstalled Node tools**: only `n` and `yarn` remain. `webpack`, `gulp`, `grunt`, `parcel`, `lerna`, `newman`, and `tsc` (typescript) are no longer preinstalled globally — a workflow that calls them without a local install or `npx` step will fail
- **Java 8** — removed; `gcc-12` / `gfortran-12` and `clang-16` / `clang-17` — removed
- `p7zip` is renamed to `7zip`; the `fastlane` gem is no longer bundled with rubygems

## Default versions that move under you

| Tool | 24.04 | 26.04 |
|---|---|---|
| Java (default) | 17 | 25 |
| Node (default) | 22 | 24 |
| PHP | 8.3 | 8.5 only |
| PostgreSQL | 16 | 18 |
| clang (default) | 18 | 21 |
| Go (default) | 1.24 | 1.26 |
| Docker / Compose | 28 / 2.38 | 29.4.2 / 5.1.3 |
| CMake | pinned at 3.31.6 | latest |

The CMake row deserves attention: on 24.04 it was deliberately held at 3.31.6 to avoid CMake 4.0 compatibility issues. On 26.04 it tracks latest, so CMake 4 behaviour may apply to projects that never opted in.

None of this matters if you pin a runner (`ubuntu-24.04`) and pin your tool versions with setup actions. It matters a lot if you use `ubuntu-latest` and rely on whatever happens to be installed.

## A 30-second check

I packaged the toolset diff as a small open-source scanner, **runner-drift-audit** (MIT, single-file Python, standard library only, no dependencies):

https://github.com/alapha888/runner-drift-audit

```bash
python3 runner_drift_audit.py /path/to/repo
```

It scans workflow files line by line and reports floating runner labels, invocations of removed tools, default-version drift where no setup action pins the version, and actions referenced by mutable tag instead of a full SHA. Exit code is 1 when any HIGH finding exists, so it can gate a CI job.

Tested behaviour, from the sample workflows bundled in the repo:

- A workflow using `ubuntu-latest`, calling `java`, `hg`, and a global `webpack`, and invoking `cmake` reports **3 HIGH** (floating label, mercurial removed, webpack no longer preinstalled) and **3 WARN** (unpinned `actions/checkout@v4`, Java default drift 17→25, CMake unpinned).
- A workflow pinned to `ubuntu-24.04`, with `actions/checkout` pinned by full SHA and Java pinned via `actions/setup-java`, reports **0 HIGH**.

## Limits

This is a line scanner with shell-aware heuristics (quotes, `sudo`/`env`/`VAR=val` prefixes, multi-line `run:` blocks), not a full YAML/shell parser. Treat findings as a review checklist, not a proof. It does not execute anything and does not phone home.

If your CI is green today on `ubuntu-latest`, the cheapest time to find out which of the 22 differences hits you is before October 19 — while you can still pin deliberately instead of debugging a runner you did not choose.
