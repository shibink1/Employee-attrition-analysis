# Employee Attrition Analysis

An interactive employee attrition analysis dashboard built with **Python**, **Pandas**, **Plotly**, and **Streamlit**. The app helps explore employee attrition patterns across people-related and workplace factors using interactive charts, filters, and summary metrics.

## Features

- KPI cards for total employees, employees who left, employees who stayed, and attrition rate
- Interactive filters for department, job role, gender, overtime, business travel, and age range
- Attrition distribution and attrition-rate charts
- Analysis by age group, gender, job role, department, and work-related factors
- Pay and tenure comparisons
- Correlation heatmap and top features associated with attrition
- High-risk group exploration with configurable groupings and minimum group size
- Dataset preview, summary statistics, missing-value review, and filtered CSV download

## Tech Stack

- Python
- Pandas
- NumPy
- Plotly Express
- Streamlit

## Project Structure

```text
employee-attrition-analysis/
├── app.py
├── Employee_Attrition_Analysis_6000_Records.csv
├── requirements.txt
└── README.md
```

Keep the CSV in the same folder as `app.py` using the filename shown above. If the file is not present, the app provides a sidebar option to upload a CSV dataset.

## Setup and Run Locally

### 1. Clone the repository

Replace `shibink1` with your GitHub username.

```bash
git clone https://github.com/shibink1/employee-attrition-analysis.git
cd employee-attrition-analysis
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

Create a `requirements.txt` file with:

```text
streamlit
pandas
numpy
plotly
```

Then run:

```bash
pip install -r requirements.txt
```

### 4. Start the dashboard

```bash
streamlit run app.py
```

Streamlit will provide a local URL to open the dashboard in your browser.

## Dataset

The app expects a CSV file named `Employee_Attrition_Analysis_6000_Records.csv` in the same folder as `app.py`. It removes duplicate rows, creates age groups when an `Age` column is available, and encodes the `Attrition` field for analysis.

Ensure the CSV contains an `Attrition` column with `Yes` and `No` values. Other charts appear when their required columns are available.

## Dashboard Sections

1. **Overview** — attrition distribution and attrition rates by department and job role.
2. **People** — attrition by gender and age group, plus age distribution.
3. **Work factors** — attrition rates by overtime, business travel, satisfaction, work-life balance, job level, and training frequency where available.
4. **Pay & tenure** — comparisons involving monthly income, years at company, and distance from home where available.
5. **Correlation** — correlation heatmap and features most associated with the encoded attrition field.
6. **High-risk groups** — compare attrition rates across selected employee categories.
7. **Data** — filtered data preview, summary statistics, and missing-value information.

## Important Note

Correlation indicates association, not causation. This dashboard is intended for exploratory data analysis and should not be used as the sole basis for employee decisions.

## Future Improvements

- Add model-based attrition prediction and model evaluation
- Add automated data validation and clearer handling of missing values
- Deploy the app online with Streamlit Community Cloud

## Author

**Shibin K**
