---
name: cangjie-distiller
version: v1.4.0
description: >-
  Windows content-distillation meta-skill: turn books (PDF/EPUB/DOCX), long videos
  (YouTube/Bilibili via yt-dlp + whisper) and audio/podcasts into a coherent pack of
  executable, agent-callable skills using the RIA-TV++ pipeline. Use when the user wants to
  "蒸馏一本书/视频/播客" / "把 XX 做成可调用 skill" / "把长内容变成方法论工具包" — NOT for plain
  summarization, book reviews, or role-playing the author.
---

# cangjie-distiller — Windows 内容蒸馏元技能

## 使命

把一本书、一场长视频、一期播客、一门课程里沉淀的**方法论、决策框架、原则、清单、概念体系**，
蒸馏成一组**原子化、可被 Agent 在真实场景下直接调用**的 skill，让知识从「看过/听过」变成「用得上」。

> 术语约定：本文档里所有「书」泛指一切被蒸馏的长内容——书籍、长视频转写、播客文字稿、课程、访谈、长文、资料集。

**边界（质量红线之一）**
- 做：方法论 / 决策框架 / 清单 / 原则 / 概念体系的蒸馏
- 不做：书摘 / 读后感 / 作者人设角色扮演（那是 nuwa 类技能的活）

## 与上游开源项目的关系（确权说明）

本技能的方法论源自开源项目 `kangarooking/cangjie-skill`（AGPL-3.0，RIA-TV++ 流水线），
由「桥山知识库」按全局规则八固化为**独占独立副本**：蒸馏判定逻辑、Windows 适配、视频/音频入库层
均为本技能原创实现，不依赖原仓库运行时，不保留 fork 引用。原项目仅作为方法论灵感来源被致谢。

## 永久署名（迭代不得删除）

> **六护栏启发自大李的AI知识库（飞书）**。作者大李，飞书文档 https://evi49lo48z.feishu.cn/wiki/Rqp5wxOi6ix9Jtk7WnRcDQmrnEc 。
> 2026-08-10 大李通过微信明确授权再分发与合并发布（回复「可以」，截图存证）。
> **此段为永久署名痕迹。不论本技能迭代至何版本，此段必须保留在 SKILL.md 或 README 中，不得移除、不得弱化。**
> **本激活副本用途说明（2026-08-10）**：当前激活的 cangjie-distiller 即「内部自用完整版 v1.3.0」（含 yizhan-shendeng-v2 / 大李的AI知识库的六护栏，cd-010 已获大李微信授权转正）。该副本默认供桥山个人内部自用；对外发布可改用归档中的「v1.3.0-publish（完整发布版-含署名）」或「v1.3.0-original（桥山原创版）」变体。


## 核心方法论：RIA-TV++

```
阶段 0: Adler 整书理解      → BOOK_OVERVIEW.md
阶段 1: 5 个 extractor 并行  → 候选方法论单元池 (candidates/)
阶段 1.5: 三重验证筛选       → verified.md + rejected/（用户轻确认）
阶段 2: RIA++ 构造 skill     → 每个 skill 的 SKILL.md (R/I/A1/A2/E/B)
阶段 3: Zettelkasten 链接    → INDEX.md + GLOSSARY.md
阶段 4: 压力测试             → test-prompts.json + 回炉淘汰
阶段 5: 交付                 → DIGEST.md 精华长文 + 安装到 ~/.workbuddy/skills/
```

- **RIA**：便签拆书法 Reading / Interpretation / Appropriation
- **TV**：Triple Verification 三重验证（跨域 / 预测力 / 独特性）
- **++**：面向 Agent 执行的扩展 —— E（Execution 可执行步骤）+ B（Boundary 边界）

## 何时调用

用户说类似：
- "帮我把《XX》蒸馏成 skill"
- "把这个 B 站/YouTube 视频/播客/课程蒸馏成 skill"
- "把这篇长文里的方法论做成可调用工具"
- "distill this book/video/audio into skills: <path|url>"

## 输入要求（开始前必须确认）

1. **内容来源**：本地书籍路径（pdf/epub/docx/md/txt）、视频 URL、或音频/播客文件或 URL。
   - 没有可访问文本时**不要凭记忆蒸馏**——停下来问用户要源文件/链接。
   - 视频/播客先用本技能的入库脚本（`scripts/ingest_video.py` / `scripts/ingest_audio.py`）拿到转写文本。
