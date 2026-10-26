"""
Download the ONS house building workbook and reshape table 3a into a long CSV for Vega-Lite.

This does the same job as the Excel steps in the walkthrough:
  1. open table 3a (UK, calendar years)
  2. keep Period and the three 'Completed' columns
  3. tidy the column names
  4. stack the sectors into long format: Period, Sector, Completed

Run from this folder:  python prepare_data.py
"""

import io

import pandas as pd
import requests

URL = (
    "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/housing/datasets/"
    "ukhousebuildingpermanentdwellingsstartedandcompleted/current/indicatorsofukhousebuilding.xlsx"
)
OUTPUT = "ons_housebuilding_uk_long.csv"

# 1. Download the workbook. ONS blocks requests without a browser-like user agent.
response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
response.raise_for_status()

# Table 3a has five rows of notes above the column headings
wide = pd.read_excel(io.BytesIO(response.content), sheet_name="3a", skiprows=5)

# 2-3. Keep Period and the completions by sector, with shorter names
wide = wide[["Period", "Completed - Private Enterprise",
             "Completed - Housing Associations", "Completed - Local Authorities"]]
wide.columns = ["Period", "Private enterprise", "Housing associations", "Local authorities"]

# 4. Stack the three sector columns into one 'Sector' column
long = wide.melt(id_vars="Period", var_name="Sector", value_name="Completed")

# ONS marks missing years with '[x2]'. Turn these into blanks so Vega-Lite skips them.
long["Completed"] = pd.to_numeric(long["Completed"], errors="coerce").astype("Int64")

long.to_csv(OUTPUT, index=False)
print(f"Saved {len(long)} rows ({long['Period'].min()} to {long['Period'].max()}) to {OUTPUT}")
