# Migration readiness report — ubuntu-latest 24.04 → 26.04

- Scanned root: `samples/bad`
- Generated: 2026-10-13
- Migration window for the `ubuntu-latest` label: October 19 - November 19, 2026
- Workflow files scanned: 1
- Findings: **6** total — HIGH: 3, WARN: 3

## Findings by workflow

### .github/workflows/ci.yml

| Severity | Line | Rule | Finding |
|---|---|---|---|
| HIGH | 5 | FLOATING_LABEL | runs-on 'ubuntu-latest' is a floating label; for Ubuntu it moves 24.04 -> 26.04 between Oct 19 and Nov 19, 2026. Pin ubuntu-24.04 to stay, or ubuntu-26.04 to migrate deliberately. |
| WARN | 7 | UNPINNED_ACTION | action 'actions/checkout' is referenced by mutable tag 'v4', not a full commit SHA; the tag can move under you. |
| WARN | 10 | DEFAULT_DRIFT | Java default changes 17 -> 25 in the Ubuntu 26.04 image (and Java 8 is removed); pin with actions/setup-java. |
| HIGH | 12 | REMOVED_TOOL | mercurial was removed from the Ubuntu 26.04 runner image. |
| HIGH | 13 | REMOVED_TOOL | webpack is no longer preinstalled globally in the Ubuntu 26.04 runner image (only n and yarn remain). |
| WARN | 14 | DEFAULT_DRIFT | CMake was pinned to 3.31.6 on 24.04 to avoid CMake 4.0 compatibility issues; the 26.04 image ships latest, so CMake 4 behavior may apply. |

## Toolset differences (Ubuntu 24.04 → 26.04)

| category | tool | change_type | ubuntu_2404 | ubuntu_2604 | ci_impact | mitigation |
|---|---|---|---|---|---|---|
| removed | mercurial (hg) | removed | preinstalled | removed | Workflows invoking hg will fail | Install mercurial explicitly or migrate to git |
| removed | mediainfo | removed | preinstalled | removed | Workflows invoking mediainfo will fail | Install mediainfo explicitly in a setup step |
| removed | sphinxsearch (searchd) | removed | preinstalled | removed | Workflows invoking sphinxsearch/searchd will fail | Install sphinxsearch explicitly or replace the search step |
| removed | haveged | removed | preinstalled | removed | Workflows invoking haveged will fail | Remove the haveged step or install it explicitly |
| removed | webpack (global) | removed_global | preinstalled globally | not preinstalled globally (only n and yarn remain) | Workflows calling webpack without a local install will fail | Add a local devDependency or call via npx |
| removed | gulp (global) | removed_global | preinstalled globally | not preinstalled globally (only n and yarn remain) | Workflows calling gulp without a local install will fail | Add a local devDependency or call via npx |
| removed | grunt (global) | removed_global | preinstalled globally | not preinstalled globally (only n and yarn remain) | Workflows calling grunt without a local install will fail | Add a local devDependency or call via npx |
| removed | parcel (global) | removed_global | preinstalled globally | not preinstalled globally (only n and yarn remain) | Workflows calling parcel without a local install will fail | Add a local devDependency or call via npx |
| removed | lerna (global) | removed_global | preinstalled globally | not preinstalled globally (only n and yarn remain) | Workflows calling lerna without a local install will fail | Add a local devDependency or call via npx |
| removed | newman (global) | removed_global | preinstalled globally | not preinstalled globally (only n and yarn remain) | Workflows calling newman without a local install will fail | Add a local devDependency or call via npx |
| removed | typescript (tsc) (global) | removed_global | preinstalled globally | not preinstalled globally (only n and yarn remain) | Workflows calling tsc without a local install will fail | Add typescript as a local devDependency or call via npx |
| removed | Java 8 | removed | available | removed | Workflows pinned to Java 8 will fail | Move to a supported Java version and pin with actions/setup-java |
| removed | gcc-12 / gfortran-12 | removed | available | removed (13/14/15 remain) | Workflows invoking gcc-12 or gfortran-12 will fail | Move to gcc/gfortran 13-15 or install 12 explicitly |
| removed | clang-16 / clang-17 | removed | available | removed (20/21/22 remain) | Workflows invoking clang-16 or clang-17 will fail | Move to clang 20-22 or install the old version explicitly |
| renamed | p7zip | renamed | p7zip-full | 7zip | Package-name and invocation assumptions may break | Check 7z invocations and package names against 7zip |
| removed | fastlane (ruby gem) | removed_global | bundled with rubygems | not bundled | Workflows calling fastlane without an install step will fail | Install fastlane explicitly in a setup step |
| default_drift | Java (default) | default_changed | 17 | 25 | Unpinned Java workflows silently build on a new major version | Pin with actions/setup-java |
| default_drift | Node (default) | default_changed | 22 | 24 | Unpinned Node workflows silently build on a new major version | Pin with actions/setup-node |
| default_drift | PHP | default_changed | 8.3 | 8.5 only | Unpinned PHP workflows move to 8.5 with no older option on the image | Pin with shivammathur/setup-php |
| default_drift | PostgreSQL | default_changed | 16 | 18 | Unpinned PostgreSQL services/defaults change major version | Pin a PostgreSQL version explicitly |
| default_drift | clang (default) | default_changed | 18 | 21 | Unpinned clang workflows silently build with a new major version | Pin a clang version explicitly |
| default_drift | Go (default) | default_changed | 1.24 | 1.26 | Unpinned Go workflows silently build with a new version | Pin with actions/setup-go |
| default_drift | Docker / Docker Compose | default_changed | 28 / 2.38.2 | 29.4.2 / 5.1.3 | Compose file behaviour may change under Compose v5 | Test compose files against Compose v5 and pin where needed |
| default_drift | CMake | unpinned | 3.31.6 (pinned to avoid CMake 4.0 issues) | latest | CMake 4 behaviour may apply to projects that never opted in | Pin a CMake version explicitly if CMake 4 is not yet adopted |