2. **内容元信息**：书名+作者+出版年；或视频/播客的标题+讲者+发布时间。用于目录命名与审计。
3. **输出位置**：默认 `./distilled\<slug>\`，可让用户改；是否安装进用户技能目录（`~/.workbuddy/skills/`）需确认。
4. **是否首次试点**：首次建议先蒸馏 1 份内容验证流程，再批量。

非书籍内容的字段映射：`source_chapter` 等「章节」字段——视频填时间戳/分P，播客填集数，课程填讲次，保证可追溯。

## 入库层（Windows 适配，本技能原创）

所有入库脚本用受管 Python 运行（依赖装进受管 venv，不污染用户环境）：

```powershell
# 一次性安装依赖（装进受管 venv）
& "<MANAGED_PYTHON_VENV>\Scripts\python.exe" `
   "<SKILL_DIR>\scripts\install_deps.py"

# 书籍 → 纯文本
& "<MANAGED_PYTHON_VENV>\Scripts\python.exe" `
   "<SKILL_DIR>\scripts\ingest_book.py" `
   --input "D:\path\to\book.pdf" --output "D:\out\book.txt"

# 视频 URL → 转写文本（优先字幕，否则音频+whisper）
& "<MANAGED_PYTHON_VENV>\Scripts\python.exe" `
   "<SKILL_DIR>\scripts\ingest_video.py" `
   --url "https://..." --output "D:\out\video.txt"

# 本地音频 / 播客 URL → 转写文本
& "<MANAGED_PYTHON_VENV>\Scripts\python.exe" `
   "<SKILL_DIR>\scripts\ingest_audio.py" `
   --input "D:\path\to\audio.m4a" --output "D:\out\audio.txt"
```

依赖：`pymupdf`（PDF）、`ebooklib`+`beautifulsoup4`（EPUB）、`python-docx`（DOCX）、
`yt-dlp`（下载）、`faster-whisper`（ASR）、`imageio-ffmpeg`（提供 ffmpeg 二进制）。
ASR 默认模型 `small`（中文内容建议 `medium` 以提升专名准确率，见 `ingest_audio.py --model`）。

## 跨平台支持与生态（v1.4.0 新增）

本技能以 **Windows 为一等公民**（受管 venv + PowerShell + yt-dlp/faster-whisper 自带入库），同时兼容 macOS / Linux（系统 Python venv）。跨平台调用方式：

```powershell
# Windows（受管 venv，默认）
& "<MANAGED_PYTHON_VENV>\Scripts\python.exe" "…/cangjie-distiller/scripts/ingest_book.py" --input book.pdf --output out.txt
```
```bash
# macOS / Linux（系统 python3 venv）
python3 -m venv .venv && . .venv/bin/activate
python scripts/install_deps.py --venv ./.venv
python scripts/ingest_book.py --input book.pdf --output out.txt
```
脚本均通过 `--input/--output/--venv/--root` 参数接收路径，**不写死 OS 专属目录**；仅在 SKILL.md/README 示例中给出 Windows 受管路径作为默认示范。

生态咬合（吸收上游 `kangarooking/cangjie-skill` 的公开定位）：
- `nuwa-skill`：蒸馏「人」（思维 DNA）；本技能蒸馏「书/视频/播客」的方法论；二者互补。
- `darwin-skill`：进化任意 skill。本技能产出的 `test-prompts.json` **严格遵循 darwin 格式**，可直接喂给 darwin-skill 做自动进化（分数只升不降）。
- 上游的视频/播客入库依赖外部 `video-downloader` skill；本技能改为**自包含入库层**（ingest_video/ingest_audio 内置 yt-dlp + faster-whisper），不依赖外部仓库。

## 蒸馏层（由 Agent 执行，本技能提供 prompts 与模板）

`scripts/scaffold.py <slug>` 会初始化输出目录结构与 `PIPELINE_STATE.md`（断点续跑用）。
每个阶段完成后更新该文件（当前阶段 / 已完成产物 / 各 skill 状态 / 下一步）。

### 阶段 0 — Adler 整书理解
读取入库得到的文本（大文件分块）。按 `references/methodology/stage0-adler.md` 的四步
（结构 / 解释 / 批判 / 应用）执行，按 `references/templates/BOOK_OVERVIEW.md` 填充。
展示给用户确认骨架后再进阶段 1。

### 阶段 1 — 5 个 extractor 并行提取
用 **Agent 工具**一次发起 5 个 sub-agent，分别加载 `references/extractors/` 下的 5 个 prompt：
框架 / 原则 / 案例 / 反例 / 术语。各自独立读原文、独立输出到 `candidates/<type>.md`。
- 长文本超出单 sub-agent 上下文：按 `references/methodology/stage1-parallel.md` 分块。
- 降级：环境不支持并行 sub-agent 时，串行执行同一组 prompt，产出格式不变。
- **覆盖率守护（移植自 yizhan-shendeng v2）**：每批五路返回后做逐块回执检查（详见 `references/methodology/stage1-parallel.md`），任一区块缺回执只补派漏块一次、不整批重来；这是长文本 sub-agent 跳读的第一道防线。

