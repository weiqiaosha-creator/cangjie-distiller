# cangjie-distiller (Content Distillation · Windows-first)

Turn the **methodology** embedded in books, long videos, podcasts, and courses
into a set of atomic, agent-callable skills. Distill a book or a 3-hour talk
into a toolbox your agent can reach for on demand — not a book summary.

The distillation methodology (RIA-TV++) originates from the open-source
`kangarooking/cangjie-skill` (**AGPL-3.0**). `cangjie-distiller` is a standalone
derivative by 桥山知识库 (Qiaoshan Knowledge Base): the Windows adaptation, the
self-contained book/video/audio ingestion layer (yt-dlp + faster-whisper), the
security gate, the self-growth engine, and the robustness guardrails are
original implementations and do not depend on the upstream runtime.

## Capabilities
- **Ingestion layer (original)**: books PDF/EPUB/DOCX/MD → text; video URL →
  subtitles-first, else audio + whisper; audio/podcast → whisper ASR.
- **Distillation layer (RIA-TV++)**: Adler comprehension → 5-way parallel
  extraction → triple verification → RIA++ construction → Zettelkasten linking
  → pressure test → delivery.
- **Output**: under `<slug>/` — BOOK_OVERVIEW / candidates / verified /
  rejected / per-skill SKILL.md / INDEX / GLOSSARY / DIGEST / test-prompts,
  installable into the user skills directory so the agent can actually call them.

## Quick start
```powershell
# 1. install deps (managed venv)
& "<MANAGED_PYTHON_VENV>\Scripts\python.exe" "<SKILL_DIR>\scripts\install_deps.py"

# 2. ingest
python scripts/ingest_book.py --input book.pdf --output out.txt
python scripts/ingest_video.py --url "https://..." --output out.txt
python scripts/ingest_audio.py --input pod.m4a --output out.txt

# 3. scaffold output dir
python scripts/scaffold.py <slug>

# 4. run RIA-TV++ (see SKILL.md)
```
Replace the `<MANAGED_PYTHON_VENV>`, `<SKILL_DIR>`, `<USER_SKILLS_DIR>`
placeholders with your real paths.

## Cross-platform
Windows is first-class (managed venv + PowerShell + bundled yt-dlp/whisper).
macOS / Linux are supported via the system `python3 -m venv`. All scripts take
paths through `--input/--output/--venv/--root` and never hard-code an OS-specific
directory.

## Ecosystem
- `nuwa-skill`: distills *people*; this skill distills *books/videos/podcasts*.
- `darwin-skill`: evolves any skill; the `test-prompts.json` produced here
  follows the darwin format and can be fed straight into darwin-skill.

## License & attribution
Derivative of `kangarooking/cangjie-skill` (AGPL-3.0), released under the same
license. See `LICENSE` and `NOTICE`. The six guardrails come from
**大李 (yizhan-shengdeng v2 / 大李的AI知识库)**, used under explicit WeChat
permission (2026-08-10) with permanent attribution retained.

## Disclaimer
The word "仓颉" (Cangjie) here is unrelated to the **Huawei Cangjie programming
language**; it is only a name for this content-distillation methodology.
