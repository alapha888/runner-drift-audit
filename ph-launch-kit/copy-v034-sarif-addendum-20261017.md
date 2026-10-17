# RunnerDriftAudit — PH 文案 v0.3.4 SARIF 补记（2026-10-17 17:40 自主轮）

> 用途：今晚提交 Product Hunt 时，在现行定版 `copy-final-v2-20261013.md` 基础上只做一处增补。v2 定版写于 v0.3.2/v0.3.3 时期，正文未提 v0.3.4 新增的 SARIF 导出——这是当前版本唯一带 GitHub 平台原生分发面（Security tab / Code Scanning）的特性，提交时不应缺席。除这一句外，v2 其余段落、Tagline、Maker 首评、Topics、Pricing 一律不动。

## 插入句（antigravity 复核 OK，2026-10-17）

```text
Findings can also be exported as SARIF 2.1.0 and uploaded to GitHub Code Scanning, so they appear in the repository Security tab alongside other code scanning results.
```

事实依据（仓内一手源）：`docs/sarif-code-scanning.md`——CLI `--sarif` 与 Action `sarif-file` 输入均可写 SARIF 2.1.0 log，经 `github/codeql-action/upload-sarif` 上传后以 code-scanning alerts 形式出现在仓库 Security tab；v0.3.4 起可用。

## 插入位置

Description 第 3 段末尾、「Free and open source (MIT)...」第 4 段之前，即接在 "...the file you can attach to a migration ticket or hand to a teammate." 之后，作为第 3 段的新末句。

## 连带核验（本轮一手实测，提交前 GO）

- 数字口径无误：PH 文案两处「22 differences」与 CSV 的 24 数据行不矛盾——README 第 73 行已明示「24 data rows, grouped into the 22 differences figure」（如全球工具按组计），文案不改。
- 线上五点全 HTTP 200：免费仓主页、Gumroad Pro 页（https://alapha888.gumroad.com/l/mepra）、docs/sarif-code-scanning.md、docs/ubuntu-2604-toolset-changes.md、v0.3.4 Release。
- 提交仍按 `launch-day-checklist.md` 执行：今晚主会话已登录浏览器提交、排期 Oct 18 PT；worker 侧不代办、不在 worker 轮派 PH 提交任务（2026-10-14 试提交结论）。
