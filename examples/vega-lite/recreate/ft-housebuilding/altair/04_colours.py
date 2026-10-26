# Step 4. Use the FT's paper background, text greys and the exact bar colours found with the browser inspector.
import altair as alt

url = "https://raw.githubusercontent.com/jhellingsdata/jhellingsdata.github.io/main/Data/ONS_UK_housebuilding_long.csv"

sectors = ["Private enterprise", "Housing associations", "Local authorities"]
colours = ["#0f5499", "#70dce6", "#ef6590"]

chart = (
    alt.Chart(url)
    .transform_filter("utcyear(datum.Period) >= 1950")
    .mark_bar(width={"band": 0.85}, binSpacing=0, opacity=0.9, fillOpacity=0.9)
    .encode(
        x=alt.X("utcyear(Period):T")
        .bandPosition(0)
        .title(None)
        .axis(
            grid=False,
            tickCount={"interval": "year", "step": 10},
            domainColor="#999189",
            tickColor="#999189",
        ),
        y=alt.Y("Completed:Q")
        .title(None)
        .scale(domain=[0, 440000], nice=False)
        .axis(
            gridColor="#ccc1b7",
            domain=False,
            ticks=False,
            labelPadding=5,
            tickCount=5,
            labelExpr="datum.value / 1000",
        ),
        color=alt.Color("Sector:N").scale(domain=sectors, range=colours),
    )
    .properties(width=649, height=389, background="#fff1e5")
    .configure_view(stroke="transparent")
    .configure_axis(labelColor="#4d4845")
)

chart
