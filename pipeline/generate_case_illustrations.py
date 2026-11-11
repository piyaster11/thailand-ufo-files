#!/usr/bin/env python3
"""Procedural X-Files-style illustrations for cases that have no truthful event photo.

Every frame is stamped ILLUSTRATION — NOT EVIDENCE. These are atmospheric art, never evidence.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "data" / "sightings.json"
OUT = ROOT / "docs" / "img" / "illustrations" / "cases"
FONT_DIR = ROOT / "docs" / "fonts"
W, H = 960, 540

NORTH = {"Chiang Mai", "Chiang Rai", "Phitsanulok", "Sukhothai", "Loei"}
MEKONG = {"Nong Khai", "Udon Thani", "Ubon Ratchathani", "Khon Kaen", "Nakhon Ratchasima", "Nakhon Sawan"}
GULF = {"Chon Buri", "Rayong", "Trat", "Prachuap Khiri Khan", "Phetchaburi"}
SOUTH = {"Phuket", "Krabi", "Surat Thani", "Songkhla"}
CITY = {"Bangkok", "Nakhon Pathom"}


def region_of(province: str | None) -> str:
    if province in NORTH:
        return "north"
    if province in MEKONG:
        return "mekong"
    if province in GULF:
        return "gulf"
    if province in SOUTH:
        return "south"
    if province in CITY:
        return "city"
    return "plain"


def font(size: int):
    for p in (
        FONT_DIR / "ShareTechMono-Regular.ttf",
        FONT_DIR / "SpecialElite-Regular.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    ):
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                pass
    return ImageFont.load_default()


def seed_for(case_id: str) -> random.Random:
    h = hashlib.sha256(case_id.encode()).digest()
    return random.Random(int.from_bytes(h[:8], "big"))


def lerp(a, b, t):
    return a + (b - a) * t


def sky(rnd: random.Random, region: str) -> Image.Image:
    img = Image.new("RGB", (W, H))
    px = img.load()
    # slight palette shift per seed
    r0, g0, b0 = 2 + rnd.randint(0, 4), 6 + rnd.randint(0, 8), 5 + rnd.randint(0, 6)
    r1, g1, b1 = 8 + rnd.randint(0, 10), 22 + rnd.randint(0, 18), 14 + rnd.randint(0, 12)
    if region == "city":
        r1, g1, b1 = 18, 28, 16
    for y in range(H):
        t = y / H
        t = t ** 1.15
        col = (
            int(lerp(r0, r1, t)),
            int(lerp(g0, g1, t)),
            int(lerp(b0, b1, t)),
        )
        for x in range(W):
            # faint horizontal banding
            band = 1 if (y // 3) % 17 == 0 else 0
            px[x, y] = (max(0, col[0] - band), min(255, col[1] + band), col[2])
    return img


def add_stars(draw: ImageDraw.ImageDraw, rnd: random.Random, n: int = 220):
    for _ in range(n):
        x = rnd.randint(0, W - 1)
        y = rnd.randint(0, int(H * 0.72))
        c = rnd.randint(90, 255)
        s = rnd.choices([1, 2, 3], weights=[70, 25, 5])[0]
        a = rnd.randint(140, 255)
        draw.ellipse([x, y, x + s, y + s], fill=(int(c * 0.7), c, int(c * 0.8), a))


def glow(draw, cx, cy, radius, color, layers=7):
    r, g, b = color
    for i in range(layers, 0, -1):
        rad = radius * i / 2
        a = int(18 + (layers - i) * (200 / layers))
        draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(r, g, b, max(8, min(230, a))))


def ground(draw, rnd, region: str):
    horizon = int(H * (0.68 + rnd.uniform(-0.04, 0.04)))
    if region == "north":
        pts = [(0, H)]
        x = 0
        while x <= W:
            peak = horizon - rnd.randint(40, 160)
            pts.append((x, peak))
            x += rnd.randint(80, 180)
        pts += [(W, H)]
        draw.polygon(pts, fill=(3, 14, 8, 255))
        # second ridge
        pts2 = [(0, H)]
        x = 0
        while x <= W:
            peak = horizon - rnd.randint(10, 70)
            pts2.append((x, peak))
            x += rnd.randint(60, 140)
        pts2 += [(W, H)]
        draw.polygon(pts2, fill=(4, 20, 11, 255))
    elif region == "mekong":
        draw.polygon([(0, horizon + 20), (W, horizon), (W, H), (0, H)], fill=(2, 18, 14, 255))
        for i in range(10):
            y = horizon + 24 + i * 8
            draw.arc([-80, y, W + 80, y + 28], 0, 180, fill=(0, 70 + i * 4, 50, 50), width=2)
        # far bank
        draw.polygon([(0, horizon + 8), (200, horizon - 12), (480, horizon + 6), (800, horizon - 8), (W, horizon + 4), (W, horizon + 22), (0, horizon + 28)], fill=(3, 16, 10, 255))
    elif region == "city":
        # glow
        for i in range(8):
            draw.ellipse([W * 0.15, horizon - 30 - i * 4, W * 0.9, horizon + 40], fill=(20, 40, 16, 12))
        x = 20
        while x < W - 10:
            bw = rnd.randint(10, 28)
            bh = rnd.randint(20, 90)
            draw.rectangle([x, horizon - bh, x + bw, H], fill=(4, 12, 8, 255))
            # windows
            for wy in range(horizon - bh + 6, horizon - 4, 8):
                if rnd.random() < 0.35:
                    draw.rectangle([x + 3, wy, x + 6, wy + 3], fill=(180, 255, 140, 80))
            x += bw + rnd.randint(4, 14)
    elif region in ("gulf", "south"):
        draw.polygon([(0, horizon + 10), (W, horizon), (W, H), (0, H)], fill=(2, 16, 18, 255))
        for i in range(8):
            y = horizon + 16 + i * 10
            draw.line([(0, y + int(3 * math.sin(i))), (W, y)], fill=(0, 50, 55, 40), width=1)
        if region == "south":
            # island lumps
            for cx in (int(W * 0.2), int(W * 0.55), int(W * 0.8)):
                draw.ellipse([cx - 70, horizon - 18, cx + 80, horizon + 22], fill=(3, 16, 12, 255))
    else:
        draw.polygon([(0, horizon + 8), (W * 0.3, horizon - 6), (W * 0.7, horizon + 4), (W, horizon - 2), (W, H), (0, H)], fill=(4, 16, 10, 255))
    return horizon


def draw_object(draw, rnd, category: str, horizon: int):
    cx = int(W * rnd.uniform(0.28, 0.72))
    cy = int(horizon * rnd.uniform(0.28, 0.62))
    if category == "light_orb":
        n = rnd.choice([1, 1, 1, 2, 3])
        for i in range(n):
            ox = cx + (i - n // 2) * rnd.randint(40, 90)
            oy = cy + rnd.randint(-20, 20)
            glow(draw, ox, oy, rnd.randint(10, 22), (80, 255, 140))
            draw.ellipse([ox - 5, oy - 5, ox + 5, oy + 5], fill=(220, 255, 230, 230))
    elif category == "fireball":
        # streak
        x0, y0 = cx - rnd.randint(80, 180), cy - rnd.randint(40, 100)
        x1, y1 = cx + rnd.randint(40, 120), cy + rnd.randint(20, 80)
        for w in range(10, 0, -1):
            a = 20 + w * 16
            draw.line([(x0, y0), (x1, y1)], fill=(255, 200, 80, a), width=w)
        glow(draw, x1, y1, 16, (255, 180, 60), 6)
    elif category == "naga_fireballs":
        for i, (ox, rise) in enumerate(((-180, 40), (-40, 80), (80, 30), (200, 70))):
            x = cx + ox + rnd.randint(-20, 20)
            y = horizon - 20 - rise + rnd.randint(-10, 10)
            glow(draw, x, y, 8 + i, (255, 90, 90) if i % 2 == 0 else (255, 140, 80), 6)
            draw.line([(x, y + 10), (x, y + 50)], fill=(255, 120, 80, 70), width=2)
    elif category == "triangle":
        size = rnd.randint(50, 80)
        pts = [(cx, cy - size // 2), (cx - size, cy + size // 2), (cx + size, cy + size // 2)]
        draw.polygon(pts, fill=(6, 20, 12, 200), outline=(0, 255, 160, 200))
        for px, py in pts:
            glow(draw, px, py, 7, (180, 255, 200), 5)
    elif category == "disc":
        glow(draw, cx, cy, 28, (40, 255, 140), 6)
        draw.ellipse([cx - 70, cy - 16, cx + 70, cy + 16], fill=(8, 30, 18, 220), outline=(0, 255, 140, 220), width=2)
        draw.ellipse([cx - 22, cy - 28, cx + 22, cy - 6], fill=(8, 28, 16, 220), outline=(140, 255, 200, 200), width=2)
        draw.ellipse([cx - 6, cy - 22, cx + 6, cy - 10], fill=(200, 255, 220, 220))
    elif category == "formation":
        n = rnd.choice([4, 5, 6, 7])
        for i in range(n):
            ox = cx + (i - n / 2) * 38
            oy = cy + int(8 * math.sin(i)) + rnd.randint(-6, 6)
            glow(draw, int(ox), oy, 8, (160, 255, 200), 5)
    elif category == "cylinder_other":
        draw.rounded_rectangle([cx - 12, cy - 70, cx + 12, cy + 70], radius=10, fill=(8, 28, 16, 220), outline=(0, 255, 140, 200), width=2)
        glow(draw, cx, cy - 70, 10, (180, 255, 200), 5)
        glow(draw, cx, cy + 70, 8, (80, 255, 140), 4)
    elif category == "rocket_reentry_starlink":
        if rnd.random() < 0.5:
            # train
            for i in range(8):
                ox = cx - 160 + i * 42
                oy = cy + i * 6
                glow(draw, ox, oy, 7, (200, 220, 255), 5)
        else:
            x0, y0 = cx - 160, cy - 80
            x1, y1 = cx + 80, cy + 40
            for w in range(8, 0, -1):
                draw.line([(x0, y0), (x1, y1)], fill=(255, 160, 80, 20 + w * 18), width=w)
            glow(draw, x1, y1, 12, (255, 180, 80), 5)
    else:
        # unspecified faint anomaly
        glow(draw, cx, cy, rnd.randint(16, 28), (100, 255, 160), 8)
        if rnd.random() < 0.5:
            draw.arc([cx - 40, cy - 20, cx + 40, cy + 20], 200, 340, fill=(0, 255, 140, 120), width=2)


def scanlines(img: Image.Image, gap=3, alpha=42) -> Image.Image:
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(0, img.height, gap):
        d.line([(0, y), (img.width, y)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img.convert("RGBA"), ov)


def vignette(img: Image.Image, strength=0.7) -> Image.Image:
    img = img.convert("RGBA")
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse([int(w * 0.04), int(h * 0.06), w - int(w * 0.04), h - int(h * 0.06)], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=min(w, h) // 6))
    black = Image.new("RGBA", (w, h), (0, 0, 0, int(255 * strength)))
    inv = Image.eval(mask, lambda p: 255 - p)
    black.putalpha(inv)
    return Image.alpha_composite(img, black)


def grain(img: Image.Image, rnd: random.Random, amount=18) -> Image.Image:
    noise = Image.new("L", img.size, 0)
    npx = noise.load()
    for y in range(0, img.height, 2):
        for x in range(0, img.width, 2):
            v = rnd.randint(0, amount)
            npx[x, y] = v
    noise = noise.resize(img.size, Image.Resampling.BILINEAR)
    overlay = Image.merge("RGBA", (noise, noise, noise, noise.point(lambda p: p)))
    return ImageChops.add(img.convert("RGBA"), overlay, scale=1.0, offset=0)


def label(draw, case_no: str, province: str | None, case_id: str):
    mono = font(16)
    small = font(13)
    big = font(18)
    # top bar
    draw.rectangle([0, 0, W, 36], fill=(0, 0, 0, 170))
    draw.text((14, 8), (case_no or case_id).upper(), font=mono, fill=(0, 255, 106, 230))
    prov = (province or "LOCATION UNSPECIFIED").upper()
    tw = draw.textlength(prov, font=small)
    draw.text((W - tw - 14, 10), prov, font=small, fill=(160, 255, 190, 210))
    # bottom evidence banner
    banner = "ILLUSTRATION  —  NOT EVIDENCE"
    bw = draw.textlength(banner, font=big)
    bx, by = (W - bw) / 2, H - 44
    draw.rectangle([bx - 16, by - 6, bx + bw + 16, by + 24], fill=(0, 0, 0, 210), outline=(255, 193, 77, 200))
    draw.text((bx, by), banner, font=big, fill=(255, 193, 77, 240))


def render_case(s: dict) -> Image.Image:
    rnd = seed_for(s["id"])
    region = region_of(s.get("province"))
    img = sky(rnd, region).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    add_stars(d, rnd, 180 + rnd.randint(0, 80))
    # occasional moon
    if rnd.random() < 0.45:
        mx, my, mr = rnd.randint(700, 900), rnd.randint(40, 120), rnd.randint(16, 26)
        d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(180, 255, 210, 50))
        d.ellipse([mx - mr + 4, my - mr + 4, mx + mr - 4, my + mr - 4], fill=(200, 255, 220, 90))
    horizon = ground(d, rnd, region)
    draw_object(d, rnd, s.get("category") or "unspecified", horizon)
    img = grain(vignette(scanlines(img, 3, 46), 0.68), rnd)
    d = ImageDraw.Draw(img, "RGBA")
    label(d, s.get("case_no") or "", s.get("province"), s["id"])
    return img.convert("RGB")


def save_webp(img: Image.Image, dest: Path, budget=140_000):
    q = 80
    while q >= 55:
        from io import BytesIO
        buf = BytesIO()
        img.save(buf, "WEBP", quality=q, method=6)
        data = buf.getvalue()
        if len(data) <= budget or q <= 55:
            dest.write_bytes(data)
            return len(data), q
        q -= 5
    dest.write_bytes(data)
    return len(data), q


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    doc = json.loads(DATA.read_text())
    sizes = []
    for s in doc["sightings"]:
        img = render_case(s)
        dest = OUT / f"{s['id']}.webp"
        n, q = save_webp(img, dest)
        sizes.append(n)
        print(f"  {dest.name:40} {n:6}B q={q}")
    print(f"wrote {len(sizes)} illustrations  max={max(sizes)}  mean={sum(sizes)//len(sizes)}")


if __name__ == "__main__":
    main()
