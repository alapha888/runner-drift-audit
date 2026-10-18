# RunnerDriftAudit — PH 上线日公告（2026-10-18 修订版，上线后使用）

> 用途：Product Hunt 上线日（北京时间 2026-10-18 15:01 后）在自有渠道发布的公告。红线：不写求票/求赞，只说「已发布、欢迎反馈」；不动用阿发既有渠道（公众号/微信群/雪球/小圈）。
> 发布落点（上线后按序，各最多一次）：① dev.to 短帖（自有账号 alapha888）② X @afa668 一条 ③ Indie Hackers 自有账号（如已注册）。链接上线后回填 PH 产品页 URL（占位 <PH_URL>）。
> 2026-10-18 14:40 修订说明：原稿写于 2026-10-16（v0.3.3 时期），未含 v0.3.4 SARIF 导出、v0.3.5 JSON 导出、v0.3.6 Markdown job summary 与 v0.3.7 的 RETIRED_LABEL（macos-14 退役）规则；本版按 v0.3.7 现行事实修订三语版本，PH 提交文案（copy-merged-final-20261017.md）冻结不动。若 PH 未按时上线（Plan B/C 顺延），本公告顺延到实际上线日再发，日期表述按实际上线日调整。

## dev.to / 通用版（英文）

Title: RunnerDriftAudit is live on Product Hunt today

Body:
I shipped RunnerDriftAudit on Product Hunt today: <PH_URL>

It is a free, open-source scanner (single Python file, no dependencies) that checks your GitHub Actions workflows ahead of two changes that start tomorrow, October 19: GitHub begins moving the `ubuntu-latest` label from Ubuntu 24.04 to 26.04 (rollout through November 19), and the `macos-14` runner images enter their brownout window ahead of retirement on November 2.

It reports, at the exact line: floating `ubuntu-latest` labels, workflows still pinned to the retiring `macos-14` labels, removed tools still called in run steps, default-version drift where nothing pins a version, and actions referenced by mutable tags instead of full commit SHAs. Findings can be exported as SARIF 2.1.0 for GitHub Code Scanning, as plain JSON, or as a Markdown summary on the run page. On the bundled samples, the messy one reports 3 HIGH + 3 WARN; the clean one reports 0 HIGH.

If you try it on your own repos, feedback on what it finds — and what it misses — is welcome, either on the PH page or in the repo issues.

For many repos at once, there is a paid batch edition ($29 one-time) that merges a whole workspace into one HTML report: https://alapha888.gumroad.com/l/mepra — the free single-repo tool stays free either way.

## X 版（≤280 字符，链接另计）

RunnerDriftAudit is live on Product Hunt today. Free scanner for GitHub Actions workflows ahead of two Oct 19 changes: `ubuntu-latest` starts moving to Ubuntu 26.04, and `macos-14` enters brownouts before its Nov 2 retirement. Feedback welcome: <PH_URL>

## 中文版（自有渠道备用）

RunnerDriftAudit 今天上线 Product Hunt：<PH_URL>
一个免费开源的单文件 Python 扫描器，赶在明天（10 月 19 日）两个变化之前检查你的 Actions 工作流：GitHub 开始把 `ubuntu-latest` 从 Ubuntu 24.04 逐步迁往 26.04（至 11 月 19 日），且 `macos-14` 镜像进入 11 月 2 日退役前的 brownout 窗口。它逐行报告浮动标签、仍在用退役标签、已移除工具调用、默认版本漂移与未 pin 的 action 引用，结果可导出 SARIF / JSON 或写进运行页摘要。欢迎试用与反馈。
