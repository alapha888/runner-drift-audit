# Plain JSON export: a short guide

RunnerDriftAudit can write its findings as plain JSON (schema v1), for
consumers that do not speak SARIF — a dashboard, a PR comment, or your own
gate script — so they do not have to scrape the text report.

Available since v0.3.5, in both forms of the tool:

- CLI: `python3 runner_drift_audit.py . --json report.json`
  (the `--json=report.json` form works too)
- Action: set the `json-file` input (see the workflow below)

## What is in the file

```json
{
  "tool": "RunnerDriftAudit",
  "schema_version": 1,
  "summary": {"files_scanned": 1, "high": 3, "warn": 3, "findings": 6},
  "files": [
    {"path": ".github/workflows/ci.yml",
     "findings": [{"severity": "HIGH", "line": 5, "rule": "FLOATING_LABEL", "message": "…"}]}
  ]
}
```

- `summary` counts every scanned file and splits findings into `high`
  and `warn`, with `findings` as their total.
- `files` lists every scanned file, including clean ones (empty
  `findings`), so "scanned and clean" is distinguishable from
  "not scanned". A scan that finds no workflow files still writes a
  valid report, with `files_scanned: 0` and an empty `files` list.
- Each finding carries `severity` (`HIGH` or `WARN`), a 1-based `line`,
  one of the six rule IDs (`FLOATING_LABEL`, `RETIRED_LABEL`,
  `REMOVED_TOOL`, `INDIRECT_RUNS_ON`, `UNPINNED_ACTION`,
  `DEFAULT_DRIFT`), and a
  human-readable `message`.
- Paths are repository-relative, matching the SARIF export.

## Workflow example

```yaml
- uses: actions/checkout@v4
- uses: alapha888/runner-drift-audit@v0.3.6
  with:
    path: "."
    json-file: "runner-drift.json"
```

The exit code is unchanged by the export: 1 when any HIGH finding
exists, else 0. A gate script can therefore keep relying on the exit
code and read the JSON only when it needs the details.

## What the JSON export does not do

- It does not change what the scanner checks, and it does not turn
  migration findings into security vulnerabilities — for the Security
  tab, use the SARIF export instead (see
  [docs/sarif-code-scanning.md](sarif-code-scanning.md)).
- It is not a history store: each run overwrites the file you name.
  Keep past reports yourself if you want a trend line.
- `schema_version` is currently 1. Consumers should check it before
  assuming the shape above.
