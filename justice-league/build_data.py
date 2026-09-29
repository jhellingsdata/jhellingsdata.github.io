"""
Build the Premier League final tables used by the points-deduction dashboard.

Steps
1. Fetch each season's Wikipedia article (2009/10 to 2025/26) and keep only the
   {{#invoke:Sports table}} block, cached in raw/ so later runs are offline and
   the snapshot is kept alongside the data.
2. Parse W/D/L/GF/GA, historic points adjustments and the actual qualification
   outcome for every position.
3. Attach the European allocation rules for each season (see RULES below).
4. Re-run the allocation with no extra deductions and check it reproduces the
   actual qualifiers from Wikipedia. The script stops if any season disagrees.
5. Write data/pl_tables.json and data/pl_tables.js (the same data, loaded by index.html).

Run: python3 build_data.py            (uses the cache in raw/)
     python3 build_data.py --refresh  (re-downloads from Wikipedia)
"""

import json
import re
import sys
import time
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "raw"
OUT = HERE / "data" / "pl_tables.json"
FIRST, LAST = 2009, 2025  # season start years
UA = "EPL-deductions-research/1.0 (hellin.gs)"

# Seasons covered by the Premier League charges (financial breaches 2009/10 to
# 2017/18). The 35 non-cooperation charges cover December 2018 to February 2023.
CHARGE_SEASONS = set(range(2009, 2018))
COOPERATION_SEASONS = set(range(2018, 2023))


# ---------------------------------------------------------------------------
# European allocation rules
#
# Berths are handed out in order. Each "pos" berth goes to the highest-ranked
# team not already qualified. A "cup" berth goes to the cup winner unless they
# have already qualified, in which case the fallback applies:
#   next        -> passed down to the highest-ranked team not yet qualified
#   runnerup    -> given to the cup runner-up (FA Cup rule before 2015/16)
#   nextOrVacate-> passed down, but vacated if the next team is only qualified
#                  through a "fixed" berth (UEFA title-holder rule, 2016/17)
# "fixed" berths belong to a team whatever its league position (UEFA
# competition winners, fair play places). They are assigned first.
# ---------------------------------------------------------------------------
def pos(comp, n, stage):
    return {"type": "pos", "comp": comp, "n": n, "stage": stage}


def cup(cup_name, winner, comp, stage, fallback="next", runnerup=None):
    r = {"type": "cup", "cup": cup_name, "winner": winner, "comp": comp,
         "stage": stage, "fallback": fallback}
    if runnerup:
        r["runnerup"] = runnerup
    return r


def fixed(team, comp, route):
    return {"team": team, "comp": comp, "route": route}


FA, LC = "FA Cup", "League Cup"
MCI, MUN = "Manchester City", "Manchester United"

