# RunnerDriftAudit — PH 画廊资产规格清单

PH 画廊推荐尺寸 1270×760。本 kit 的图全部为该尺寸（缩略图除外），已生成完毕并逐张目检通过（无文字溢出、无重叠）。生成脚本 `make_gallery.py` 在本目录，改文字后 `python3 make_gallery.py` 即可复现全部图。配色与仓 icon 一致（GitHub dark：#0d1117 底、#58a6ff 蓝、#3fb950 绿、#f0883e 橙）。

## 上传顺序（共 3 张画廊图 + 1 张缩略图）

### 0. thumbnail-512.png — 产品缩略图（512×512）
- 内容：按仓内 `icons/runner-drift-audit.svg` 的图形与配色用 PIL 重绘的 PNG 版（蓝 `>` 提示符 + 绿下划线 + 橙对勾）。
- 为什么需要：PH 缩略图只收 PNG/JPG，仓里的 SVG 传不了。发布时传这张。

### 1. gallery-1-terminal.png — 终端运行图（首图）
- 内容：终端窗口样式渲染：对 `samples/bad` 的真实运行结果（3 HIGH＋3 WARN，逐条规则名与行号）、退出码 1 的 CI gate 说明、对 `samples/clean` 的 0 HIGH 结果。
- 来源：2026-10-10 本机实测输出（`python3 runner_drift_audit.py samples/bad` / `samples/clean`），图内文字为实测输出的保真缩写（汇总行与真实输出一致）。
- 制作方式：已生成，无需再截真实终端图——渲染图比照片式截图更清晰且无路径/用户名噪声。

### 2. gallery-2-differences.png — 22 处差异概览图
- 内容：三栏——「Removed from the image」（mercurial、mediainfo、全局 npm 工具、gcc-12、clang-16/17、p7zip 等）/「Default versions jump」（Java 17→25、Node 22→24、PHP 8.3→8.5、PostgreSQL 16→18、Go、Docker、Compose）/「Also flagged」（浮动标签、可变 tag、CMake 未锁定）。
- 来源：仓 README 与 `runner_drift_audit.py` 的规则表（源自官方 toolset-2404.json vs toolset-2604.json 对比）。

### 3. gallery-3-timeline.png — 迁移时间线图
- 内容：横轴三节点——Oct 19 rollout 开始 → Oct 19–Nov 19 渐进切换 → Nov 19 窗口关闭；顶部蓝色条标注「Launching Oct 17-18」；底部条为退出码 gate 提示。

## 备注
- 三张图均为静态生成图，不含任何未经核实的数据：图中数字（22 处差异、3 HIGH＋3 WARN、0 HIGH、日期）全部与 README 及实测输出对过。
- 可选加图（如想凑 4 张）：在自己电脑终端真跑一次 `python3 runner_drift_audit.py samples/bad` 截全屏图。不加也不影响发布，本 kit 以 3 张为准。