## Fix checklist

1. Inventory: list every file in .github/workflows and confirm each one is expected before changing anything.
2. [HIGH] .github/workflows/ci.yml line 5 (FLOATING_LABEL): Pin the runner label: use ubuntu-24.04 to stay on the current image, or ubuntu-26.04 to migrate deliberately. Finding: runs-on 'ubuntu-latest' is a floating label; for Ubuntu it moves 24.04 -> 26.04 between Oct 19 and Nov 19, 2026. Pin ubuntu-24.04 to stay, or ubuntu-26.04 to migrate deliberately.
3. [WARN] .github/workflows/ci.yml line 7 (UNPINNED_ACTION): Pin the action to a full commit SHA if your policy requires immutable refs. Finding: action 'actions/checkout' is referenced by mutable tag 'v4', not a full commit SHA; the tag can move under you.
4. [WARN] .github/workflows/ci.yml line 10 (DEFAULT_DRIFT): Pin the version explicitly (setup action, service/image pin, or version file) instead of relying on the image default. Finding: Java default changes 17 -> 25 in the Ubuntu 26.04 image (and Java 8 is removed); pin with actions/setup-java.
5. [HIGH] .github/workflows/ci.yml line 12 (REMOVED_TOOL): Replace or drop this step, or install the tool explicitly in a setup step before use. Finding: mercurial was removed from the Ubuntu 26.04 runner image.
6. [HIGH] .github/workflows/ci.yml line 13 (REMOVED_TOOL): Replace or drop this step, or install the tool explicitly in a setup step before use. Finding: webpack is no longer preinstalled globally in the Ubuntu 26.04 runner image (only n and yarn remain).
7. [WARN] .github/workflows/ci.yml line 14 (DEFAULT_DRIFT): Pin the version explicitly (setup action, service/image pin, or version file) instead of relying on the image default. Finding: CMake was pinned to 3.31.6 on 24.04 to avoid CMake 4.0 compatibility issues; the 26.04 image ships latest, so CMake 4 behavior may apply.
8. Re-run the scanner (or this report) until no HIGH findings remain.
9. Attach the final report to the migration PR so reviewers can see what was checked.

---
Generated by runner-drift-audit. Line scanner with heuristics, not a full YAML/shell parser; treat findings as a review checklist, not a proof.
Rule sources: actions/runner-images toolset-2404.json vs toolset-2604.json.
