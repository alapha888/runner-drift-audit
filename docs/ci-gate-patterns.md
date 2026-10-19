# Using RunnerDriftAudit as a CI gate

The scanner was built to be usable as a gate, not just a report: its exit code is the contract. This page collects the three gate patterns that cover most repositories, the exit codes each one relies on, and what a gate cannot do.

## The exit-code contract

Command line (`runner_drift_audit.py`):

| Exit code | Meaning |
|---|---|
| 0 | The scan ran and found no HIGH findings. WARN findings may still be present — they never fail the gate. |
| 1 | Either the scan ran and found at least one HIGH finding, **or** the scan did not run at all: a usage error (unknown option, missing option argument) prints its message and exits 1 as well. The output tells the two apart — a completed scan always ends with a `HIGH findings:` count line; a usage error prints no scan output. |

The CLI has no exit code 2. Code 2 exists only in the composite Action (`uses: alapha888/runner-drift-audit@v0.3.7`):

- The Action propagates the scanner's exit code, so 0 and 1 mean the same as above.
- An invalid `fail-on-high` or `step-summary` input (anything other than `true`/`false`) exits 2 before scanning.
- Because a CLI usage error shares exit code 1 with real findings, the Action checks the scanner's output for the `HIGH findings:` line: if it is missing, the Action reports `scanner failed to run` and exits with the scanner's code instead of mistaking the failure for findings.
- With `fail-on-high: "false"`, HIGH findings are printed, the step summary and any SARIF/JSON outputs are still written, and the step always exits 0.

## Pattern 1 — Report-only first

Start here if the repository has never been scanned. You get the findings on every relevant run — in the log, on the job summary page, and in the Security tab if you also write SARIF — without breaking anyone's build while the existing pile is cleared.

```yaml
- uses: alapha888/runner-drift-audit@v0.3.7
  with:
    fail-on-high: "false"
```

## Pattern 2 — Enforce on workflow changes

Once the pile is clear, gate the pull requests that can reintroduce drift: the ones that touch workflow files.

```yaml
name: workflow-drift-gate
on:
  pull_request:
    paths:
      - ".github/workflows/**"
jobs:
  gate:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: alapha888/runner-drift-audit@v0.3.7
        # fail-on-high defaults to "true"
```

Two honest caveats:

- A failing job only blocks a merge if the job is configured as a **required status check** in branch protection. The Action can fail the run; it cannot make itself required.
- The `paths:` filter means a scanner update (a new rule, a newly retired label) is not re-checked against untouched workflows until one of them changes. Pattern 3 covers that gap.

## Pattern 3 — Scheduled re-scan after scanner updates

Findings are a function of the workflow files **and the scanner version**: v0.3.7 added the `RETIRED_LABEL` rule, so a repository that scanned clean under v0.3.6 could gain HIGH findings under v0.3.7 with no commit of its own. A weekly scheduled run in report-only mode surfaces that before the gated pull request does:

```yaml
on:
  schedule:
    - cron: "17 6 * * 1"
```

Keep the scheduled job report-only (`fail-on-high: "false"`). A red scheduled run notifies; it should not be a required check, or an unrelated merge can be blocked by a finding nobody introduced in that pull request.

## What the gate cannot do

- **WARN never blocks.** Unpinned action tags, default-version drift, and indirect runner labels are WARN by design: they are migration risks, not breakages. If your policy needs them enforced, gate on the JSON or SARIF output yourself — the exit code will not do it.
- **It scans files, not runners.** The gate reads the workflow files in the scanned path. A `runs-on:` value supplied indirectly (a single `vars` / `env` / `inputs` expression) is flagged as `INDIRECT_RUNS_ON` precisely because the scanner cannot resolve it from the file — the gate cannot judge a label it cannot see.
- **A green gate is not a migration.** Exit 0 means no HIGH findings under the current rules. It says nothing about whether the workflow's steps will behave the same on the 26.04 image; that still needs a real run on `ubuntu-26.04`.

## Get the scanner

Free and MIT: https://github.com/alapha888/runner-drift-audit — CLI, composite Action, SARIF/JSON export, and the per-rule remediation guides. Scanning many repositories in one workspace and need one combined report: RunnerDriftAudit Pro ($29 one-time) — https://alapha888.gumroad.com/l/mepra
