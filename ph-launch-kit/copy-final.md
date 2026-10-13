# RunnerDriftAudit — Product Hunt 文案定稿

> 合成方式：antigravity 两档（Gemini 3.8 Flash Medium / Claude Sonnet 4.6）各出一版（原稿存 `drafts/`），本定稿由主 agent 重新合成——tagline 取「迁移在你脚下发生」的核心洞察并补齐版本号，Description 按 PH 阅读节奏重排，Maker 首评重写缘起段。所有事实与仓 README 及实测输出一致；付费形态（$29 fleet audit）未建成、未开售，全文案不提、不暗示可购买。

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

## 3. Description

```
On October 19, 2026, GitHub starts moving the `ubuntu-latest` runner label from Ubuntu 24.04 to Ubuntu 26.04, with the rollout running through November 19. Nothing in your repository changes — the machine underneath your CI does.

Diffing GitHub's official runner-images toolsets (toolset-2404.json vs toolset-2604.json) surfaces 22 differences that can break a build or change it silently: tools removed from the image (mercurial, mediainfo, globally installed webpack/gulp/grunt, gcc-12, clang-16/17, p7zip), default versions that jump when nothing pins them (Java 17→25 with Java 8 gone, Node 22→24, PHP 8.3→8.5 only, PostgreSQL 16→18, Go 1.24→1.26, Docker 28→29), and a CMake that is no longer held back.

RunnerDriftAudit scans your workflow files and reports each risk at the exact line: floating `ubuntu-latest` labels, removed tools invoked in run steps, default-version drift where no setup action pins a version, and actions referenced by mutable tags instead of full commit SHAs. Findings are graded HIGH and WARN, and the exit code is 1 whenever a HIGH exists, so it can gate a CI job.

Free and open source (MIT): a single Python file, standard library only, no dependencies, and it never phones home.
```

## 4. Topics（3–5 个，按 PH 选择器实际可选项贴近选）

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

## 5. Maker 首评（发布成功后立刻由 maker 本人贴出）

```
Hi, I'm the maker of RunnerDriftAudit.

I built it after reading GitHub's migration notice for the `ubuntu-latest` label. The label is convenient, but it means the OS under your CI changes on GitHub's schedule, not yours: between October 19 and November 19 it moves from Ubuntu 24.04 to 26.04, and your workflow files don't change at all.

The raw material is public — GitHub publishes the toolset JSON for both runner images. Almost nobody diffs two files that size, so I did. The diff holds 22 differences: removed tools, default version jumps, and a few quiet removals. I turned each one into a scan rule.

On the sample workflows bundled in the repo, the deliberately messy one reports 3 HIGH (a floating `ubuntu-latest` label, a mercurial call, a global webpack call) and 3 WARN (Java drift, CMake drift, an unpinned action tag). The clean sample reports 0 HIGH.

Honest limits: this is a line scanner with shell-aware heuristics, not a full YAML or shell parser. Treat the output as a review checklist, not as proof that a build is safe.

If you run it on your own repos, I'd like to hear what it finds — and what the 26.04 move breaks for you that the rules don't cover yet.
```

## 6. 其他表单字段

- **Website / Link**：`https://github.com/alapha888/runner-drift-audit`
- **Pricing**：Free
- **Thumbnail**：用 `thumbnail-512.png`（本 kit 内；PH 要求 PNG/JPG，仓里的 SVG 不能直接用）
- **Gallery 顺序**：`gallery-1-terminal.png` → `gallery-2-differences.png` → `gallery-3-timeline.png`
- **Makers**：只加本人账号为 maker
