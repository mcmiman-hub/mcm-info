#!/usr/bin/env python3
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

FEED = "https://newsfeed.zeit.de/index"
REQ = urllib.request.Request(
    FEED,
    headers={"User-Agent": "Mozilla/5.0 MCM-Info/1.0"}
)

with urllib.request.urlopen(REQ, timeout=30) as r:
    raw = r.read()

root = ET.fromstring(raw)
items = []
for item in root.findall(".//item")[:20]:
    title = (item.findtext("title") or "").strip()
    link = (item.findtext("link") or "").strip()
    pub = (item.findtext("pubDate") or "").strip()
    if title:
        items.append({"title": title, "link": link, "published": pub})

if not items:
    raise RuntimeError("ZEIT RSS returned no news items")

data = {
    "source": "ZEIT ONLINE",
    "updated": datetime.now(timezone.utc).isoformat(),
    "items": items
}
with open("news.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("Saved", len(items), "ZEIT headlines")
