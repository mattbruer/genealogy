"""Guess each photo's year, family branches and topics from its caption -> src/lib/data/tags.json

Rules, not certainty. Ids already in tags.json are kept as-is, so hand fixes survive re-runs
(delete an entry to have it re-guessed).
"""
import json, re, statistics
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "src" / "lib" / "data"

# Branch -> caption patterns (case-sensitive, so names don't match ordinary words)
FAMILIES = {
    "W.T. & Clara Kate Bruer": r"W\.T|Clara Kate|Ewart|Lura|Clara Bell|Clarabell|Cramer|Clair \"Bud\"|\bBud\b|\bOra\b|Cecil|\bWes\b|Wesley|\bLora\b|\bFrank\b|\bLaura\b|Joe W(ilda|\.)",
    "Joe & Jessie Bruer": r"Jessie(?! Koch)(?! \(Sara)|Granny|Joe W(ilda|\.)|Tarryall|wagon|Leafy Dell",
    "Fitch family": r"Fitch|Lella|Willa|Edith|Helen Lower|Helen \(Lower\)|Brittain|Comstock|Uncle Vol|Aunt Bess|\bBess\b|Bessie",
    "Massey family": r"Massey(?! Fitch)|Gertrude|Gertie|Minnie|Aunt Min|Josephine|Brumfield|Piper|Coffman|Watson",
    "Tom & Reta's family": r"\bReta\b|Phyllis|Allhands|Tom & Reta",
    "Jack & Joann's family": r"Joann|Barbara|Nancy Jane|Janie|Mildred|Jack's son|son of Jack",
    "Homer & Lucy's family": r"Lucy|Susan|\bSara\b|Sandy|Sandra|\bCarol\b|Cathy|twins|Koch|Tiernan|Herstein|Hot Springs",
    "Bob & Mary": r"Uncle Bob|Aunt Mary|Robert \"Bob\"|McNutt",
    "Volney & Betty's family": r"Betty|Jerry|Bobby|Claudia|Patty|Graves|\bAnn\b|\bRob\b|Matt|Dan Bruer|Parker|Campbell|\(me\)|Your's truly|Mom and Dad|Mom & Dad",
    "Joe C. & Freida's family": r"Freida|Frieda|Joey|Dennie|Joseph,|Joseph Bruer|Emma|Grayson",
    "Nancy's family": r"David Jones|Bowles|Max Jones",
}

TOPICS = {
    "Tarryall ranch": r"Tarryall",
    "1925 wagon trip": r"wagon|[Ee]nroute|cotton|bonnet|Bonnet|trip home",
    "Military": r"\bWar\b|WW|Army|Navy|Randolph Field|Ft\. Benning|OCS|Camp McKinley|soldier|soidier|Combat",
    "Documents & letters": r"census|[Pp]ost ?card|obituary|Obituary|receipt|announcement|memorabilia|written on|Written on|[Bb]ack (of|side)",
    "Gatherings": r"gather|Gather|Christmas|Thanksgiving|[Pp]icnic|funeral|wedding|reunion|Four generations|Four Generations|get together",
    "School photos": r"SCHOOL DAYS|graduat|Senior High|[Ss]chool",
    "Cars & machines": r"\bcar\b|Model [TA]|Ford|Chevrolet|BMW|motorcycle|m/cycle|license plate|Crown Victoria|Studebaker|airplane",
    "Hunting & fishing": r"hunt|fish|bird dog|birddog",
    "Commercial Street": r"Commercial|Com'l",
}

# Where/what, when no year is written: (pattern, typical year)
ERA_HINTS = [
    (r"wagon|[Ee]nroute|cotton|bonnet", 1925), (r"Tarryall", 1922), (r"Williams Canyon|Manitou", 1918),
    (r"Cheyenne|Laramie|Wyoming", 1918), (r"Lake George", 1916), (r"Osawatomie", 1910),
    (r"Blaine St", 1935), (r"Velma|Muskogee", 1920), (r"Spanish American|Camp McKinley", 1898),
    (r"Graves|Koch|Tiernan|Herstein|Hope Allhands|Melissa|Emma|Grayson|Parker|Ayla|Rob,? Liz", 2015),
    (r"Joseph,|Joseph Bruer|Dennie", 2000), (r"David Jones", 1975),
    (r"Twins|twins|Susan|\bSara\b|Sandy|Cathy|Carol", 1960), (r"Barbara|Nancy Jane|Janie", 1955),
    (r"Phyllis", 1950), (r"Joey", 1955), (r"Jerry|Bobby|Claudia", 1950),
    (r"Uncle Bob|Aunt Mary", 1960), (r"Joe C\.|Joe Clair", 1945), (r"Wes and Lora|Wes & Lora|Lora", 1935),
    (r"Ewart|Clara Bell|Clara Kate|W\.T", 1910), (r"Clair|Ora|Bill|Cecil", 1920),
    (r"Gertrude|Gertie|Minnie|Josephine|Brumfield", 1905), (r"Lella|John Fitch", 1925),
    (r"Nancy", 1940), (r"Volney|Vol\b", 1930), (r"Jessie", 1930),
]

NOT_PHOTO_DATE = r"(born|b\.|died|death|passed|married|since|until|completed|built)\s+(in\s+|on\s+)?([A-Z][a-z]+\.?\s+(\d+,\s+)?)?$"


def year_from_text(caption):
    """Years written in the caption that look like when the photo was taken (not births, deaths...)."""
    years = []
    for m in re.finditer(r"(?<![\d/-])(18[6-9]\d|19\d\d|20[0-2]\d)(?![\d-])(?!\s+[NSEW]\.)", caption):
        before = caption[max(0, m.start() - 40):m.start()]
        if re.search(NOT_PHOTO_DATE, before) or re.search(r"\d-$", before):
            continue
        prefer = re.search(r"(~|about|circa|in|taken|Taken)\s*$", before)
        years.append((not prefer, int(m.group(1))))
    if not years:
        return None
    preferred = [y for flag, y in years if not flag]
    return int(statistics.median(preferred or [y for _, y in years]))


def tilde_year(caption):
    m = re.search(r"~\s*'?(\d\d)\b", caption)
    return 1900 + int(m.group(1)) if m else None


def guess_year(caption):
    year = year_from_text(caption) or tilde_year(caption)
    if year:
        return year, "caption"
    for pattern, typical in ERA_HINTS:
        if re.search(pattern, caption):
            return typical, "guess"
    return None, None


def tag(caption):
    year, source = guess_year(caption)
    return {
        "year": year,
        "yearIsGuess": source == "guess",
        "families": [f for f, p in FAMILIES.items() if re.search(p, caption)],
        "topics": [t for t, p in TOPICS.items() if re.search(p, caption)],
    }


def main():
    captions = json.loads((DATA / "captions.json").read_text())
    tags_file = DATA / "tags.json"
    tags = json.loads(tags_file.read_text()) if tags_file.exists() else {}
    for id_, caption in captions.items():
        tags.setdefault(id_, tag(caption))
    tags_file.write_text(json.dumps(tags, indent=1))
    undated = sum(1 for t in tags.values() if not t["year"])
    print(f"tagged {len(tags)} photos, {undated} undated")


if __name__ == "__main__":
    main()
