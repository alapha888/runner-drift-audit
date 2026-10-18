# SARIF and GitHub Code Scanning: a short guide

RunnerDriftAudit can write its findings as a SARIF 2.1.0 log, so they show
up as code-scanning alerts in a repository's Security tab instead of only
existing in a CI log. This page explains what is in the log, how the
severities map, and what SARIF does not change.

Available since v0.3.4, in both forms of the tool:

- CLI: `python3 runner_drift_audit.py . --sarif runner-drift.sarif`
- Action: set the `sarif-file` input (see the workflow below)

## The six rules in the log

Every result carries one of these rule IDs, with a short and a full
description embedded in the log itself:

| Rule ID | Meaning | Default level |
|---|---|---|
| `FLOATING_LABEL` | A `runs-on` label such as `ubuntu-latest` moves to a new runner image on the provider's schedule | error |
| `RETIRED_LABEL` | A pinned `runs-on` label such as `macos-14` belongs to a runner image being retired (macOS 14, November 2, 2026) | error |
| `REMOVED_TOOL` | A `run:` step invokes a tool removed from the Ubuntu 26.04 runner image | error |
| `INDIRECT_RUNS_ON` | A `runs-on` value is supplied indirectly (env/vars/inputs) and cannot be resolved by the scanner | warning |
| `UNPINNED_ACTION` | An action is referenced by a mutable tag instead of a full commit SHA | warning |
| `DEFAULT_DRIFT` | A tool's default version changes in the Ubuntu 26.04 image and no setup action pins it | warning |

Per-result levels follow the scan's own severities: HIGH findings are
written as `error`, WARN findings as `warning`. Finding locations use
repository-relative paths and line numbers, so Code Scanning can place
each alert on the exact workflow line.

An empty scan still writes a valid log: the run lists all six rules and
zero results. Uploading that log is harmless and closes alerts that a
later commit has fixed.

## Workflow: scan, then upload

```yaml
permissions:
  security-events: write   # required by the upload step

jobs:
  drift:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: alapha888/runner-drift-audit@v0.3.4
        with:
          path: "."
          fail-on-high: "false"   # let the upload step run even with HIGH findings
          sarif-file: "runner-drift.sarif"
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: "runner-drift.sarif"
          category: "runner-drift-audit"
```

Two details matter:

- `fail-on-high: "false"` — with the default `"true"`, a HIGH finding
  fails the scan step and the upload step never runs, so the alerts never
  reach the Security tab. Set it to `"false"` on the scanning step when
  the point of the run is uploading results; the findings and the exit
  behaviour of a plain scan are unchanged.
- `category` — a stable category keeps uploads from successive runs
  grouped as one tool's results, so fixed alerts close automatically
  instead of piling up as duplicates.

Writing the SARIF file never changes the exit code: a scan that exits 1
without `--sarif` still exits 1 with it.

## What SARIF does not do

- It does not turn runner-drift findings into security vulnerabilities.
  The alerts describe migration and pinning risks in workflow files;
  Code Scanning is used purely as the display and tracking surface.
- It does not follow indirection. A `runs-on` value built from an
  expression is reported once as `INDIRECT_RUNS_ON` at the place it is
  used; composite and reusable workflows are not followed into.
- It does not replace the plain report. The terminal output and the
  SARIF log are written from the same findings list, so the counts
  always agree.

## See also

- [Ubuntu 26.04 toolset changes](ubuntu-2604-toolset-changes.md) — the
  full per-tool diff the `REMOVED_TOOL` and `DEFAULT_DRIFT` rules are
  grounded in.
- The free scanner and the Pro report are linked from the
  [project README](../README.md).
