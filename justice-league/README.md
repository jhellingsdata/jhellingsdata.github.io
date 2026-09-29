# Justice League

An interactive page for exploring how Premier League final tables change if Manchester City are given points deductions, following the September 2026 verdict on the 115 charges.

Live at <https://hellin.gs/justice-league/>.

## Files

| File | Purpose |
|---|---|
| `index.html` | The page (D3). Loads `data/pl_tables.js`. |
| `build_data.py` | Builds `data/pl_tables.json` and `data/pl_tables.js` from the Wikipedia table snapshots in `raw/`. |
| `raw/` | The league table block from each season's Wikipedia article, 2009/10 to 2025/26. |
| `fetch_logos.py` | Downloads club crests into `logos/`. Not used by the page yet. |
| `articles/` | Source articles for reference. Git-ignored, as they must not be republished. |

## Rebuilding the data

```sh
python3 build_data.py            # from the snapshots in raw/
python3 build_data.py --refresh  # re-download from Wikipedia first
```

The build stops if the European allocation rules fail to reproduce the actual qualifiers and relegated clubs for any season. The JavaScript in `index.html` mirrors `allocate()` in `build_data.py`, so change both together.

## Club crests (on hold)

`python3 fetch_logos.py` fetches a crest for all 42 clubs into `logos/` (git-ignored) and writes `logos/manifest.json`, which maps each club and season to a file. It needs the GitHub CLI (`gh`).

- **Sources.** [luukhopman/football-logos](https://github.com/luukhopman/football-logos) has season-by-season Premier League crests from 2021/22, plus the current season (the only source for Hull City). The 14 clubs not in the Premier League since then come from ESPN's logo CDN (current crest only): Birmingham, Blackburn, Blackpool, Bolton, Cardiff, Huddersfield, Middlesbrough, Portsmouth, QPR, Reading, Stoke, Swansea, West Brom and Wigan.
- **Crest changes in the repo.** Aston Villa (2024/25), Burnley (2023/24), Leeds (2022/23), Liverpool (2025/26) and Tottenham (2025/26). Chelsea has three files that look identical.
- **No crests before 2021/22.** Earlier seasons would show the current crest. Clubs that changed crest within 2009 to 2021 include Manchester City (2016), West Ham (2016), Everton (2014) and Crystal Palace (2013). Older crests are on Wikipedia, but as non-free (fair use) files.
- **Dark mode.** Tottenham, Swansea, QPR, Luton and Bolton are navy or black and need a light backing in dark mode.
- **Sizes.** Repo crests are 139×181, ESPN crests 500×500, all transparent. Show them with `object-fit: contain` in a fixed square.
- **Licensing.** The repo has no licence and crests are club trademarks. If used, keep them small, for identification only, and credit the sources.
