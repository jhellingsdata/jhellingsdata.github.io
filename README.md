# jhellingsdata.github.io

Source for [hellin.gs](https://hellin.gs): charts, dashboards and data stories by Josh Hellings.

The work spans a university data science course, research for the Economics Observatory and the LSE, personal projects, and teaching examples for students. Most charts are Vega-Lite specs, written by hand or exported from Altair.

## Layout

| Path | Contents |
|---|---|
| `index.html` | Home page. Each card links to a project. |
| `charts/` | Vega-Lite chart specs, grouped by project. `charts/teaser/` holds the home page previews. |
| `data-story/` | Longer interactive pieces, such as the tax explorer. |
| `justice-league/` | Premier League points deduction dashboard. |
| `examples/` | Teaching material: Vega-Lite and Python examples. |
| `tutorials/` | Step-by-step chart tutorials. `index.html` lists them (hellin.gs/tutorials/), and the pages share `tutorial.css` and `tutorial.js`. Their specs live in `examples/vega-lite/recreate/`. `tutorials-home.html` redirects here. |
| `EcoObservatory/`, `Hexmaps/` | Economics Observatory articles and UK hex maps. |
| `Portfolio/`, `Project/` | University of Bristol data science coursework. |
| `Data/` | Datasets used by the charts. |
| `fonts/`, `css/`, `js/` | Shared assets, including the Circular Std font. |

## Run locally

Charts load their data over HTTP, so serve the folder rather than opening files directly:

```bash
python3 -m http.server
```

Then open <http://localhost:8000>.

## Notes

- Circular Std is the Economics Observatory house font. `js/fonts-ready.js` delays chart rendering until it loads, because Vega does not redraw canvas text when a web font arrives.
- Two home page teasers are built with [ecostyles](https://github.com/jhellingsdata/ecostyles). See `charts/teaser/scripts/build_eco_teasers.py` to rebuild them.
- Map boundaries come from [map-data](https://github.com/jhellingsdata/map-data).
