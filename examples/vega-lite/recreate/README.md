# Recreating charts in Vega-Lite

Step-by-step rebuilds of charts from news organisations, used as teaching material. Each recreation starts from a default Vega-Lite chart and adds one idea per step, with matching Altair code. The walkthroughs are published at [hellin.gs/tutorials-home.html](https://hellin.gs/tutorials-home.html).

## Recreations

| Chart | Walkthrough | Files |
|---|---|---|
| FT: UK housebuilding by sector | [tutorials/ft-housebuilding.html](../../../tutorials/ft-housebuilding.html) | [`ft-housebuilding/`](ft-housebuilding/) |

## Folder layout

| Path | Contents |
|---|---|
| `<chart>/specs/` | One Vega-Lite spec per step, numbered in order |
| `<chart>/altair/` | The same steps in Altair. Each script runs on its own (e.g. in Colab) |
| `<chart>/data/` | Scripts to fetch and reshape the source data |
| `<chart>/images/` | The target chart and browser-inspector screenshots used in the walkthrough |
| `candidates/` | Charts we might recreate next |
| `notes/` | Working notes, exported from Notion |

The walkthrough pages live in [`/tutorials`](../../../tutorials/) and share `tutorial.css` and `tutorial.js`. They load the specs and scripts from these folders, so each step's code exists in one place.

## Process

1. Pick a target and save a screenshot to `<chart>/images/target-*.png`.
2. Find the source data and write a script that reshapes it into long format.
3. Use the browser inspector on the original to read sizes, colours and fonts.
4. Build the spec in small steps, saving each as `specs/NN_name.json`.
5. Write the matching Altair script for each step, and check both render the same chart.

## Candidates

| File | Chart |
|---|---|
| `candidates/ft-school-teachers.png` | FT: school teachers |
| `candidates/ft-cashflow-dark.png` | FT: Alphabet's quarterly free cash flow (dark theme, negative bar) |
| `candidates/economist-indexed-line.png` | The Economist: indexed line chart |
| `candidates/economist-stock-markets.png` | The Economist: European stock markets |
| `candidates/cbp-transport-spending.png` | Centre for British Progress (Datawrapper): UK transport spending vs OECD peers, highlighted horizontal bars |
