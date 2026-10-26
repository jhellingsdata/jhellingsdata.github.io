# Step 8. Add the title, subtitle and a source note, switch to a Metric-like font and line everything up on the left.
import altair as alt

url = "https://raw.githubusercontent.com/jhellingsdata/jhellingsdata.github.io/main/Data/ONS_UK_housebuilding_long.csv"

sectors = ["Private enterprise", "Housing associations", "Local authorities"]
colours = ["#0f5499", "#70dce6", "#ef6590"]

# Layer: shaded area for the years with no data
gap = (
    alt.Chart(alt.Data(values=[{"start": "2019-07-01", "end": "2022-07-01"}]))
    .mark_rect(color="#ccc1b7", opacity=0.5)
    .encode(x="start:T", x2="end")
)

# Layer: stacked bars
bars = (
    alt.Chart(url)
    .transform_filter("utcyear(datum.Period) >= 1950")
    .transform_calculate(SectorOrder=f"indexof({sectors}, datum.Sector)")
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
        color=alt.Color("Sector:N")
        .scale(domain=sectors, range=colours)
        .legend(
            orient="none",
            legendX=-31,
            legendY=-75,
            rowPadding=0,
            direction="vertical",
            title=None,
            symbolType="M-1.8,-1H1.8V1H-1.8Z",
            symbolSize=120,
            labelFontSize=16,
            labelColor="#33302e",
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

# Layer: source note below the chart. One empty row, so the text is drawn once.
source = alt.Chart(alt.Data(values=[{}])).mark_text(
    text=[
        "Recreated from an FT chart",
        "Source: ONS • Covid affected data collection between 2020 and 2022",
    ],
    x=-31,
    y=alt.expr("height + 40"),
    align="left",
    baseline="top",
    lineHeight=17,
    fontSize=13,
    color="#4d4845",
)

chart = (
    alt.layer(gap, bars, rule, label, source)
    .properties(
        width=649,
        height=389,
        background="#fff1e5",
        padding=16,
        title=alt.Title(
            "The UK has not built 300,000 homes a year since 1977",
            subtitle="Completed dwellings (000)",
            anchor="start",
            offset=16,
            fontSize=21,
            fontWeight="normal",
            color="#33302e",
            subtitleFontSize=16,
            subtitleColor="#4d4845",
            subtitlePadding=8,
        ),
    )
    .configure(font="Hanken Grotesk, Arial, sans-serif")
    .configure_view(stroke="transparent")
    .configure_axis(labelColor="#4d4845", labelFontSize=14.4)
)

chart