RULES = {
    2009: {"fixed": [], "berths": [
        pos("UCL", 4, "group stage / play-off"), pos("UEL", 1, "play-off round"),
        cup(LC, MUN, "UEL", "play-off round"),
        cup(FA, "Chelsea", "UEL", "third qualifying round"),
    ], "note": "FA Cup runners-up Portsmouth did not hold a UEFA licence, so their place passed to the best-placed league team."},
    2010: {"fixed": [fixed("Fulham", "UEL", "Fair play place")], "berths": [
        pos("UCL", 4, "group stage / play-off"), pos("UEL", 1, "play-off round"),
        cup(FA, MCI, "UEL", "play-off round", "runnerup", "Stoke City"),
        cup(LC, "Birmingham City", "UEL", "play-off round"),
    ]},
    2011: {"fixed": [fixed("Chelsea", "UCL", "Champions League holders")], "berths": [
        pos("UCL", 3, "group stage"), pos("UEL", 1, "group stage"), pos("UEL", 1, "play-off round"),
        cup(LC, "Liverpool", "UEL", "third qualifying round"),
    ], "note": "Chelsea won the Champions League from 6th. England was capped at four entrants, so 4th place dropped into the Europa League."},
    2012: {"fixed": [], "berths": [
        pos("UCL", 4, "group stage / play-off"), pos("UEL", 1, "play-off round"),
        cup(FA, "Wigan Athletic", "UEL", "group stage"),
        cup(LC, "Swansea City", "UEL", "third qualifying round"),
    ]},
    2013: {"fixed": [], "berths": [
        pos("UCL", 4, "group stage / play-off"), pos("UEL", 1, "group stage"),
        cup(FA, "Arsenal", "UEL", "third qualifying round", "runnerup", "Hull City"),
        cup(LC, MCI, "UEL", "play-off round"),
    ]},
    2014: {"fixed": [fixed("West Ham United", "UEL", "Fair play place")], "berths": [
        pos("UCL", 4, "group stage / play-off"), pos("UEL", 1, "group stage"),
        cup(FA, "Arsenal", "UEL", "group stage"),
        cup(LC, "Chelsea", "UEL", "third qualifying round"),
    ]},
    2015: {"fixed": [], "berths": [
        pos("UCL", 4, "group stage / play-off"), pos("UEL", 1, "group stage"),
        cup(FA, MUN, "UEL", "group stage"),
        cup(LC, MCI, "UEL", "third qualifying round"),
    ]},
    2016: {"fixed": [fixed(MUN, "UCL", "Europa League holders")], "berths": [
        pos("UCL", 4, "group stage / play-off"), pos("UEL", 1, "group stage"),
        cup(FA, "Arsenal", "UEL", "group stage", "nextOrVacate"),
        cup(LC, MUN, "UEL", "third qualifying round"),
    ], "note": "Manchester United won the Europa League, so the Europa League place their league position earned was left vacant."},
    2017: {"fixed": [], "berths": [
        pos("UCL", 4, "group stage"), pos("UEL", 1, "group stage"),
        cup(FA, "Chelsea", "UEL", "group stage"),
        cup(LC, MCI, "UEL", "second qualifying round"),
    ]},
    2018: {"fixed": [], "berths": [
        pos("UCL", 4, "group stage"), pos("UEL", 1, "group stage"),
        cup(FA, MCI, "UEL", "group stage"),
        cup(LC, MCI, "UEL", "second qualifying round"),
    ]},
    2019: {"fixed": [], "berths": [
        pos("UCL", 4, "group stage"), pos("UEL", 1, "group stage"),
        cup(FA, "Arsenal", "UEL", "group stage"),
        cup(LC, MCI, "UEL", "second qualifying round"),
    ]},
    2020: {"fixed": [], "berths": [
        pos("UCL", 4, "group stage"), pos("UEL", 1, "group stage"),
        cup(FA, "Leicester City", "UEL", "group stage"),
        cup(LC, MCI, "UECL", "play-off round"),
    ]},
    2021: {"fixed": [], "berths": [
        pos("UCL", 4, "group stage"), pos("UEL", 1, "group stage"),
        cup(FA, "Liverpool", "UEL", "group stage"),
        cup(LC, "Liverpool", "UECL", "play-off round"),
    ]},
    2022: {"fixed": [fixed("West Ham United", "UEL", "Conference League holders")], "berths": [
        pos("UCL", 4, "group stage"), pos("UEL", 1, "group stage"),
        cup(FA, MCI, "UEL", "group stage"),
        cup(LC, MUN, "UECL", "play-off round"),
    ]},
    2023: {"fixed": [], "berths": [
        pos("UCL", 4, "league phase"), pos("UEL", 1, "league phase"),
        cup(FA, MUN, "UEL", "league phase"),
        cup(LC, "Liverpool", "UECL", "play-off round"),
    ]},
    2024: {"fixed": [fixed("Tottenham Hotspur", "UCL", "Europa League holders"),
                     fixed("Crystal Palace", "UECL", "FA Cup winners (moved from Europa League by UEFA)")], "berths": [
        pos("UCL", 5, "league phase"), pos("UEL", 2, "league phase"),
    ], "note": "England earned a fifth Champions League place. FA Cup winners Crystal Palace were moved to the Conference League under UEFA multi-club ownership rules, and their Europa League place passed down the table."},
    2025: {"fixed": [fixed("Crystal Palace", "UEL", "Conference League holders")], "berths": [
        pos("UCL", 5, "league phase"), pos("UEL", 1, "league phase"),
        cup(FA, MCI, "UEL", "league phase"),
        cup(LC, MCI, "UECL", "play-off round"),
    ], "note": "England earned a fifth Champions League place."},
}


# ---------------------------------------------------------------------------
# Fetch and parse
# ---------------------------------------------------------------------------
def season_label(y):
    return f"{y}/{str(y + 1)[2:]}"


def fetch_table_block(y, refresh=False):
    path = RAW / f"{y}-{str(y + 1)[2:]}.wikitext"
    if path.exists() and not refresh:
        return path.read_text()
    title = f"{y}–{str(y + 1)[2:]} Premier League"
    url = ("https://en.wikipedia.org/w/api.php?action=parse&prop=wikitext&format=json"
           f"&formatversion=2&redirects=1&page={urllib.parse.quote(title)}")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req) as resp:
                text = json.load(resp)["parse"]["wikitext"]
            break
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 4:
                raise
            time.sleep(30 * (attempt + 1))  # back off when rate-limited
    m = re.search(r"\{\{#invoke:[Ss]ports table\|main.*?\}\}</onlyinclude>", text, re.S)
    if not m:
        raise ValueError(f"No sports table found for {title}")
    RAW.mkdir(exist_ok=True)
    path.write_text(m.group(0))
    time.sleep(3)  # Wikipedia rate-limits bursts of requests
    return m.group(0)


def strip_markup(s):
    s = re.sub(r"<ref[^>]*/>", "", s)
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    return re.sub(r"<!--.*?-->", "", s, flags=re.S)


def delink(s):
    s = re.sub(r"\{\{nowrap\|(.*?)\}\}", r"\1", s)
    s = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", s)
    return s.strip()


