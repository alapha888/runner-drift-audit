# dev.to 帖 · Migration Window, Morning One — 待主会话已登录会话发布（Gist 版先行公开）

> 定位：迁移窗口开启日（10-19）当天实证帖。与 10-15 自查帖不重复：那篇讲窗口开启前扫描器自身的两处弯折，这篇讲窗口开启当天清晨先扫自有仓、抓到一个今晚就会红的真问题并当场修掉。事实全部来自 field-reports/2026-10-19-day1-self-scan.md（公开仓在档，含 CI run 号）。克制、无 hype、判定仍以订单为准。
> 外链：公开仓 + field report + Pro 版各一处，不堆链。

---

Title: **Migration Window, Morning One: My Scanner Caught One of My Own Repos Still on macos-14**

Tags: githubactions, cicd, devops, opensource

Today, October 19, two GitHub runner changes start on the same morning: the `ubuntu-latest` label begins its rolling move to Ubuntu 26.04 (through November 19), and the first `macos-14` brownout runs tonight, 14:00–24:00 UTC, ahead of the November 2 retirement of that image.

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

## The one that would have gone red tonight

The `photoveil-ios` finding was the real one. Its CI was still running on `macos-14` — the image that starts failing on purpose tonight during the brownout window and stops working entirely on November 2. Nothing about the repo had changed; the label underneath it was expiring.

The fix was one line, `macos-14` → `macos-15`, pushed the same morning. CI on the new image passed in 32 seconds (core tests and iOS typecheck; run 39146373675 in that repo's history, if you want to check rather than take my word for it).

That is the whole argument for scanning before the window, not after the first red build: this class of finding is invisible until the day it turns red, and for `macos-14` that day is today.

## What I deliberately did not fix

The other floating labels stayed floating — by decision, now written down:

- The two `cn-ai-coding-workflow` install-test matrices exist to prove an install script works on whatever "latest" currently means across three operating systems. Pinning those labels would defeat the test. If a leg goes red during the rollout, that red *is* the signal the job exists to produce.
- The `windows-latest` jobs ride no announced migration in this window, so they stay floating for now, recorded as checked-and-inert rather than unexamined.

And one honest non-fix: the unpinned `actions/checkout@v4` warnings are still open, including in the scanner's own self-test workflow. The scanner reports it; I have not done that pass yet. It is recorded as not-yet-fixed, not quietly dropped from the list.

## If you have not scanned yet

The brownout starts at 14:00 UTC today. A scan takes under a minute per repo:

```bash
python3 runner_drift_audit.py path/to/your-repo --json day1.json --summary-file day1-summary.md
```

The scanner is free and open source (MIT, single-file Python, standard library only): https://github.com/alapha888/runner-drift-audit — the full morning scan, including the rows I left alone and why, is in `field-reports/2026-10-19-day1-self-scan.md`. Tomorrow I re-run the frozen October 13 baseline inventory for the scheduled comparison with a reader who walked the same checklist on his own machine; the delta lands as a new field report, including the rows that did not move.

If you maintain many repositories, a paid batch edition ($29 one-time) scans a whole workspace into one merged HTML report: https://alapha888.gumroad.com/l/mepra — the free single-repo tool stays free either way.

One repo, one retired label, one line fixed before the window opened. I would rather read about where the checklist bends on your repos than hear it was all green.
