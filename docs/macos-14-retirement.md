# macOS 14 runner retirement: a short guide

A pinned runner label does not drift — it can stop working. GitHub
retires the macOS 14 runner image on **November 2, 2026** (GitHub
Changelog, 2026-10-01). This page explains which labels are affected,
what happens before the retirement date, and how RunnerDriftAudit
reports them.

Available since v0.3.7, in both forms of the tool:

- CLI: `python3 runner_drift_audit.py .`
- Action: `uses: alapha888/runner-drift-audit@v0.3.7`

## Which labels retire

| Label | Status |
|---|---|
| `macos-14` | Retired November 2, 2026 |
| `macos-14-large` | Retired November 2, 2026 |
| `macos-14-xlarge` | Retired November 2, 2026 |

Until this release, the scanner only flagged floating (`*-latest`)
labels, so a workflow pinned to `macos-14` scanned clean. That was a
blind spot: the label is stable, so nothing drifts — and then the
image is removed.

## What happens before November 2

Jobs on the retired labels fail on purpose during scheduled
brownouts. One scheduled brownout runs **October 19, 14:00 UTC to
October 20, 00:00 UTC**. A red job in that window on a `macos-14`
runner is the retirement rehearsing, not a flake — re-running will
not fix it once the window is active, and after November 2 the jobs
fail every time.

## How the scanner reports it

The finding carries the rule ID `RETIRED_LABEL` at HIGH severity
(SARIF level `error`). The scanner reports the three labels on every
path a runner label can appear:

- a direct `runs-on:` value — scalar, quoted, or inline list;
- a matrix axis, inline or as a block list, including matrix
  `include` entries;
- a multi-line `runs-on:` list;
- a label assigned to a referenced `*RUNNER*` key, or resolved from
  an `env:` key at the `runs-on` site.

Supported pinned labels (`macos-15`, `ubuntu-24.04`, and the rest)
stay silent. The rule appears in every output: the text report, the
SARIF log, the plain JSON export, the Markdown job summary, and the
migration report generator, which adds a fix line for it.

## What to do instead

Move the job to a label GitHub recommends in the retirement notice:
`macos-15`, or `macos-latest` (currently macos-26). Pin deliberately:
`macos-latest` is a floating label, so the scanner will flag it as
`FLOATING_LABEL` — that is the trade-off working as intended. If the
job needs a stable image, choose the pinned label; if it should track
the newest macOS image, accept the floating-label finding knowingly
and record why.

Then re-run the scan. A workflow that is clean of `RETIRED_LABEL`
findings will not be stopped by the November 2 retirement.

## What this guide does not cover

- It does not list every macOS image change. The Ubuntu 24.04 to
  26.04 toolset differences are in
  [docs/ubuntu-2604-toolset-changes.md](ubuntu-2604-toolset-changes.md).
- It does not predict further retirement dates. Dates here are the
  ones GitHub published in the 2026-10-01 Changelog notice.
