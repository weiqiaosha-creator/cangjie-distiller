#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill-growth-engine - 反馈吸收器（轴 1）
把桥山的纠错/补充/偏好写入目标 skill 的 registry.json。
  - absorbed_from="feedback"，authority_level=5（桥山本人），merge_status 默认 merged
  - 数值/事实型建议标 needs_review（与 study-note-forge 规则十四同构）

用法:
  python absorb_feedback.py --skill-dir DIR --title "..." --content "..." [--category 蒸馏判据] [--review]
  python absorb_feedback.py --skill-dir DIR --input feedback.md   # 取首行作标题，全文作内容
"""
import json
import os
import re
import sys
from datetime import date


def reg_path_for(skill_dir):
    return os.path.join(skill_dir, "knowledge", "registry.json")


def next_id(reg):
    nums = []
    for e in reg.get("entries", []):
        m = re.match(r".*-(\d+)$", str(e.get("id", "")))
        if m:
            nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1


def main():
    skill_dir = title = content = category = None
    inp = None
    review = False
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--skill-dir" and i + 1 < len(args):
            skill_dir = args[i + 1]
        elif a == "--title" and i + 1 < len(args):
            title = args[i + 1]
        elif a == "--content" and i + 1 < len(args):
            content = args[i + 1]
        elif a == "--category" and i + 1 < len(args):
            category = args[i + 1]
        elif a == "--input" and i + 1 < len(args):
            inp = args[i + 1]
        elif a == "--review":
            review = True

    if not skill_dir:
        print("--skill-dir required", file=sys.stderr)
        sys.exit(2)
    rp = reg_path_for(skill_dir)
    if not os.path.isfile(rp):
        print("registry not found:", rp, file=sys.stderr)
        sys.exit(2)

    if inp and os.path.isfile(inp):
        with open(inp, encoding="utf-8") as f:
            body = f.read().strip()
        if not title:
            title = body.splitlines()[0][:40] if body else "反馈条目"
        if not content:
            content = body

    if not title or not content:
        print("需要 --title + --content 或 --input 文件", file=sys.stderr)
        sys.exit(2)

    with open(rp, encoding="utf-8") as f:
        reg = json.load(f)

    eid = f"fb-{next_id(reg):03d}"
    entry = {
        "id": eid,
        "category": category or "反馈吸收",
        "title": title,
        "content": content,
        "source": "桥山反馈（对话）",
        "last_verified": date.today().isoformat(),
        "freshness_days": reg.get("default_freshness_days", 180),
        "confidence": "高",
        "authority_level": 5,
        "absorbed_from": "feedback",
        "derived_from": "",
        "verify_action": "下次相关对话复核",
        "merge_status": "needs_review" if review else "merged",
    }
    reg.setdefault("entries", []).append(entry)
    with open(rp, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)

    flag = "needs_review" if review else "merged"
    print(f"[absorb_feedback] 写入 {reg.get('skill')} <- {eid} 「{title}」 [{flag}]")


if __name__ == "__main__":
    main()
