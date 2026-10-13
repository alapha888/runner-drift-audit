# Pre-cutover self-audit — 2026-10-13

Running the migration checklist in this repository against the workflows I
maintain myself, before the `ubuntu-latest` move (October 19 – November 19,
2026). Written in the checklist's own discipline: rows that do not apply are
recorded as checked-inert with a date, not deleted. Findings are from
`runner_drift_audit.py` run on the local working copies on 2026-10-13.

## Inventory (checklist step 1)

Workflow files that exist across the product repositories maintained here:

| File | Status |
|---|---|
| `cn-ai-coding-workflow/.github/workflows/test-install.yml` | active |
| `cn-ai-coding-workflow-lite/.github/workflows/test-install.yml` | active |
| `runner-drift-audit/pending-workflow-scope/self-test.yml` | written, not yet pushed (token lacks the workflow scope) — audited anyway |

Every other product repository here has no `.github/workflows` directory —
checked on 2026-10-13, inert by construction.

## Scan results (steps 2–4, 7)

`cn-ai-coding-workflow` and `cn-ai-coding-workflow-lite` carry the same
install-test workflow (full and lite editions). Per file:

- **HIGH — matrix axis `os: [ubuntu-latest, macos-latest, windows-latest]`**
  feeding `runs-on: ${{ matrix.os }}`. The Ubuntu leg will ride the
  24.04 → 26.04 move. Disposition: **accepted, deliberately.** This CI
  exists to prove the install scripts work on the images users actually
  get; a failure on a new image generation is the signal it is for. The
  acceptance is now on record instead of being an accident of nobody
  having looked.
- **HIGH — `windows-latest`** on the PowerShell install job. Same
  disposition, same reasoning.
- **WARN — `actions/checkout@v4`** (two references per file, six across
  the inventory including the pending self-test). Mutable tag, recorded;
  pinning policy not adopted for first-party actions in these repos.
- Removed tools: none invoked — checked on 2026-10-13, inert.
- Default-version drift: the run steps use only `bash` / `pwsh` and the
  install scripts under test; no Java/Node/PHP/PostgreSQL/Go/clang/CMake
  defaults are consumed — checked on 2026-10-13, inert.

The pending `self-test.yml` pins `ubuntu-24.04` in both jobs; its only
findings are the two `checkout@v4` warnings above.

## Manual steps (steps 5–6)

- **Container images by tag:** neither workflow defines `container:` jobs
  or `services:`, and no step pulls an image — checked on 2026-10-13,
  inert.
- **Locale / timezone defaults:** the steps count installed files
  (`ls … | wc -l`, `Get-ChildItem … .Count`) and grep frontmatter; nothing
  parses, sorts, or diffs timestamped log text — checked on 2026-10-13,
  inert.

## Where the scanner bent

The first pass of this audit is the honest part. The pre-fix scanner
reported the two install workflows as "1 HIGH" each — the standalone
`windows-latest` job — and said **nothing about the matrix axis**, because
it only read labels off the `runs-on:` line itself. The most common
floating-label shape in real workflows (a matrix list feeding
`runs-on: ${{ matrix.os }}`) was invisible to it. It also told me the
Windows job was risky because "for Ubuntu it moves 24.04 → 26.04" — the
right severity attached to the wrong reason.

Both are fixed in v0.3.1: labels are now also collected from bracket lists
on the `os` axis and on keys the file references as `matrix.<key>`, and
from bare list items carrying a GitHub-hosted runner prefix (block matrix
axes, multi-line `runs-on:` lists) — narrow on purpose, so a
`browser: [chrome-latest]` axis or a `- docker-latest` argument is not
mistaken for a runner label. Non-Ubuntu labels get a message that does
not claim the Ubuntu move. Regression tests cover the matrix shapes, the
wording, and the false-positive guards. Re-running the fixed scanner over
this inventory produces the table above — 4 HIGH per install workflow,
all of them now seen, all of them dispositioned.

A checklist that only reports green runs is marketing; the bends are the
data. This one bent in two places, on my own files, a week before the
window opens — which is what the pre-cutover run is for.

## Addendum (same day, evening) — the indirection class

A reader's follow-up on the write-up named the general class the matrix
fix belongs to: the scanner reads one line, while the migration flows
through indirection. Matrix was the first hop. The same class covers
labels fed by `env:` / `vars:` / `inputs:` expressions, and the targets
of composite actions and reusable workflows.

Fixed in v0.3.2, narrowly: a floating label assigned to a `*RUNNER*` key
and referenced as `${{ env.<key> }}` in the same file is flagged at the
assignment; a `runs-on:` fed by a single `${{ vars.* }}`,
`${{ inputs.* }}`, or in-file-unresolved `${{ env.* }}` expression gets
an `INDIRECT_RUNS_ON` warning (no verdict the scanner cannot support).
Compound expressions are not matched — they can pin every branch in the
same line. Composite-action and reusable-workflow targets are **not**
followed; that limit is now stated in the README instead of left
implicit. Six regression tests cover the new shapes and the guards
(unreferenced `*RUNNER*` keys, pinned env labels, pinned compound
expressions). My own inventory above contains no env/vars/inputs-fed
labels — checked on 2026-10-13, inert.