### 阶段 1.5 — 三重验证筛选（主料/配料分离 + 自校准 + 降级）
按 `references/methodology/stage1.5-triple-verify.md` 对每个候选做：
- **V1 跨域**：原文至少 2 处独立段落佐证？
- **V2 预测力**：能回答书里没明说的新问题？
- **V3 独特性**：不是任何聪明人都懂的常识？**新增公开理论阈值过滤**——剔除 SWOT/MECE/金字塔原理等已广泛流传的框架，但保留作者在其上加的具体阈值/判据（详见该文件）。
- **主料/配料分离（移植自 yizhan-shendeng v2）**：框架、原则过三重验证；案例、反例、术语只去重、不验证（反例是阶段 2 的 B 段边界素材，误杀会掏空「何时不该用」）。
- **通过率自校准（移植自 v2）**：书 30%–50%、转写稿 15%–30% 为正常区间，越界只重筛一次即放行，防烧额度。
- **全军覆没降级（移植自 v2）**：重筛后仍 0 通过，留 `candidates/` 待捞，不静默失败、不硬造。
通过的写 `verified.md`，不通过的写 `rejected/` 并附原因（保留审计轨迹，允许事后捞回）。
**用户轻确认★**：展示「通过 N 个 + 淘汰 M 个」列表，确认后再进阶段 2。

### 阶段 2 — RIA++ 构造 skill
对每个通过单元，按 `references/templates/SKILL.md.template` 填充六段：
- **R** 原文引用 ≤150 字/段（英文 ≤100 词）
- **I** 用自己的话重写方法论骨架
- **A1** 书中作者用过的案例
- **A2** ★ 未来触发情境 → 即该 skill 的 `description`（必须含明确 trigger 条件）
- **E** 1-2-3 可执行步骤
- **B** 何时不适用 / 作者盲点（来自阶段 0 批判）

细则见 `references/methodology/stage2-ria-plus.md`。A2「与相邻 skill 区分」先写初稿，阶段 3 回填定稿。

### 阶段 3 — Zettelkasten 链接
按 `references/methodology/stage3-zettelkasten.md`：找 skill 间引用关系（依赖/对比/组合），
在每个 SKILL.md 末尾补「相关 skills」并回填 A2 区分；生成 `INDEX.md`（含 mermaid 引用图）与 `GLOSSARY.md`。

### 阶段 4 — 压力测试（双层诱饵 + 自触发必考题）
按 `references/methodology/stage4-pressure-test.md`：每个 skill 写 5–10 条 `test-prompts.json`，
含三类——应调用 / 不应调用（诱饵）/ 边界模糊；诱饵至少 1 条是「应触发同包另一 skill」的跨 skill 混淆测试。
**新增自触发必考题（移植自 yizhan-shendeng v2）**：必含一题「帮我把这本书蒸馏成技能」，正确判定须触发 cangjie-distiller 自身、而非任一新产出的 skill——防产物抢走本技能 trigger 导致再也无法蒸馏。
优先用独立 sub-agent 盲测，对照预期统计；**未过则回炉重做阶段 2**，不表面修补。结果写 `<skill>/test-results.md`。

### 阶段 5 — 交付
按 `references/methodology/stage5-deliver.md`：生成 `DIGEST.md` 精华长文（不读全书看这篇够）；
询问安装位置，把通过测试的 skill 复制/软链进 `~/.workbuddy/skills/<slug>-<skill-name>/`——
**没有这一步，产出的 skill 无法被真正调用**。告知用户可继续迭代。

## 质量红线（违反则阻止输出）

1. 每个 skill 必须通过**全部**三重验证。
2. 每个 skill 必须有完整的 R / I / A1 / A2 / E / B 六段。
3. 原文引用 ≤150 字/段（英文 ≤100 词/段）。
4. 每个 skill 必须有 `test-prompts.json` 且含诱饵测试，诱饵至少 1 条是同包兄弟 skill 场景。
5. `description` 必须明确 trigger 条件，不能只是「一个关于 X 的 skill」。

## 调用惯例

- 永远先试点 1 份，除非用户明确说「批量」。
- 阶段之间主动汇报进度，不要静默跑完再 dump。
- 不凭记忆蒸馏——没文本就停下来问。
- 保留审计轨迹——`candidates/` 与 `rejected/` 都要留。
- 随时可续跑——每完成一阶段更新 `PIPELINE_STATE.md`。

