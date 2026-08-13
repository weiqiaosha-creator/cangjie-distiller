#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill-growth-engine - 外部源扫描器（本地重叠检测 + 上游 watchlist 到期检查）
注意：本脚本只做"本地可爬取"部分，不联网。真正的 WebSearch/WebFetch 回拉由自动化中的 Agent 执行。

轴 2（外部 4 源）：
  - WorkBuddy 市场：遍历本地已装 skills + 专家内嵌 skills 的 registry.json 找能力重叠/互补
  - GitHub / SkillHub / ClawHub：读 watchlist（上游 repo/市场链接），检查 derived_from 到期
轴 3（派生溯源）：derived_from != original 且 upstream_last_checked 超 upstream_freshness_days → 标 due

输出 candidates.json：
  { "overlaps": [...], "upstream_due": [...], "new_external_todo": "由 Agent 经 WebSearch 补" }

用法:
  python scan_external.py --skill-dir DIR [--watchlist FILE] [--out candidates.json]
"""
import json
import os
import sys
from datetime import date, datetime

USER = os.path.expanduser("~")
SKILLS_ROOT = os.path.join(USER, ".workbuddy", "skills")
EXPERT_SKILLS = os.path.join(USER, ".workbuddy", "plugins", "marketplaces", "my-experts", "plugins")


def reg_path_for(skill_dir):
    return os.path.join(skill_dir, "knowledge", "registry.json")


def discover_registries():
    """返回全部本地 registry 路径（含专家内嵌）。"""
    out = []
    if os.path.isdir(SKILLS_ROOT):
        for name in os.listdir(SKILLS_ROOT):
            rp = os.path.join(SKILLS_ROOT, name, "knowledge", "registry.json")
            if os.path.isfile(rp):
                out.append(rp)
    if os.path.isdir(EXPERT_SKILLS):
        for exp in os.listdir(EXPERT_SKILLS):
            sdir = os.path.join(EXPERT_SKILLS, exp, "skills")
            if not os.path.isdir(sdir):
                continue
            for sk in os.listdir(sdir):
                rp = os.path.join(sdir, sk, "knowledge", "registry.json")
                if os.path.isfile(rp):
                    out.append(rp)
    return out


def norm(text):
    return "".join(text.lower().split())


def jaccard(a, b):
    sa, sb = set(norm(a)), set(norm(b))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def main():
    skill_dir = None
    watchlist = None
    out_path = "candidates.json"
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--skill-dir" and i + 1 < len(args):
            skill_dir = args[i + 1]
        elif a == "--watchlist" and i + 1 < len(args):
            watchlist = args[i + 1]
        elif a == "--out" and i + 1 < len(args):
            out_path = args[i + 1]

    if not skill_dir:
        print("--skill-dir required", file=sys.stderr)
        sys.exit(2)
    tgt = reg_path_for(skill_dir)
    if not os.path.isfile(tgt):
        print("target registry not found:", tgt, file=sys.stderr)
        sys.exit(2)

    with open(tgt, encoding="utf-8") as f:
        treg = json.load(f)
    tentries = treg.get("entries", [])
    tcorpus = [f"{e.get('title','')} {e.get('content','')}" for e in tentries]

    # 本地重叠检测
    overlaps = []
    for rp in discover_registries():
        if os.path.abspath(rp) == os.path.abspath(tgt):
            continue
        try:
            with open(rp, encoding="utf-8") as f:
                oreg = json.load(f)
        except Exception:
            continue
        if not isinstance(oreg, dict):
            continue  # 跳过非标准（如顶层为 list）的账本
        oname = oreg.get("skill") or os.path.basename(os.path.dirname(os.path.dirname(rp)))
        oauth = oreg.get("authority_level", 4) if "authority_level" in oreg else 4
        for e in oreg.get("entries", []):
            ec = f"{e.get('title','')} {e.get('content','')}"
            best = max((jaccard(tc, ec) for tc in tcorpus), default=0.0)
            if best >= 0.18:  # 文本重合阈值，命中即疑似重叠/互补
                overlaps.append({
                    "source_skill": oname,
                    "source_authority": oauth,
                    "entry_id": e.get("id"),
                    "entry_title": e.get("title"),
                    "similarity": round(best, 3),
                    "merge_status_proposal": "merged" if oauth >= 3 else "needs_review",
                })

    # 上游 watchlist 到期
    upstream_due = []
    if treg.get("derived_from") not in (None, "original", ""):
        uc = None
        try:
            uc = datetime.strptime(treg.get("upstream_last_checked", ""), "%Y-%m-%d").date()
        except Exception:
            pass
        uf = treg.get("upstream_freshness_days", 90)
        if uc:
            age = (date.today() - uc).days
            if age > uf:
                upstream_due.append({
                    "derived_from": treg.get("derived_from"),
                    "url": treg.get("derived_from_url", ""),
                    "days_overdue": age - uf,
                })
    # watchlist 文件（额外上游 URL）
    if watchlist and os.path.isfile(watchlist):
        try:
            wl = json.load(open(watchlist, encoding="utf-8"))
            for item in wl.get("watch", []):
                uc = None
                try:
                    uc = datetime.strptime(item.get("last_checked", ""), "%Y-%m-%d").date()
                except Exception:
                    pass
                uf = item.get("freshness_days", 90)
                if uc and (date.today() - uc).days > uf:
                    upstream_due.append({
                        "derived_from": item.get("name"),
                        "url": item.get("url", ""),
                        "days_overdue": (date.today() - uc).days - uf,
                    })
        except Exception as ex:
            print("watchlist parse warn:", ex, file=sys.stderr)

    result = {
        "skill": treg.get("skill"),
        "scanned_at": date.today().isoformat(),
        "overlaps": overlaps,
        "upstream_due": upstream_due,
        "note": "new_external_todo（GitHub/SkillHub/ClawHub 新发现）由自动化 Agent 经 WebSearch 补，并据权威门禁提案。",
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[scan_external] {treg.get('skill')}: 本地重叠 {len(overlaps)} 条，上游到期 {len(upstream_due)} 条 -> {out_path}")


if __name__ == "__main__":
    main()
