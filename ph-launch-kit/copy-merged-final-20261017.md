# RunnerDriftAudit — Product Hunt 提交合并终版（2026-10-17 晚制备，今晚提交只用这一份）

> 为什么有这份：定版 `copy-final-v2-20261013.md` 写于 v0.3.2/v0.3.3 时期，Description 未提 v0.3.4 的 SARIF 导出；SARIF 那句只存在于单独的补记文件 `copy-v034-sarif-addendum-20261017.md`，而 `launch-day-checklist.md` 第三节第 5 步仍只写「粘贴 v2 第 3 节」。照清单或照 v2 提交都会漏掉 SARIF。本文件 = v2 全文 + 按补记指定的位置插入 SARIF 句，其余一字未改。今晚提交请只用本文件，不要再拼 v2＋补记。
> 提交方式不变：今晚主会话已登录浏览器提交、排期 Oct 18（太平洋时间），北京时间 10-18 15:01 上线；阿发零动作，被人机验证/登录卡住才走清单 Plan B/C。

## 1. 产品名（Name）

```
RunnerDriftAudit
```

## 2. Tagline（主选，56 字符）

```
Audit your CI before ubuntu-latest moves to Ubuntu 26.04
```

## 3. Description（全文粘贴；SARIF 句已插入第 3 段末尾）

```
On October 19, 2026, GitHub starts moving the `ubuntu-latest` runner label from Ubuntu 24.04 to Ubuntu 26.04, with the rollout running through November 19. Nothing in your repository changes — the machine underneath your CI does.

Diffing GitHub's official runner-images toolsets (toolset-2404.json vs toolset-2604.json) surfaces 22 differences that can break a build or change it silently: tools removed from the image (mercurial, mediainfo, globally installed webpack/gulp/grunt, gcc-12, clang-16/17, p7zip), default versions that jump when nothing pins them (Java 17→25 with Java 8 gone, Node 22→24, PHP 8.3→8.5 only, PostgreSQL 16→18, Go 1.24→1.26, Docker 28→29), and a CMake that is no longer held back.

RunnerDriftAudit scans your workflow files and reports each risk at the exact line: floating `ubuntu-latest` labels (including labels supplied through matrix axes, and floating labels assigned to env keys the workflow actually references), removed tools invoked in run steps, default-version drift where no setup action pins a version, and actions referenced by mutable tags instead of full commit SHAs. Findings are graded HIGH and WARN, and the exit code is 1 whenever a HIGH exists, so it can gate a CI job. One more command turns the scan into a standalone migration-readiness report (Markdown + HTML): a severity overview, per-workflow findings, the full difference table, and a fix checklist derived from the findings — the file you can attach to a migration ticket or hand to a teammate. Findings can also be exported as SARIF 2.1.0 and uploaded to GitHub Code Scanning, so they appear in the repository Security tab alongside other code-scanning results.

Free and open source (MIT): a single Python file, standard library only, no dependencies, and it never phones home.
```

## 4. Topics

首选三个：`Developer Tools`、`GitHub`、`Open Source`；可加第 4 个时补 `DevOps`。

## 5. Website / Link

```
https://github.com/alapha888/runner-drift-audit
```

Thumbnail：`thumbnail-512.png`；Gallery 按序：`gallery-1-terminal.png`、`gallery-2-differences.png`、`gallery-3-timeline.png`。Pricing：选 **Free**。

## 6. Maker 首评（10-18 15:01 上线后第一小时内贴，全文与 v2 第 5 节一致，未改动）

```
Hi, I'm the maker of RunnerDriftAudit.

I built it after reading GitHub's migration notice for the `ubuntu-latest` label. The label is convenient, but it means the OS under your CI changes on GitHub's schedule, not yours: between October 19 and November 19 it moves from Ubuntu 24.04 to 26.04, and your workflow files don't change at all.

The raw material is public — GitHub publishes the toolset JSON for both runner images. Almost nobody diffs two files that size, so I did. The diff holds 22 differences: removed tools, default version jumps, and a few quiet removals. I turned each one into a scan rule.

On the sample workflows bundled in the repo, the deliberately messy one reports 3 HIGH (a floating `ubuntu-latest` label, a mercurial call, a global webpack call) and 3 WARN (Java drift, CMake drift, an unpinned action tag). The clean sample reports 0 HIGH. The scanner can also emit the whole result as a Markdown + HTML migration-readiness report, which is the format I actually ended up sharing with teammates.

Honest limits: this is a line scanner with shell-aware heuristics, not a full YAML or shell parser. Treat the output as a review checklist, not as proof that a build is safe.

If you run it on your own repos, I'd like to hear what it finds — and what the 26.04 move breaks for you that the rules don't cover yet.

One more thing: if you maintain many repos, there is a paid batch edition ($29 one-time) that scans a whole workspace of repositories and merges everything into a single HTML report — per-repo findings plus a cross-repo summary and fix checklists. It is on Gumroad (https://alapha888.gumroad.com/l/mepra); the free single-repo tool above stays free and open source either way.
```

> 若 PH 首评不允许外链：删去末段括号中的链接，其余不动。红线：任何地方不写求 upvote/求赞，只说欢迎反馈。
