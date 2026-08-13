#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scaffold.py — 初始化蒸馏产物的目录结构与 PIPELINE_STATE.md（断点续跑用）。

用法:
  python scaffold.py <slug> [--root "./distilled"]
"""
import argparse
import os

DEFAULT_ROOT = r"./distilled"

STRUCTURE = [
    "candidates",
    "rejected",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", help="内容 slug，如 influence-2026")
    ap.add_argument("--root", default=DEFAULT_ROOT)
    args = ap.parse_args()

    base = os.path.join(args.root, args.slug)
    os.makedirs(base, exist_ok=True)
    for sub in STRUCTURE:
        os.makedirs(os.path.join(base, sub), exist_ok=True)

    state_path = os.path.join(base, "PIPELINE_STATE.md")
    if not os.path.exists(state_path):
        with open(state_path, "w", encoding="utf-8") as f:
            f.write(f"# PIPELINE_STATE — {args.slug}\n\n")
            f.write("当前阶段: 0 (未开始)\n\n")
            f.write("## 阶段清单\n")
            for i, name in enumerate([
                "阶段0 Adler理解", "阶段1 并行提取", "阶段1.5 三重验证",
                "阶段2 RIA++构造", "阶段3 Zettelkasten链接",
                "阶段4 压力测试", "阶段5 交付",
            ]):
                f.write(f"- [ ] {i} {name}\n")
            f.write("\n## 各 skill 状态\n(待提取)\n")
    print(f"[scaffold] 已初始化: {base}")
    print(f"[scaffold] PIPELINE_STATE.md 路径: {state_path}")


if __name__ == "__main__":
    main()
