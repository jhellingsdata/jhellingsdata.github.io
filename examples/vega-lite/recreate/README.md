# Recreating charts in Vega-Lite

Step-by-step rebuilds of charts from news organisations, used as teaching material. Each recreation starts from a default Vega-Lite chart and adds one idea per step, with matching Altair code. The walkthroughs are published at [hellin.gs/tutorials](https://hellin.gs/tutorials/).

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

## Planned walkthroughs

Targets are in [`candidates/`](candidates/). Listed roughly from simplest to hardest, with the main new idea each one teaches.

| Target | Level | Techniques |
|---|---|---|
| [FT: Alphabet's free cash flow](candidates/ft-cashflow-dark.png) | First chart (simpler than housebuilding) | One bar series on a quarterly time axis, a negative bar, a dark theme set once in `config` |
| [FT: teacher recruitment against target](candidates/ft-school-teachers.png) | Beginner | Bars above and below zero coloured by sign with a `condition`, value labels inside bars, a heavier zero line, an "Above target" annotation |
| [Centre for British Progress: transport spending](candidates/cbp-transport-spending.png) | Beginner | Horizontal bars sorted by value, one country and the average highlighted, labels inside bars, grey "track" bars behind, a long footnote |
| [The Economist: European stock markets](candidates/economist-stock-markets.png) | Intermediate | Rebasing to 100 with `joinaggregate` and `calculate`, multi-line chart, direct line labels instead of a legend, one series in bold |
| [The Economist: rat sightings](candidates/economist-rat-sightings.png) | Intermediate | Two panels with `hconcat`, a moving average with `window`, a log scale, a highlighted line among muted ones |
