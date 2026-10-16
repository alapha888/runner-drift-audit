# runner-drift-audit

Scans GitHub Actions workflows for floating runner labels, unpinned action refs, and tool-version drift ahead of the ubuntu-latest 24.04→26.04 migration.

GitHub moves the `ubuntu-latest` label from Ubuntu 24.04 to Ubuntu 26.04 between **October 19 and November 19, 2026**. Nothing in your repository changes — the machine underneath your CI does. This tool scans your workflow files and reports, line by line, what is likely to break or silently change.

Free, MIT, single-file Python (stdlib only, no dependencies).

## Usage

```bash
python3 runner_drift_audit.py [path-to-repo]   # default: current directory
```

Exit code is 1 when any HIGH finding exists, so it can gate a CI job. Sample workflows live in `samples/bad` and `samples/clean`.

## Generate a migration-readiness report

```bash
python3 generate_report.py [path-to-repo] [--out DIR]
```

Writes `migration-readiness-report.md` and `migration-readiness-report.html` into the output directory (default `runner-drift-report/`): a severity summary, findings per workflow file, the full toolset-differences table, and a fix checklist derived from the findings — the file you attach to a migration PR. Exit code matches the scanner (1 when any HIGH finding exists). A sample report generated from `samples/bad` lives in `samples/report/`. Tests: `python3 -m unittest discover -s tests`.

## Use as a GitHub Action

The same scanner ships as a composite action in this repository, so a workflow can gate on it directly:

```yaml
- uses: actions/checkout@v4
- uses: alapha888/runner-drift-audit@v0.3.3
  with:
    path: "."              # directory that contains .github/workflows
    fail-on-high: "true"   # set to "false" to report findings without failing
```

`fail-on-high: "true"` (the default) exits 1 when any HIGH finding exists; `"false"` prints the same report and always passes. No Marketplace listing is required to use the `uses:` form above.

## What it checks

Rules are grounded in a diff of the official `actions/runner-images` toolsets (`toolset-2404.json` vs `toolset-2604.json`, compared 2026-10-10 — 22 differences):

| Rule | Severity | Examples from the official toolset diff |
|---|---|---|
| Floating runner label | HIGH | `runs-on: ubuntu-latest` (also quoted / list forms, and labels referenced from a matrix axis or other list) |
| Removed tool invoked in a run step | HIGH | `hg` (mercurial removed), `mediainfo`, `sphinxsearch`, `haveged`, `fastlane` gem, globally preinstalled `webpack`/`gulp`/`grunt`/`parcel`/`lerna`/`newman`/`tsc` (only `n` and `yarn` remain), `gcc-12`, `clang-16/17`, `p7zip` |
| Default version drift (no setup action pins it) | WARN | Java 17→25 (Java 8 removed), Node 22→24, PHP 8.3→8.5 only, PostgreSQL 16→18, clang 18→21, Go 1.24→1.26, CMake unpinned (was held at 3.31.6 to avoid CMake 4.0 issues), Docker 28→29 / Compose 2.38→5.1 |
| Action referenced by mutable tag instead of a full SHA | WARN | `uses: actions/checkout@v4` |

## Machine-readable differences list

The complete 24.04 to 26.04 toolset differences table is available as a CSV in this repository: [`toolset-differences-2404-2604.csv`](toolset-differences-2404-2604.csv) (24 data rows, grouped into the 22 differences figure). It includes the following columns: `category`, `tool`, `change_type`, `ubuntu_2404`, `ubuntu_2604`, `ci_impact`, `mitigation`. The file's first line is a `# schema-v1:` comment row documenting each column's type and the allowed `change_type` values, so the schema travels with the data — skip lines starting with `#` before parsing (the bundled report generator does). As a plain CSV, it can be checked mechanically in a CI job or spreadsheet rather than requiring a human to read a prose changelog. The report generator uses this same file as its source.

