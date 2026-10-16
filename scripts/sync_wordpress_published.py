#!/usr/bin/env python3
"""Import newly published WordPress news into the Git-canonical static corpus.

Only public posts with a valid slug, >=250 characters of body text, and at least
one external HTTPS source link are imported. Existing Git slugs are immutable:
conflicts are logged and never overwritten. Drafts are never fetched or exported.
"""
from __future__ import annotations
import argparse, datetime as dt, html, json, re, subprocess, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "content" / "articles"
API = "https://news.reazromen.com/wp-json/wp/v2"
SITE_HOSTS = {"news.reazromen.com", "reazromen.com", "www.reazromen.com"}
TZ = ZoneInfo("Asia/Dhaka")

class BodyParser(HTMLParser):
    BLOCK = {"p", "div", "section", "article", "h1", "h2", "h3", "h4", "li", "blockquote", "br"}
    SKIP = {"figure", "picture", "svg", "script", "style", "noscript", "iframe"}
    def __init__(self):
        super().__init__(convert_charrefs=True); self.parts=[]; self.links=[]; self.skip=0; self.anchor=None
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag in self.SKIP: self.skip += 1
        if self.skip: return
        if tag in self.BLOCK: self.parts.append("\n\n")
        if tag == "a": self.anchor=[attrs.get("href", ""), []]
        if tag in ("strong", "b"): self.parts.append("**")
        if tag in ("em", "i"): self.parts.append("*")
    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip: self.skip -= 1
        if self.skip: return
        if tag in self.BLOCK: self.parts.append("\n\n")
        if tag in ("strong", "b"): self.parts.append("**")
        if tag in ("em", "i"): self.parts.append("*")
        if tag == "a" and self.anchor:
            href, words = self.anchor; label="".join(words).strip()
            if href and label: self.links.append((href, label))
            self.anchor=None
    def handle_data(self, data):
        if self.skip: return
        text=data.replace("\xa0", " ")
        self.parts.append(text)
        if self.anchor is not None: self.anchor[1].append(text)
    def markdown(self):
        raw="".join(self.parts)
        blocks=[]
        for block in re.split(r"\n\s*\n", raw):
            block=re.sub(r"[ \t]+", " ", block).strip()
            if not block: continue
            # Publisher source attribution belongs in front matter, not duplicated in body.
            if "তথ্যসূত্র:" in block or re.match(r"(?i)^sources?:", block): continue
            blocks.append(block)
        return "\n\n".join(blocks).strip()

def fetch_json(url):
    req=Request(url, headers={"User-Agent":"NewsGitWordPressSync/1.0", "Accept":"application/json"})
    with urlopen(req, timeout=20) as response:
        if response.status != 200: raise RuntimeError(f"HTTP {response.status}: {url}")
        return json.load(response)

def safe_yaml(value):
    return '"' + str(value).replace('\\','\\\\').replace('"','\\"').replace('\n',' ') + '"'

def category_name(ids, cache):
    for cat_id in ids or []:
        if cat_id not in cache:
            try: cache[cat_id]=fetch_json(f"{API}/categories/{int(cat_id)}?context=view").get("name", "")
            except Exception: cache[cat_id]=""
        if cache[cat_id]: return html.unescape(cache[cat_id]).strip()
    return "বাংলাদেশ"

