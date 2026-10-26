# Step 3. Match the FT's plot size, start in 1950, centre one bar on each year and strip back the axes.
import altair as alt

url = "https://raw.githubusercontent.com/jhellingsdata/jhellingsdata.github.io/main/Data/ONS_UK_housebuilding_long.csv"

chart = (
    alt.Chart(url)
    .transform_filter("utcyear(datum.Period) >= 1950")
    .mark_bar(width={"band": 0.85}, binSpacing=0)
    .encode(
        x=alt.X("utcyear(Period):T")
        .bandPosition(0)
        .title(None)
        .axis(
            grid=False,
            tickCount={"interval": "year", "step": 10},
            domainColor="#999189",
            tickColor="#999189",
            tickSize=7,
        ),
        y=alt.Y("Completed:Q")
        .title(None)
        .scale(domain=[0, 440000], nice=False)
        .axis(
            gridColor="#ccc1b7",
            domain=False,
            ticks=False,
            labelPadding=7,
            tickCount=5,
            labelExpr="datum.value / 1000",
        ),
        color="Sector:N",
    )
    .properties(width=649, height=389)
    .configure_view(stroke="transparent")
)

chart
