#!/usr/bin/env python3
"""Scrape today's lunch menus from lounaat.info and write menus.json."""
import json
import re
import sys
import urllib.request
from datetime import datetime
from html import unescape
from zoneinfo import ZoneInfo

SLUGS = [
    "southpark",
    "sodexo-kiltakellari",
    "ravintola-brod-punavuori",
    "levant-bulevardi",
    "ravintola-lonkka",
    "mekong",
    "salve",
]

FI_WEEKDAYS = {
    0: "maanantaina",
    1: "tiistaina",
    2: "keskiviikkona",
    3: "torstaina",
    4: "perjantaina",
    5: "lauantaina",
    6: "sunnuntaina",
}

UA = "Mozilla/5.0 (compatible; bulevardi-lunch-bot/1.0; +https://github.com)"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace")


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    s = unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def parse_today(html: str, day_fi: str, dnum: int, mnum: int) -> list[dict]:
    """Find <h3>{Day} {d}.{m}.</h3> and parse the <li>s under it."""
    heading_re = re.compile(
        rf"<h3[^>]*>\s*{day_fi.capitalize()}\s+{dnum}\.{mnum}\.\s*</h3>"
        r"([\s\S]*?)(?=<h3|<h2|<div\s+class=\"menu\"|$)",
        re.IGNORECASE,
    )
    m = heading_re.search(html)
    if not m:
        return []
    block = m.group(1)

    items = []
    for li_match in re.finditer(r"<li[^>]*>([\s\S]*?)</li>", block, re.IGNORECASE):
        inner = li_match.group(1)

        # Price
        price = ""
        pm = re.search(r"(\d+[.,]\d{2})\s*[e€]", inner, re.IGNORECASE)
        if pm:
            price = pm.group(1).replace(".", ",") + "€"

        # Tags from <a class="l|g|m|veg|...">
        tags = set()
        for am in re.finditer(r'<a[^>]*\bclass="([^"]+)"', inner, re.IGNORECASE):
            cls = am.group(1).lower().strip()
            if cls in ("l", "g", "m", "vl"):
                tags.add(cls.upper())
            elif cls in ("veg", "veg*"):
                tags.add("V")

        text = strip_tags(inner)
        if re.search(r"\bvegaaninen\b", text, re.IGNORECASE):
            tags.add("VE")
        elif re.search(r"\bveg\b", text, re.IGNORECASE) and "VE" not in tags:
            tags.add("V")

        # Name = text minus price minus trailing diet letters
        name = re.sub(r"\d+[.,]\d{2}\s*[e€]", "", text, flags=re.IGNORECASE)
        name = re.sub(
            r"\s+([lgmvLGMV]\s*)+(veg\*?)?\s*,?\s*(pähkinä)?\s*$",
            "",
            name,
            flags=re.IGNORECASE,
        ).strip()
        name = re.sub(r"^[•·\-*]\s*", "", name).strip()

        if name:
            items.append({"name": name, "price": price, "tags": sorted(tags)})

    return items


def scrape_one(slug: str, day_fi: str, d: int, mo: int) -> list[dict]:
    url = f"https://www.lounaat.info/lounas/{slug}/helsinki"
    try:
        html = fetch(url)
        return parse_today(html, day_fi, d, mo)
    except Exception as e:
        print(f"  ! {slug}: {e}", file=sys.stderr)
        return []


def main() -> int:
    now = datetime.now(ZoneInfo("Europe/Helsinki"))
    day_fi = FI_WEEKDAYS[now.weekday()]
    d, mo = now.day, now.month

    print(f"Scraping for {day_fi} {d}.{mo}. ({now.isoformat()})")

    out = {"fetchedAt": now.isoformat(), "date": f"{d}.{mo}.", "menus": {}}
    for slug in SLUGS:
        items = scrape_one(slug, day_fi, d, mo)
        out["menus"][slug] = items
        print(f"  - {slug}: {len(items)} items")

    with open("menus.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("Wrote menus.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
