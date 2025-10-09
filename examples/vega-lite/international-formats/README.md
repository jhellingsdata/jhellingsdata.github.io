# Working with International Number Formats

## Overview

When working with data visualisations across different regional settings, you may encounter issues with how numbers and CSV files are formatted. This guide explains common problems and solutions. 

## Understanding the problem
### The two main issues

**1. Number formatting (decimals and thousands separators)**
- **US/UK format**: `1,234.56` (comma for thousands, period for decimal)
- **European (& others) format**: `1.234,56` (period for thousands, comma for decimal)

Most data tools, including Vega-Lite, expect the US/UK format by default.


**2. CSV delimiters**

CSV stands for **C**omma **S**eparated **V**alues. However, in regions where commas are used as decimal separators, Excel and other programs will save CSV files using a different delimiter (usually a semicolon `;`) to avoid confusion.

### What Vega-Lite expects

For data to work correctly in Vega-Lite, it should look like this:

```csv
date,value
1971,42.5
1972,43.7
1973,45.8
```

**Key requirements:**
- Columns separated by commas (`,`)
- Decimal points represented by periods (`.`)
- No thousands separators in the data itself

---
## Common Issues and symptoms

### Issue 1: CSV opens with all data in one column

**What it looks like in Excel:** Instead of seeing data spread across columns, everything appears in a single column with visible commas or semicolons:

```
date,value
1971,42.5
1972,43.7
```

**Why this happens:** Your Excel is configured for a different delimiter (expecting `;`) but the file uses commas (`,`).


### Issue 2: Saved CSV uses semicolons instead of commas

**What it looks like when you open the saved file in a text editor:**

```csv
date;value
1971;42.5
1972;43.7
```

**Why this happens:** When Excel's regional settings use commas as decimal separators, it automatically switches to semicolons as the CSV delimiter to prevent conflicts.


### Issue 3: Vega-Lite chart doesn't display data

**Symptoms:**
- Chart appears blank or shows no data points
- Console errors about parsing failures
- Data preview in Vega Editor shows empty or incorrectly parsed values

**Why this happens:** Either the delimiter is wrong (semicolons instead of commas) or the decimal separator is wrong (commas instead of periods), preventing Vega-Lite from reading the data correctly.

---

## Solutions

### Solution 1: Fix within Vega-Lite

If your data file already exists with non-standard formatting, you can handle it directly in your Vega-Lite specification.

#### A. Handling custom delimiters (e.g., semicolons)

If your CSV uses semicolons instead of commas, modify the `data` object:

**Before:**
```json
"data": {
  "url": "https://raw.githubusercontent.com/username/repo/main/data.csv"
}
```

**After:**
```json
"data": {
  "url": "https://raw.githubusercontent.com/username/repo/main/data.csv",
  "format": {"type": "dsv", "delimiter": ";"}
}
```

**Explanation:**
- `"type": "dsv"` tells Vega-Lite to expect a delimited text file with a custom delimiter
- `"delimiter": ";"` specifies that semicolons separate the columns
- DSV stands for **D**elimiter **S**eparated **V**alues (the general version of CSV)

