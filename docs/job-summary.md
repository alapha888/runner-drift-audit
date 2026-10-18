# Job summary: a short guide

RunnerDriftAudit can write its findings as a Markdown summary, so they
appear on the GitHub Actions job summary page — the page reviewers
already open — instead of only existing in a CI log.

Available since v0.3.6, in both forms of the tool:

- Action: on by default. The `step-summary` input defaults to `"true"`;
  set it to `"false"` to disable it.
- CLI: `python3 runner_drift_audit.py . --summary-file summary.md`
  (the `--summary-file=summary.md` form works too)

## What is in the summary

The summary opens with the scan counts, then gives every scanned file
its own section with a per-finding table:

```markdown
## Runner Drift Audit

Scanned 1 workflow file(s): **3 HIGH**, **3 WARN** (6 finding(s) total).

### `.github/workflows/ci.yml`

| Severity | Line | Rule | Finding |
| --- | ---: | --- | --- |
| HIGH | 5 | FLOATING_LABEL | runner label 'ubuntu-latest' is a floating label; … |
| WARN | 7 | UNPINNED_ACTION | action 'actions/checkout' is referenced by mutable tag 'v4', … |
```

- Counts split findings into `HIGH` and `WARN`, with the total in
  parentheses. Each finding row carries its severity, a 1-based `line`,
  one of the six rule IDs (`FLOATING_LABEL`, `RETIRED_LABEL`,
  `REMOVED_TOOL`, `INDIRECT_RUNS_ON`, `UNPINNED_ACTION`,
  `DEFAULT_DRIFT`), and the same
  human-readable message the text report prints.
- Paths are repository-relative. A `|` inside a finding message is
  escaped as `\|`, so the table stays valid Markdown.
- Every scanned file gets a section, including a file whose only
  findings are warnings. A scan that finds no workflow files still
  writes a valid summary: `Scanned 0 workflow file(s)` followed by
  `No workflow files were found to scan.`
- The summary closes with the rule sources line: the
  `actions/runner-images` toolset diff it is grounded in.

## Workflow example

No extra step is needed — the Action appends the summary itself:

```yaml
- uses: actions/checkout@v4
- uses: alapha888/runner-drift-audit@v0.3.6
  with:
    path: "."
    # step-summary defaults to "true"; this line is only
    # needed to turn it off:
    # step-summary: "false"
```

The Action validates the input: any value other than `"true"` or
`"false"` fails the step with an error before the scan runs.

With the CLI in a hand-written workflow step, point `--summary-file`
at `$GITHUB_STEP_SUMMARY` to get the same page:

```yaml
- run: python3 runner_drift_audit.py . --summary-file "$GITHUB_STEP_SUMMARY"
```

The exit code is unchanged by the summary: 1 when any HIGH finding
exists, else 0. On success the CLI also prints a
`Markdown summary written to …` line to stdout.

## What the job summary does not do

- It does not change what the scanner checks, and it is a rendering of
  one run, not a history store: each run replaces the summary for that
  job. Keep the file yourself if you want a trend line.
- It is not the machine-readable export. A script or dashboard should
  read the plain JSON export instead (see
  [docs/json-export.md](json-export.md)); the Security tab should use
  the SARIF export (see
  [docs/sarif-code-scanning.md](sarif-code-scanning.md)).
- Outside GitHub Actions there is no job summary page: the CLI form
  simply writes the same Markdown to the file you name, for example to
  attach to a migration PR.
