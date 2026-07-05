📊 Story-Driven Data Analysis
Customer Sales and Business Insights Dashboard
� � � � � �
An end-to-end Story-Driven Data Analysis project that transforms retail sales data into actionable business insights through data storytelling, visualization, and predictive analytics.
📖 Table of Contents
Project Overview
Business Problem
Dataset Information
Technologies Used
Project Architecture
Key Insights
Dashboard
Installation
How to Run
Results
Future Improvements
Author
🧭 Project Overview
This project analyzes four years of retail transactions from a fictional "Superstore" chain and turns raw rows of orders into a coherent business narrative — not just charts. It follows a six-chapter storytelling structure (Business Problem → Data Exploration → Key Findings → Hidden Insights → Recommendations → Future Forecast), backed by a fully reproducible Python pipeline, an interactive Streamlit dashboard, and Power BI-ready processed data.
Everything in this repository — the cleaning pipeline, the charts, the PDF report, the slide deck, and the dashboard — is generated from the same underlying src/ modules, so numbers always agree across every artifact.
❓ Business Problem
"We are generating strong revenue, but our profit margin feels thin. Where exactly is money being made — and where is it quietly being lost — and what should we do about it?"
Leadership needs a clear, evidence-based answer covering regional performance, product profitability, customer value, and the impact of discounting — plus a concrete action plan, not just a data dump.
🗃 Dataset Information
This project is built around the schema of the well-known Superstore Sales Dataset (order-level U.S. retail transactions — Sales, Profit, Discount, Region, Category, Segment, etc.), commonly distributed on Kaggle.
Note on the data file: Kaggle's terms of use don't permit redistributing their raw CSV inside third-party repositories. So this repo ships with data/raw/superstore.csv, a synthetic dataset generated to match the exact schema, value ranges, and statistical patterns of the real Superstore data (seasonality, regional mix, discount-driven losses, category mix, injected duplicates/missing values for the cleaning step to handle) — so the project runs end-to-end immediately after cloning. To use the real data: download it from Kaggle and drop it in at data/raw/superstore.csv with the same column names; every notebook, script, and the dashboard will work unchanged.
Column
Description
Order ID, Order Date, Ship Date, Ship Mode
Order & fulfillment details
Customer ID, Customer Name, Segment
Customer information
Country, City, State, Postal Code, Region
Geography
Product ID, Category, Sub-Category, Product Name
Product hierarchy
Sales, Quantity, Discount, Profit
Transaction metrics
🛠 Technologies Used
Python — core analysis language
Pandas / NumPy — data cleaning, transformation, feature engineering
Matplotlib / Seaborn — static statistical charts
Plotly — interactive charts
Jupyter Notebook — exploratory & narrative analysis
Streamlit — interactive dashboard (Power BI-equivalent, code-first)
statsmodels / scikit-learn — sales forecasting
ReportLab / python-pptx — automated PDF report & slide deck generation
Git & GitHub — version control
🏗 Project Architecture
Story-Driven-Data-Analysis/
│
├── data/
│   ├── raw/
│   │   └── superstore.csv              # Raw Superstore-schema dataset
│   └── processed/
│       └── cleaned_data.csv            # Cleaned, feature-engineered dataset
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb          # Cleaning walkthrough
│   ├── 02_exploratory_data_analysis.ipynb
│   ├── 03_business_insights.ipynb      # The 6-chapter story
│   └── 04_sales_forecasting.ipynb
│
├── src/
│   ├── data_cleaning.py                # Cleaning pipeline
│   ├── eda.py                          # Reusable aggregation functions
│   ├── visualization.py                # Matplotlib/Seaborn + Plotly charts
│   ├── forecasting.py                  # Holt-Winters forecasting
│   └── utils.py                        # Shared paths, logging, KPIs
│
├── dashboard/
│   ├── app.py                          # Streamlit interactive dashboard
│   └── dashboard_screenshots/
│
├── reports/
│   ├── business_insights.pdf           # Full 6-chapter report
│   └── presentation.pptx               # Stakeholder-ready slide deck
│
├── images/
│   ├── sales_trend.png
│   ├── profit_analysis.png
│   └── dashboard_preview.png
│
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
└── main.py                             # End-to-end pipeline entry point
💡 Key Insights
(from the generated dataset — see reports/business_insights.pdf for the full narrative)
💰 $31.6M in total sales generated only $1.35M in profit — a thin 4.27% overall margin, confirming leadership's concern.
📉 Discounts above ~20% flip average profit-per-order negative; above 40%, average profit per order falls to -$740.
🪑 The entire Furniture category is a margin drag — Chairs and Tables post net losses despite strong sales volume.
🗺️ West and East lead in raw revenue, but Central converts sales to profit most efficiently — a useful internal benchmark.
👥 A concentrated base of High Value customers drives a disproportionate share of profit (a classic 80/20 pattern).
📦 Shipping speed is not the margin risk it's assumed to be — Same-Day and First Class orders are not meaningfully less profitable than Standard.
📅 Sales are strongly seasonal, peaking every Q4, which directly informs inventory and staffing recommendations.
See Chapter 5 in notebooks/03_business_insights.ipynb (or the PDF / PPTX in reports/) for the full list of 10 prioritized recommendations.
📊 Dashboard
An interactive Streamlit dashboard (dashboard/app.py) mirrors every analysis in this repo with live filters for date range, region, category, and segment, across five tabs: Sales Trend, Profit Analysis, Customers, Regional, and Forecast.
streamlit run dashboard/app.py
A static preview of the same KPIs is available at images/dashboard_preview.png. Add your own screenshots to dashboard/dashboard_screenshots/ once you run it locally (see the README in that folder for instructions).
Prefer Power BI? The cleaned dataset at data/processed/cleaned_data.csv is plug-and-play — import it into Power BI Desktop and rebuild the same visuals using native Power BI charts if you'd rather present via .pbix.
⚙️ Installation
# 1. Clone the repository
git clone https://github.com/<your-username>/Story-Driven-Data-Analysis.git
cd Story-Driven-Data-Analysis

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
▶️ How to Run
Run the full pipeline (cleaning → analysis → charts → forecast):
python main.py
Explore the story interactively in Jupyter:
jupyter notebook notebooks/
Launch the interactive dashboard:
streamlit run dashboard/app.py
Regenerate the cleaned dataset only:
python src/data_cleaning.py
📈 Results
Running python main.py end-to-end on the bundled dataset produces:
Metric
Value
Total Sales
$31,627,536.71
Total Profit
$1,350,996.33
Overall Profit Margin
4.27%
Total Orders
8,623
Total Customers
799
Average Order Value
$3,667.81
6-Month Sales Forecast
Generated via Holt-Winters Exponential Smoothing
All static charts are written to images/, the full narrative report to reports/business_insights.pdf, and the stakeholder deck to reports/presentation.pptx.
🚀 Future Improvements
Add a live database/API connector (e.g., PostgreSQL, Snowflake) instead of a static CSV for real-time refreshes.
Extend forecasting with Prophet or an ML-based model (XGBoost / LightGBM regression) and backtest against multiple horizons.
Add automated anomaly detection to flag margin drops as they happen.
Deploy the Streamlit dashboard (Streamlit Community Cloud / Docker) for a shareable public link.
Publish a native Power BI .pbix file alongside the Streamlit app.
Add unit tests (pytest) for src/ modules and wire up GitHub Actions CI.
👤 Author
Story-Driven Data Analysis Project Built as an end-to-end portfolio project demonstrating data cleaning, EDA, storytelling, visualization, forecasting, and dashboarding with Python.
Feel free to fork, adapt, and extend this project — contributions and issues are welcome!
�
If this project helped you, consider giving it a ⭐ on GitHub! 
