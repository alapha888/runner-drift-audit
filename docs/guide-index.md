# RunnerDriftAudit guide index: every guide, by the job you are doing

The guides in this repository grew one at a time — a page per rule, per output format, and per date in the rollout window. This page is the map: which guide to read for which job, in which order, and what each one does not cover. Everything linked here is in this repository unless marked as a field report.

## Start here

- **You have not scanned yet.** Run the scanner first (see the [README](https://github.com/alapha888/runner-drift-audit#readme)); the guides below assume you have findings in hand.
- **You have findings and want to fix them.** Go to the per-rule guides below — one page per rule ID in your output.
- **You want the findings somewhere other than a log.** Go to the output-format guides: SARIF, JSON, job summary, and CI gating.
- **You are working during the rollout window (October 19 – November 19, 2026).** Go to the timeline guides.

## Fixing findings, rule by rule

| Rule ID | Severity | Guide |
|---|---|---|
| `RETIRED_LABEL` | HIGH | [macOS 14 runner retirement](macos-14-retirement.md) — the retired labels, the brownout windows before the November 2, 2026 retirement, and the migration choices. |
| `REMOVED_TOOL` | HIGH | [Replacing removed tools](replacing-removed-tools.md) — per-group fix paths for tools removed from the Ubuntu 26.04 image, and what a re-scan should show. |
| `DEFAULT_DRIFT` | WARN | [Pinning default tool versions](pinning-default-versions.md) — per-tool pins, and why some warnings stay visible after pinning. |
| `UNPINNED_ACTION` | WARN | [Pinning actions by commit SHA](pinning-actions-by-sha.md) — resolving a tag to its SHA, writing the pin with a version comment, and keeping pins fresh with Dependabot. |
| `INDIRECT_RUNS_ON` | WARN | [Resolving indirect runner labels](resolving-indirect-runs-on.md) — per-source fix paths for labels fed by `env` / `vars` / `inputs`, and why the warning can stay visible after a fix at the source. |
| `FLOATING_LABEL` | HIGH | [Pinning floating runner labels](pinning-runner-labels.md) — the two deliberate pins for `ubuntu-latest`, what to do with the other `-latest` labels, and what a re-scan should show. |

The full background table behind the Ubuntu rules is [Ubuntu 26.04 toolset changes](ubuntu-2604-toolset-changes.md): every removed tool, global removal, rename, and default-version jump, with what to do for each. The same differences ship as a machine-readable CSV in the repository root.

## Output formats and gating

- [SARIF and GitHub Code Scanning](sarif-code-scanning.md) — findings as SARIF 2.1.0 alerts in the Security tab: the six rule IDs, the severity mapping, and the two workflow details that decide whether alerts actually reach the tab.
- [Plain JSON export](json-export.md) — the schema v1 fields, the empty-scan behaviour, and what the JSON export does not do.
- [Job summary](job-summary.md) — the Markdown summary format on the run page, the empty-scan behaviour, and its limits.
- [Using RunnerDriftAudit as a CI gate](ci-gate-patterns.md) — the exit-code contract (including why a usage error shares exit code 1 with real findings, and where exit code 2 comes from) and three patterns: report-only first, enforce on workflow changes, and a scheduled re-scan.

## Timeline guides for the rollout window

- [October 19 eve checklist](october-19-eve-checklist.md) — five steps for the evening before both October 19 changes. Written for October 18; the steps still work as a pre-window check before any later brownout.
- [October 19 day guide](october-19-day-guide.md) — the hour-by-hour timeline for the first day, and first-failure triage.
- [After the first brownout](after-the-first-brownout.md) — the morning-after checklist for October 20: sorting the night's failures by the clock, why a green run today is a reprieve rather than a fix, and migrating while both labels still work.
- [Rollout-week playbook](rollout-week-playbook.md) — for the weeks when the same workflow can land on either image from one run to the next (October 19 – November 19, 2026).

## Field reports (what happened when the scanner ran on real repositories)

- [Pre-cutover self-audit — 2026-10-13](../field-reports/2026-10-13-pre-cutover-self-audit.md) — the migration checklist run against the author's own workflows before the window opened.
- [October 19, morning: I scanned my own repos first](../field-reports/2026-10-19-day1-self-scan.md) — five repositories, 11 HIGH findings, and one repository still on `macos-14` fixed before that night's brownout.
- [Day-1 re-walk snapshot — October 19, 2026](../field-reports/2026-10-19-day1-rewalk-snapshot.md) — an intermediate run of the October 20 re-walk protocol: the October 13 baseline reproduces exactly.
- [Brownout eve: the rest of the estate, swept](../field-reports/2026-10-19-brownout-eve-estate-sweep.md) — the other 17 non-fork repos scanned from fresh clones an hour before the first brownout; the only HIGH findings were the twice-recorded deliberate `windows-latest` float in pubaudit-windows.
- [Post-cutover self-audit — 2026-10-20](../field-reports/2026-10-20-post-cutover-self-audit.md) — the frozen October 13 baseline re-run with scanner v0.3.7 after the window opened: identical rows (4/2, 4/2, 0/2), no inert-to-flagged moves, and a version-honesty table separating scanner changes from platform effects.
- [Day-3 re-walk — 2026-10-21](../field-reports/2026-10-21-day3-rewalk.md) — the same frozen inventory re-run on day 3 of the window with scanner v0.3.8: identical rows again (4/2, 4/2, 0/2), no inert-to-flagged moves, and the v0.3.8 dedupe fix recorded as scanner growth, not a migration effect.
- [Day-4 re-walk — 2026-10-22](../field-reports/2026-10-22-day4-rewalk.md) — the same frozen inventory re-run on day 4 of the window with scanner v0.3.8: identical rows again (4/2, 4/2, 0/2), no inert-to-flagged moves, and the scanner byte-identical to October 21, so this re-walk introduces no scanner-version variable at all.
- [Day-5 re-walk — 2026-10-23](../field-reports/2026-10-23-day5-rewalk.md) — the same frozen inventory re-run on day 5 of the window with scanner v0.3.8: identical rows again (4/2, 4/2, 0/2), no inert-to-flagged moves, and the scanner byte-identical to October 20, 21 and 22, so four consecutive re-walks introduce no scanner-version variable at all.
- [Day-6 re-walk — 2026-10-24](../field-reports/2026-10-24-day6-rewalk.md) — the same frozen inventory re-run on day 6 of the window with scanner v0.3.8: identical rows again (4/2, 4/2, 0/2), no inert-to-flagged moves, and the scanner byte-identical to October 20, 21, 22 and 23, so five consecutive re-walks introduce no scanner-version variable at all.
- [Day-7 re-walk — 2026-10-25](../field-reports/2026-10-25-day7-rewalk.md) — the same frozen inventory re-run on day 7 of the window with scanner v0.3.8: identical rows again (4/2, 4/2, 0/2), no inert-to-flagged moves, and the scanner byte-identical to October 20, 21, 22, 23 and 24, so six consecutive re-walks introduce no scanner-version variable at all.
- [Day-8 re-walk — 2026-10-26](../field-reports/2026-10-26-day8-rewalk.md) — the same frozen inventory re-run on day 8 of the window with scanner v0.3.8: identical rows again (4/2, 4/2, 0/2), no inert-to-flagged moves, and the scanner byte-identical to October 20, 21, 22, 23, 24 and 25, so seven consecutive re-walks introduce no scanner-version variable at all.
- [Seven identical re-walks — cross-cutting summary, October 20–26](https://gist.github.com/alapha888/10fe87578dd5e27ef5f9889409f88cf7) — the seven daily results side by side: identical rows every day (4/2, 4/2, 0/2), scanner v0.3.8 byte-identical throughout, with the narrowed claim stated explicitly: no migration effect was observed in this inventory, which does not prove nothing migrated underneath or that CI behaviour is unchanged.

## What this index does not do

An index is not a verdict on your repository. Each guide states its own limits — the scanner reads workflow files statically, it does not run your jobs, and a clean scan does not prove a workflow will pass on the new image. If a guide and the scanner's output disagree, the output from the version you ran is the one to trust, and the mismatch is worth reporting.
