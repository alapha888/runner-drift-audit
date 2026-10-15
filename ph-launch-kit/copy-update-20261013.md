# RunnerDriftAudit — PH 文案增补（2026-10-13，替代 copy-final 的对应段落）

> 【已归并】2026-10-13 21:40：本文件内容已并入 `copy-final-v2-20261013.md`（唯一现行口径），且 Pro 已开售、B 段改为无条件并入。本文件仅存档，提交时不要再用。

> 背景：copy-final.md 定稿于付费版建成之前，其合成说明里「付费形态未建成、未开售」的口径已过期。2026-10-13 已落地两件事：①免费侧新增迁移就绪报告生成器（一条命令产出 Markdown + HTML 报告：严重度总览、逐工作流发现项、完整差异表、修复清单，commit cf8aa78，已推送）；②付费侧多仓批量版已建成（私有仓 runner-drift-audit-pro，$29 一次性，Gumroad 上架稿已备，点火与否等阿发一句话，截至 10-13 09:48 未定）。
> 用法：10-17 晚提交时，Description 用下面 A 版全文替换 copy-final 第 3 节；Maker 首评用 A 版替换第 5 节。若届时 Gumroad 已点火，再按 B 版在首评末尾加一段即可，其余不动。Pricing 字段仍选 Free（PH 产品本体是免费工具，付费版是独立的多仓批量版，不改 PH 定价字段）。

## A 版 Description（替换 copy-final 第 3 节全文）

```
On October 19, 2026, GitHub starts moving the `ubuntu-latest` runner label from Ubuntu 24.04 to Ubuntu 26.04, with the rollout running through November 19. Nothing in your repository changes — the machine underneath your CI does.

Diffing GitHub's official runner-images toolsets (toolset-2404.json vs toolset-2604.json) surfaces 22 differences that can break a build or change it silently: tools removed from the image (mercurial, mediainfo, globally installed webpack/gulp/grunt, gcc-12, clang-16/17, p7zip), default versions that jump when nothing pins them (Java 17→25 with Java 8 gone, Node 22→24, PHP 8.3→8.5 only, PostgreSQL 16→18, Go 1.24→1.26, Docker 28→29), and a CMake that is no longer held back.

RunnerDriftAudit scans your workflow files and reports each risk at the exact line: floating `ubuntu-latest` labels, removed tools invoked in run steps, default-version drift where no setup action pins a version, and actions referenced by mutable tags instead of full commit SHAs. Findings are graded HIGH and WARN, and the exit code is 1 whenever a HIGH exists, so it can gate a CI job. One more command turns the scan into a standalone migration-readiness report (Markdown + HTML): a severity overview, per-workflow findings, the full difference table, and a fix checklist derived from the findings — the file you can attach to a migration ticket or hand to a teammate.

Free and open source (MIT): a single Python file, standard library only, no dependencies, and it never phones home.
```

与旧版的差异只有第三段最后一句（报告生成器），其余逐字未动——旧版已核过的事实口径全部保留。

## A 版 Maker 首评（替换 copy-final 第 5 节全文）

```
Hi, I'm the maker of RunnerDriftAudit.

I built it after reading GitHub's migration notice for the `ubuntu-latest` label. The label is convenient, but it means the OS under your CI changes on GitHub's schedule, not yours: between October 19 and November 19 it moves from Ubuntu 24.04 to 26.04, and your workflow files don't change at all.

The raw material is public — GitHub publishes the toolset JSON for both runner images. Almost nobody diffs two files that size, so I did. The diff holds 22 differences: removed tools, default version jumps, and a few quiet removals. I turned each one into a scan rule.

On the sample workflows bundled in the repo, the deliberately messy one reports 3 HIGH (a floating `ubuntu-latest` label, a mercurial call, a global webpack call) and 3 WARN (Java drift, CMake drift, an unpinned action tag). The clean sample reports 0 HIGH. The scanner can also emit the whole result as a Markdown + HTML migration-readiness report, which is the format I actually ended up sharing with teammates.

Honest limits: this is a line scanner with shell-aware heuristics, not a full YAML or shell parser. Treat the output as a review checklist, not as proof that a build is safe.

If you run it on your own repos, I'd like to hear what it finds — and what the 26.04 move breaks for you that the rules don't cover yet.
```

## B 版增补（仅当 Gumroad 付费版在 10-17 提交前已点火，追加在首评末尾，其余不动）

```
One more thing: if you maintain many repos, there is a paid batch edition ($29 one-time) that scans a whole workspace of repositories and merges everything into a single HTML report — per-repo findings plus a cross-repo summary and fix checklists. It is on Gumroad; the free single-repo tool above stays free and open source either way.
```

注意：B 版里的 Gumroad 链接 PH 首评是否可带外链以提交时界面为准；若不能贴链接，删去 "It is on Gumroad;" 半句、保留其余文字即可，不要为贴链接改动其他段落。

## 提交清单的连带修正（launch-day-checklist.md 不动原件，照此执行）

- 第三节第 5 步「Description 粘贴 copy-final 第 3 节」改为粘贴本文件 A 版 Description。
- 第四节第 1 步「首评粘贴 copy-final 第 5 节」改为粘贴本文件 A 版首评；已点火才加 B 版段落。
- 第三节第 10 步 Pricing 仍选 Free，不因付费版改动。
- 画廊图无需重做：gallery-1 的终端输出仍是现行扫描结果，报告生成器不入图（首评文字已覆盖）。
