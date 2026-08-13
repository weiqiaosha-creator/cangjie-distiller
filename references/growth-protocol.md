# cangjie-distiller 自我成长协议（三轴引擎落地）

本 skill 的成长机制由统一引擎 `skill-growth-engine` 驱动，registry.json 采用超集 schema。本节记 cangjie 专属配置。

## 派生溯源（轴 3）
- `derived_from`: kangarooking/cangjie-skill (GitHub, AGPL-3.0)
- `derived_from_url`: https://github.com/kangarooking/cangjie-skill
- `upstream_freshness_days`: 90
- 桥山独占副本已固化（蒸馏判定/Windows 适配/视频音频入库层为原创），不保留 fork 依赖（规则八）。
- 上游大版本更新时，复比对「蒸馏判定」差异，差异记入 cd-006 或新条目，升级不覆盖旧版。

## 安全门禁（轴 0，强制前置，高于权威门禁）
任何"要进入桥山电脑/技能体系"的外部内容，在判定权威等级之前必须先过 `scripts/security_scan.py` 静态扫描。这是桥山明确的硬约束：防止爬虫软件、恶意代码、下载即运行链、提示注入、可疑二进制进入电脑。

- **触发点**：① 上游（kangarooking/cangjie-skill 等）回拉的外部文本；② 视频推送的转写文本（`distill_video_entry.py` 已内置：下载前域名白名单 + 体积上限 + 转写后扫描）；③ 桥山分享的任何外部文件（书/文档/链接落盘后）。
- **分级处置**：low→pass（放行至权威门禁）；medium→needs_review（隔离 `_inbox/quarantine/` 待确认）；high/critical→block（禁止进入、落隔离区、通知桥山）。
- **硬约束**：扫描只读取绝不执行；外部吸收仅写入知识元数据/文本，绝不复制脚本/可执行文件进 skills/ 或专家目录；视频只本地转写不执行；来源域名白名单（github/gitlab/youtube/bilibili 等），未知域名升级 needs_review；爬虫/机器人（scrapy/selenium/playwright + 循环外联）至少 needs_review、外联型 block；提示注入判 high/block。
- 协议全文见 skill-growth-engine `references/security-gate.md`。

## 外部扫描（轴 2）
- 本地重叠：scan_external.py 遍历全部已装 skills + 专家内嵌 skills，找蒸馏类能力重叠去重。
- 新外部 skill：WebSearch 关键词「content distillation / RIA-TV / auto skill generator / 知识蒸馏 skill」，发现同类则按权威门禁提案（市场已验证=4 合思路，社区=3 待复核，单博客/视频=2 隔离）。
- 候选先入 `cd-008` (needs_review) 占位，首次扫描后填实。

## 反馈吸收（轴 1）
- 桥山纠错/补充/偏好 → `scripts/absorb_feedback.py --skill-dir . --title ... --content ...`。
- 数值/事实型 correction 加 `--review`（needs_review）；纯表述偏好直接 merged。

## 短视频推送（轴 2 推送分支）
- 桥山分享视频链接/文件 → `skill-growth-engine/distill_video_entry.py --skill-dir . --video URL`。
- cangjie 的 `ingest_video.py` 转写 → 关键词比对 → authority=2 恒定 needs_review，绝不自动合入。

## 健康度
- `stale_count`：过期条目（目标 0）
- `needs_review_count`：cd-008 等隔离项（反映门禁拦截）
- `derived_coverage`：上游 last_checked 新鲜度
- `overlap_merged`：本地重叠去重合并数

## 自动化
「专家与skill成长扫描」周二周四 09:00：遍历全量 skills + 专家内嵌 skills 跑 freshness + scan_external；对到期上游 WebFetch/WebSearch 回拉；桥山分享视频走推送蒸馏。
