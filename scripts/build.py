#!/usr/bin/env python3
"""Build a small, database-free static Bengali news site from Markdown."""
from __future__ import annotations
import argparse, datetime as dt, html, re, shutil
from pathlib import Path
from urllib.parse import quote
from xml.etree.ElementTree import Element, SubElement, ElementTree

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "content" / "articles"
BASE_URL = "https://news.reazromen.com"

def parse_article(path: Path):
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---\n"):
        raise ValueError(f"{path}: missing front matter")
    parts = raw.split("---\n", 2)
    if len(parts) != 3:
        raise ValueError(f"{path}: malformed front matter")
    meta, body = parts[1], parts[2].strip()
    fields = {}
    for line in meta.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"{path}: malformed metadata line")
        k, v = line.split(":", 1)
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        fields[k.strip()] = v
    required = ("title", "slug", "date", "source_name", "source_url", "summary", "category", "status")
    missing = [k for k in required if not fields.get(k)]
    if missing:
        raise ValueError(f"{path}: missing {', '.join(missing)}")
    if fields["status"] != "published":
        raise ValueError(f"{path}: only status: published can be built")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", fields["slug"]):
        raise ValueError(f"{path}: invalid slug")
    if not fields["source_url"].startswith("https://"):
        raise ValueError(f"{path}: source_url must use HTTPS")
    stamp = dt.datetime.fromisoformat(fields["date"].replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError(f"{path}: date needs an explicit timezone")
    if len(body) < 250:
        raise ValueError(f"{path}: article body is too short to publish")
    return {**fields, "date_dt": stamp, "body": body, "path": path}

def md(text):
    """Render safe, deliberately small Markdown subset."""
    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        if not block.strip(): continue
        lines = block.splitlines()
        if all(x.lstrip().startswith("- ") for x in lines):
            out.append("<ul>" + "".join("<li>"+inline(x.lstrip()[2:])+"</li>" for x in lines) + "</ul>")
        elif lines[0].startswith("### "):
            out.append("<h3>"+inline(lines[0][4:])+"</h3>")
        elif lines[0].startswith("## "):
            out.append("<h2>"+inline(lines[0][3:])+"</h2>")
        else:
            out.append("<p>" + "<br>".join(inline(x) for x in lines) + "</p>")
    return "\n".join(out)

def inline(s):
    s = html.escape(s, quote=True)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s

def shell(title, desc, body, canonical):
    return f'''<!doctype html>
<html lang="bn"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc, quote=True)}">
<link rel="canonical" href="{html.escape(canonical, quote=True)}"><link rel="alternate" type="application/rss+xml" title="সংবাদ ফিড" href="{BASE_URL}/feed.xml">
<style>
:root{{color-scheme:light dark;--line:color-mix(in srgb,CanvasText 18%,transparent);--muted:color-mix(in srgb,CanvasText 68%,transparent)}}
*{{box-sizing:border-box}}body{{margin:0;font:18px/1.8 system-ui,-apple-system,"Noto Sans Bengali",sans-serif;background:Canvas;color:CanvasText}}
header,main,footer{{max-width:850px;margin:auto;padding:20px}}header{{border-bottom:1px solid var(--line)}}a{{color:inherit}}.brand{{font-size:24px;font-weight:750;text-decoration:none}}.muted,small{{color:var(--muted)}}article{{padding:24px 0;border-bottom:1px solid var(--line)}}h1{{line-height:1.35;font-size:clamp(30px,6vw,44px)}}h2{{line-height:1.4}}.meta{{font-size:14px;color:var(--muted)}}.summary{{font-size:19px}}.source{{border-left:3px solid var(--line);padding:10px 16px;margin:28px 0;font-size:15px}}footer{{border-top:1px solid var(--line);font-size:14px;color:var(--muted)}}
</style></head><body><header><a class="brand" href="/">সংবাদ · News</a><div class="muted">তথ্যসূত্রসহ বাংলা সংবাদ · Git-canonical publication</div></header><main>{body}</main><footer>প্রতিটি প্রতিবেদনের মূল কপি Git-এ সংরক্ষিত। তথ্যসূত্র ও প্রকাশের তারিখ প্রতিটি প্রতিবেদনে দেওয়া থাকে।</footer></body></html>'''

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="dist")
    args = p.parse_args()
    out = (ROOT / args.output).resolve()
    if out.exists(): shutil.rmtree(out)
    (out / "article").mkdir(parents=True)
    shutil.copy2(ROOT / "CNAME", out / "CNAME")
    articles = [parse_article(x) for x in sorted(ARTICLES.glob("*.md")) if x.name.lower() != "readme.md"]
    slugs = [a["slug"] for a in articles]
    sources = [a["source_url"] for a in articles]
    if len(slugs) != len(set(slugs)): raise SystemExit("Duplicate article slug detected")
    if len(sources) != len(set(sources)): raise SystemExit("Duplicate source URL detected")
    articles.sort(key=lambda a: a["date_dt"], reverse=True)
    cards = []
    for a in articles:
        url = f"{BASE_URL}/article/{a['slug']}/"
        (out / "article" / a["slug"]).mkdir(parents=True)
        body = f'<article><div class="meta">{html.escape(a["category"])} · {a["date_dt"].strftime("%Y-%m-%d %H:%M %z")}</div><h1>{html.escape(a["title"])}</h1><p class="summary">{html.escape(a["summary"])}</p>{md(a["body"])}<div class="source">তথ্যসূত্র: <a rel="nofollow noopener" href="{html.escape(a["source_url"], quote=True)}">{html.escape(a["source_name"])}</a></div></article>'
        (out / "article" / a["slug"] / "index.html").write_text(shell(a["title"], a["summary"], body, url), encoding="utf-8")
        cards.append(f'<article><div class="meta">{html.escape(a["category"])} · {a["date_dt"].strftime("%Y-%m-%d %H:%M %z")}</div><h2><a href="/article/{quote(a["slug"])}/">{html.escape(a["title"])}</a></h2><p>{html.escape(a["summary"])}</p><div class="meta">তথ্যসূত্র: {html.escape(a["source_name"])}</div></article>')
    if not cards:
        cards.append('<article><h1>সংবাদ প্রকাশের প্রস্তুতি চলছে</h1><p>Git-ভিত্তিক প্রকাশনা ব্যবস্থা প্রস্তুত করা হচ্ছে। যাচাই করা প্রতিবেদন প্রকাশিত হলে এখানে দেখা যাবে।</p><p class="muted">এখনও কোনো সংবাদ প্রকাশিত হয়নি।</p></article>')
    home = '<h1>সর্বশেষ সংবাদ</h1>' + "".join(cards)
    (out / "index.html").write_text(shell("সর্বশেষ বাংলা সংবাদ", "তথ্যসূত্রসহ যাচাইকৃত বাংলা সংবাদ", home, BASE_URL + "/"), encoding="utf-8")
    feed = Element("rss", version="2.0"); channel = SubElement(feed, "channel")
    SubElement(channel, "title").text = "সংবাদ · News"
    SubElement(channel, "link").text = BASE_URL + "/"
    SubElement(channel, "description").text = "তথ্যসূত্রসহ বাংলা সংবাদ"
    for a in articles:
        item = SubElement(channel, "item")
        SubElement(item, "title").text = a["title"]
        SubElement(item, "link").text = f'{BASE_URL}/article/{a["slug"]}/'
        SubElement(item, "guid").text = f'{BASE_URL}/article/{a["slug"]}/'
        SubElement(item, "description").text = a["summary"]
        SubElement(item, "pubDate").text = a["date_dt"].strftime("%a, %d %b %Y %H:%M:%S %z")
    ElementTree(feed).write(out / "feed.xml", encoding="utf-8", xml_declaration=True)
    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for url in [BASE_URL + "/"] + [f'{BASE_URL}/article/{a["slug"]}/' for a in articles]:
        SubElement(urlset, "url").append(Element("loc"))
        urlset[-1][0].text = url
    ElementTree(urlset).write(out / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    print(f"Built static site with {len(articles)} articles in {out}")

if __name__ == "__main__":
    main()
