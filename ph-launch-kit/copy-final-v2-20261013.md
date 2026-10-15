# RunnerDriftAudit — Product Hunt 文案定版 v2（2026-10-13 合并版，唯一现行口径）

> 合并来源：copy-final.md（基础稿）＋ copy-update-20261013.md（A/B 版增补）。本文件自包含，10-17 提交时只用这一份，另两份仅存档。
> 10-13 当日变化已全部并入：①付费版 RunnerDriftAudit Pro 已开售（2026-10-13 发布，$29 一次性，https://alapha888.gumroad.com/l/mepra ），B 版段落由「条件追加」改为无条件并入 Maker 首评末尾；②扫描器已升 v0.3.2——Description 第三段首句按实测更新：覆盖经 matrix 轴供给的浮动标签，以及经被实际引用的 env 键赋值的浮动标签（antigravity 复核提醒：不写成泛化的「表达式解析」，vars/inputs 供给仅报 INDIRECT 警告，文案据此收窄）；③samples/bad 实测输出与 v0.3.2 一致（3 HIGH＋3 WARN、clean 0 HIGH），画廊图无需重做。

## 1. 产品名（Name）

```
RunnerDriftAudit
```

## 2. Tagline（≤60 字符）

主选（56 字符）：

```
Audit your CI before ubuntu-latest moves to Ubuntu 26.04
```

备选 1（52 字符）：

```
Audit your CI before ubuntu-latest changes under you
```

备选 2（56 字符）：

```
Find what the Ubuntu 26.04 runner move will break, early
```

## 3. Description（全文粘贴）

```
On October 19, 2026, GitHub starts moving the `ubuntu-latest` runner label from Ubuntu 24.04 to Ubuntu 26.04, with the rollout running through November 19. Nothing in your repository changes — the machine underneath your CI does.

Diffing GitHub's official runner-images toolsets (toolset-2404.json vs toolset-2604.json) surfaces 22 differences that can break a build or change it silently: tools removed from the image (mercurial, mediainfo, globally installed webpack/gulp/grunt, gcc-12, clang-16/17, p7zip), default versions that jump when nothing pins them (Java 17→25 with Java 8 gone, Node 22→24, PHP 8.3→8.5 only, PostgreSQL 16→18, Go 1.24→1.26, Docker 28→29), and a CMake that is no longer held back.

RunnerDriftAudit scans your workflow files and reports each risk at the exact line: floating `ubuntu-latest` labels (including labels supplied through matrix axes, and floating labels assigned to env keys the workflow actually references), removed tools invoked in run steps, default-version drift where no setup action pins a version, and actions referenced by mutable tags instead of full commit SHAs. Findings are graded HIGH and WARN, and the exit code is 1 whenever a HIGH exists, so it can gate a CI job. One more command turns the scan into a standalone migration-readiness report (Markdown + HTML): a severity overview, per-workflow findings, the full difference table, and a fix checklist derived from the findings — the file you can attach to a migration ticket or hand to a teammate.

Free and open source (MIT): a single Python file, standard library only, no dependencies, and it never phones home.
```

## 4. Topics

首选三个：

```
Developer Tools
GitHub
Open Source
```

如选择器允许第 4 个或上述某项不存在，依次补/换：

```
DevOps
GitHub Actions
CI/CD
```

## 5. Maker 首评（上线后立刻贴出，全文粘贴，末段为 Pro 补充）

```
Hi, I'm the maker of RunnerDriftAudit.

I built it after reading GitHub's migration notice for the `ubuntu-latest` label. The label is convenient, but it means the OS under your CI changes on GitHub's schedule, not yours: between October 19 and November 19 it moves from Ubuntu 24.04 to 26.04, and your workflow files don't change at all.

The raw material is public — GitHub publishes the toolset JSON for both runner images. Almost nobody diffs two files that size, so I did. The diff holds 22 differences: removed tools, default version jumps, and a few quiet removals. I turned each one into a scan rule.

On the sample workflows bundled in the repo, the deliberately messy one reports 3 HIGH (a floating `ubuntu-latest` label, a mercurial call, a global webpack call) and 3 WARN (Java drift, CMake drift, an unpinned action tag). The clean sample reports 0 HIGH. The scanner can also emit the whole result as a Markdown + HTML migration-readiness report, which is the format I actually ended up sharing with teammates.

Honest limits: this is a line scanner with shell-aware heuristics, not a full YAML or shell parser. Treat the output as a review checklist, not as proof that a build is safe.

If you run it on your own repos, I'd like to hear what it finds — and what the 26.04 move breaks for you that the rules don't cover yet.

One more thing: if you maintain many repos, there is a paid batch edition ($29 one-time) that scans a whole workspace of repositories and merges everything into a single HTML report — per-repo findings plus a cross-repo summary and fix checklists. It is on Gumroad (https://alapha888.gumroad.com/l/mepra); the free single-repo tool above stays free and open source either way.
```

> 若 PH 首评不允许外链：删去末段括号中的链接，其余不动。

## 6. Pricing 字段

选 **Free**（PH 产品本体是免费工具；付费版是独立的多仓批量版，不改 PH 定价字段）。
