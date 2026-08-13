#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill-growth-engine - 通用新鲜度扫描器
扫描目标 skill 的 knowledge/registry.json，输出：
  - 普通过期/临期条目（基于 freshness_days）
  - 上游到期条目（derived_from != original 且 upstream_last_checked 超 upstream_freshness_days）
供周二周四 09:00 自动化调用。

用法:
  python freshness.py [--skill-dir DIR] [--json] [--warn-days 30]
  --skill-dir 省略时扫描本引擎自身 registry（便于单独测试）。
"""
import json
import os
import sys
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))


def reg_path_for(skill_dir):
    if skill_dir:
        return os.path.join(skill_dir, "knowledge", "registry.json")
    return os.path.join(HERE, "..", "knowledge", "registry.json")


def parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None


def main():
    warn_days = 30
    as_json = False
    skill_dir = None
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--json":
            as_json = True
        elif a == "--skill-dir" and i + 1 < len(args):
            skill_dir = args[i + 1]
        elif a == "--warn-days" and i + 1 < len(args):
            try:
                warn_days = int(args[i + 1])
            except ValueError:
                pass

    rp = reg_path_for(skill_dir)
    if not os.path.isfile(rp):
        print("registry not found:", rp, file=sys.stderr)
        sys.exit(2)

    with open(rp, encoding="utf-8") as f:
        reg = json.load(f)

    today = date.today()
    default_fresh = reg.get("default_freshness_days", 180)
    entries = reg.get("entries", [])

    stale, soon, upstream_due, ok = [], [], [], []
    for e in entries:
        lv = parse_date(e.get("last_verified", ""))
        if not lv:
            stale.append((e, "日期缺失"))
            continue
        fresh = e.get("freshness_days", default_fresh)
        age = (today - lv).days
        if age > fresh:
            stale.append((e, f"过期 {age - fresh} 天 (fresh={fresh})"))
        elif age > fresh - warn_days:
            soon.append((e, f"剩 {fresh - age} 天到期"))
        else:
            ok.append((e, f"新鲜 ({age} 天)"))

    # 上游到期（轴 3）
    if reg.get("derived_from") not in (None, "original", ""):
        uc = parse_date(reg.get("upstream_last_checked", ""))
        uf = reg.get("upstream_freshness_days", 90)
        if uc:
            uage = (today - uc).days
            if uage > uf:
                upstream_due.append((reg.get("derived_from"), f"上游 {uage - uf} 天未回拉 (uf={uf})"))

    if as_json:
        out = {
            "skill": reg.get("skill"),
            "owner": reg.get("owner"),
            "derived_from": reg.get("derived_from"),
            "total": len(entries),
            "stale": [{"id": e.get("id"), "title": e.get("title"), "reason": r} for e, r in stale],
            "soon": [{"id": e.get("id"), "title": e.get("title"), "reason": r} for e, r in soon],
            "upstream_due": upstream_due,
            "ok_count": len(ok),
            "needs_review": len([e for e in entries if e.get("merge_status") == "needs_review"]),
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        sys.exit(0 if not (stale or upstream_due) else 1)

    print(f"# {reg.get('skill')} 成长账本新鲜度扫描 ({today.isoformat()})")
    print(f"  归属: {reg.get('owner')} | 派生: {reg.get('derived_from')} | 条目: {len(entries)}")
    print()
    if stale:
        print(f"[过期 {len(stale)}] 须立即复核:")
        for e, r in stale:
            print(f"  - {e.get('id')} {e.get('title', '')[:40]} ... {r}")
    else:
        print("[过期 0] 无过期条目")
    if upstream_due:
        print(f"\n[上游到期 {len(upstream_due)}] 须回拉上游:")
        for name, r in upstream_due:
            print(f"  - {name} ... {r}")
    if soon:
        print(f"\n[临期 {len(soon)}] 即将到期:")
        for e, r in soon:
            print(f"  - {e.get('id')} {e.get('title', '')[:40]} ... {r}")
    nr = len([e for e in entries if e.get("merge_status") == "needs_review"])
    print(f"\n[健康] 正常 {len(ok)} 条；needs_review 隔离 {nr} 条")
    print("刷新动作: 过期条目重新核验权威源更新 last_verified；上游到期走 WebFetch/WebSearch 回拉差异。")


if __name__ == "__main__":
    main()
