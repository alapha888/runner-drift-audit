# Day-1 re-walk snapshot — October 19, 2026

An intermediate run of the October 20 re-walk protocol, taken on the morning the
`ubuntu-latest` migration window opened — one day early, on purpose. Tomorrow's
report compares against the frozen October 13 baseline; this snapshot exists so
that anything that changes between today and tomorrow is visible, and so that
the re-walk script itself was proven end-to-end before the agreed day.

Companion files:

- Frozen baseline: `field-reports/2026-10-13-pre-cutover-self-audit.md`
  (scanner v0.3.2 — do not edit)
- Tomorrow's report skeleton: `field-reports/rewalk-20261020/2026-10-20-post-cutover-self-audit-SKELETON.md`
- Runner: `field-reports/rewalk-20261020/run-rewalk.sh`

## Run metadata

- Run at: 2026-10-18T17:43Z (Oct 19, 01:43 CST), and re-run after the script
  fix below at Oct 19, 01:5x CST with identical findings
- Scanner: v0.3.7 (latest release), file SHA256
  `3daa012b813d8cf3f9440a382e5d1fdbdc1ea26a6bd5a986467a3699a6156061`,
  repo HEAD `d582f3d`
- Test suite at run time: 64 passed

## Results — all three baseline rows reproduce exactly

| Target | Baseline (Oct 13, v0.3.2) | Day-1 snapshot (Oct 19, v0.3.7) | Delta |
|---|---|---|---|
| cn-ai-coding-workflow `test-install.yml` | 4 HIGH / 2 WARN | 4 HIGH / 2 WARN | none |
| cn-ai-coding-workflow-lite `test-install.yml` | 4 HIGH / 2 WARN | 4 HIGH / 2 WARN | none |
| runner-drift-audit self-test | 0 HIGH / 2 WARN | 0 HIGH / 2 WARN | none |

Rows that moved from checked-inert to flagged: none.
Rows that did not move: all of the above, plus the two manual rows from the
baseline (container images by tag; locale / timezone defaults) — the inventory
still contains no `container:` / `services:` image pulls, and the scanned steps
still only count files and grep frontmatter.

## One script bug found and fixed before it could corrupt tomorrow's report

The runner's third target still pointed at `pending-workflow-scope/`, the
directory that held `self-test.yml` on October 13 when it could not be pushed
(the token lacked the workflow scope). That scope was granted on October 15,
the file was pushed as `.github/workflows/self-test.yml` (commit `662c3bd`),
and the pending directory no longer exists. The unpatched script therefore
reported "No workflow files found" for target 3 — which, read naively, looks
like a change from the baseline (0 HIGH / 2 WARN → nothing scanned).

The runner now scans the repository root for that target, which finds exactly
`.github/workflows/self-test.yml` and reproduces the baseline row. This is a
path move, recorded here as protocol housekeeping — it is not a migration
effect and not a scanner-growth row.

## Version honesty: scanner growth since the v0.3.2 baseline

The scanner changed between the baseline and this snapshot. Per protocol,
these are scanner-growth rows, not migration rows:

- v0.3.4 — SARIF 2.1.0 export for GitHub Code Scanning (output format only;
  no finding changes)
- v0.3.5 — plain JSON export (output format only)
- v0.3.6 — Markdown job summary (output format only)
- v0.3.7 — new HIGH rule `RETIRED_LABEL` for `macos-14` / `macos-14-large` /
  `macos-14-xlarge` (retirement November 2, 2026; brownouts from October 19).
  This rule does not fire on any of the three re-walk targets — none of them
  references a `macos-14` label — which is why the counts above still match
  the v0.3.2 baseline exactly. It did fire in this morning's separate five-repo
  self-scan, where it caught a real `macos-14` pin in photoveil-ios that has
  since been fixed to `macos-15` (see
  `field-reports/2026-10-19-day1-self-scan.md`).

## What this does and does not show

This snapshot is a static re-scan: it shows the scanner's findings have not
moved on the first morning of the window. It does not show which image any
given `ubuntu-latest` run actually landed on — that is a runtime fact, read
from each run's setup step, as covered in
`docs/october-19-day-guide.md`. Tomorrow's re-walk repeats this same run;
any difference between this snapshot and tomorrow's is then either a workflow
edit made in between or a protocol problem, and will be reported as such in
the exchange with Yuhe He.

## Get the scanner

RunnerDriftAudit is free and open source (MIT): a single Python file, standard
library only, no dependencies, and it never phones home.

- Repository: https://github.com/alapha888/runner-drift-audit
- Action: `uses: alapha888/runner-drift-audit@v0.3.7`

If you maintain many repositories, [RunnerDriftAudit Pro](https://alapha888.gumroad.com/l/mepra)
($29 one-time) scans a whole workspace in one run and merges everything into a
single HTML report. The free single-repo tool above stays free either way.

## Limits

This is a line scanner with shell-aware heuristics, not a full YAML or shell
parser. Treat its findings as a review checklist, not as proof that a build is
safe. It does not execute workflows.
