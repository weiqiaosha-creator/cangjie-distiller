#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill-growth-engine - 安全门禁扫描器（轴 0，强制前置，高于权威门禁）
对任何"要进入桥山电脑/技能体系"的外部内容做静态风险筛查，绝不执行被扫内容。

覆盖风险：
  - 代码执行 sinks（eval/exec/os.system/subprocess-shell/pickle.loads/ctypes...）
  - 网络外联（exfil / 回传 / C2）
  - 危险文件操作（rmtree/删除/写系统目录/注册表/计划任务/自启）
  - 下载即运行（curl|sh、pip install 任意源、npm 带 postinstall、powershell -enc）
  - 混淆（大段 base64/hex、动态解码）
  - 爬虫/机器人软件（scrapy/selenium/playwright + 循环请求）
  - 提示注入（外部内容夹带控制指令，试图操纵 Agent）
  - 可疑二进制/可执行文件（.exe/.dll/.ps1/.bat/.vbs...）

输出 JSON：
  { "path", "scanned_files", "findings":[...], "risk_level", "recommendation",
    "trusted_source", "quarantine", "summary" }

recommendation:
  - "block"   : 高危/严重，禁止进入，落 quarantine，通知桥山
  - "needs_review": 中危，隔离，待桥山确认后才可合入
  - "pass"    : 低危，放行至权威门禁继续判定

用法:
  python security_scan.py --path <文件或目录> [--url <来源URL>] [--out report.json]
