#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ingest_audio.py — 把本地音频文件或播客 URL 转写为带时间戳文本（Windows）。

支持: 本地 .mp3/.wav/.m4a/.flac 等；或播客/音频 URL（先 yt-dlp 下载再 ASR）。
ASR: faster-whisper（默认 small，中文专名多建议 medium）。
用法:
  python ingest_audio.py --input "D:/podcast.m4a" --output "D:/out/audio.txt" [--model medium]
  python ingest_audio.py --url "https://podcast.example.com/ep.mp3" --output "D:/out/audio.txt"
"""
import argparse
import os
import subprocess
import sys
import tempfile
import traceback

SUPPORTED = (".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg", ".oga")


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def to_wav(src: str, workdir: str) -> str:
    wav = os.path.join(workdir, "audio.wav")
    subprocess.run(
        [ffmpeg_exe(), "-y", "-i", src, "-ar", "16000", "-ac", "1", wav],
        capture_output=True, text=True, timeout=300,
    )
    if not os.path.exists(wav):
        raise RuntimeError(f"ffmpeg 未能生成 wav: {src}")
    return wav


def asr(wav: str, model: str) -> str:
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
    ap.add_argument("--input")
    ap.add_argument("--url")
    ap.add_argument("--output", required=True)
    ap.add_argument("--model", default="small")
    args = ap.parse_args()

    if not args.input and not args.url:
        print("[ingest_audio][ERROR] 必须提供 --input 或 --url", file=sys.stderr)
        sys.exit(1)

    workdir = tempfile.mkdtemp(prefix="cangjie_aud_")
    try:
        if args.url:
            print("[ingest_audio] 下载音频 URL ...")
            dl = os.path.join(workdir, "media", "%(id)s.%(ext)s")
            subprocess.run(["yt-dlp", "-f", "bestaudio/best", "-o", dl, args.url],
                           capture_output=True, text=True, timeout=600)
            files = [os.path.join(workdir, "media", f) for f in os.listdir(os.path.join(workdir, "media"))]
            if not files:
                raise RuntimeError("下载失败")
            src = files[0]
        else:
            src = args.input
            ext = os.path.splitext(src)[1].lower()
            if ext not in SUPPORTED:
                raise ValueError(f"不支持的音频格式: {ext}")
        wav = to_wav(src, workdir)
        text = asr(wav, args.model)
    except Exception as e:
        print(f"[ingest_audio][ERROR] {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(f"<!-- source: {args.input or args.url} -->\n")
        f.write(text)
    print(f"[ingest_audio] 完成: {len(text)} 字 -> {args.output}")


if __name__ == "__main__":
    main()
