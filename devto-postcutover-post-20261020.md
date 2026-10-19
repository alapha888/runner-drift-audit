# dev.to 帖 · Post-Cutover Re-Walk — 待主会话已登录会话发布

> 定位：Oct-20 复跑对账的正式文章版，兑现 Day-1 帖结尾的承诺（"Tomorrow I re-run the frozen October 13 baseline inventory… the delta lands as a new field report, including the rows that did not move"）。事实全部来自 field-reports/2026-10-20-post-cutover-self-audit.md（公开仓在档，含脚本、原始输出与 SHA256）。克制、无 hype、判定仍以订单为准。
> 外链：公开仓 + field report + Pro 版各一处，不堆链。与 Yuhe He 的对账状态如实写 pending，不预支他的报告。

---

Title: **Post-Cutover Re-Walk: Nothing Moved — and Why That Is the Finding**

Tags: githubactions, cicd, devops, opensource

On October 13, before the migration window opened, I froze a baseline: three of my own workflow files, scanned with RunnerDriftAudit v0.3.2, every row written down. The agreement — made in the open, in a comment thread with a reader who ran the same checklist on his own machine — was that after the window opened, we would both re-run the same inventory and compare second reports line by line.

The window opened yesterday, October 19: `ubuntu-latest` began its rolling move to Ubuntu 26.04 (through November 19), and the first `macos-14` brownout ran last night. This morning I re-ran the frozen inventory. Here is the whole result:

| Target | HIGH | WARN | Delta vs baseline |
|---|---:|---:|---|
| cn-ai-coding-workflow `test-install.yml` | 4 | 2 | none — identical rows |
| cn-ai-coding-workflow-lite `test-install.yml` | 4 | 2 | none — identical rows |
| runner-drift-audit self-test | 0 | 2 | none — identical rows |

No row moved. Nothing flipped from checked-inert to flagged. The two manual rows I track alongside the scan — container images pulled by tag, and locale/timezone defaults — are still inert, grep-verified on the day: this inventory pulls no container images, and its steps still only count files and grep frontmatter.

## A null result is still a result — if the baseline was frozen

It would be easy to read that table as "nothing happened, nothing to write." That reading is wrong in a specific way, and the specificity is the point of freezing a baseline before the event instead of reconstructing one after it.

The scanner flags the floating `ubuntu-latest` label itself. Its counts therefore do not change when the image underneath the label flips — by design. A count delta was never the signal this inventory could produce. Any real migration effect would show up as a behaviour change in CI on the jobs I deliberately left floating (the install-test matrices exist to go red if "latest" breaks the install script), not as a new row in this table.

So the honest statement is narrow: on day one of the window, the platform switch produced no scanner-visible change in this inventory, and the floated jobs have not gone red. That is a dated, checkable claim — the run script, the raw scanner output, and the scanner's SHA256 are all in the repo — not a vibe.

## Version honesty, because the scanner changed too

One trap in any before/after comparison: the measuring tool moved between measurements. Mine did, and the report separates that from platform effects:

- Baseline scanner: v0.3.2 (October 13). Re-walk scanner: v0.3.7, test suite 64 passed on the day.
- v0.3.3–v0.3.6 changed output formats only (Marketplace metadata, SARIF export, JSON export, Markdown summary) — no rule changes that affect counts.
- v0.3.7 did add one rule: `RETIRED_LABEL`, a HIGH for workflows pinned to the retiring `macos-14` labels. None of the three baseline targets pin `macos-14`, so the new rule changed no count here. It is listed in the report anyway, so that a future `macos-14` finding is never mistaken for a migration effect.

If your own before/after numbers moved, the first question is which of those two columns moved them: the platform, or your tooling.

## What is still open

- The other half of the exchange is pending: my counterpart's second report has not arrived yet. My reply, with the filled comparison template, goes into the original thread today; his rows will be recorded as a dated addendum when they land, including any line where we disagree.
- The deliberately floated jobs stay floating through the window (until November 19). If one goes red, that red is the signal the job exists to produce, and it will get its own field report.
- The unpinned `actions/checkout@v4` warnings are still open, including in the scanner's own self-test. Still recorded as not-yet-fixed.

The scanner is free and open source (MIT, single-file Python, standard library only): https://github.com/alapha888/runner-drift-audit — the full re-walk, including the rows that did not move and the version-honesty table, is in `field-reports/2026-10-20-post-cutover-self-audit.md`. If you maintain many repositories, a paid batch edition ($29 one-time) scans a whole workspace into one merged HTML report: https://alapha888.gumroad.com/l/mepra — the free single-repo tool stays free either way.

If you froze a baseline before the window opened, I would like to compare rows — especially if yours moved and mine did not.
