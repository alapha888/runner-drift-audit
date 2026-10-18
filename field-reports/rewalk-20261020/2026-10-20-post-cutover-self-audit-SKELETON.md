# Post-cutover self-audit — 2026-10-20 (SKELETON — fill on the day)

Companion to the frozen baseline: `field-reports/2026-10-13-pre-cutover-self-audit.md`
(baseline scanner v0.3.2, do not edit that file; corrections land as dated addenda).
Protocol agreed with reader Yuhe He on 2026-10-13: he re-runs his own walkthrough
after the Oct 19–Nov 19 `ubuntu-latest` migration window opens; both sides compare
second reports line by line. Scanner-version changes are recorded separately from
platform-switch effects.

## How to run (5 minutes)

1. `bash field-reports/rewalk-20261020/run-rewalk.sh`
2. Paste the three scan outputs into the table below, row by row.
3. Fill the Version honesty section from `output/metadata.md`.
4. Reply to Yuhe He in the original dev.to thread with the delta summary and a
   link to this report once pushed.

## Baseline (frozen 2026-10-13, verified reproducible on 2026-10-14)

| Target | HIGH | WARN | Notes |
|---|---|---|---|
| cn-ai-coding-workflow `test-install.yml` | 4 | 2 | matrix `os:` axis: ubuntu-latest / macos-latest / windows-latest HIGH, plus standalone windows-latest job HIGH; checkout@v4 ×2 WARN. Disposition: accepted deliberately. |
| cn-ai-coding-workflow-lite `test-install.yml` | 4 | 2 | Same workflow, lite edition — same findings. |
| runner-drift-audit self-test (was `pending-workflow-scope/self-test.yml`) | 0 | 2 | Pins `ubuntu-24.04` in both jobs; only checkout@v4 WARN ×2. File has since been pushed as `.github/workflows/self-test.yml` (workflow scope granted Oct 15; commit `662c3bd`) — the runner now scans the repo root for this target; see the Oct 19 day-1 snapshot. State on Oct 20: ___ |
| Manual: container images by tag | inert | — | No `container:`/`services:`/image pulls in inventory. |
| Manual: locale / timezone defaults | inert | — | Steps count files and grep frontmatter only. |

## Oct-20 re-walk results (fill in)

| Target | HIGH | WARN | Delta vs baseline |
|---|---|---|---|
| cn-ai-coding-workflow | ___ | ___ | ___ |
| cn-ai-coding-workflow-lite | ___ | ___ | ___ |
| pending self-test | ___ | ___ | ___ |
| Manual: container images by tag | ___ | — | moved inert→flagged? ___ |
| Manual: locale / timezone defaults | ___ | — | moved inert→flagged? ___ |

Rows that did not move (must be listed, per protocol):
- ___

Rows that moved from checked-inert to flagged (must be listed, per protocol):
- ___ (or: none)

## Version honesty

- Scanner version used for this re-walk: ___ (from `output/metadata.md`: SHA256 + repo HEAD + latest release tag)
- Changes since v0.3.2, listed as scanner-growth rows (NOT migration rows):
  - ___ (or: none — scanner unchanged since v0.3.2)

## Migration-effect rows (platform switch only, scanner growth excluded)

- ___

## Exchange with Yuhe He

- His second report received: ___ (date / link)
- Line-by-line differences between the two reports: ___
- Follow-ups agreed: ___
