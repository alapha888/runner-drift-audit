# October 19 day guide: the rollout and the brownout, hour by hour

October 19, 2026 is the first day of two separate GitHub runner changes. The [eve checklist](october-19-eve-checklist.md) covered preparing the night before. This page covers the day itself: what starts when, what a failure on October 19 most likely means, and what to record before the day ends.

## The day in one timeline

All times below are given in UTC, with US Pacific, US Eastern, and China Standard Time alongside.

| When | What happens |
|---|---|
| Oct 19, from the start of the day | The `ubuntu-latest` rollout is open. GitHub begins moving `ubuntu-latest` from Ubuntu 24.04 to Ubuntu 26.04, in stages, through **November 19, 2026**. Any single run can land on either image. |
| Oct 19, 14:00 UTC (07:00 PDT / 10:00 EDT / 22:00 CST) | The first scheduled `macos-14` brownout **starts**. Jobs on `macos-14`, `macos-14-large`, and `macos-14-xlarge` fail on purpose. |
| Oct 20, 00:00 UTC (Oct 19, 17:00 PDT / 20:00 EDT / Oct 20, 08:00 CST) | The first `macos-14` brownout **ends**. The labels still exist after this hour, but they retire in full on **November 2, 2026**. |
| Nov 19, 2026 | The `ubuntu-latest` rollout window closes. After this date, `ubuntu-latest` means Ubuntu 26.04. |

## What to watch during the day

1. **Read the image before reading the log.** For any red `ubuntu-latest` job, open the run's setup step and note which image it actually ran on before looking at the failing step. During a staged rollout, the same commit can pass on 24.04 and fail on 26.04 an hour apart. A retry that passes proves the failure is image-dependent; it does not close it.

2. **Treat a `macos-14` failure inside the brownout window as expected, not as a signal.** Between 14:00 UTC on October 19 and 00:00 UTC on October 20, those labels fail by design. Do not debug your code against them in that window, and do not conclude that a replacement label works or fails based on a comparison run while the old label is browned out. Test the replacement — `macos-15` for a fixed image, or `macos-latest` if floating is acceptable — on its own.

3. **Match the failure to the change before changing code.** If a step fails because a tool is missing on Ubuntu 26.04 — for example `hg`, `mediainfo`, the globally installed `webpack` / `gulp` / `grunt`, `gcc-12`, or `clang-16/17` — the fix is an explicit install step or a replacement tool, not a retry and not a code change. The full list is in [Ubuntu 26.04 toolset changes](ubuntu-2604-toolset-changes.md).

4. **Re-scan after any fix, and keep the day's baseline.** If you saved a baseline on the eve (see the eve checklist, step 5), re-run the same scan after each fix and diff the two:

   ```bash
   python3 runner_drift_audit.py path/to/your-repo --json day1.json --summary-file day1-summary.md
   ```

   Findings that remain should be listed as checked-and-inert, not deleted. The week-by-week practices for the rest of the window are in the [rollout-week playbook](rollout-week-playbook.md); the `macos-14` details are in the [macOS 14 retirement guide](macos-14-retirement.md).

## End-of-day check (five minutes)

- Every repository you maintain has either been pinned on purpose (`ubuntu-24.04` or `ubuntu-26.04`) or is floating through the window by a recorded decision, not by default.
- No workflow still needs `macos-14` to pass tonight; anything left on those labels has a dated migration note before November 2.
- One scan output from today is saved next to the eve baseline, so tomorrow's results have something to be compared against.

## Get the scanner

RunnerDriftAudit is free and open source (MIT): a single Python file, standard library only, no dependencies, and it never phones home.

- Repository: https://github.com/alapha888/runner-drift-audit
- Action: `uses: alapha888/runner-drift-audit@v0.3.7`

If you maintain many repositories, [RunnerDriftAudit Pro](https://alapha888.gumroad.com/l/mepra) ($29 one-time) scans a whole workspace in one run and merges everything into a single HTML report. The free single-repo tool above stays free either way.

## Limits

This is a line scanner with shell-aware heuristics, not a full YAML or shell parser. Treat its findings as a review checklist, not as proof that a build is safe. It does not execute workflows.
