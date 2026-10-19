# Post-cutover self-audit — 2026-10-20

Companion to the frozen baseline: `field-reports/2026-10-13-pre-cutover-self-audit.md`
(baseline scanner v0.3.2, not edited). Protocol agreed with reader Yuhe He on
2026-10-13: both sides re-run the same inventory after the Oct 19–Nov 19
`ubuntu-latest` migration window opens, and compare second reports line by line.
Scanner-version changes are recorded separately from platform-switch effects.

Run: 2026-10-20 00:54 CST (2026-10-19T16:54:31Z), via
`field-reports/rewalk-20261020/run-rewalk.sh`. Raw outputs are in
`field-reports/rewalk-20261020/output-20261020/` (metadata.md, scans-all.txt).

## Oct-20 re-walk results

| Target | HIGH | WARN | Delta vs baseline |
|---|---|---|---|
| cn-ai-coding-workflow `test-install.yml` | 4 | 2 | none — 4 HIGH / 2 WARN, identical rows |
| cn-ai-coding-workflow-lite `test-install.yml` | 4 | 2 | none — 4 HIGH / 2 WARN, identical rows |
| runner-drift-audit self-test `.github/workflows/self-test.yml` | 0 | 2 | none — 0 HIGH / 2 WARN, identical rows |
| Manual: container images by tag | inert | — | did not move — no `container:`/`services:`/image pulls in the inventory (grep-verified on the day) |
| Manual: locale / timezone defaults | inert | — | did not move — steps still only count files and grep frontmatter |

Rows that did not move (per protocol, listed explicitly):

- cn-ai-coding-workflow: ubuntu-latest / macos-latest / windows-latest matrix-axis
  FLOATING_LABEL HIGH ×3, standalone windows-latest FLOATING_LABEL HIGH ×1,
  actions/checkout@v4 UNPINNED_ACTION WARN ×2 — all unchanged.
- cn-ai-coding-workflow-lite: same six rows, unchanged.
- self-test: actions/checkout@v4 UNPINNED_ACTION WARN ×2 — unchanged; the two
  jobs still pin `ubuntu-24.04`.
- Both manual rows (container images, locale/timezone) remain checked-inert.

Rows that moved from checked-inert to flagged:

- None.

## Version honesty

- Scanner used for this re-walk: v0.3.7 (latest release, 2026-10-18).
  Scanner file SHA256: `3daa012b813d8cf3f9440a382e5d1fdbdc1ea26a6bd5a986467a3699a6156061`;
  repo HEAD at run time: `96380d6`. Test suite on the day: 64 passed.
- Scanner-growth rows since baseline v0.3.2 (NOT migration rows):
  - v0.3.3 — Marketplace-ready action metadata (no rule changes affecting counts).
  - v0.3.4 — SARIF 2.1.0 export for GitHub Code Scanning (output format only).
  - v0.3.5 — plain JSON export (output format only).
  - v0.3.6 — Markdown job summary output (output format only).
  - v0.3.7 — new HIGH rule RETIRED_LABEL for workflows pinned to the retiring
    macos-14 labels. None of the three targets pin macos-14, so this rule
    changed no count in this inventory; it is listed here so a future
    macos-14 finding is never mistaken for a migration effect.

## Migration-effect rows (platform switch only, scanner growth excluded)

- None observed yet. The window opened on Oct 19; the scanner flags the
  floating `ubuntu-latest` label itself, so its counts do not change when the
  underlying image flips. Any real migration effect would show up as a CI
  behaviour change on the deliberately floated jobs, not as a count delta in
  this table — that distinction is the point of keeping the baseline frozen.

## Exchange with Yuhe He

- His second report received: pending — reply with the filled template
  (`field-reports/rewalk-20261020/reply-to-yuhe-filled-20261020.md`) goes out
  in the original dev.to thread today; his report link will be recorded here
  as a dated addendum when it arrives.
- Line-by-line differences between the two reports: pending his report.
- Follow-ups agreed: pending his report.
