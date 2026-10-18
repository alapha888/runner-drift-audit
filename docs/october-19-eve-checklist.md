# October 19 eve checklist: two runner changes start tomorrow

Two separate GitHub runner changes begin on **October 19, 2026**. They affect different labels, and a repository can be hit by either one independently. This page is a short checklist for the evening before — October 18 — while both changes can still be prepared for calmly.

## What starts on October 19

1. **The `ubuntu-latest` rollout opens.** GitHub starts moving the `ubuntu-latest` label from Ubuntu 24.04 to Ubuntu 26.04. The rollout is staged and runs through **November 19, 2026**: during the window, two runs of the same workflow can land on different images. Nothing in your repository changes — the machine underneath your CI does.
2. **The first scheduled `macos-14` brownout runs.** Jobs on `macos-14`, `macos-14-large`, and `macos-14-xlarge` fail on purpose from **October 19, 14:00 UTC to October 20, 00:00 UTC**, ahead of the full retirement of those labels on **November 2, 2026** (GitHub Changelog, 2026-10-01). A red job in that window on a `macos-14` runner is the retirement rehearsing, not a flake.

## Tonight, in order

1. **Scan every repository you maintain.** One command per repository:

   ```bash
   python3 runner_drift_audit.py path/to/your-repo
   ```

   The exit code is 1 whenever a HIGH finding exists, so the scan can gate a job. Read the findings by rule: floating labels, removed tools, default-version drift, unpinned action tags, and — since v0.3.7 — `RETIRED_LABEL` for the `macos-14` family.

2. **Decide per repository: pin, or migrate on purpose.** If a repository is not ready for Ubuntu 26.04, pin `runs-on` to `ubuntu-24.04` for the rollout window and migrate later in one reviewed change. If it is ready, pin to `ubuntu-26.04` explicitly instead of floating on a label that is mid-move. Either choice is deliberate; floating through the window is the only option that leaves the image to chance.

3. **Move `macos-14` workflows before the brownout, not during it.** Change `macos-14` / `macos-14-large` / `macos-14-xlarge` to a supported label — `macos-15` for a fixed image, or `macos-latest` if floating is acceptable for that job — and merge before October 19, 14:00 UTC. After that time, a failing `macos-14` job cannot tell you whether your replacement works, because the old label is failing by design.

4. **Test on the target image once, deliberately.** A branch run pinned to `ubuntu-26.04` (and to your new macOS label) exercises the new images today, while `ubuntu-latest` may still resolve to 24.04. One deliberate run on the target image is worth more than several incidental runs during the rollout.

5. **Save the scan output with the migration change.** Keep one machine-readable copy alongside the human-readable one, so tomorrow's results can be compared against tonight's baseline:

   ```bash
   python3 runner_drift_audit.py path/to/your-repo --json baseline.json --summary-file baseline-summary.md
   ```

   Findings can also be exported as SARIF 2.1.0 (`--sarif FILE`) and uploaded to GitHub Code Scanning. Re-scan after every fix; findings that remain should be listed as checked-and-inert, not deleted.

## Tomorrow, when something fails

- Note which image the job ran on before re-running. A retry that passes on the other image closes nothing — it shows the failure is image-dependent, which is the finding.
- Do not debug drift as flakiness. If a step invokes a tool that was removed from Ubuntu 26.04 (for example `hg`, `mediainfo`, the globally installed `webpack` / `gulp` / `grunt`, `gcc-12`, or `clang-16/17` — full table in [Ubuntu 26.04 toolset changes](ubuntu-2604-toolset-changes.md)), the fix is an explicit install or a replacement, not another retry.
- The week-by-week practices for the full rollout window are in the [rollout-week playbook](rollout-week-playbook.md); the `macos-14` details are in the [macOS 14 retirement guide](macos-14-retirement.md).

## Get the scanner

RunnerDriftAudit is free and open source (MIT): a single Python file, standard library only, no dependencies, and it never phones home.

- Repository: https://github.com/alapha888/runner-drift-audit
- Action: `uses: alapha888/runner-drift-audit@v0.3.7`

If you maintain many repositories, [RunnerDriftAudit Pro](https://alapha888.gumroad.com/l/mepra) ($29 one-time) scans a whole workspace in one run and merges everything into a single HTML report. The free single-repo tool above stays free either way.

## Limits

This is a line scanner with shell-aware heuristics, not a full YAML or shell parser. Treat its findings as a review checklist, not as proof that a build is safe. It does not execute workflows.
