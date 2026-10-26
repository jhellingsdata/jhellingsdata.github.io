# Step 1. The Vega-Lite 'simple bar chart' example, pointed at the ONS housebuilding data.
import altair as alt

url = "https://raw.githubusercontent.com/jhellingsdata/jhellingsdata.github.io/main/Data/ONS_UK_housebuilding_long.csv"

chart = alt.Chart(url).mark_bar().encode(
    x="Period:N",
    y="Completed:Q",
)

chart
