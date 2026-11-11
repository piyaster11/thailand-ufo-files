#!/usr/bin/env python3
"""Generate obviously-illustrated atmospheric art. Never presented as evidence."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import math, random

OUT = Path(__file__).resolve().parents[1] / "docs" / "img" / "illustrations"
OUT.mkdir(parents=True, exist_ok=True)

def try_font(size, bold=False):
    candidates = [
        "/workspace/thailand-ufo-files/docs/fonts/ShareTechMono-Regular.ttf",
        "/workspace/thailand-ufo-files/docs/fonts/SpecialElite-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def scanlines(img, gap=3, alpha=40):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(0, img.height, gap):
        d.line([(0, y), (img.width, y)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img.convert("RGBA"), ov)

def vignette(img, strength=0.65):
    img = img.convert("RGBA")
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    # radial-ish by drawing a white ellipse and blurring
    margin_x, margin_y = int(w * 0.05), int(h * 0.08)
    md.ellipse([margin_x, margin_y, w - margin_x, h - margin_y], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=min(w, h) // 6))
    black = Image.new("RGBA", (w, h), (0, 0, 0, int(255 * strength)))
    # where mask is white, keep original; where black, darken
    inv = Image.eval(mask, lambda p: 255 - p)
    black.putalpha(inv)
    return Image.alpha_composite(img, black)

def label_banner(draw, w, h, text="ILLUSTRATION — NOT EVIDENCE"):
    font = try_font(max(14, w // 42))
    pad = 8
    tw = draw.textlength(text, font=font)
    x = (w - tw) / 2
    y = h - 36
    draw.rectangle([x - 14, y - 6, x + tw + 14, y + 22], fill=(0, 0, 0, 200), outline=(0, 255, 106, 160))
    draw.text((x, y), text, font=font, fill=(0, 255, 106, 230))

# 1. Hero night-sky Mekong illustration
def hero():
    w, h = 1600, 700
    img = Image.new("RGB", (w, h), (3, 8, 5))
    px = img.load()
    rnd = random.Random(42)
    # gradient sky
    for y in range(h):
        t = y / h
        r = int(3 + t * 8)
        g = int(10 + t * 18)
        b = int(8 + t * 12)
        for x in range(w):
            px[x, y] = (r, g, b)
    # stars
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(220):
        x, y = rnd.randint(0, w - 1), rnd.randint(0, int(h * 0.62))
        c = rnd.randint(80, 255)
        s = rnd.choice([1, 1, 1, 2])
        d.ellipse([x, y, x + s, y + s], fill=(c, 255, int(c * 0.8), rnd.randint(140, 255)))
    # distant hills
    d.polygon([(0, 480), (200, 430), (420, 470), (700, 400), (980, 455), (1200, 390), (1600, 460), (1600, 700), (0, 700)], fill=(4, 14, 8, 255))
    # river
    d.polygon([(0, 560), (1600, 530), (1600, 700), (0, 700)], fill=(2, 20, 14, 255))
    # river highlights
    for i in range(18):
        y = 560 + i * 8
        d.arc([ -200, y, w + 200, y + 40], 0, 180, fill=(0, 80, 50, 60), width=2)
    # rising fireballs (illustrated, stylized)
    for i, (x, y0, rad) in enumerate([(420, 500, 10), (690, 470, 16), (980, 510, 8), (1180, 455, 12)]):
        for k in range(8, 0, -1):
            col = (40 + k * 20, 255, 80 + k * 10, 20 + k * 12)
            d.ellipse([x - rad * k // 2, y0 - rad * k // 2 - k * 8, x + rad * k // 2, y0 + rad * k // 2 - k * 8], fill=col)
        # trail
        d.line([(x, y0 + 10), (x, y0 + 80)], fill=(0, 255, 120, 80), width=2)
    # moon
    d.ellipse([1320, 70, 1400, 150], fill=(180, 255, 200, 40))
    d.ellipse([1330, 80, 1390, 140], fill=(200, 255, 220, 90))
    img = vignette(scanlines(img.convert("RGBA"), 3, 50), 0.7)
    d = ImageDraw.Draw(img)
    font = try_font(54)
    d.text((64, 40), "THAILAND UFO FILES", font=font, fill=(0, 255, 106, 230))
    font2 = try_font(22)
    d.text((66, 110), "THE TRUTH IS OUT THERE  //  CLASSIFIED ARCHIVE", font=font2, fill=(0, 200, 90, 200))
    label_banner(d, w, h)
    img.convert("RGB").save(OUT / "hero-mekong.png", quality=90)
    print("wrote hero-mekong.png")

# 2. Classified folder background
def folder():
    w, h = 900, 1200
    img = Image.new("RGB", (w, h), (10, 16, 11))
    d = ImageDraw.Draw(img, "RGBA")
    # paper lines
    for y in range(0, h, 28):
        d.line([(40, y), (w - 40, y)], fill=(0, 40, 22, 80), width=1)
    # stamps
    d.rectangle([40, 40, 320, 120], outline=(255, 40, 40, 220), width=5)
    d.text((58, 58), "CLASSIFIED", font=try_font(36), fill=(255, 50, 50, 230))
    d.rectangle([w - 300, 40, w - 40, 120], outline=(0, 255, 106, 200), width=3)
    d.text((w - 280, 62), "CASE FILE", font=try_font(28), fill=(0, 255, 106, 230))
    img = scanlines(img.convert("RGBA"), 4, 35)
    img.convert("RGB").save(OUT / "folder-bg.png", quality=88)
    print("wrote folder-bg.png")

# 3. Radar / night disc illustration
def radar_disc():
    w, h = 1000, 700
    img = Image.new("RGB", (w, h), (2, 6, 4))
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy = w // 2, int(h * 0.58)
    for r in range(280, 40, -30):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 255, 106, 40 + (280 - r) // 4), width=2)
    # sweep wedge
    d.pieslice([cx - 260, cy - 260, cx + 260, cy + 260], 240, 280, fill=(0, 255, 106, 28))
    # stylized disc silhouette
    d.ellipse([cx - 90, cy - 22, cx + 90, cy + 22], fill=(0, 40, 20, 200), outline=(0, 255, 106, 180), width=2)
    d.ellipse([cx - 28, cy - 36, cx + 28, cy - 8], fill=(0, 30, 16, 200), outline=(0, 255, 160, 160), width=2)
    d.ellipse([cx - 8, cy - 28, cx + 8, cy - 14], fill=(180, 255, 200, 200))
    # stars
    rnd = random.Random(7)
    for _ in range(120):
        x, y = rnd.randint(0, w - 1), rnd.randint(0, int(h * 0.7))
        d.point((x, y), fill=(180, 255, 200, 200))
    img = vignette(scanlines(img.convert("RGBA"), 3, 45), 0.6)
    d = ImageDraw.Draw(img)
    label_banner(d, w, h)
    img.convert("RGB").save(OUT / "radar-disc.png", quality=90)
    print("wrote radar-disc.png")

# 4. Open folder icon-ish og image / social
def og():
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), (4, 8, 5))
    d = ImageDraw.Draw(img, "RGBA")
    # grid
    for x in range(0, w, 40):
        d.line([(x, 0), (x, h)], fill=(0, 40, 22, 70), width=1)
    for y in range(0, h, 40):
        d.line([(0, y), (w, y)], fill=(0, 40, 22, 70), width=1)
    d.rectangle([40, 40, w - 40, h - 40], outline=(0, 255, 106, 180), width=3)
    d.text((70, 80), "THE TRUTH IS OUT THERE", font=try_font(28), fill=(0, 200, 90, 220))
    d.text((70, 160), "THAILAND", font=try_font(92), fill=(0, 255, 106, 240))
    d.text((70, 270), "UFO FILES", font=try_font(92), fill=(0, 255, 106, 240))
    d.text((70, 400), "A public archive of reported sky anomalies  //  ไฟล์ยูเอฟโอประเทศไทย", font=try_font(22), fill=(160, 255, 190, 200))
    d.text((70, 470), "UNVERIFIED REPORTS  ·  NOT PROOF  ·  MANY HAVE MUNDANE EXPLANATIONS", font=try_font(18), fill=(255, 200, 80, 220))
    img = scanlines(img.convert("RGBA"), 3, 40)
    img.convert("RGB").save(OUT / "og-cover.png", quality=90)
    print("wrote og-cover.png")

if __name__ == "__main__":
    hero(); folder(); radar_disc(); og()
    print("all illustrations written to", OUT)
