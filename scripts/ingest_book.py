#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ingest_book.py — 把书籍文件解析为统一 UTF-8 纯文本（Windows）。

支持: .pdf (PyMuPDF) / .epub (ebooklib+bs4) / .docx (python-docx) / .md / .txt
输出: 带章节分隔标记的单文件 .txt，供 RIA-TV++ 蒸馏层消费。

用法:
  python ingest_book.py --input "D:/book.pdf" --output "D:/out/book.txt"
"""
import argparse
import os
import sys
import traceback


def extract_pdf(path: str) -> str:
    import fitz  # PyMuPDF
    out = []
    doc = fitz.open(path)
    for i, page in enumerate(doc):
        txt = page.get_text("text")
        if txt.strip():
            out.append(f"\n\n# 第 {i+1} 页\n\n" + txt)
    doc.close()
    return "".join(out)


def extract_epub(path: str) -> str:
    from ebooklib import epub
    from bs4 import BeautifulSoup
    book = epub.read_epub(path)
    out = []
    for item in book.get_items_of_type(9):  # DOCUMENT type
        soup = BeautifulSoup(item.get_content(), "html.parser")
        # 标题层级保留
        for h in soup.find_all(["h1", "h2", "h3", "h4"]):
            out.append(f"\n\n# {h.get_text(strip=True)}\n")
        text = soup.get_text(separator="\n")
        out.append(text)
    return "\n".join(out)


def extract_docx(path: str) -> str:
    import docx
    d = docx.Document(path)
    out = []
    for p in d.paragraphs:
        if p.style.name.startswith("Heading"):
            out.append(f"\n\n# {p.text}\n")
        else:
            out.append(p.text)
    return "\n".join(out)


def extract_plain(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_pdf(path)
    if ext == ".epub":
        return extract_epub(path)
    if ext == ".docx":
        return extract_docx(path)
    if ext in (".md", ".txt", ".text"):
        return extract_plain(path)
    raise ValueError(f"不支持的书籍格式: {ext}（支持 pdf/epub/docx/md/txt）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="书籍文件路径")
    ap.add_argument("--output", required=True, help="输出 .txt 路径")
    args = ap.parse_args()

    try:
        text = extract(args.input)
    except Exception as e:
        print(f"[ingest_book][ERROR] {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(f"<!-- source: {os.path.basename(args.input)} -->\n")
        f.write(text)
    nchars = len(text)
    print(f"[ingest_book] 完成: {nchars} 字 -> {args.output}")


if __name__ == "__main__":
    main()
