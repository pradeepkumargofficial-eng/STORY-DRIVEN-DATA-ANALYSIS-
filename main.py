"""
main.py
-------
End-to-end pipeline entry point for the Story-Driven Data Analysis project.

Running this script after `pip install -r requirements.txt` will:
    1. Clean the raw Superstore dataset -> data/processed/cleaned_data.csv
    2. Run the core EDA aggregations (sales, profit, customers, regions)
    3. Generate all static chart images -> images/*.png
    4. Run a short-term sales forecast and print a summary
    5. Print a concise, story-style console summary of key findings

Usage:
    python main.py
"""

import sys
import time

from src.utils import (
    RAW_DATA_PATH,
    PROCESSED_DATA_PATH,
    get_logger,
    kpi_summary,
    currency,
    pct,
)
from src.data_cleaning import run_pipeline
from src import eda, visualization as viz, forecasting as fc

logger = get_logger("main")


def print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def main() -> None:
    start = time.time()

    print_header("STORY-DRIVEN DATA ANALYSIS — FULL PIPELINE")
    logger.info("Step 1/5: Cleaning raw data...")
    df = run_pipeline(RAW_DATA_PATH, PROCESSED_DATA_PATH)

    print_header("STEP 2/5 — HEADLINE KPIs")
    kpis = kpi_summary(df)
    print(f"Total Sales        : {currency(kpis['total_sales'])}")
    print(f"Total Profit       : {currency(kpis['total_profit'])}")
    print(f"Overall Margin     : {pct(kpis['profit_margin'])}")
    print(f"Total Orders       : {kpis['total_orders']:,}")
    print(f"Total Customers    : {kpis['total_customers']:,}")
    print(f"Avg. Order Value   : {currency(kpis['avg_order_value'])}")

    print_header("STEP 3/5 — CORE ANALYSIS")
    monthly = eda.monthly_sales_trend(df)
    category_perf = eda.profit_by_category(df)
    region_perf = eda.regional_performance(df)
    segment_perf = eda.segment_performance(df)
    discount_effect = eda.discount_vs_profit(df)

    print("\nTop 5 most profitable Sub-Categories:")
    print(category_perf.sort_values("Profit", ascending=False).head(5).to_string(index=False))

    print("\nBottom 5 least profitable Sub-Categories:")
    print(category_perf.sort_values("Profit").head(5).to_string(index=False))

    print("\nRegional performance:")
    print(region_perf.to_string(index=False))

    print("\nSegment performance:")
    print(segment_perf.to_string(index=False))

    print("\nProfit by discount band:")
    print(discount_effect.to_string(index=False))

    print_header("STEP 4/5 — GENERATING VISUALIZATIONS")
    logger.info("Rendering static charts to images/ ...")
    viz.plot_sales_trend(monthly)
    viz.plot_profit_by_category(category_perf)
    viz.plot_region_heatmap(df)
    viz.plot_discount_scatter(df)
    viz.plot_correlation_matrix(eda.correlation_matrix(df))
    viz.plot_dashboard_preview(df)
    logger.info("All charts saved to images/")

    print_header("STEP 5/5 — SALES FORECAST (NEXT 6 MONTHS)")
    result = fc.forecast_sales(df, periods=6)
    accuracy = fc.forecast_accuracy(result)
    future = result[result["is_forecast"]][["ds", "forecast"]]
    for _, row in future.iterrows():
        print(f"  {row['ds'].strftime('%Y-%m')}: {currency(row['forecast'])}")
    print(f"\nIn-sample accuracy -> MAE: {currency(accuracy['MAE'])} | MAPE: {accuracy['MAPE_%']}%")

    print_header("STORY SUMMARY")
    print(
        "Revenue is healthy but margin is thin, driven by a small number of\n"
        "over-discounted sub-categories and region/category combinations.\n"
        "A concentrated base of high-value customers drives outsized profit.\n"
        "Sales are seasonal, peaking in Q4. See notebooks/03_business_insights.ipynb\n"
        "for the full six-chapter narrative and 10 prioritized recommendations,\n"
        "or run `streamlit run dashboard/app.py` for the interactive dashboard."
    )

    elapsed = time.time() - start
    logger.info(f"Pipeline completed in {elapsed:.1f}s")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover
        logger.error(f"Pipeline failed: {exc}")
        sys.exit(1)
