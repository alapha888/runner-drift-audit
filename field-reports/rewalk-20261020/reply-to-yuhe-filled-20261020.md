# Reply to Yuhe He — Oct-20 re-walk (FILLED 2026-10-20 — post in the original dev.to thread)

Hi Yuhe,

Thanks for following up and sticking to the agreed schedule.

Here are our second-run figures using RunnerDriftAudit v0.3.7. Note that the scanner has expanded since v0.3.2; scanner rule updates have been itemized separately from actual ubuntu-latest migration drift so the two effects are not conflated. The only new rule since v0.3.2 is RETIRED_LABEL (macos-14 retirement, v0.3.7); none of these three targets pin macos-14, and the other releases only added output formats (SARIF, JSON, job summary), so no count below is a scanner-growth artefact.

Target results vs. our Oct 13 baseline:
1. cn-ai-coding-workflow: 4 HIGH (delta: 0), 2 WARN (delta: 0) [Baseline: 4 HIGH / 2 WARN]
2. cn-ai-coding-workflow-lite: 4 HIGH (delta: 0), 2 WARN (delta: 0) [Baseline: 4 HIGH / 2 WARN]
3. self-test: 0 HIGH (delta: 0), 2 WARN (delta: 0) [Baseline: 0 HIGH / 2 WARN]

Rows that did not move between runs:
- All six findings in each of the two cn-ai-coding-workflow targets (three matrix-axis floating labels, one standalone windows-latest, two checkout@v4 warnings) (status: unchanged)
- Both checkout@v4 warnings in self-test, which still pins ubuntu-24.04 in both jobs (status: unchanged)
- Manual rows for container images by tag and locale/timezone defaults (status: still inert — no container/service/image pulls in the inventory)

No row moved from checked-inert to flagged, and we observed no migration-effect rows yet: the scanner flags the floating label itself, so counts stay flat when the image underneath flips — any real effect would surface as a CI behaviour change on the floated jobs instead.

Full report: https://github.com/alapha888/runner-drift-audit/blob/main/field-reports/2026-10-20-post-cutover-self-audit.md

Could you share the link to your second walkthrough report once it is ready? Looking forward to comparing our second reports line by line.

Best,
alapha888
