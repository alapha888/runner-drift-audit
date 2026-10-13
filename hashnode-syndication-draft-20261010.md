# Hashnode 同步稿 · RunnerDriftAudit 到达稿（2026-10-10 克制推广备稿，待主会话发布）

> 状态：待主会话在已登录 Hashnode 会话中发布（子任务浏览器无 Hashnode 登录态，与既往 Hashnode 发布口径一致，不重复派发子任务发布）。
> 渠道依据：Hashnode 是本项目唯一出现过真实外部互动的内容渠道；本稿为同步分发（syndication），非新写长文：正文与 dev.to 首发一致，发布时请在 Hashnode 设置 canonical URL 指向 dev.to 原文，避免重复内容分散权重。
> dev.to 原文（canonical，请在 Hashnode 发布设置中填此 URL）：https://dev.to/alapha888/ubuntu-latest-moves-to-ubuntu-2604-on-october-19-22-toolset-differences-that-can-break-your-ci-4fch
> 验证口径：RunnerDriftAudit 付费形态登记验证不变（2026-11-19 前登记 ≥20 才建多仓审计报告）；本帖为该产品继 dev.to 首发、GitHub topics、主页入口、迁移指南 Gist 之后的新增外部到达面，卡 ubuntu-latest 迁移窗口 2026-10-19 开启前的时点。
> 发布位置：Hashnode 博客 https://alapha888.hashnode.dev/ ；发布后把本文 URL 回填探索队列。
> 资源终账：grok-4.5 -p → ubuntu 迁移社区落点给出实质结论（runner-images #14748/#14747、社区讨论 #187595，Reddit/HN 无对口帖），经 browser.search 复核属实；antigravity（约束版 prompt）→ 5 份论坛回复文案定稿已采用，本稿标题微调自主完成；browser.search → 全部关键事实复核。

Title: ubuntu-latest Moves to Ubuntu 26.04 on October 19 — 22 Toolset Differences That Can Break Your CI
Tags: githubactions, ci, devops, opensource

> 定稿来源：标题较 dev.to 首发作大小写微调（区分化处理，避免同题重复），正文与首发逐字一致；canonical 仍指向 dev.to 原文。

---

*This article is cross-posted from dev.to, where it was originally published. The scanner it describes, runner-drift-audit, is a small open-source CLI (MIT) that audits workflow files against the Ubuntu 24.04 → 26.04 runner toolset differences, available on GitHub at github.com/alapha888/runner-drift-audit.*

---

Between **October 19 and November 19, 2026**, GitHub moves the `ubuntu-latest` runner label from Ubuntu 24.04 to Ubuntu 26.04. Nothing in your repository changes — the machine underneath your CI does.

I diffed the official `actions/runner-images` toolsets (`toolset-2404.json` vs `toolset-2604.json`) on 2026-10-10 and found **22 differences**. These are the ones most likely to break or silently change a build:

## Removed outright

- **mercurial (`hg`)**, `mediainfo`, `sphinxsearch`, `haveged` — removed from the image
- **Globally preinstalled Node tools**: only `n` and `yarn` remain. `webpack`, `gulp`, `grunt`, `parcel`, `lerna`, `newman`, and `tsc` (typescript) are no longer preinstalled globally — a workflow that calls them without a local install or `npx` step will fail
- **Java 8** — removed; `gcc-12` / `gfortran-12` and `clang-16` / `clang-17` — removed
- `p7zip` is renamed to `7zip`; the `fastlane` gem is no longer bundled with rubygems

## Default versions that move under you

| Tool | 24.04 | 26.04 |
|---|---|---|
| Java (default) | 17 | 25 |
| Node (default) | 22 | 24 |
| PHP | 8.3 | 8.5 only |
| PostgreSQL | 16 | 18 |
| clang (default) | 18 | 21 |
| Go (default) | 1.24 | 1.26 |
| Docker / Compose | 28 / 2.38 | 29.4.2 / 5.1.3 |
| CMake | pinned at 3.31.6 | latest |

The CMake row deserves attention: on 24.04 it was deliberately held at 3.31.6 to avoid CMake 4.0 compatibility issues. On 26.04 it tracks latest, so CMake 4 behaviour may apply to projects that never opted in.

None of this matters if you pin a runner (`ubuntu-24.04`) and pin your tool versions with setup actions. It matters a lot if you use `ubuntu-latest` and rely on whatever happens to be installed.

## A 30-second check

I packaged the toolset diff as a small open-source scanner, **runner-drift-audit** (MIT, single-file Python, standard library only, no dependencies):

https://github.com/alapha888/runner-drift-audit

```bash
python3 runner_drift_audit.py /path/to/repo
```

It scans workflow files line by line and reports floating runner labels, invocations of removed tools, default-version drift where no setup action pins the version, and actions referenced by mutable tag instead of a full SHA. Exit code is 1 when any HIGH finding exists, so it can gate a CI job.

Tested behaviour, from the sample workflows bundled in the repo:

- A workflow using `ubuntu-latest`, calling `java`, `hg`, and a global `webpack`, and invoking `cmake` reports **3 HIGH** (floating label, mercurial removed, webpack no longer preinstalled) and **3 WARN** (unpinned `actions/checkout@v4`, Java default drift 17→25, CMake unpinned).
- A workflow pinned to `ubuntu-24.04`, with `actions/checkout` pinned by full SHA and Java pinned via `actions/setup-java`, reports **0 HIGH**.

## Limits

This is a line scanner with shell-aware heuristics (quotes, `sudo`/`env`/`VAR=val` prefixes, multi-line `run:` blocks), not a full YAML/shell parser. Treat findings as a review checklist, not a proof. It does not execute anything and does not phone home.

If your CI is green today on `ubuntu-latest`, the cheapest time to find out which of the 22 differences hits you is before October 19 — while you can still pin deliberately instead of debugging a runner you did not choose.
