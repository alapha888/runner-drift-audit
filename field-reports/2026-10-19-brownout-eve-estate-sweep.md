# Brownout eve: the rest of the estate, swept

This morning's Day-1 scan covered the five repositories I maintain that I *knew* had workflows. That word — knew — was doing more work than it should. Tonight, an hour before the first `macos-14` brownout (14:00 UTC), I swept the other 17 non-fork repositories under the same account with RunnerDriftAudit v0.3.7, from fresh shallow clones, so the result rests on files on disk rather than on my memory of which repos have CI.

## What the sweep found

- **15 of the 17 have no workflow files at all.** The waitlist and landing-page repositories, `cb-alerts`, `web-highlighter`, and the rest are static sites or code that has never had CI. Nothing to drift.
- **`md-publisher`:** the scanner read its two YAML files (`pnpm-lock.yaml`, `pnpm-workspace.yaml` — package-manager configuration, not workflows). 0 findings.
- **`pubaudit-windows`:** 2 HIGH, both `FLOATING_LABEL` on `windows-latest` (`.github/workflows/ci.yml` line 18, `.github/workflows/smoke.yml` line 14), plus 9 `UNPINNED_ACTION` warnings. This is not a new finding: this morning's Day-1 report already listed these two jobs and recorded the decision to leave them floating — it is a Windows desktop build, the .NET SDK is pinned separately by `setup-dotnet` (8.0.x), and no Windows image migration is announced in this window.

## A mistake, caught and reverted

The sweep's first draft treated the `pubaudit-windows` result as new work. A pin to `windows-2025` was committed and pushed; its CI run passed in 3m21s (run 39263856534), so the pin itself was sound. Then the Day-1 report was re-read, the recorded decision surfaced, and the pin was reverted within the hour (commit `b3e3d8e`). A scanner finding is an input to a decision, not a decision — and a decision already made and written down should not be silently overridden by the next automated pass. The float stays, now twice-recorded as deliberate.

## The point

The estate is now fully covered: every non-fork repository has been scanned today, and the only HIGH findings anywhere are ones with a written decision behind them. If your own estate is bigger than the repos you *know* have workflows, an hour before a brownout is a good time to find out — a shallow clone plus a scan takes under a minute per repo:

```bash
python3 runner_drift_audit.py path/to/your-repo --json sweep.json --summary-file sweep-summary.md
```

- Free scanner (MIT, single Python file, no dependencies): https://github.com/alapha888/runner-drift-audit
- Action: `uses: alapha888/runner-drift-audit@v0.3.7`
- This morning's scan, and the decision this report defers to: https://github.com/alapha888/runner-drift-audit/blob/main/field-reports/2026-10-19-day1-self-scan.md
- RunnerDriftAudit Pro ($29 one-time, scans a whole workspace into one HTML report): https://alapha888.gumroad.com/l/mepra

## Limits

The sweep covers non-fork repositories on their default branches, scanned from shallow clones on 2026-10-19 at ~21:50 CST. Forks, other branches, and scheduled workflows that live outside `.github/workflows` are out of scope. `windows-latest` staying in `pubaudit-windows` is a recorded choice for this window, not a claim that floating labels are generally safe.
