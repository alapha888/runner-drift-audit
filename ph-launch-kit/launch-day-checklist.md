# RunnerDriftAudit — Product Hunt 发布日操作清单（照着做版）

> 你只需要照着本清单在自己的电脑上操作。文案、图全部在同目录备好（`copy-final.md` + 3 张 gallery 图 + `thumbnail-512.png`），每一步贴哪段都写明了。Muse 的浏览器过不了 PH 人机验证，所以提交动作由你完成；发布后的跟进（评论回复口径、数据回收）由 Muse 接手。

## 一、先定时间（结论先行）

- **发布日：2026 年 10 月 18 日（周日，太平洋时间）。**
- PH 的「一天」从太平洋时间 00:01 开始。10 月太平洋时间是 PDT（UTC−7），与北京时间差 15 小时：**PT 10 月 18 日 00:01 = 北京时间 10 月 18 日 15:01**。产品的展示日就是北京时间 10/18 15:01 → 10/19 14:59。
- 两种操作方式，任选其一：
  - **方式 A（推荐，排期）**：10 月 17 日（周六）晚上把表单全部填好，选排期到 Oct 18 上线，之后不用守时间。
  - **方式 B（当天手动）**：存草稿，**10 月 18 日 15:01（北京时间）之后**再点 Launch now。注意：15:01 之前点会落进 10 月 17 日的 PH 日，只剩半天曝光，不要提前手滑。
- 为什么选 18 日：17 日是周六、PH 流量最弱；18 日周日略好，且离 19 日迁移窗口开启只差一天，「窗口开始前先审计」的叙事最紧。

## 二、发布前准备（10 月 17 日白天，约 5 分钟）

1. 打开本文件夹 `ph-launch-kit/`，确认有：`copy-final.md`、`gallery-1-terminal.png`、`gallery-2-differences.png`、`gallery-3-timeline.png`、`thumbnail-512.png`。
2. 在自己电脑的浏览器打开 producthunt.com，确认右上角显示已登录（就是 10 月 10 日用 Google 授权注册的那个账号，头像在即已登录）。
3. 若站点提示先完善个人资料：bio 填一句即可——`Indie maker building small developer tools.`；能跳过就跳过，不影响发产品。

## 三、提交步骤（照着贴）

1. 点右上角 **Submit** → 选 **Product / New product**。
2. 链接框粘贴：`https://github.com/alapha888/runner-drift-audit`，点继续（站点会自动抓取仓库信息）。
3. **Name**：确认是 `RunnerDriftAudit`，不对就手动改成这个。
4. **Tagline**：打开 `copy-final.md` 第 2 节，粘贴「主选」那一整行（不要自己加句号或改词）。
5. **Description**：粘贴 `copy-final.md` 第 3 节的全部四段。
6. **Website / Link**：确认是第 2 步那个 GitHub 地址。
7. **Thumbnail**：上传 `thumbnail-512.png`（不要传仓里的 SVG，PH 不收）。
8. **Gallery**：按顺序上传 `gallery-1-terminal.png`、`gallery-2-differences.png`、`gallery-3-timeline.png`。
9. **Topics**：搜索并选 `Developer Tools`、`GitHub`、`Open Source`；若某项搜不到就跳过，若还能多选就加 `DevOps`。
10. **Pricing**：选 **Free**。
11. **Makers**：确认名单里有你自己（默认会带上提交账号）。
12. **上线时间**：选 **Schedule launch**，日期选 **October 18, 2026**（站点按太平洋时间 00:01 自动上线，即北京时间 10/18 15:01）。如果界面上没有排期选项：先存草稿，按方式 B 在 10/18 15:01 后回来点 **Launch now**。
13. 点提交（Launch / Schedule）。看到产品页生成就是成功——把产品页网址留存（微信/备忘录随手记下即可，之后告诉 Muse）。

## 四、发布后第一小时动作（北京时间 10/18 15:01–16:01；不方便守点的话当晚补做，但首评越早贴越好）

1. **贴首评**：打开产品页评论区，粘贴 `copy-final.md` 第 5 节的 Maker 首评全文。这是固定动作，不要改写。
2. **回评论**：有人评论就回，原则是感谢＋一句实质回应，不求票。可直接套用的两条：
   - `Thanks! The rules come from diffing GitHub's two official toolset JSONs — happy to add a check if your stack hits something I missed.`
   - `Good question — it's a line scanner with heuristics, not a full parser, so treat the findings as a review checklist. The README has the details.`
   - 拿不准怎么答的，截图发给 Muse 拟稿，你贴回去即可。
3. **红线（务必遵守）**：
   - 不要在任何地方写「求 upvote / 帮我投票 / 点个赞」——PH 明文禁止拉票，查到会降权。只能说「今天在 PH 发布了，欢迎反馈」。
   - 不要把链接刷到无关帖子、群聊里；不要动用公众号、微信群、雪球等既有渠道（军令状独立性红线）。
   - 不要注册小号给自己投票或评论。
   - 当天最多在 1–2 个与 GitHub Actions / ubuntu 迁移直接相关的讨论里提一次，且先回答问题、再附链接。
4. 把产品页网址和值得注意的评论告诉 Muse，后续跟进归 Muse。

## 五、如果发帖资格仍被「一周等待期」拦住

先说清为什么大概率不会发生：账号 10 月 10 日注册，到 10 月 17 日已满一周；且注册时已订阅 newsletter，按 PH 官方口径订阅可豁免等待。若仍被拦：

1. 不要反复改资料或重复提交。把拦截提示**截图发给 Muse** 判断原因。
2. **Plan B（改期一天，材料零改动）**：顺延到 **10 月 19 日（周一，太平洋时间）**，北京时间 10/19 15:01 上线。周一是 PH 流量最好的日子之一，且当天正是迁移窗口开启日——文案里 "starts moving"、"between October 19 and November 19" 当天读起来全部成立，全套材料一个字不用改。
3. **Plan C**：再延到 10 月 20–22 日（周二至周四）任一天，同样北京时间 15:01 上线；迁移进行中的叙事仍成立（窗口持续到 11 月 19 日）。
4. 若需联系 PH 支持，用这句英文（只在支持渠道用）：`Hi, I registered on Oct 10 and subscribed to the newsletter, but I'm still unable to post my first product. Could you check my account? Thanks.`
5. 无论走哪个 Plan，都不要另注册新账号（PH 对多账号很严）。

## 六、时间换算备查

| PH 日期（PT） | 上线时刻（PT） | 北京时间 |
|---|---|---|
| Oct 18（周日）首选 | 00:01 PDT | 10 月 18 日 15:01 |
| Oct 19（周一）Plan B | 00:01 PDT | 10 月 19 日 15:01 |
| Oct 20–22 Plan C | 00:01 PDT | 对应日期 15:01 |

- [ ] Maker 首评与产品描述带上付费版：RunnerDriftAudit Pro（多仓合并报告）$29 已上线 https://alapha888.gumroad.com/l/mepra （2026-10-13 发布），免费版照常主推，Pro 只作一行补充。