## 与桥山知识库既有体系的协同

- 蒸馏产物（skill 包）落 `./distilled\`，不散落主目录（遵规则十六）。
- 入库前的原始长内容如需永久留存，按 AGENTS.md 文件收纳规则归入 `原始素材/` 对应分类。
- 与 `study-note-expert`（学习笔记）分工：本技能产出「可执行工具」，学习笔记产出「可读沉淀」，二者互补不重叠。
- 本地成长账本见 `knowledge/registry.json`（蒸馏判据、ASR 纠词、压力测试先例，含 last_verified + 180 天新鲜度）。

## 自我成长（三轴引擎，详见 skill-growth-engine）

本 skill 采用统一自我成长引擎，registry.json 为超集 schema（`derived_from`/`authority_level`/`absorbed_from`/`merge_status`）。

- **轴 1 反馈吸收**：桥山纠错/补充 → `scripts/absorb_feedback.py` 写入 registry（`absorbed_from=feedback`，authority=5；数值型标 needs_review）。
- **轴 2 外部扫描**：遍历本地已装 skills + 专家内嵌 skills 找重叠去重（`scripts/scan_external.py`）；对 `derived_from` 上游（kangarooking/cangjie-skill）到期回拉；新外部蒸馏类 skill 经权威门禁提案合并。
- **轴 3 派生溯源**：`derived_from="kangarooking/cangjie-skill"`，`upstream_freshness_days=90`，定期回拉上游更新，使桥山独占副本不滞后于源。
- **安全门禁（轴 0，强制前置）**：任何外部内容（上游回拉文本/视频转写/桥山分享文件）进入体系前先过 `scripts/security_scan.py`；block 直接丢弃并通知，needs_review 隔离，pass 才进权威门禁。针对桥山硬约束：防爬虫软件、恶意代码、下载即运行链、提示注入、可疑二进制进入电脑。详见 skill-growth-engine references/security-gate.md。
- **权威门禁**：authority>=4 自动合并，==3 合并待复核，<=2（含单条短视频演示）一律 needs_review 隔离，**绝不自动合入**。
- **短视频推送**：桥山分享视频链接/文件 → `skill-growth-engine/distill_video_entry.py` 调本 skill `ingest_video.py` 转写 → 经门禁判定合入或催生新 skill（详见 skill-growth-engine references/video-push-protocol.md）。
- **自动化**：「专家与skill成长扫描」周二周四 09:00 驱动全量 freshness + scan_external + 上游回拉 + 视频推送。
- **v1.3.0 合并来源（轴 2 派生溯源扩展，已授权）**：本次吸收外部蒸馏类 skill `yizhan-shendeng-v2`（一盏神灯 v2 / 大李的AI知识库）的执行层护栏（逐块回执覆盖率 / 主料配料验证分离 / 公开理论阈值过滤 / 通过率自校准 / 全军覆没降级 / 自触发必考题）。**2026-08-10 已获大李微信授权（回复「可以」），cd-010 转正 merged（authority=5），永久署名义务见上方「永久署名」段。** 护栏已并入蒸馏逻辑，本技能原有的三轴成长、安全门禁、权威门禁保持不变。

## 开源发布合规（v1.4.0 新增）

本技能为 `kangarooking/cangjie-skill`（**AGPL-3.0**）的演绎作品。对外发布（如 GitHub）须满足：

- **许可证**：发布包必须以 **AGPL-3.0** 发布，附完整 LICENSE 全文；不得改以 MIT / 专有等更宽松许可。
- **署名**：保留上游 `kangarooking/cangjie-skill` 原作者署名与 AGPL-3.0 声明；保留「永久署名」段对大李（yizhan-shendeng v2）六护栏的署名与授权说明。
- **变更声明**：标注「基于 AGPL-3.0 上游演绎，重大变更见 commit 历史」。
- **源码可得**：GitHub 公开仓库天然满足 AGPL 对应源码要求。
- **脱敏**：发布前移除 `<USER_HOME>/…` / `<YOUR_KB>/…` 等个人路径（发布就绪包见 `技能版本归档/仓颉内容蒸馏/v1.4.0-publish/`）。
- **不打包未授权组件**：上游视频入库依赖的外部 `video-downloader` skill 不在本技能内，勿误打包。
- **免责**：README 注明「与华为仓颉编程语言无关」，降低同名混淆。

合规发布即合法，不构成侵权；非合规发布（改宽松许可 / 删署名 / 闭源）才构成 AGPL 侵权。
