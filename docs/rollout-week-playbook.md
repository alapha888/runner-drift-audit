# Rollout-week playbook — when `ubuntu-latest` starts moving (Oct 19 – Nov 19, 2026)

GitHub moves the `ubuntu-latest` label from Ubuntu 24.04 to Ubuntu 26.04 in a staged rollout between **October 19 and November 19, 2026**. The pre-migration checklist in the [README](https://github.com/alapha888/runner-drift-audit#migration-checklist) is for before the move. This page is for the weeks when the move is actually happening — when the same workflow can land on either image from one run to the next.

## Why the rollout window is its own problem

- The label does not flip once for everyone. During the window, two runs of the same workflow, minutes apart, can execute on different images.
- A failure that appears and then disappears is not necessarily flaky tests. It can be image-dependent: the run that failed landed on 26.04, the retry landed on 24.04.
- Default-version drift (Java 17→25, Node 22→24, PHP 8.3→8.5 only, PostgreSQL 16→18, Go 1.24→1.26, clang 18→21, Docker 28→29 / Compose 2.38→5.1, CMake unpinned) does not fail loudly. A green run on 26.04 can still be building on a different major version than the green run before it.

## During the window: five practices

1. **Record the image with the result.** For any failure you plan to investigate, note which image the job ran on before re-running. A retry that passes on the other image closes nothing — it only shows the failure is image-dependent, which is the finding.
2. **Do not debug drift as flakiness.** If a step invokes a tool that was removed or is no longer installed globally on 26.04 (`hg`, `mediainfo`, `sphinxsearch`, `haveged`, `fastlane`, global `webpack`/`gulp`/`grunt`/`parcel`/`lerna`/`newman`/`tsc`, `gcc-12`, `clang-16/17` — full table in [Ubuntu 26.04 toolset changes](ubuntu-2604-toolset-changes.md)), the correct fix is an explicit install or a replacement, not another retry.
3. **Pin first, migrate deliberately.** If a repository is not ready, pin `runs-on` to `ubuntu-24.04` for the duration of the window and migrate on your own schedule by changing the pin to `ubuntu-26.04` in one reviewed change. If it is ready, pin to `ubuntu-26.04` explicitly instead of floating on a label that is mid-move.
4. **Test on 26.04 before the label reaches you.** A workflow pinned to `ubuntu-26.04` in a branch run exercises the new image today, while `ubuntu-latest` may still resolve to 24.04. One deliberate run on the target image is worth more than several incidental runs during the rollout.
5. **Re-scan after every fix.** Run the scanner again after pinning and replacement changes, and keep the final report with the migration PR. Findings that remain should be listed as checked-and-inert, not deleted from the list.

```bash
python3 runner_drift_audit.py path/to/your-repo
```

The scanner is free and open source (MIT), a single Python file with no dependencies. It reports each risk at the exact line: floating runner labels (including matrix and `env`-referenced labels), removed tools invoked in `run` steps, default-version drift with no pinning setup action, and actions referenced by mutable tags instead of full commit SHAs.

## If you maintain many repositories

[RunnerDriftAudit Pro](https://alapha888.gumroad.com/l/mepra) ($29 one-time) scans a whole workspace of repositories in one run and merges everything into a single HTML report, so the rollout window can be worked repo by repo from one document. The free single-repo tool above stays free either way.

## Limits

This is a line scanner with shell-aware heuristics, not a full YAML or shell parser. Treat its findings as a review checklist, not as proof that a build is safe. It does not execute workflows and never phones home.
