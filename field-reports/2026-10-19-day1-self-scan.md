# October 19, morning: I scanned my own repos first

Today is the first day of two GitHub runner changes: the `ubuntu-latest` rollout to Ubuntu 26.04 opens (through November 19), and the first `macos-14` brownout runs 14:00–24:00 UTC tonight, ahead of the November 2 retirement.

Before writing anything else about it, I ran RunnerDriftAudit v0.3.7 on the five repositories I maintain that actually have workflows. Six workflow files, scanned this morning (October 19, ~00:45 CST):

| Repo | HIGH | What the HIGH findings were |
|---|---:|---|
| photoveil-ios | 1 | `RETIRED_LABEL` — CI still on `macos-14` |
| cn-ai-coding-workflow-lite | 4 | Floating `ubuntu-latest` / `macos-latest` / `windows-latest` in the install-test matrix, plus `windows-latest` |
| cn-ai-coding-workflow | 4 | Same matrix pattern as the lite repo |
| pubaudit-windows | 2 | Floating `windows-latest` in both workflows |
| runner-drift-audit | 0 | — (2 WARN: `actions/checkout@v4` not pinned to a SHA) |

Total: 11 HIGH, all floating or retired labels. Plus a WARN in almost every file: `actions/checkout` (and friends) referenced by the mutable `v4` tag instead of a full commit SHA.

## What I fixed, and what I deliberately did not

**Fixed within the hour:** `photoveil-ios` moved from `macos-14` to `macos-15`. That job would have failed on purpose tonight during the brownout window, and would have stopped working entirely on November 2. One line, pushed this morning; CI on macos-15 passed in 32s (core tests and iOS typecheck), run 39146373675 in the photoveil-ios repo history.

**Left floating on purpose, now recorded as checked-and-inert:** the two `cn-ai-coding-workflow` install-test matrices. Their job is to prove an install script works on whatever "latest" currently means on three operating systems — pinning those labels would defeat the test. The `windows-latest` jobs in `pubaudit-windows` are in the same category for now: the product is a Windows desktop build, and there is no announced Windows image migration in this window. These stay floating by decision, not by default — which is the distinction the day guide asks for.

**Not fixed yet, honestly:** the unpinned `actions/checkout@v4` warnings are mine too, including in RunnerDriftAudit's own self-test workflow. Pinning to SHAs is a separate pass; the scanner reports it, and I have not done it yet.

## The point

The scanner's own house was not in order. One of my five repos was still on a runner label that starts failing tonight. That is exactly the class of finding that stays invisible until the day it turns red — and today is that day for `macos-14`.

If you have not scanned yet, the brownout starts at 14:00 UTC today. A scan takes under a minute per repo:

```bash
python3 runner_drift_audit.py path/to/your-repo --json day1.json --summary-file day1-summary.md
```

- Free scanner (MIT, single Python file, no dependencies): https://github.com/alapha888/runner-drift-audit
- Action: `uses: alapha888/runner-drift-audit@v0.3.7`
- October 19 day guide (timeline and first-failure triage): https://github.com/alapha888/runner-drift-audit/blob/main/docs/october-19-day-guide.md
- RunnerDriftAudit Pro ($29 one-time, scans a whole workspace into one HTML report): https://alapha888.gumroad.com/l/mepra

## Limits

This was a scan of five small repositories I maintain, run locally with v0.3.7. It is a field note, not a survey. The scanner is a line scanner with shell-aware heuristics, not a full YAML or shell parser; treat findings as a review checklist, not as proof that a build is safe.
