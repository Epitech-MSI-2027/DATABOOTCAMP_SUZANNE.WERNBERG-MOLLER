# Pharmaceutical Sales Analysis with Streamlit

This project lets you **clean and aggregate pharmaceutical sales data** and then **analyze it interactively** using **Streamlit**.

## 1. Prerequisites

* Install **Python** (version 3.9 or higher)
* Use a terminal (or PowerShell on Windows)

Check your Python version:

```bash
python --version
```

## 2. Installation

Clone or download the project:

```bash
git clone https://example.com/my-project.git
cd my-project
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## 3. Data preparation

Before launching the app, raw sales data must be cleaned and aggregated using `datacleaner.py`.

### 3.1 Required input files

Place the following files in the project directory:

* `Pharma_Ventes_Weekly.csv`
* `Pharma_Ventes_Daily.csv`
* `Pharma_Ventes_Hourly.csv`
* `Pharma_Ventes_Monthly.csv`

### 3.2 Run the data cleaning script

Execute:

```bash
python3 datacleaner.py
```

The script will:

* Clean and reorganize the data
* Aggregate temporal datasets
* Generate the following cleaned files:

  * `clean_hourly_full.csv`
  * `clean_daily_full.csv`
  * `clean_weekly_full.csv`
  * `clean_monthly_full.csv`
  * `pharma_consolidated_full.csv`  ← this one is used by the Streamlit app

## 4. Launching the Streamlit application

Once the cleaned files are generated, run:

```bash
streamlit run app.py
```

The app will open automatically in your browser at:

```
http://localhost:8501
```

## 5. How to use

* The interface allows you to filter by products, time period, and temporal granularity.
* The visualizations include:

  * Line chart (evolution over time)
  * Stacked area chart (product contribution)
  * Bar chart (top and bottom products)
  * Heatmap (hour × day to detect peak activity)
* KPI cards at the top show total quantity, daily average, top product, and number of time points.

---

✅ **Tip**: if you update the raw CSV files, just re-run

```bash
python3 datacleaner.py
```

and refresh the app to see the updated data.
