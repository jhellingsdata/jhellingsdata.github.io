# Step 9. Finishing touches: thin gaps between stacked segments and a tooltip.
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
    .mark_bar(
        width={"band": 0.95},
        binSpacing=0,
        opacity=0.9,
        fillOpacity=0.9,
        stroke="#fff1e5",
        strokeWidth=1,
    )
    .encode(
        x=alt.X(
            "utcyear(Period):T",
            bandPosition=0,
            title="Source: ONS • Covid affected data collection between 2020 and 2022",
            axis=alt.Axis(
                grid=False,
                tickCount={"interval": "year", "step": 10},
                domainColor="#999189",
                tickColor="#999189",
                titleAnchor="start",
                titleAlign="left",
                titleX=-29,
                titlePadding=16,
                titleFontSize=13,
                titleFontWeight="normal",
                titleColor="#4d4845",
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
                orient="none",
                legendX=-29,
                legendY=-75,
                rowPadding=0,
                direction="vertical",
                title=None,
                symbolType="M-1.5,-1H1.5V1H-1.5Z",
                symbolSize=120,
                labelFontSize=16,
                labelColor="#33302e",
            ),
        ),
        order="SectorOrder:Q",
        tooltip=[
            alt.Tooltip("utcyear(Period):T", title="Year"),
            alt.Tooltip("Sector:N"),
            alt.Tooltip("Completed:Q", format=","),
        ],
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
    alt.layer(gap, bars, rule, label)
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
            subtitlePadding=6,
        ),
    )
    .configure(font="Hanken Grotesk, Arial, sans-serif")
    .configure_view(stroke="transparent")
    .configure_axis(labelColor="#4d4845", labelFontSize=14.4)
)

chart

# Save the spec to embed on your own site with vegaEmbed
# chart.save("ft_housebuilding.json")
