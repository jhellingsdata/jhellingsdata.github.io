# Step 6. Turn the chart into a layered spec and add the dashed target line and its label.
import altair as alt

url = "https://raw.githubusercontent.com/jhellingsdata/jhellingsdata.github.io/main/Data/ONS_UK_housebuilding_long.csv"

sectors = ["Private enterprise", "Housing associations", "Local authorities"]
colours = ["#0f5499", "#70dce6", "#ef6590"]

# Layer: stacked bars
bars = (
    alt.Chart(url)
    .transform_filter("utcyear(datum.Period) >= 1950")
    .transform_calculate(SectorOrder=f"indexof({sectors}, datum.Sector)")
    .mark_bar(width={"band": 0.85}, binSpacing=0, opacity=0.9, fillOpacity=0.9)
    .encode(
        x=alt.X(
            "utcyear(Period):T",
            bandPosition=0,
            title=None,
            axis=alt.Axis(
                grid=False,
                tickCount={"interval": "year", "step": 10},
                domainColor="#999189",
                tickColor="#999189",
            ),
        ),
        y=alt.Y(
            "Completed:Q",
            title=None,
            scale=alt.Scale(domain=[0, 440000], nice=False),
            axis=alt.Axis(
                gridColor="#ccc1b7",
                domain=False,
                ticks=False,
                labelPadding=5,
                tickCount=5,
                labelExpr="datum.value / 1000",
            ),
        ),
        color=alt.Color(
            "Sector:N",
            scale=alt.Scale(domain=sectors, range=colours),
            legend=alt.Legend(
                orient="top",
                direction="vertical",
                title=None,
                symbolType="M-1.5,-1H1.5V1H-1.5Z",
                symbolSize=120,
                labelFontSize=16,
                labelColor="#33302e",
            ),
        ),
        order="SectorOrder:Q",
    )
)

# Layer: dashed target line with a two-line label
target = alt.Chart(alt.Data(values=[{"target": 300000}])).encode(y="target:Q")
rule = target.mark_rule(strokeDash=[6, 4], strokeWidth=2.2, color="#33302e")
label = target.mark_text(
    text=["Labour", "target"],
    x=alt.expr("width / 2"),
    dy=-30,
    lineHeight=17,
    fontSize=14.4,
    fontWeight=600,
    color="#33302e",
)

chart = (
    alt.layer(bars, rule, label)
    .properties(width=649, height=389, background="#fff1e5")
    .configure_view(stroke="transparent")
    .configure_axis(labelColor="#4d4845")
)

chart
