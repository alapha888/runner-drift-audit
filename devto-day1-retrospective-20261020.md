# dev.to 帖 · Migration Window, Morning One（回顾版）— 2026-10-20 晚发布用

> 定位：Day-1 帖（devto-day1-post-20261019.md）的时态修正回顾版。原稿写于 10-19 当天、以「今日/今晚/明日」口径叙事，10-20 晚已不可逐字发布；本版把时态改为回顾、把原稿结尾「明日复跑」的承诺替换为已兑现的复跑结果与已发布长文链接，其余事实、数字、表格与原稿及 field-reports/2026-10-19-day1-self-scan.md 逐字一致。克制、无 hype。

---

Title: **Migration Window, Morning One: My Scanner Caught One of My Own Repos Still on macos-14**

Tags: githubactions, cicd, devops, opensource

Yesterday, October 19, two GitHub runner changes started on the same morning: the `ubuntu-latest` label began its rolling move to Ubuntu 26.04 (through November 19), and the first `macos-14` brownout ran that night, 14:00–24:00 UTC, ahead of the November 2 retirement of that image.

Before writing anything else about either change, I ran my own scanner — RunnerDriftAudit v0.3.7 — on the five repositories I maintain that actually have workflows. Six workflow files. The result was not a victory lap.

## What the scan found at home

| Repo | HIGH | What it was |
|---|---:|---|
| photoveil-ios | 1 | `RETIRED_LABEL` — CI still on `macos-14` |
| cn-ai-coding-workflow-lite | 4 | Floating `ubuntu-latest` / `macos-latest` / `windows-latest` in the install-test matrix, plus a standalone `windows-latest` job |
| cn-ai-coding-workflow | 4 | The same four as the lite repo |
| pubaudit-windows | 2 | Floating `windows-latest` in both workflows |
| runner-drift-audit | 0 | — (2 WARN: `actions/checkout@v4` not pinned to a SHA) |

Eleven HIGH findings, all floating or retired labels — in the repos of the person who wrote the scanner. Plus a WARN in almost every file: `actions/checkout` referenced by the mutable `v4` tag instead of a full commit SHA.

## The one that would have gone red that night

The `photoveil-ios` finding was the real one. Its CI was still running on `macos-14` — the image that started failing on purpose that night during the brownout window and stops working entirely on November 2. Nothing about the repo had changed; the label underneath it was expiring.

The fix was one line, `macos-14` → `macos-15`, pushed the same morning. CI on the new image passed in 32 seconds (core tests and iOS typecheck; run 39146373675 in that repo's history, if you want to check rather than take my word for it).

That is the whole argument for scanning before the window, not after the first red build: this class of finding is invisible until the day it turns red, and for `macos-14` that day was October 19.

## What I deliberately did not fix

The other floating labels stayed floating — by decision, now written down:

- The two `cn-ai-coding-workflow` install-test matrices exist to prove an install script works on whatever "latest" currently means across three operating systems. Pinning those labels would defeat the test. If a leg goes red during the rollout, that red *is* the signal the job exists to produce.
- The `windows-latest` jobs ride no announced migration in this window, so they stay floating for now, recorded as checked-and-inert rather than unexamined.

And one honest non-fix: the unpinned `actions/checkout@v4` warnings are still open, including in the scanner's own self-test workflow. The scanner reports it; I have not done that pass yet. It is recorded as not-yet-fixed, not quietly dropped from the list.

## If you have not scanned yet

The window is still open: `ubuntu-latest` keeps rolling through November 19, and `macos-14` retires on November 2. A scan takes under a minute per repo:

```bash
python3 runner_drift_audit.py path/to/your-repo --json day1.json --summary-file day1-summary.md
```

The scanner is free and open source (MIT, single-file Python, standard library only): https://github.com/alapha888/runner-drift-audit — the full morning scan, including the rows I left alone and why, is in `field-reports/2026-10-19-day1-self-scan.md`. The next day I re-ran the frozen October 13 baseline inventory for the scheduled comparison with a reader who walked the same checklist on his own machine; nothing moved, and why that is itself the finding is written up here: https://dev.to/alapha888/post-cutover-re-walk-nothing-moved-and-why-that-is-the-finding-287o

If you maintain many repositories, a paid batch edition ($29 one-time) scans a whole workspace into one merged HTML report: https://alapha888.gumroad.com/l/mepra — the free single-repo tool stays free either way.

One repo, one retired label, one line fixed before the window opened. I would rather read about where the checklist bends on your repos than hear it was all green.
