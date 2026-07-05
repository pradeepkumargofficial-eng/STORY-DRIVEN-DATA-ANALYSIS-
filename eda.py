"""
eda.py
------
Reusable exploratory-data-analysis functions: sales trends, profit analysis,
customer segmentation, regional performance, and category analysis. Each
function returns a tidy DataFrame so it can feed both notebooks and the
Streamlit dashboard without duplicating logic.
"""

import pandas as pd

from src.utils import get_logger

logger = get_logger(__name__)


def monthly_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate sales and profit by calendar month across all years."""
    out = (
        df.groupby("Order YearMonth")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .reset_index()
        .sort_values("Order YearMonth")
    )
    return out


def yearly_growth(df: pd.DataFrame) -> pd.DataFrame:
    """Year-over-year sales and profit growth rates."""
    out = df.groupby("Order Year").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
    out["Sales Growth %"] = out["Sales"].pct_change() * 100
    out["Profit Growth %"] = out["Profit"].pct_change() * 100
    return out


def profit_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Profit, sales, and margin rolled up by Category and Sub-Category."""
    out = (
        df.groupby(["Category", "Sub-Category"])
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"))
        .reset_index()
    )
    out["Profit Margin %"] = (out["Profit"] / out["Sales"] * 100).round(2)
    return out.sort_values("Profit", ascending=False)


def discount_vs_profit(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate profit outcomes by discount band to quantify margin erosion."""
    out = (
        df.groupby("Discount Band", observed=True)
        .agg(
            Avg_Discount=("Discount", "mean"),
            Avg_Profit=("Profit", "mean"),
            Total_Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
        )
        .reset_index()
    )
    return out


def customer_segmentation(df: pd.DataFrame) -> pd.DataFrame:
    """RFM-style rollup per customer: recency, frequency, monetary value, tier."""
    snapshot_date = df["Order Date"].max() + pd.Timedelta(days=1)
    out = (
        df.groupby(["Customer ID", "Customer Name", "Segment", "Customer Value Tier"], observed=True)
        .agg(
            Recency_Days=("Order Date", lambda s: (snapshot_date - s.max()).days),
            Frequency=("Order ID", "nunique"),
            Monetary=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
        )
        .reset_index()
        .sort_values("Monetary", ascending=False)
    )
    return out


def segment_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Sales/profit/order performance rolled up by customer Segment."""
    out = (
        df.groupby("Segment")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Customers=("Customer ID", "nunique"),
        )
        .reset_index()
    )
    out["Avg Order Value"] = (out["Sales"] / out["Orders"]).round(2)
    return out.sort_values("Sales", ascending=False)


def regional_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Sales, profit, and margin rolled up by Region and State."""
    region_out = (
        df.groupby("Region")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .reset_index()
    )
    region_out["Profit Margin %"] = (region_out["Profit"] / region_out["Sales"] * 100).round(2)
    return region_out.sort_values("Sales", ascending=False)


def state_performance(df: pd.DataFrame) -> pd.DataFrame:
    """State-level rollup, useful for choropleth-style maps in Power BI / Plotly."""
    out = (
        df.groupby("State")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .reset_index()
        .sort_values("Sales", ascending=False)
    )
    return out


def top_products(df: pd.DataFrame, n: int = 10, by: str = "Sales") -> pd.DataFrame:
    """Top-N products ranked by Sales or Profit."""
    out = (
        df.groupby("Product Name")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"))
        .reset_index()
        .sort_values(by, ascending=False)
        .head(n)
    )
    return out


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Correlation matrix across the core numeric fields."""
    numeric_cols = ["Sales", "Quantity", "Discount", "Profit", "Profit Margin", "Shipping Days"]
    numeric_cols = [c for c in numeric_cols if c in df.columns]
    return df[numeric_cols].corr()
