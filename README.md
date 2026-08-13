# cangjie-distiller（仓颉内容蒸馏 · Windows 版）

把书籍、长视频、播客、课程里沉淀的**方法论**，蒸馏成一组**原子化、可被 Agent 直接调用**的 skill。
方法论源自开源 `kangarooking/cangjie-skill`（AGPL-3.0，RIA-TV++ 流水线），由「桥山知识库」固化为独占独立副本：
蒸馏判定逻辑、Windows 适配、视频/音频入库层均为本技能原创实现，不依赖原仓库运行时。

## 能力
- **入库层（原创）**：书籍 PDF/EPUB/DOCX/MD → 文本；视频 URL → 字幕优先/否则音频+whisper；音频/播客 → whisper ASR。
- **蒸馏层（RIA-TV++）**：Adler 理解 → 5 路并行提取 → 三重验证 → RIA++ 构造 → Zettelkasten 链接 → 压力测试 → 交付。
- **产出**：`<slug>/` 下的 BOOK_OVERVIEW / candidates / verified / rejected / 各 skill / INDEX / GLOSSARY / DIGEST / test-prompts，并可安装进用户技能目录真正可被调用。

## 快速开始
```powershell
# 1. 装依赖（受管 venv）
& "<MANAGED_PYTHON_VENV>\Scripts\python.exe" `
   "<SKILL_DIR>\scripts\install_deps.py"

# 2. 入库
python scripts/ingest_book.py --input book.pdf --output out.txt
python scripts/ingest_video.py --url "https://..." --output out.txt
python scripts/ingest_audio.py --input pod.m4a --output out.txt

# 3. 初始化产物目录
python scripts/scaffold.py <slug>

# 4. 由 Agent 执行 RIA-TV++（见 SKILL.md）
```

## 目录
```
cangjie-distiller/
├── SKILL.md
├── README.md
├── icon.ico
├── references/   RIA-TV++ 方法论 + 5 个 extractor + 模板
├── scripts/      install_deps / ingest_book / ingest_video / ingest_audio / scaffold
└── knowledge/    registry.json 成长账本
```

## 边界
做方法论/框架/原则蒸馏；不做书摘、读后感、作者人设角色扮演。

## 跨平台
本技能以 **Windows 为一等公民**（受管 venv + PowerShell + yt-dlp/faster-whisper 自带入库），同时兼容 macOS / Linux（系统 `python3 -m venv`）。示例中的 `<MANAGED_PYTHON_VENV>`、`<SKILL_DIR>`、`<USER_SKILLS_DIR>` 为占位符，请替换为你的实际路径。

## 生态
- `nuwa-skill`：蒸馏「人」；本技能蒸馏「书/视频/播客」的方法论，互补。
- `darwin-skill`：进化任意 skill；本技能产出的 `test-prompts.json` 遵循 darwin 格式，可直接进化。
- 上游 `kangarooking/cangjie-skill` 的视频入库依赖外部 `video-downloader` skill；本技能改为自包含入库层。

## 许可证与署名
- 本作品为 `kangarooking/cangjie-skill`（**AGPL-3.0**）的演绎作品，以相同许可证发布。详见 `LICENSE` 与 `NOTICE`。
- 六护栏（逐块回执覆盖率 / 主料配料验证分离 / 公开理论阈值过滤 / 通过率自校准 / 全军覆没降级 / 自触发必考题）来自 **大李（yizhan-shendeng v2 / 大李的AI知识库）**，依其 2026-08-10 微信授权（再分发+合并发布）使用，永久署名保留。

## 免责声明
本项目的「仓颉」一词与**华为仓颉编程语言**无关，仅为内容蒸馏方法论的命名，请勿混淆。