def existing_slugs():
    slugs=set()
    for path in ARTICLES.glob("*.md"):
        if path.name.lower()=="readme.md": continue
        match=re.search(r"(?m)^slug:\s*[\"']?([^\"'\s]+)", path.read_text(encoding="utf-8"))
        if match: slugs.add(match.group(1))
        slugs.add(path.stem)
    return slugs

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="show eligible imports without writing or committing")
    ap.add_argument("--since-id", type=int, default=681, help="only consider WordPress post IDs greater than this cutover watermark (default: 681)")
    ap.add_argument("--no-push", action="store_true", help="write and commit locally but do not push")
    args=ap.parse_args()
    if not args.dry_run:
        if subprocess.run(["git","-C",str(ROOT),"status","--porcelain"],capture_output=True,text=True,check=True).stdout.strip():
            print("ERROR: Git checkout has local changes; refusing WordPress import.",file=sys.stderr); return 2
        subprocess.run(["git","-C",str(ROOT),"fetch","origin","main"],check=True,stdout=subprocess.DEVNULL)
        ancestry=subprocess.run(["git","-C",str(ROOT),"merge-base","--is-ancestor","origin/main","HEAD"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if ancestry.returncode != 0:
            print("ERROR: origin/main has diverged from local HEAD; refusing automatic sync.",file=sys.stderr); return 2
        local_head=subprocess.run(["git","-C",str(ROOT),"rev-parse","HEAD"],capture_output=True,text=True,check=True).stdout.strip()
        remote_head=subprocess.run(["git","-C",str(ROOT),"rev-parse","origin/main"],capture_output=True,text=True,check=True).stdout.strip()
        if local_head != remote_head:
            subprocess.run(["git","-C",str(ROOT),"push","origin","main"],check=True)
            print("Pushed previously committed local news changes to origin/main.")
    posts=[]; page=1
    while page <= 100:
        url=f"{API}/posts?{urlencode({'status':'publish','per_page':100,'page':page,'orderby':'date','order':'desc','_fields':'id,date,date_gmt,slug,status,link,title,content,excerpt,categories'})}"
        try: batch=fetch_json(url)
        except HTTPError as e:
            if e.code == 400 and page > 1: break
            raise
        if not batch: break
        posts.extend(batch)
        if len(batch)<100: break
        page += 1
    known=existing_slugs(); cats={}; additions=[]; skipped=0
    for post in posts:
        post_id=int(post.get("id", 0))
        if post_id <= args.since_id:
            continue
        slug=str(post.get("slug", ""))
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            print(f"SKIP id={post.get('id')} invalid slug={slug!r}"); skipped+=1; continue
        if slug in known:
            print(f"EXISTS id={post.get('id')} slug={slug}; Git remains authoritative; no overwrite")
            continue
        content=post.get("content",{}).get("rendered","")
        parser=BodyParser(); parser.feed(content); body=parser.markdown()
        sources=[]
        for href,label in parser.links:
            u=urlparse(html.unescape(href))
            if u.scheme=="https" and u.hostname and u.hostname.lower() not in SITE_HOSTS and label and (href,label) not in sources:
                sources.append((html.unescape(href), html.unescape(label).strip()))
        # Include explicit source links found in rendered content, never infer a source from the slug.
        if not sources:
            print(f"SKIP id={post.get('id')} slug={slug}: no external HTTPS source link in article body"); skipped+=1; continue
        plain=re.sub(r"[*_`#]", "", body)
        if len(plain) < 250:
            print(f"SKIP id={post.get('id')} slug={slug}: body too short ({len(plain)} chars)"); skipped+=1; continue
        title=html.unescape(post.get("title",{}).get("rendered", "")).strip()
        summary_parser=BodyParser(); summary_parser.feed(post.get("excerpt",{}).get("rendered", "")); summary=summary_parser.markdown().replace("\n", " ").strip()
        if not summary: summary=plain[:220].rsplit(" ",1)[0]
        stamp=post.get("date_gmt") or post.get("date")
        try:
            parsed=dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            if parsed.tzinfo is None: parsed=parsed.replace(tzinfo=dt.timezone.utc)
            local=parsed.astimezone(TZ).isoformat(timespec="seconds")
        except Exception:
            print(f"SKIP id={post.get('id')} slug={slug}: invalid publication date"); skipped+=1; continue
        category=category_name(post.get("categories",[]),cats)
        fields=[("title",title),("slug",slug),("date",local),("updated",local),("source_name",sources[0][1]),("source_url",sources[0][0])]
        if len(sources)>1:
            fields.extend([("secondary_source_name",sources[1][1]),("secondary_source_url",sources[1][0])])
        fields.extend([("summary",summary),("category",category),("status","published"),("wordpress_post_id",str(post.get("id")))])
        front="---\n"+"".join(f"{k}: {safe_yaml(v)}\n" for k,v in fields)+"---\n\n"
        dest=ARTICLES/f"{slug}.md"
        additions.append((dest,front+body+"\n",int(post.get("id",0)),slug))
        known.add(slug)
    print(f"WordPress published posts scanned: {len(posts)}; cutover watermark: ID > {args.since_id}; eligible new Git articles: {len(additions)}; skipped for validation: {skipped}")
    for dest,_,post_id,slug in additions: print(f"IMPORT id={post_id} slug={slug} -> {dest.name}")
    if args.dry_run or not additions: return 0
    for dest,content,_,_ in additions:
        if dest.exists(): print(f"ERROR: refusing to overwrite {dest}",file=sys.stderr); return 3
        dest.write_text(content,encoding="utf-8")
    subprocess.run(["git","-C",str(ROOT),"add",*[str(x[0].relative_to(ROOT)) for x in additions]],check=True)
    message="Import published WordPress news into Git: "+", ".join(x[3] for x in additions[:4])
    subprocess.run(["git","-C",str(ROOT),"commit","-m",message],check=True)
    if not args.no_push:
        subprocess.run(["git","-C",str(ROOT),"push","origin","main"],check=True)
        print("Pushed import to origin/main; local static deploy poll will rebuild the public site.")
    else: print("Committed locally only (--no-push).")
    return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except (HTTPError, URLError, TimeoutError, RuntimeError, ValueError) as exc:
        print(f"ERROR: WordPress-to-Git sync failed: {exc}",file=sys.stderr); raise SystemExit(1)
