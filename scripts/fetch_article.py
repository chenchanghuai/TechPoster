#!/usr/bin/env python3
"""
抓取并提取文章正文，输出干净、去重的纯文本（供解读使用）。

一步完成 curl 抓取 + 正文提取，替代每次手写的内联 Python，
并消除微信正文在 HTML 中重复出现导致的读取浪费（仅输出一份正文）。

用法:
    # 直接抓取 URL（自动带微信反爬 headers），打印正文
    python3 scripts/fetch_article.py <url>

    # 抓取并把原始 HTML 也存下来（供 extract_images.py 用）
    python3 scripts/fetch_article.py <url> --save-html /path/article.html

    # 已有 HTML 文件时跳过抓取，直接提取
    python3 scripts/fetch_article.py --html /path/article.html

输出格式:
    TITLE: ...
    SOURCE: ...
    URL: ...
    ---
    <逐段正文，已去重>
"""

import argparse
import subprocess
import sys

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


def fetch(url: str) -> str:
    cmd = [
        "curl", "-s", "-L", "-A", UA,
        "-H", "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8",
        "-H", "Referer: https://mp.weixin.qq.com/",
        url,
    ]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout


def extract(html: str):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")

    # 标题
    title = soup.find("h1", class_="rich_media_title") or soup.find("h1")
    title = title.get_text(strip=True) if title else ""

    # 来源 / 作者（微信）
    source = ""
    meta = soup.find("div", id="meta_content") or soup.find("div", id="js_name")
    if meta:
        source = " ".join(dict.fromkeys(meta.get_text(" ", strip=True).split()))

    # 正文容器：微信 js_content 优先，否则退回 article/main
    body = (soup.find("div", id="js_content")
            or soup.find("article")
            or soup.find("main")
            or soup.body)

    lines, seen, prev = [], set(), None
    if body:
        for el in body.find_all(["p", "section", "h1", "h2", "h3", "h4", "li", "blockquote"]):
            # 跳过含子块的容器，避免父子重复输出
            if el.find(["p", "section", "li", "blockquote"]):
                continue
            t = el.get_text(" ", strip=True)
            if not t or t == prev:
                continue
            # 去掉与前一行完全重复 / 已出现过的整段
            if t in seen:
                continue
            lines.append(t)
            seen.add(t)
            prev = t
    return title, source, lines


def main() -> int:
    ap = argparse.ArgumentParser(description="抓取并提取文章正文（去重纯文本）")
    ap.add_argument("url", nargs="?", help="文章 URL")
    ap.add_argument("--html", help="已有 HTML 文件路径（提供时跳过抓取）")
    ap.add_argument("--save-html", help="把抓取的原始 HTML 存到此路径")
    args = ap.parse_args()

    if args.html:
        html = open(args.html, encoding="utf-8", errors="ignore").read()
    elif args.url:
        html = fetch(args.url)
        if args.save_html:
            open(args.save_html, "w", encoding="utf-8").write(html)
    else:
        ap.error("需要提供 url 或 --html")

    if len(html) < 500:
        print(f"[warn] HTML 仅 {len(html)} 字节，可能抓取失败或被拦截", file=sys.stderr)

    title, source, lines = extract(html)
    print(f"TITLE: {title}")
    print(f"SOURCE: {source}")
    if args.url:
        print(f"URL: {args.url}")
    print("---")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