> See the [Vega-Lite data documentation](https://vega.github.io/vega-lite/docs/data.html#csv) for more details.

#### B. Handling comma decimal separators

If your numerical data uses commas as decimal separators (e.g., `42,5` instead of `42.5`), Vega-Lite won't parse it as quantitative data. You need to add a transformation to replace commas with periods:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "data": {
    "url": "https://raw.githubusercontent.com/username/repo/main/data.csv",
    "format": {"type": "dsv", "delimiter": ";"}
  },
  "transform": [
    {"calculate": "replace(datum.value, ',', '.')", "as": "value_clean"}
  ],
  "mark": "line",
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "value_clean", "type": "quantitative"}
  }
}
```

**Key points:**
- The `transform` property is an array that can contain multiple transformation objects
- `calculate` creates a new field (i.e. column) using an expression
- `replace(datum.value, ',', '.')` finds commas in the `value` field and replaces them with periods
- `"as": "value_clean"` names the new cleaned field (can choose any name here)
- Use `datum.columnname` to reference columns in expressions
- If your column name has spaces, use brackets: `datum['column name']`
- Remember to update your encoding to use the new `value_clean` field instead of `value`

> See the [transform documentation](https://vega.github.io/vega-lite/docs/transform.html) and [expression functions](https://vega.github.io/vega/docs/expressions/).


---

### Solution 2: Fix CSV file opening in excel

If you've downloaded a CSV that appears all in one column when opened in Excel, you can split it properly using the **Text to Columns** feature.

**Steps:**
1. Open the problematic CSV file in Excel
2. Select the column containing all the data (usually column A)
3. Go to the **Data** tab in the ribbon
4. Click **Text to Columns**
5. In the wizard:
   - Keep **Delimited** selected, click **Next >**
   - Uncheck any pre-selected delimiters
   - Check the delimiter your data uses (usually **Comma** `,` or **Semicolon** `;`)
   - Click **Next >**, then **Finish**

Your data should now be properly separated into columns.

**Alternative: import method**

For more control, import the CSV rather than opening it directly:
1. Open a blank Excel workbook
2. Go to **File** → **Import**
3. Select **CSV file** and locate your file
4. Follow the import wizard to specify the correct delimiter
5. Click **Finish**

This method gives you a preview before importing and allows you to specify all formatting options upfront.

---

### Solution 3: Change Excel settings (recommended for ongoing work)

To avoid these issues consistently, configure Excel to use standard number formats regardless of your system settings.

#### On Mac
1. Open **Excel**
2. Go to **Excel** → **Preferences** (or **Settings** in some versions)
3. Click **Edit** (or **Authoring**)
4. **Uncheck** "Use system separators"
5. Set **Decimal separator** to `.` (period)
6. Set **Thousands separator** to `,` (comma)

#### On Windows ([official guide](https://support.microsoft.com/en-us/office/change-the-character-used-to-separate-thousands-or-decimals-c093b545-71cb-4903-b205-aebb9837bd1e))
1. Go to **File** → **Options** → **Advanced**
2. Scroll to **Editing options**
3. **Uncheck** "Use system separators"
4. Set **Decimal separator** to `.` (period)
5. Set **Thousands separator** to `,` (comma)


After making these changes, Excel will save CSVs with commas as delimiters and periods as decimals, regardless of your system's regional settings.

---

### Solution 4: Change system settings (system-wide fix)

For a system-wide solution that affects all applications, you can change your operating system's number format settings.

#### On Mac
1. Open **System Settings** (or **System Preferences**)
2. Go to **General** → **Language & Region**
3. Under **Number format**, select or customise to `1,234,567.89`

#### On Windows
1. Open **Control Panel** → **Region**
2. Click **Additional settings**
3. Set **Decimal symbol** to `.` (period)
4. Set **Digit grouping symbol** to `,` (comma)
5. Click **OK** on all dialogs

**Note:** This changes the format system-wide, which may affect other applications and how numbers appear in your operating system.

---



## Displaying Numbers in Your Regional Format

After successfully getting your data into Vega-Lite (using periods for decimals), you may want to display the numbers in your chart using your regional format preferences.

You can do this by adding a `locale` configuration to your Vega-Lite specification:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "config": {
    "locale": {
      "number": {
        "decimal": ",",
        "thousands": ".",
        "grouping": [3],
        "currency": ["", " €"]
      }
    }
  },
  "data": {"url": "..."},
  "mark": "line",
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "value", "type": "quantitative"}
  }
}
```

**Explanation:**
- `"decimal": ","` displays decimals with commas (e.g., `3,14`)
- `"thousands": "."` displays thousands with periods (e.g., `1.234`)
- `"grouping": [3]` groups digits in sets of three
- `"currency": [""," €"]` sets currency symbols (optional). Set the symbol prefix / suffix for currency values (this only applies when we set a currency display format, with "format": "$").

You can also customise date and time formats by adding a `"time"` property within the `locale` object.
>  See the [Vega locale documentation](https://vega.github.io/vega/docs/api/locale/) and [config usage](https://vega.github.io/vega/docs/config/#usage).

**Important:** This only affects how numbers are *displayed* in the chart. The underlying data must still use standard formatting (periods for decimals) for Vega-Lite to parse it correctly.

---

## Quick Reference

| Issue                      | Quick Fix                                                                             |
| -------------------------- | ------------------------------------------------------------------------------------- |
| Semicolon delimiters       | Add `"format": {"type": "dsv", "delimiter": ";"}` to data object                      |
| Comma decimals             | Add transform: `{"calculate": "replace(datum.value, ',', '.')", "as": "value_clean"}` |
| CSV opens in one column    | Use Excel's **Text to Columns** feature                                               |
| Want to change permanently | Override Excel's separator settings or change in system-wide systems                  |
| Want regional display      | Add `locale` to `config` object in Vega-Lite chart                                    |


Overview: Most international formatting issues can be resolved either by preprocessing your data or by adding a few lines to your Vega-Lite specification. Choose the method that works best for your workflow.