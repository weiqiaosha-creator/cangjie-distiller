#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ingest_video.py — 把视频 URL 转写为带时间戳的文本（Windows）。

策略:
  1. 优先抽取平台字幕（yt-dlp --write-subs，自动选中文/英文）。
  2. 无字幕时：下载最佳音视频 -> ffmpeg 提取音频 -> faster-whisper ASR。

依赖: yt-dlp, faster-whisper, imageio-ffmpeg（提供 ffmpeg 二进制）。
用法:
  python ingest_video.py --url "https://..." --output "D:/out/video.txt" [--model medium]
"""
import argparse
import os
import subprocess
import sys
import tempfile
import traceback


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        # 用户自行安装了 ffmpeg 并加入 PATH
        return "ffmpeg"


def try_subtitles(url: str, workdir: str) -> str | None:
    """尝试抽取字幕；成功返回字幕文本，否则返回 None。"""
    # 先列出可用字幕
    try:
        listing = subprocess.run(
            ["yt-dlp", "--list-subs", url],
            capture_output=True, text=True, timeout=120,
        )
    except Exception:
        return None
    # 优先 zh-Hans/zh-CN/zh/zh-Hant，其次 en
    prefs = ["zh-Hans", "zh-CN", "zh", "zh-Hant", "en", "en-US", "en-GB"]
    chosen = None
    for lang in prefs:
        if lang in listing.stdout:
            chosen = lang
            break
    if not chosen:
        return None
    # 下载字幕为 .vtt
    sub_path = os.path.join(workdir, "subs")
    subprocess.run(
        ["yt-dlp", "--write-subs", "--sub-langs", chosen,
         "--skip-download", "-o", os.path.join(sub_path, "%(id)s.%(ext)s"), url],
        capture_output=True, text=True, timeout=180,
    )
    for f in os.listdir(sub_path):
        if f.endswith(".vtt"):
            return _vtt_to_text(os.path.join(sub_path, f))
    return None


def _vtt_to_text(vtt_path: str) -> str:
    import re
    with open(vtt_path, "r", encoding="utf-8", errors="ignore") as fh:
        raw = fh.read()
    # 去掉 WEBVTT 头与计时行
    lines = []
    for ln in raw.splitlines():
        if ln.strip().startswith("WEBVTT"):
            continue
        if re.match(r"^\d{2}:\d{2}", ln):
            continue
        if "-->" in ln:
            continue
        if ln.strip():
            lines.append(ln.strip())
    return "\n".join(lines)


def asr_audio(url: str, workdir: str, model: str) -> str:
    # 1. 下载最佳音视频
    dl = os.path.join(workdir, "media", "%(id)s.%(ext)s")
    subprocess.run(
        ["yt-dlp", "-f", "bestaudio/best", "-o", dl, url],
        capture_output=True, text=True, timeout=600,
    )
    media_files = [os.path.join(workdir, "media", f) for f in os.listdir(os.path.join(workdir, "media"))]
    if not media_files:
        raise RuntimeError("下载失败，未得到媒体文件")
    src = media_files[0]
    # 2. ffmpeg 提取 16k 单声道 wav
    wav = os.path.join(workdir, "audio.wav")
    subprocess.run(
        [ffmpeg_exe(), "-y", "-i", src, "-ar", "16000", "-ac", "1", wav],
        capture_output=True, text=True, timeout=300,
    )
    # 3. faster-whisper ASR
    from faster_whisper import WhisperModel
    m = WhisperModel(model, device="cpu", compute_type="int8")
    segments, _ = m.transcribe(wav, beam_size=5, language=None)
    out = []
    for seg in segments:
        mm = int(seg.start // 60)
        ss = int(seg.start % 60)
        out.append(f"[{mm:02d}:{ss:02d}] {seg.text}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--model", default="small", help="whisper 模型 small/medium/large")
    args = ap.parse_args()

    workdir = tempfile.mkdtemp(prefix="cangjie_vid_")
    text = None
    try:
        print("[ingest_video] 尝试抽取字幕 ...")
        text = try_subtitles(args.url, workdir)
        if text:
            print("[ingest_video] 字幕抽取成功。")
        else:
            print("[ingest_video] 无字幕，走音频 ASR ...")
            text = asr_audio(args.url, workdir, args.model)
    except Exception as e:
        print(f"[ingest_video][ERROR] {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(f"<!-- source: {args.url} -->\n")
        f.write(text)
    print(f"[ingest_video] 完成: {len(text)} 字 -> {args.output}")


if __name__ == "__main__":
    main()
