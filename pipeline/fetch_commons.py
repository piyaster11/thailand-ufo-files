#!/usr/bin/usr/bin/env python3
"""Download selected Wikimedia Commons stills, convert to optimized WebP, write a manifest.

Only freely licensed images. Credits come from Commons extmetadata — never invented.
"""
from __future__ import annotations

import json
import re
import ssl
import time
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "img" / "commons"
OUT.mkdir(parents=True, exist_ok=True)
MANIFEST = Path(__file__).resolve().parent / "commons_manifest.json"

UA = "ThailandUFOFilesBot/1.0 (research archive; https://github.com/piyaster11/thailand-ufo-files)"
CTX = ssl.create_default_context()

# Files chosen because they truthfully illustrate a phenomenon or a place,
# never because they claim to be a photograph of a specific Thai sighting
# (except the 2013 Naga fireball series, which was taken that night).
FILES = [
    "Beung Fai Phraya Nag (183) ball.JPG",
    "Beung Fai Phraya Nag (187) ball.JPG",
    "The Mekong River in the down going sun. East of Nong Khai - panoramio.jpg",
    "The Mekong River at Phon Phisai, NE Thailand - panoramio.jpg",
    "Starlink 6 satellites.jpg",
    "Yi Peng lanterns in Chiang Mai (11067469754).jpg",
    "Radiosonde-wx-balloon.jpg",
    "The blue and green lights of fishing boats dot the Gulf of Thailand and the Andaman Sea (iss074e0526743).jpg",
    "Cosmic Fireball Falling Over ALMA.jpg",
    "Fireball Over Kitt Peak (iotw2522a).jpg",
    "ISS-56 International Space Station fly-around.jpg",
    "International Space Station after undocking of STS-134.jpg",
    "ISS expedition 42 closeup.jpg",
]

SLUGS = {
    "Beung Fai Phraya Nag (183) ball.JPG": "naga-183",
    "Beung Fai Phraya Nag (187) ball.JPG": "naga-187",
    "The Mekong River in the down going sun. East of Nong Khai - panoramio.jpg": "mekong-nongkhai-dusk",
    "The Mekong River at Phon Phisai, NE Thailand - panoramio.jpg": "mekong-phonphisai",
    "Starlink 6 satellites.jpg": "starlink-train",
    "Yi Peng lanterns in Chiang Mai (11067469754).jpg": "yipeng-chiangmai",
    "Radiosonde-wx-balloon.jpg": "weather-balloon",
    "The blue and green lights of fishing boats dot the Gulf of Thailand and the Andaman Sea (iss074e0526743).jpg": "gulf-fishing-lights",
    "Cosmic Fireball Falling Over ALMA.jpg": "fireball-alma",
    "Fireball Over Kitt Peak (iotw2522a).jpg": "fireball-kittpeak",
    "ISS-56 International Space Station fly-around.jpg": "iss-flyaround",
    "International Space Station after undocking of STS-134.jpg": "iss-sts134",
    "ISS expedition 42 closeup.jpg": "iss-exp42",
}


def strip_html(s: str) -> str:
    s = re.sub(r"<br\s*/?>", ", ", s or "")
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"&amp;", "&", s)
    s = re.sub(r"&nbsp;", " ", s)
    s = re.sub(r"&quot;", '"', s)
    s = re.sub(r"&#39;", "'", s)
    return re.sub(r"\s+", " ", s).strip()


def api(params: dict) -> dict:
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40, context=CTX) as r:
        return json.loads(r.read().decode())


def fetch_info(title: str) -> dict | None:
    data = api({
        "action": "query",
        "titles": f"File:{title}",
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|size|mime|canonicaltitle",
        "iiurlwidth": 1280,
        "format": "json",
    })
    pages = (data.get("query") or {}).get("pages") or {}
    for p in pages.values():
        if p.get("missing") or "imageinfo" not in p:
            return None
        ii = p["imageinfo"][0]
        em = ii.get("extmetadata") or {}

        def g(k):
            return strip_html((em.get(k) or {}).get("value") or "")

        return {
            "title": p.get("title") or f"File:{title}",
            "page": f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(p.get('title') or 'File:'+title)}",
            "url": ii.get("thumburl") or ii.get("url"),
            "full_url": ii.get("url"),
            "mime": ii.get("mime"),
            "width": ii.get("thumbwidth") or ii.get("width"),
            "height": ii.get("thumbheight") or ii.get("height"),
            "license": g("LicenseShortName") or g("License") or "see Commons",
            "license_url": g("LicenseUrl"),
            "artist": g("Artist") or g("Credit") or "see Commons",
            "date": g("DateTimeOriginal") or g("DateTime") or g("Date"),
            "description": g("ImageDescription")[:240],
            "credit_line": g("Credit"),
        }
    return None


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
        return r.read()


def to_webp(raw: bytes, dest: Path, max_w: int = 1280, budget: int = 145_000) -> dict:
    im = Image.open(BytesIO(raw))
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    elif im.mode == "L":
        im = im.convert("RGB")
    w, h = im.size
    if w > max_w:
        h = int(h * max_w / w)
        w = max_w
        im = im.resize((w, h), Image.Resampling.LANCZOS)
    quality = 80
    while quality >= 55:
        buf = BytesIO()
        im.save(buf, "WEBP", quality=quality, method=6)
        data = buf.getvalue()
        if len(data) <= budget or quality <= 55:
            dest.write_bytes(data)
            return {"bytes": len(data), "width": w, "height": h, "quality": quality}
        quality -= 5
    dest.write_bytes(data)
    return {"bytes": len(data), "width": w, "height": h, "quality": quality}


def main() -> None:
    items = []
    for title in FILES:
        slug = SLUGS[title]
        print("fetch", title, flush=True)
        info = fetch_info(title)
        if not info:
            print("  MISSING", title)
            continue
        try:
            raw = download(info["url"])
        except Exception as e:
            print("  download failed, trying full url:", e)
            raw = download(info["full_url"])
        dest = OUT / f"{slug}.webp"
        meta = to_webp(raw, dest)
        rec = {
            "slug": slug,
            "src": f"img/commons/{slug}.webp",
            **info,
            **meta,
        }
        items.append(rec)
        print(f"  wrote {dest.name} {meta['bytes']}B  lic={info['license']}  artist={info['artist'][:80]}")
        time.sleep(0.4)
    MANIFEST.write_text(json.dumps(items, indent=2, ensure_ascii=False))
    print("manifest", MANIFEST, "n=", len(items))


if __name__ == "__main__":
    main()
