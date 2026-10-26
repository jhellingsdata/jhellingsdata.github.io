# Step 2. Treat Period as a date and split each bar by sector with the color channel.
import altair as alt

url = "https://raw.githubusercontent.com/jhellingsdata/jhellingsdata.github.io/main/Data/ONS_UK_housebuilding_long.csv"

chart = alt.Chart(url).mark_bar().encode(
    x="Period:T",
    y="Completed:Q",
    color="Sector:N",
)

chart
