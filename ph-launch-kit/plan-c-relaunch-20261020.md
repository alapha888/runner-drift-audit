# RunnerDriftAudit — Product Hunt Plan C 重提就绪包（2026-10-20 制备）

> 用途：Plan B（10-19 15:01 上线）公开侧未生效，本包供主会话在已登录浏览器里执行 Plan C 时照着做。执行者仍是主会话已登录浏览器（worker 侧无 PH 登录态，既往实证不再重试）。阿发零动作；只有 PH 人机验证/登录确实卡住时才找他。

## 一、Plan B 未上线的证据（2026-10-20 06:40 轮定性，已闭合）

- 站内搜索：精确名 `RunnerDriftAudit` 与拆分名 `Runner Drift Audit` 均显示 No products found；部分词只出无关产品；Posts/Topics 亦 0。
- 10-19 当日榜单：Featured 视图 17 条无此产品；All 视图完整加载全部 866 条后定向检出仍无此名称。
- 结论：10-19 的提交/排期在公开侧没有产生任何可检索痕迹。账号内状态（草稿未提交／排期未生效／被资格拦截）未知，必须先在账号内查清再重提，避免建出重复产品。

## 二、重提前的账号内诊断（先查后提，约 2 分钟）

1. 登录后先看 **My products / Drafts / Scheduled** 三处：有没有 RunnerDriftAudit 的草稿或待上线排期。
   - 有草稿 → 打开草稿，核对内容后直接走第三节提交，不要新建第二个产品。
   - 有排期但日期已过且未上线 → 取消旧排期，按第三节重新排期/上线。
   - 三处都没有 → 按第三节从零提交。
2. 若任何一步出现资格拦截提示（一周等待期、完善资料要求等），截图留存，不要反复改资料或重复提交；按 `launch-day-checklist.md` 第五节的英文支持话术联系 PH 支持，并把日期顺延一天。
3. 提交完成后立刻做公开侧复核：退出登录态（或无痕窗口）打开产品页 URL，确认可访问；再用站内搜索精确名确认能搜到。把产品页 URL 记下来回传。

## 三、提交口径（与清单第三节相同，只改日期）

- 文案唯一现行版仍是 `copy-merged-final-20261017.md`（含 SARIF 句），Name / Tagline / Description / Topics / Pricing=Free / Website 一律照贴。
- Thumbnail：`thumbnail-512.png`（512×512）；Gallery 按序 `gallery-1-terminal.png`、`gallery-2-differences.png`、`gallery-3-timeline.png`（均 1270×760）。2026-10-20 预检：四张 PNG 尺寸与格式实测无误。
- 上线时间（三选一，均北京时间 15:01 = 当日 PT 00:01）：
  - 首选 **Oct 20（周二 PT）**：今日 15:01 前完成排期，或 15:01 后 Launch now。
  - 次选 Oct 21（周三 PT）／末选 Oct 22（周四 PT）：同样 15:01 口径。
  - Oct 22 之后不再顺延 PH：迁移窗口叙事开始变旧，改以 dev.to 长文＋目录收录为主线，PH 只作有机会再补的渠道。
- 预检（2026-10-20 07:40 实测）：仓库公开页 https://github.com/alapha888/runner-drift-audit 可达；扫描器测试 64 项全绿；README 的 Action 引用为 v0.3.7；Pro Gumroad 链接 https://alapha888.gumroad.com/l/mepra 仍写在首评末段（照原文贴；若 PH 不允许首评外链，按合并终版的注记删去括号中的链接，其余不动）。

## 四、文案时态核查（Oct 20 口径，只有两处可选微调，其余零改动）

合并终版写于窗口开启前。Oct 20 读起来仍成立的部分不要动；只有下面两处时态可按需替换，换不换都不影响事实：

1. Description 第一句可选替换：
   - 原文：`On October 19, 2026, GitHub starts moving the ubuntu-latest runner label from Ubuntu 24.04 to Ubuntu 26.04, with the rollout running through November 19.`
   - Oct 20 版：`On October 19, 2026, GitHub started moving the ubuntu-latest runner label from Ubuntu 24.04 to Ubuntu 26.04, with the rollout running through November 19.`
2. 首评第二段可选替换：
   - 原文：`between October 19 and November 19 it moves from Ubuntu 24.04 to 26.04`
   - Oct 20 版：`between October 19 and November 19 it is moving from Ubuntu 24.04 to 26.04`

Description 第 3 段与首评其余段落全部照原文，包括数字（22 处差异、样本 3 HIGH/3 WARN 与 0 HIGH）——2026-10-20 复跑实测仍与基线一致，不改数字。

## 五、首评可加的一句新鲜证据（可选，加在首评「Honest limits」段之前）

窗口开启后已有实证，合并终版里还没有；加这一句能让 Oct 20 的读者看到产品不是窗口前的一次性发布：

```
Since launch week began: the scanner caught a `macos-14` pin in one of my own repositories hours before its first brownout window (fixed the same morning), and a re-run of my October 13 baseline on October 20 reproduced it exactly — no finding appeared or disappeared just because the window opened.
```

事实出处：`field-reports/2026-10-19-day1-self-scan.md`（PhotoVeil 仓 macos-14 于 brownout 当日修复）与 `field-reports/2026-10-20-post-cutover-self-audit.md`（基线 4/2、4/2、0/2 精确复现）。不加也不影响提交；不要再加第二句，避免首评变长。

## 六、上线后第一小时（与清单第四节相同）

1. 贴首评（合并终版第 6 节全文，含可选时态替换与可选新增句）。
2. 回评论只感谢＋实质回应，不求票、不刷无关帖、不动用阿发既有渠道、不注册小号。
3. 把产品页 URL 与值得注意的评论回传，后续跟进归 Muse。

## 七、判定口径

- Oct 20–22 任一天公开侧可检索到产品页＝Plan C 成功，此后按评论/流量/Pro 点击判定 PH 渠道价值。
- 三天内仍无法上线（资格拦截且支持未解）＝PH 渠道暂时 blocked，记档后转其他渠道，不再逐日重试。
