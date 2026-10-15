# dev.to 帖 · RunnerDrift 自查弯折记 — 待主会话已登录会话发布（Gist 版已先行公开）

> 定位：迁移窗口（10-19 起）前最后一篇 RunnerDrift 内容。与 10-09 工具集差异文（4825830）不重复：那篇讲 22 项差异，这篇讲「拿自己的清单查自己的仓，扫描器弯折了两处」的一手自查结果。事实全部来自 field-reports/2026-10-13-pre-cutover-self-audit.md（公开仓在档）。克制、无 hype、判定仍以订单为准。
> 外链：公开仓 + field report + Pro 版各一处，不堆链。

---

Title: **I Ran My Own CI Migration Checklist on My Own Repos — My Scanner Missed the Matrix Axis**

Tags: githubactions, cicd, devops, opensource

The `ubuntu-latest` label moves from Ubuntu 24.04 to 26.04 starting October 19. I built a small scanner for that move, and last week I did the thing I tell everyone else to do: I ran my own migration checklist against my own workflows, before the window opens.

The checklist did not report all green. It reported something more useful: two places where the scanner itself bent.

## What the inventory actually held

Across the repositories I maintain, only three workflow files exist: two identical install-test workflows (full and lite editions of the same product), and one pending self-test file that is written but not yet pushed. Everything else has no `.github/workflows` directory at all — checked, and recorded as checked-inert with a date, not deleted from the list. A row you verified does not apply is evidence; a deleted row is just a shorter list.

Both install workflows came back with findings I had to disposition on the record:

- A matrix axis `os: [ubuntu-latest, macos-latest, windows-latest]` feeding `runs-on: ${{ matrix.os }}` — the Ubuntu leg rides the 24.04 → 26.04 move.
- A standalone `windows-latest` job.
- Mutable `actions/checkout@v4` tags.

My disposition for the floating labels was: accepted, deliberately. That CI exists to prove install scripts work on the images users actually get, so a failure on a new image generation is the signal it is for. But an acceptance that is written down is a decision; the same acceptance unwritten is just nobody having looked.

## Bend one: the most common shape was invisible

The first pass reported "1 HIGH" per install workflow — the standalone Windows job — and said nothing about the matrix axis. The scanner only read labels off the `runs-on:` line itself. A list feeding `${{ matrix.os }}` was not on that line, so it was not seen.

That is arguably the most common floating-label shape in real workflows, and my own repos were using it while my scanner certified them nearly clean.

The fix in v0.3.1 collects labels from the `os` axis and from keys the file actually references as `matrix.<key>`, plus bare list items carrying a GitHub-hosted runner prefix. It is narrow on purpose: a `browser: [chrome-latest]` axis, or a `- docker-latest` argument, must not be mistaken for a runner label. False positives are how a checklist tool gets uninstalled.

## Bend two: right severity, wrong reason

The pre-fix scanner also explained the Windows job's risk with Ubuntu wording — as if `windows-latest` moved 24.04 → 26.04. Same HIGH, wrong justification. If a tool gives the right grade for the wrong reason, you cannot trust the grade on the file where the reason would have changed it. Non-Ubuntu labels now get a message that does not claim the Ubuntu move.

## The class underneath both bends

A reader who walked the checklist on his own machine named the general pattern: the scanner reads one line, while a migration flows through indirection. Matrix was the first hop. Labels assigned to an `env:` key and referenced later, or fed by `vars:` / `inputs:` expressions, are the same hop in different clothes.

v0.3.2 covers that narrowly: a floating label assigned to a `*RUNNER*` key and actually referenced in the same file is flagged at the assignment, and a `runs-on:` fed by a single unresolved expression gets a warning that says "indirect" instead of a verdict the scanner cannot support. Composite actions and reusable workflows are not followed — that limit is now stated in the README instead of left implicit.

## The comparison is already scheduled

The same reader has committed to re-walking his machine after the cutover, on October 19/20, with the scanner pinned at v0.3.2. I will re-run the then-current release over this same inventory on October 20 and publish the row-by-row delta as a new field report — including the rows that did not move. The baseline is frozen; corrections land as dated addenda, not retroactive edits. A comparison you can be wrong in a checkable way is worth more than a victory lap.

The scanner is free and open source (MIT, single-file Python, standard library only): https://github.com/alapha888/runner-drift-audit — the full self-audit is in `field-reports/2026-10-13-pre-cutover-self-audit.md`. If you maintain many repositories, a paid batch edition ($29 one-time) scans a whole workspace into one merged report: https://alapha888.gumroad.com/l/mepra — the free single-repo tool stays free either way.

If you run the checklist on your own repos this week, I would rather hear where it bends than hear that it was green.
