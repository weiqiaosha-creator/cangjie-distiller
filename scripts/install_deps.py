#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
install_deps.py — 将 cangjie-distiller 的依赖安装进受管 venv（不污染用户环境）。

用法:
  python install_deps.py [--venv "<USER_HOME>/.workbuddy/binaries/python/envs/default"]
"""
import subprocess
import sys
import os

# 受管 venv 默认位置（与二进制上下文一致）
DEFAULT_VENV = r"<MANAGED_PYTHON_VENV>"

# 依赖清单：书籍解析 + 视频/音频入库 + ASR
DEPS = [
    "pymupdf",          # PDF 文本抽取
    "ebooklib",         # EPUB 解析
    "beautifulsoup4",   # EPUB/HTML 清洗
    "python-docx",      # DOCX 解析
    "yt-dlp",           # 视频下载（优酷/B站/YouTube 等）
    "faster-whisper",   # 本地 ASR（ctranslate2，Windows 友好）
    "imageio-ffmpeg",   # 提供 ffmpeg 二进制（视频提取音频用）
    "numpy",            # faster-whisper 运行依赖兜底
]


def find_python(venv: str) -> str:
    # Windows venv 的 python 解释器
    cand = os.path.join(venv, "Scripts", "python.exe")
    if os.path.exists(cand):
        return cand
    # 退化为系统 python（不推荐）
    return sys.executable


def main():
    venv = DEFAULT_VENV
    if "--venv" in sys.argv:
        venv = sys.argv[sys.argv.index("--venv") + 1]
    py = find_python(venv)
    print(f"[install_deps] 目标 venv python: {py}")

    # 确保 venv 存在
    if not os.path.exists(os.path.join(venv, "Scripts", "python.exe")):
        print("[install_deps] venv 不存在，正在创建 ...")
        subprocess.check_call([sys.executable, "-m", "venv", venv])

    for pkg in DEPS:
        print(f"[install_deps] 安装 {pkg} ...")
        try:
            subprocess.check_call([py, "-m", "pip", "install", "--upgrade", pkg])
        except subprocess.CalledProcessError as e:
            print(f"[install_deps][WARN] {pkg} 安装失败: {e}", file=sys.stderr)

    print("[install_deps] 完成。可用 `python ingest_book.py --help` 验证。")


if __name__ == "__main__":
    main()
