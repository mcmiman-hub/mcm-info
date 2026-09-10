#!/usr/bin/env python3
import json, re, html as htmlmod
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

FEED = "https://newsfeed.zeit.de/news/index"

def clean_html(value):
    value = value or ""
    value = re.sub(r"<[^>]+>", " ", value)
    value = htmlmod.unescape(value)
    return re.sub(r"\s+", " ", value).strip()

def first_image(item):
    # RSS media/enclosure if ZEIT supplies one.
    for child in list(item):
        tag = child.tag.lower()
        if tag.endswith("content") or tag.endswith("thumbnail") or tag.endswith("enclosure"):
            url = child.attrib.get("url", "")
            typ = child.attrib.get("type", "")
            if url and (("image" in typ) or tag.endswith("content") or tag.endswith("thumbnail")):
                if url.startswith("http"):
                    return url
    # Fallback: image embedded in RSS description/content.
    for child in list(item):
        txt = child.text or ""
        m = re.search(r'<img[^>]+src=["\']([^"\']+)', txt, re.I)
        if m and m.group(1).startswith("http"):
            return m.group(1)
    return ""

req = urllib.request.Request(FEED, headers={"User-Agent":"Mozilla/5.0 MCM-Info/2.0"})
with urllib.request.urlopen(req, timeout=30) as r:
    raw = r.read()

root = ET.fromstring(raw)
items = []
for item in root.findall(".//item")[:20]:
    title = clean_html(item.findtext("title"))
    link = (item.findtext("link") or "").strip()
    pub = (item.findtext("pubDate") or "").strip()
    desc = clean_html(item.findtext("description"))
    if len(desc) > 280:
        desc = desc[:277].rsplit(" ",1)[0] + "…"
    display = ""
    if pub:
        try:
            dt = parsedate_to_datetime(pub)
            display = dt.astimezone().strftime("%d.%m.%Y · %H:%M Uhr")
        except Exception:
            display = pub
    if title:
        items.append({
            "title": title,
            "summary": desc,
            "image": first_image(item),
            "link": link,
            "published": pub,
            "published_display": display
        })

if not items:
    raise RuntimeError("ZEIT RSS returned no news items")

data={"source":"ZEIT ONLINE","updated":datetime.now(timezone.utc).isoformat(),"items":items}
with open("news.json","w",encoding="utf-8") as f:
    json.dump(data,f,ensure_ascii=False,indent=2)
    f.write("\n")
print("Saved",len(items),"ZEIT items;",sum(1 for x in items if x["image"]),"with RSS images")