def split_params(body):
    """Split template parameters on pipes that are not inside [[...]] or {{...}}."""
    parts, cur, depth, i = [], "", 0, 0
    while i < len(body):
        two = body[i:i + 2]
        if two in ("[[", "{{"):
            depth += 1; cur += two; i += 2; continue
        if two in ("]]", "}}"):
            depth -= 1; cur += two; i += 2; continue
        if body[i] == "|" and depth == 0:
            parts.append(cur); cur = ""
        else:
            cur += body[i]
        i += 1
    parts.append(cur)
    return {k.strip(): v.strip() for k, v in (p.split("=", 1) for p in parts if "=" in p)}


def comp_from_text(text):
    """Map Wikipedia's qualification text to a competition code."""
    for key, code in (("Champions League", "UCL"), ("Europa League", "UEL"),
                      ("Conference League", "UECL")):
        if key in text:
            return code
    return None


def parse_season(y, block):
    body = strip_markup(block.split("|main", 1)[1].rsplit("}}</onlyinclude>", 1)[0])
    P = split_params(body)
    if "team_order" in P:
        order = [t.strip() for t in P["team_order"].split(",") if t.strip()]
    else:
        order = [P[f"team{i}"] for i in range(1, 21)]
    assert len(order) == 20, y

    teams = []
    for position, code in enumerate(order, 1):
        w, d, l, gf, ga = (int(P[f"{k}_{code}"]) for k in ("win", "draw", "loss", "gf", "ga"))
        adj = int(P.get(f"adjust_points_{code}") or 0)
        r = P.get(f"result{position}")
        text = delink(P.get(f"text_{r}", "")) if r else ""
        team = {"pos": position, "team": delink(P[f"name_{code}"]), "w": w, "d": d, "l": l,
                "gf": gf, "ga": ga, "adj": adj, "pts": 3 * w + d + adj,
                "actual_comp": comp_from_text(text), "relegated": "elegation" in text}
        if adj:
            team["adj_note"] = re.sub(r"\s+", " ", delink(P.get(f"hth_{code}", "")))
        teams.append(team)
    return teams


# ---------------------------------------------------------------------------
# Allocation (mirrors the JavaScript in index.html)
# ---------------------------------------------------------------------------
def allocate(teams, rules):
    ranked = [t["team"] for t in teams]  # already in rank order
    q, fixed_only = {}, set()
    for f in rules["fixed"]:
        q[f["team"]] = f["comp"]
        fixed_only.add(f["team"])

    def next_free(skip_fixed=True):
        for t in ranked:
            if t not in q or (not skip_fixed and t in fixed_only):
                return t

    for b in rules["berths"]:
        if b["type"] == "pos":
            for _ in range(b["n"]):
                t = next_free()
                q[t] = b["comp"]; fixed_only.discard(t)
        elif b["winner"] not in q:
            q[b["winner"]] = b["comp"]
        elif b["fallback"] == "runnerup" and b["runnerup"] not in q:
            q[b["runnerup"]] = b["comp"]
        elif b["fallback"] == "nextOrVacate":
            t = next_free(skip_fixed=False)
            if t not in fixed_only:
                q[t] = b["comp"]
        else:
            q[next_free()] = b["comp"]
    return q


def main():
    refresh = "--refresh" in sys.argv
    seasons, problems = [], []
    for y in range(FIRST, LAST + 1):
        teams = parse_season(y, fetch_table_block(y, refresh))
        # Checks: 38 games each and order consistent with points, GD, goals scored
        assert all(t["w"] + t["d"] + t["l"] == 38 for t in teams), y
        keys = [(-t["pts"], -(t["gf"] - t["ga"]), -t["gf"]) for t in teams]
        assert keys == sorted(keys), f"{y}: order does not follow pts/GD/GF"
        rules = RULES[y]
        q = allocate(teams, rules)
        for t in teams:
            if q.get(t["team"]) != t["actual_comp"]:
                problems.append(f"{season_label(y)} {t['team']}: model {q.get(t['team'])}, actual {t['actual_comp']}")
            if t["relegated"] != (t["pos"] >= 18):
                problems.append(f"{season_label(y)} {t['team']}: relegation mismatch")
            del t["actual_comp"], t["relegated"]
        seasons.append({"season": season_label(y), "start": y,
                        "charge_period": y in CHARGE_SEASONS,
                        "cooperation_period": y in COOPERATION_SEASONS,
                        "source": f"https://en.wikipedia.org/wiki/{y}%E2%80%93{str(y + 1)[2:]}_Premier_League",
                        "rules": rules, "teams": teams})
    if problems:
        sys.exit("Allocation model disagrees with actual outcomes:\n  " + "\n  ".join(problems))
    OUT.parent.mkdir(exist_ok=True)
    payload = json.dumps({"built": time.strftime("%Y-%m-%d"), "seasons": seasons},
                         separators=(",", ":"))
    OUT.write_text(payload)
    # Same data as a script, so index.html also works when opened from disk
    OUT.with_suffix(".js").write_text(f"window.PL_DATA = {payload};\n")
    print(f"Wrote {OUT.relative_to(HERE)} (+ .js): {len(seasons)} seasons, allocation matches actual outcomes.")


if __name__ == "__main__":
    main()