Human-readable version: [Ubuntu 26.04 toolset changes](docs/ubuntu-2604-toolset-changes.md) — every removed tool, global removal, rename, and default-version jump in tables, with what to do for each.

## Migration checklist

Before the `ubuntu-latest` label moves (October 19 – November 19, 2026):

1. **Inventory first.** List every file in `.github/workflows` and confirm each one is expected — a migration is one of the few moments teams look at the whole set, and an unfamiliar file is worth a question before anything runs on a new image.
2. **Scan.** Run the scanner (or add the composite Action) and work through the report line by line.
3. **Clear the HIGH findings.** Pin `runs-on` to `ubuntu-24.04` if you are not ready to migrate, or move deliberately to `ubuntu-26.04`; replace or drop steps that invoke removed tools (for example `hg`, `mediainfo`, `gcc-12`).
4. **Pin what drifts.** Where a WARN flags a default version change (Java, Node, PHP, PostgreSQL, Go, clang, CMake, Docker), pin the version explicitly instead of relying on the image default — a setup action for language runtimes, a service or image pin for PostgreSQL and Docker.
5. **Enumerate container images by tag.** List the images your workflows pull by tag (service containers, `container:` jobs, `docker pull` steps). Their base can move to the new image generation on a schedule you do not control, independently of the runner label — pin by digest or to an explicit tag where the image contents matter. This is a manual pass; the scanner does not inspect image references.
6. **Check locale and timezone defaults.** If anything in your pipeline diffs or parses log output, timestamps, or sorted text, record the current locale/timezone behaviour and re-check it after the move. Default changes here bite even single-language projects, and they do not show up as version bumps.
7. **Review action refs.** Mutable tags are flagged as WARN; pin to a full SHA where your policy requires it.
8. **Re-run** until no HIGH findings remain, and keep the final report with the migration PR so reviewers can see what was checked.

Treat the checklist and the differences list as a filter, not a list to shorten: for every row that does not apply, write "not installed / not used, checked on <date>" instead of deleting it. Proving most rows inert is the value — an unchecked row and a checked-inert row look identical in a shortened list, and only one of them is evidence.

## Field reports

- [2026-10-13 — pre-cutover self-audit](field-reports/2026-10-13-pre-cutover-self-audit.md): this checklist run against the workflows maintained here, including where the scanner itself bent (it missed matrix-axis labels until v0.3.1).

## Limits

- This is a line scanner with shell-aware heuristics (quotes, `sudo`/`env`/`VAR=val` prefixes, multi-line `run:` blocks), not a full YAML/shell parser. Treat findings as a review checklist, not a proof.
- It checks invocations in `run:` steps and runner labels in `runs-on:` (including labels referenced from a matrix axis or another list in the same file); it does not execute anything and does not phone home.
- Indirection is followed one level, and only where it is visible in the same file: a floating label assigned to a `*RUNNER*` key and referenced as `${{ env.<key> }}` is flagged at the assignment, and a `runs-on:` fed by a single `${{ vars.* }}` / `${{ inputs.* }}` / unresolved `${{ env.* }}` expression gets an `INDIRECT_RUNS_ON` warning instead of a verdict. It does not follow labels into composite actions or reusable workflows that live in other files or repositories — scan those targets separately; their `runs-on:` lines are outside the files this run reads.

## Paid option — Pro edition (on sale)

The multi-repo edition is on sale: **RunnerDriftAudit Pro** scans every repository in a local workspace in one run and writes one combined HTML report (cross-repo summary table, per-repo findings with file and line, and a fix checklist per repo). **$29 one-time** on Gumroad: https://alapha888.gumroad.com/l/mepra

The audit rules and findings are identical to this free edition — Pro is the fleet-wide run and the single combined document.

## More from the same author

- Full index of free tools, paid tiers, and waitlists: https://gist.github.com/alapha888/fe51434e80dbc0ef5610aeab38b025f4
