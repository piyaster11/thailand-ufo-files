#!/usr/bin/env python3
"""Attach hosted images to every case.

Real Wikimedia Commons photographs are used only when they are truthful for that
case (the 2013 Naga night, or a clearly captioned example / location photo).
Every other case gets a generated illustration stamped ILLUSTRATION — NOT EVIDENCE.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path(__file__).resolve().parent / "commons_manifest.json"
ILLUSTRATIONS = ROOT / "docs" / "img" / "illustrations" / "cases"

REAL_KINDS = {"source_photo", "example_photo", "location_photo"}


def _page(rec: dict) -> str:
    title = rec.get("title") or ""
    slug = title.replace("File:", "").replace(" ", "_")
    if slug:
        return "https://commons.wikimedia.org/wiki/File:" + slug
    return rec.get("page") or ""


def credit(rec: dict, note: str) -> str:
    artist = rec.get("artist") or "see Commons"
    license_ = rec.get("license") or "see Commons"
    date = (rec.get("date") or "").split(" (")[0].strip()
    if "T" in date and len(date) > 10:
        date = date[:10]
    bits = [f"Photo: {artist}"]
    if date:
        bits.append(date)
    bits.append(f"Licence: {license_}. Source: Wikimedia Commons.")
    line = ", ".join(bits[:2]) + ". " + bits[2] if date else bits[0] + ". " + bits[2]
    if rec.get("credit_note"):
        line += " " + rec["credit_note"]
    if note:
        line += " " + note
    return line


def photo(by_slug: dict, slug: str, kind: str, alt: str, note: str) -> dict:
    rec = by_slug[slug]
    return {
        "src": rec["src"],
        "alt": alt,
        "credit": credit(rec, note),
        "page": _page(rec),
        "kind": kind,
        "license": rec.get("license"),
        "artist": rec.get("artist"),
    }


def illustration(s: dict) -> dict:
    path = f"img/illustrations/cases/{s['id']}.webp"
    loc = s.get("province") or s.get("location_name") or "an unspecified Thai location"
    return {
        "src": path,
        "alt": f"Atmospheric X-Files-style illustration of a night sky over {loc}, labelled illustration not evidence",
        "credit": "Generated illustration for this archive — not a photograph, not evidence of the reported object.",
        "kind": "illustration",
    }


def assignments(by_slug: dict) -> dict[str, list[dict]]:
    loc_note = (
        "Location photograph of the Mekong in Nong Khai Province — not a picture of this year's Naga fireballs."
    )
    naga_later = {}
    # Alternate the two Mekong stills so later festival years are not identical.
    mekong_cycle = ["mekong-phonphisai", "mekong-nongkhai-dusk"]
    for i, year in enumerate(["2015", "2021", "2022", "2023", "2024", "2025"]):
        slug = mekong_cycle[i % 2]
        place = "Phon Phisai" if slug == "mekong-phonphisai" else "east of Nong Khai"
        naga_later[f"naga-{year}"] = [
            photo(
                by_slug,
                slug,
                "location_photo",
                f"The Mekong River at {place}. Location photograph — not a picture of the {year} Naga fireballs.",
                loc_note,
            )
        ]

    fireball_note = (
        "Example photograph of a meteor fireball, taken outside Thailand. "
        "This is not a photograph of the Thai event in this case file."
    )
    return {
        "naga-2013": [
            photo(
                by_slug,
                "naga-183",
                "source_photo",
                "Pinkish ball of light above a riverbank at night, photographed near Nong Khai on 19 October 2013",
                "Photographed on the festival night of 19 October 2013, near Nong Khai / the Mekong.",
            ),
            photo(
                by_slug,
                "naga-187",
                "source_photo",
                "Another frame of a Naga fireball over the Mekong, 19 October 2013",
                "Photographed on the same night, 19 October 2013.",
            ),
        ],
        **naga_later,
        "starlink-north-2023": [
            photo(
                by_slug,
                "starlink-train",
                "example_photo",
                "A train of Starlink satellites crossing a night sky, photographed in 2020 outside Thailand",
                "Example photograph of a Starlink satellite train (Jud McCranie, 2020). Not a photograph of the 1 June 2023 northern-Thailand pass.",
            )
        ],
        "chiangmai-lantern-2020": [
            photo(
                by_slug,
                "yipeng-chiangmai",
                "example_photo",
                "Sky lanterns released at the Yi Peng festival in Chiang Mai",
                "Typical sky lanterns at Yi Peng in Chiang Mai. This is not a frame from the 2020 Doi Suthep video.",
            )
        ],
        "iss-prachuap-2021": [
            photo(
                by_slug,
                "iss-sts134",
                "example_photo",
                "The International Space Station photographed from space shuttle Endeavour in 2011",
                "NASA photograph of the ISS after STS-134 undocking, 30 May 2011 (public domain). Not taken from Prachuap Khiri Khan; the 2021 report described a bright, slowly moving light, not this close-up.",
            )
        ],
        "prachuap-balloon-2022": [
            photo(
                by_slug,
                "weather-balloon",
                "example_photo",
                "A meteorological weather balloon in flight",
                "Public-domain U.S. National Weather Service / NOAA photograph of a radiosonde weather balloon. An example of the kind of balloon identified at Wa Ko in 2022, not a picture of that Thai object.",
            )
        ],
        "krabi-2021-balloon": [
            photo(
                by_slug,
                "weather-balloon",
                "example_photo",
                "A meteorological weather balloon in flight",
                "Public-domain U.S. National Weather Service / NOAA photograph of a weather balloon. Scientists suggested a balloon as one possible explanation for the 2021 Krabi object; this is not a photograph of that object.",
            )
        ],
        "kaeng-krachan-2023": [
            photo(
                by_slug,
                "gulf-fishing-lights",
                "example_photo",
                "Blue and green fishing-boat lights in the Gulf of Thailand and the Andaman Sea, seen from the International Space Station",
                "NASA photograph of fishing-boat lights in the Gulf of Thailand and the Andaman Sea, taken from the ISS (public domain). An example of the lamps thought to have caused the 2023 Kaeng Krachan glow, not a picture from Panoenthung on 3 November 2023.",
            )
        ],
        "fireball-2015-11-02": [
            photo(
                by_slug,
                "fireball-alma",
                "example_photo",
                "A meteor fireball falling over the ALMA observatory in Chile",
                fireball_note,
            )
        ],
        "phitsanulok-fireball-2021": [
            photo(
                by_slug,
                "fireball-kittpeak",
                "example_photo",
                "A meteor fireball over Kitt Peak National Observatory, Arizona",
                fireball_note,
            )
        ],
        "fireball-2024-03-04": [
            photo(
                by_slug,
                "fireball-alma",
                "example_photo",
                "A meteor fireball falling over the ALMA observatory in Chile",
                fireball_note,
            )
        ],
        "fireball-2025-08-04": [
            photo(
                by_slug,
                "fireball-kittpeak",
                "example_photo",
                "A meteor fireball over Kitt Peak National Observatory, Arizona",
                fireball_note,
            )
        ],
    }


def attach_photos(items: list[dict]) -> dict:
    by_slug = {r["slug"]: r for r in json.loads(MANIFEST.read_text())}
    assigned = assignments(by_slug)
    real = 0
    illus = 0
    for s in items:
        photos = list(assigned.get(s["id"]) or [])
        # Every case without a real hosted photograph gets its illustration.
        if not photos:
            illu_path = ILLUSTRATIONS / f"{s['id']}.webp"
            if not illu_path.exists():
                raise SystemExit(f"missing illustration for {s['id']}")
            photos = [illustration(s)]
            illus += 1
        else:
            real += 1
        s["photos"] = photos
        s["has_real_photo"] = any(p.get("kind") in REAL_KINDS for p in photos)
        s["has_illustration"] = any(p.get("kind") == "illustration" for p in photos)
    return {"with_real_photo": real, "with_illustration_only": illus, "total": len(items)}


PHOTO_METHODOLOGY = (
    "Every case file has a picture. Event photographs are hosted only when a freely licensed "
    "image of that event exists (J A Forbes's Naga fireball series, 19 October 2013, CC BY-SA 4.0). "
    "A smaller set of Wikimedia Commons stills is used as clearly captioned examples "
    "(a Starlink train, Yi Peng lanterns, the ISS, a weather balloon, Gulf of Thailand fishing lights, "
    "meteor fireballs photographed outside Thailand) or as Mekong location photographs for later "
    "Naga fireball years — never as pictures of those specific nights. All other cases use a "
    "generated X-Files-style illustration stamped 'ILLUSTRATION — NOT EVIDENCE'. "
    "News-agency photographs are not copied; those cases keep a 'View source' link. "
    "Example and location photographs must not be treated as evidence of the Thai event."
)


if __name__ == "__main__":
    data_path = ROOT / "docs" / "data" / "sightings.json"
    doc = json.loads(data_path.read_text())
    stats = attach_photos(doc["sightings"])
    if "methodology" in doc:
        doc["methodology"]["photos"] = PHOTO_METHODOLOGY
    doc["counts"]["with_hosted_photos"] = stats["total"]
    doc["counts"]["with_real_photo"] = stats["with_real_photo"]
    doc["counts"]["with_illustration_only"] = stats["with_illustration_only"]
    data_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print("attached", stats)