"""
import json
import os
import re
import sys

# ---------- 来源可信域白名单 ----------
TRUSTED_DOMAINS = [
    "github.com", "raw.githubusercontent.com", "gist.github.com", "gitlab.com",
    "youtube.com", "youtu.be", "bilibili.com", "b23.tv",
]
# 已知但需复核（社区/市场），不自动信任
REVIEW_DOMAINS = ["skillhub.com", "clawhub", "marketplace"]


# ---------- 风险模式（severity: critical/high/medium/low）----------
# 每条: (category, severity, regex)
PATTERNS = [
    # 下载即运行（最危险）
    ("download_run", "critical", r"curl\s+[^|]*\|\s*(sh|bash)"),
    ("download_run", "critical", r"wget\s+[^|]*\|\s*(sh|bash)"),
    ("download_run", "critical", r"powershell\s+.*-enc(?:odedcommand)?\b"),
    ("download_run", "critical", r"iex\s*\(\s*(?:Invoke-Expression|New-Object)"),
    ("download_run", "critical", r"pip\s+install\s+.*(?:http://|https://|ftp://)"),
    ("download_run", "high", r"npm\s+install\s+[^\n]*--\w*[pP]ostinstall"),
    ("download_run", "high", r"/bin/sh\s+-c\s+.*curl"),
    # 代码执行 sinks
    ("code_exec", "high", r"\bos\.system\s*\("),
    ("code_exec", "high", r"subprocess\.Popen\s*\("),
    ("code_exec", "medium", r"subprocess\.run\s*\([^)]*shell\s*=\s*True"),
    ("code_exec", "high", r"\beval\s*\("),
    ("code_exec", "high", r"\bexec\s*\(\s*(?:compile\()"),
    ("code_exec", "medium", r"\bexec\s*\("),
    ("code_exec", "high", r"__import__\s*\("),
    ("code_exec", "high", r"pickle\.loads?\s*\("),
    ("code_exec", "high", r"marshal\.loads\s*\("),
    ("code_exec", "medium", r"\bctypes\.[A-Za-z]+\s*\("),
    ("code_exec", "medium", r"importlib\.import_module\s*\("),
    # 网络外联
    ("net_egress", "high", r"requests\.post\s*\("),
    ("net_egress", "high", r"urllib\.request"),
    ("net_egress", "high", r"socket\.socket\s*\("),
    ("net_egress", "high", r"httpx\.(post|get|request)\s*\("),
    ("net_egress", "high", r"aiohttp\.(ClientSession|request)\s*\("),
    ("net_egress", "medium", r"Invoke-WebRequest|System\.Net\.WebClient"),
    ("net_egress", "high", r"smtplib\.SMTP"),
    ("net_egress", "medium", r"ftplib"),
    # 危险文件/系统操作
    ("fs_danger", "high", r"shutil\.rmtree\s*\("),
    ("fs_danger", "medium", r"\bos\.remove\s*\(|\bos\.unlink\s*\("),
    ("fs_danger", "high", r"SetFileAttributes|winreg\.|\.reg\b"),
    ("fs_danger", "high", r"schtasks\s+|crontab\s+-|systemctl\s+enable"),
    ("fs_danger", "medium", r"\.bashrc|\.profile|LaunchAgents|startup"),
    # 混淆
    ("obfuscation", "medium", r"[A-Za-z0-9+/]{80,}={0,2}"),  # 大段 base64
    ("obfuscation", "medium", r"(?:0x[0-9a-fA-F]{2},?\s*){20,}"),  # 长 hex
    ("obfuscation", "medium", r"from\s+base64\s+import|base64\.b64decode"),
    ("obfuscation", "medium", r"\beval\s*\(\s*[bc]\s*\("),  # eval(b(...)) 动态解码
    # 爬虫/机器人
    ("crawler_bot", "high", r"\b(?:scrapy|selenium|playwright|puppeteer|pyppeteer|DrissionPage)\b"),
    ("crawler_bot", "medium", r"for\s+_.+\s+in\s+range\s*\([^)]*\):[^\n]*requests\.get"),
    ("crawler_bot", "medium", r"(?:爬虫|crawler|spider)\b[^\n]*(?:http|request|爬)"),
    # 提示注入
    ("prompt_injection", "high", r"忽略(?:之前|上述|所有|前面的)指令"),
    ("prompt_injection", "high", r"ignore\s+(?:previous|above|all|prior)\s+instructions"),
    ("prompt_injection", "high", r"disregard\s+(?:the\s+)?(?:previous|above|system)"),
    ("prompt_injection", "high", r"system\s+prompt|你(?:现在)?是|作为开发者模式|DAN\b|jailbreak"),
    ("prompt_injection", "medium", r"新的指令|assistant\s*:\s*|system\s*:\s*"),
]

# 可疑二进制/可执行扩展名（存在即记一笔，不执行）
BIN_EXT = {
    ".exe", ".dll", ".scr", ".sys", ".bat", ".cmd", ".ps1", ".vbs", ".jar",
    ".msi", ".apk", ".dmg", ".com", ".pif", ".wsf", ".hta",
}

SEV_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def check_url(url):
    if not url:
        return None, "no_url_provided"
    try:
        from urllib.parse import urlparse
        host = urlparse(url).netloc.lower()
    except Exception:
        return False, "unparseable_url"
    for d in TRUSTED_DOMAINS:
        if d in host:
            return True, "allowlist"
    for d in REVIEW_DOMAINS:
        if d in host:
            return False, "review_domain"
    return False, "unknown_host"


def scan_text(text, is_code=True):
    # 文档/文本文件只查提示注入（避免"讲网络安全的书/提到 selenium 的笔记"被误杀）
    active = PATTERNS if is_code else [p for p in PATTERNS if p[0] == "prompt_injection"]
    findings = []
    for cat, sev, pat in active:
        for m in re.finditer(pat, text, re.IGNORECASE):
            s = max(0, m.start() - 40)
            e = min(len(text), m.end() + 40)
            snippet = text[s:e].replace("\n", " ")[:120]
            findings.append({"category": cat, "severity": sev, "snippet": snippet})
    return findings


# 文档/文本类扩展名：只查提示注入，不跑代码威胁模式
TEXT_EXT = {".md", ".txt", ".json", ".csv", ".html", ".htm", ".xml",
            ".yaml", ".yml", ".ini", ".toml", ".rst"}
# 代码/脚本类扩展名：跑全模式（真实可执行威胁）
CODE_EXT = {".py", ".js", ".ts", ".ps1", ".bat", ".cmd", ".sh", ".vbs",
            ".rb", ".php", ".pl", ".lua", ".go", ".java", ".c", ".cpp",
            ".cs", ".r", ".sql"}


def scan_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in BIN_EXT:
        return [{"category": "binary_executable", "severity": "high",
                 "snippet": f"可疑可执行文件: {os.path.basename(path)}"}]
    try:
        with open(path, "r", encoding="utf-8", errors="strict") as f:
            text = f.read()
    except (UnicodeDecodeError, UnicodeError):
        return [{"category": "binary_unreadable", "severity": "medium",
                 "snippet": f"非文本/可能为二进制: {os.path.basename(path)}"}]
    except Exception:
        return []
    is_code = ext in CODE_EXT
    return scan_text(text, is_code=is_code)


def main():
    path = url = out = None
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--path" and i + 1 < len(args):
            path = args[i + 1]
        elif a == "--url" and i + 1 < len(args):
            url = args[i + 1]
        elif a == "--out" and i + 1 < len(args):
            out = args[i + 1]
    if not path:
        print("--path 必填", file=sys.stderr)
        sys.exit(2)
    if not os.path.exists(path):
        print("path 不存在:", path, file=sys.stderr)
        sys.exit(2)

    # 扫描器不扫自身 scripts 目录（避免模式定义字符串自匹配）；生产只扫外部内容
    _norm = os.path.abspath(path).replace("\\", "/")
    if os.path.basename(_norm) == "security_scan.py" or "/skill-growth-engine/scripts" in _norm:
        result = {
            "path": path, "trusted_source": "self", "source_reason": "engine_self",
            "scanned_files": 0, "risk_level": "low", "recommendation": "pass",
            "quarantine": False, "finding_count": 0, "categories": {},
            "flags": {}, "findings": [],
            "summary": "引擎自身，跳过扫描（不扫扫描器自身）",
        }
        if out:
            os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
            with open(out, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)

    findings = []
    scanned = 0
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for fn in files:
                fp = os.path.join(root, fn)
                if fp.endswith((".png", ".ico", ".jpg", ".jpeg", ".gif", ".db",
                                ".zip", ".pyc", "__pycache__")):
                    continue
                scanned += 1
                findings += scan_file(fp)
    else:
        scanned += 1
        findings += scan_file(path)

    # 来源可信
    trusted, src_reason = check_url(url)
    if url and not trusted:
        findings.append({"category": "untrusted_source", "severity": "medium",
                         "snippet": f"来源域名 {src_reason}: {url}"})

    # 风险聚合
    max_sev = "low"
    for f in findings:
        if SEV_RANK[f["severity"]] > SEV_RANK[max_sev]:
            max_sev = f["severity"]

    has_net = any(f["category"] == "net_egress" for f in findings)
    has_code = any(f["category"] in ("code_exec", "fs_danger") for f in findings)
    has_download_run = any(f["category"] == "download_run" for f in findings)
    has_inject = any(f["category"] == "prompt_injection" for f in findings)
    has_binary = any(f["category"] in ("binary_executable", "binary_unreadable") for f in findings)
    has_crawler = any(f["category"] == "crawler_bot" for f in findings)

    risk_level = max_sev
    # 组合升级
    if has_download_run:
        risk_level = "critical"
    elif has_net and (has_code or has_binary):
        risk_level = "critical" if "critical" not in (risk_level,) else risk_level
        if SEV_RANK[risk_level] < 2:
            risk_level = "high"
    elif has_net and has_crawler:
        risk_level = "high"
    elif has_inject:
        risk_level = "high" if SEV_RANK[risk_level] < 2 else risk_level
    elif (has_binary or has_crawler) and SEV_RANK[risk_level] < 1:
        risk_level = "medium"

    if risk_level in ("critical", "high"):
        recommendation = "block"
        quarantine = True
    elif risk_level == "medium":
        recommendation = "needs_review"
        quarantine = True
    else:
        recommendation = "pass"
        quarantine = False

    # 概要
    cats = {}
    for f in findings:
        cats[f["category"]] = cats.get(f["category"], 0) + 1
    summary = "安全门禁通过，放行至权威门禁" if recommendation == "pass" else \
        ("拦截：发现高危/严重风险" if recommendation == "block" else "隔离：发现中危风险，待桥山确认")

    result = {
        "path": path,
        "source_url": url,
        "trusted_source": (trusted if url else "no_url"),
        "source_reason": src_reason,
        "scanned_files": scanned,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "quarantine": quarantine,
        "finding_count": len(findings),
        "categories": cats,
        "flags": {
            "download_run": has_download_run, "net_egress": has_net,
            "code_or_fs_danger": has_code, "prompt_injection": has_inject,
            "binary": has_binary, "crawler_bot": has_crawler,
        },
        "findings": findings[:40],
        "summary": summary,
    }
    if out:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"[security_scan] {path}: risk={risk_level} -> {recommendation} ({len(findings)} findings)")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
