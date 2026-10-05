"""Build the home page teaser charts for the ECO Styles and ECO Search cards.

Both charts use the ecostyles 'article' theme, so run with the ecostyles environment:

    ~/work/github/ecostyles/.venv/bin/python charts/teaser/scripts/build_eco_teasers.py

Outputs (in charts/teaser/):
    202501_EcoStyles.json  UK GDP growth (live from the ECO API) with recession shading
    202502_EcoSearch.json  Cumulative count of ECO articles in the search index
"""

import json
from pathlib import Path

import altair as alt
import pandas as pd
from ecostyles import EcoStyles

TEASER_DIR = Path(__file__).resolve().parents[1]
ARTICLES = Path.home() / "work/github/search-app/backend/data/all_articles.json"
GDP_URL = "https://api.economicsobservatory.com/gbr/grow?vega"
START = "1990-01-01"

styles = EcoStyles()
styles.register_and_enable_theme("article")


def save(chart, name):
    spec = chart.properties(width="container", height="container").to_dict()
    (TEASER_DIR / name).write_text(json.dumps(spec, indent=2))
    print(f"Saved {name}")


# ECO Styles: show the package at work, theme plus recession shading helper.
recessions = styles.get_recessions("uk")
recessions = recessions[recessions["start"] >= START]

gdp = (
    alt.Chart(alt.Data(url=GDP_URL))
    .mark_line(strokeWidth=1.5)
    .encode(
        x=alt.X("date:T", title=None, axis=alt.Axis(format="%Y", tickCount=4)),
        y=alt.Y("value:Q", title="GDP growth, %", axis=alt.Axis(tickCount=5)),
        tooltip=[alt.Tooltip("date:T", format="%b %Y", title="Quarter"),
                 alt.Tooltip("value:Q", title="Growth, %")],
    )
    .transform_filter(f"year(datum.date) >= {START[:4]}")
)
save(styles.add_shaded_area(periods=recessions) + gdp, "202501_EcoStyles.json")


# ECO Search: articles indexed over time.
articles = json.loads(ARTICLES.read_text())
dates = pd.to_datetime(pd.Series([a["date"] for a in articles.values()]))
monthly = dates.dt.to_period("M").value_counts().sort_index().cumsum()
counts = pd.DataFrame({"month": monthly.index.to_timestamp().strftime("%Y-%m"),
                       "articles": monthly.values})

base = alt.Chart(counts).encode(
    x=alt.X("month:T", title=None, axis=alt.Axis(format="%Y", tickCount=6)),
    y=alt.Y("articles:Q", title="Articles indexed", axis=alt.Axis(tickCount=4)),
)
area = base.mark_area(line={"color": "#0063AF"}, color="#179FDB", opacity=0.25).encode(
    tooltip=[alt.Tooltip("month:T", format="%b %Y", title="Month"),
             alt.Tooltip("articles:Q", format=",", title="Articles")]
)
label = (
    alt.Chart(counts.tail(1))
    .mark_text(align="right", dx=-4, dy=-10, fontSize=12, fontWeight="bold", color="#0063AF")
    .encode(x="month:T", y="articles:Q", text=alt.Text("articles:Q", format=","))
)
save(area + label, "202502_EcoSearch.json")
