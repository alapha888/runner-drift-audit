# RunnerDriftAudit — PH 上线日公告草稿（2026-10-16 制备，10-18 上线后使用）

> 用途：Product Hunt 上线日（北京时间 2026-10-18 15:01 后）在自有渠道发布的公告。红线：不写求票/求赞，只说「已发布、欢迎反馈」；不动用阿发既有渠道（公众号/微信群/雪球/小圈）。
> 发布落点（上线后按序，各最多一次）：① dev.to 短帖（自有账号 alapha888）② X @afa668 一条 ③ Indie Hackers 自有账号（如已注册）。链接上线后回填 PH 产品页 URL（占位 <PH_URL>）。

## dev.to / 通用版（英文）

Title: RunnerDriftAudit is live on Product Hunt today

Body:
I shipped RunnerDriftAudit on Product Hunt today: <PH_URL>

It is a free, open-source scanner (single Python file, no dependencies) that checks your GitHub Actions workflows before GitHub moves the `ubuntu-latest` label from Ubuntu 24.04 to 26.04 — the rollout starts October 19 and runs through November 19.

It reports, at the exact line: floating `ubuntu-latest` labels, removed tools still called in run steps, default-version drift where nothing pins a version, and actions referenced by mutable tags instead of full commit SHAs. On the bundled samples, the messy one reports 3 HIGH + 3 WARN; the clean one reports 0 HIGH.

If you try it on your own repos, feedback on what it finds — and what it misses — is welcome, either on the PH page or in the repo issues.

## X 版（≤280 字符，链接另计）

RunnerDriftAudit is live on Product Hunt today. Free, open-source scanner that checks your GitHub Actions workflows before `ubuntu-latest` moves from Ubuntu 24.04 to 26.04 — rollout starts Oct 19, through Nov 19. Feedback welcome: <PH_URL>

## 中文版（自有渠道备用）

RunnerDriftAudit 今天上线 Product Hunt：<PH_URL>
一个免费开源的单文件 Python 扫描器，在 GitHub 于 10 月 19 日起至 11 月 19 日把 `ubuntu-latest` 从 Ubuntu 24.04 逐步迁往 26.04 之前，逐行检查你的 Actions 工作流会踩到哪些移除工具与默认版本漂移。欢迎试用与反馈。
