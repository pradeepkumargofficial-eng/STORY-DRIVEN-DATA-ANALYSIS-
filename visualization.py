"""
visualization.py
-----------------
Chart-generation helpers built on Matplotlib / Seaborn (for static PNG export
into images/) and Plotly (for interactive charts used in the dashboard and
notebooks). Keeping plotting logic here means notebooks stay short and the
Streamlit app can reuse the exact same figures.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # safe for headless / notebook execution
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd

try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:  # plotly is optional at import time (e.g. minimal CI images);
    px = None         # required for the interactive Plotly functions below and
    go = None          # for the Streamlit dashboard. Install via requirements.txt.

from src.utils import IMAGES_DIR, ensure_dir, get_logger

sns.set_theme(style="whitegrid", palette="deep")
logger = get_logger(__name__)

PALETTE = ["#2E5EAA", "#4CA6A8", "#F2A541", "#D9534F", "#5B5F97", "#8AC926"]


def _save(fig, filename: str) -> str:
    ensure_dir(IMAGES_DIR)
    path = IMAGES_DIR / filename
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved chart -> {path}")
    return str(path)


def plot_sales_trend(monthly_df: pd.DataFrame, filename: str = "sales_trend.png") -> str:
    """Line chart of monthly sales & profit trend, saved as a static PNG."""
    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax1.plot(monthly_df["Order YearMonth"], monthly_df["Sales"], color=PALETTE[0], linewidth=2, label="Sales")
    ax1.set_ylabel("Sales ($)", color=PALETTE[0])
    ax1.tick_params(axis="x", rotation=75)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    ax2 = ax1.twinx()
    ax2.plot(monthly_df["Order YearMonth"], monthly_df["Profit"], color=PALETTE[3], linewidth=2, label="Profit")
    ax2.set_ylabel("Profit ($)", color=PALETTE[3])
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    every_nth = max(len(monthly_df) // 18, 1)
    for n, label in enumerate(ax1.xaxis.get_ticklabels()):
        if n % every_nth != 0:
            label.set_visible(False)

    fig.suptitle("Monthly Sales & Profit Trend", fontsize=14, fontweight="bold")
    fig.legend(loc="upper left", bbox_to_anchor=(0.08, 0.9))
    fig.tight_layout()
    return _save(fig, filename)


def plot_profit_by_category(category_df: pd.DataFrame, filename: str = "profit_analysis.png") -> str:
    """Bar chart of profit by Sub-Category, colored by parent Category."""
    fig, ax = plt.subplots(figsize=(11, 6))
    data = category_df.sort_values("Profit")
    colors = data["Category"].map(dict(zip(data["Category"].unique(), PALETTE)))
    ax.barh(data["Sub-Category"], data["Profit"], color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Total Profit ($)")
    ax.set_title("Profit by Sub-Category", fontsize=14, fontweight="bold")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    fig.tight_layout()
    return _save(fig, filename)


def plot_region_heatmap(df: pd.DataFrame, filename: str = "region_category_heatmap.png") -> str:
    """Heatmap of profit margin across Region x Category."""
    pivot = df.pivot_table(index="Region", columns="Category", values="Profit Margin", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(pivot, annot=True, fmt=".1%", cmap="RdYlGn", center=0, ax=ax, cbar_kws={"label": "Avg Profit Margin"})
    ax.set_title("Average Profit Margin: Region x Category", fontsize=13, fontweight="bold")
    fig.tight_layout()
    return _save(fig, filename)


def plot_discount_scatter(df: pd.DataFrame, filename: str = "discount_vs_profit_scatter.png") -> str:
    """Scatter plot of Discount vs Profit to visualize margin erosion."""
    fig, ax = plt.subplots(figsize=(9, 6))
    sample = df.sample(min(2000, len(df)), random_state=1)
    sns.scatterplot(data=sample, x="Discount", y="Profit", hue="Category", alpha=0.6, ax=ax, palette=PALETTE[:3])
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Discount vs Profit", fontsize=14, fontweight="bold")
    fig.tight_layout()
    return _save(fig, filename)


def plot_correlation_matrix(corr: pd.DataFrame, filename: str = "correlation_matrix.png") -> str:
    """Heatmap of the numeric correlation matrix."""
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlation Matrix", fontsize=14, fontweight="bold")
    fig.tight_layout()
    return _save(fig, filename)


def plot_dashboard_preview(df: pd.DataFrame, filename: str = "dashboard_preview.png") -> str:
    """A 2x2 static summary grid used as a stand-in dashboard preview image."""
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    monthly = df.groupby("Order YearMonth")["Sales"].sum()
    axes[0, 0].plot(monthly.index, monthly.values, color=PALETTE[0])
    axes[0, 0].set_title("Monthly Sales")
    axes[0, 0].tick_params(axis="x", rotation=90)
    every_nth = max(len(monthly) // 10, 1)
    for n, label in enumerate(axes[0, 0].xaxis.get_ticklabels()):
        if n % every_nth != 0:
            label.set_visible(False)

    region_sales = df.groupby("Region")["Sales"].sum().sort_values(ascending=False)
    axes[0, 1].bar(region_sales.index, region_sales.values, color=PALETTE[1])
    axes[0, 1].set_title("Sales by Region")

    cat_profit = df.groupby("Category")["Profit"].sum().sort_values()
    axes[1, 0].barh(cat_profit.index, cat_profit.values, color=PALETTE[2])
    axes[1, 0].set_title("Profit by Category")

    seg_sales = df.groupby("Segment")["Sales"].sum()
    axes[1, 1].pie(seg_sales.values, labels=seg_sales.index, autopct="%1.0f%%", colors=PALETTE[3:])
    axes[1, 1].set_title("Sales Share by Segment")

    fig.suptitle("Superstore Business Dashboard - Preview", fontsize=16, fontweight="bold")
    fig.tight_layout()
    return _save(fig, filename)


# ---------------------------------------------------------------------------
# Interactive Plotly figures (used in dashboard/app.py and notebooks)
# ---------------------------------------------------------------------------

def plotly_sales_trend(monthly_df: pd.DataFrame) -> go.Figure:
    fig = px.line(monthly_df, x="Order YearMonth", y=["Sales", "Profit"],
                   title="Monthly Sales & Profit Trend", markers=True)
    fig.update_layout(xaxis_title="Month", yaxis_title="Amount ($)", legend_title="Metric")
    return fig


def plotly_category_treemap(category_df: pd.DataFrame) -> go.Figure:
    fig = px.treemap(category_df, path=["Category", "Sub-Category"], values="Sales",
                      color="Profit Margin %", color_continuous_scale="RdYlGn",
                      title="Sales Composition by Category (colored by margin)")
    return fig


def plotly_region_bar(region_df: pd.DataFrame) -> go.Figure:
    fig = px.bar(region_df, x="Region", y=["Sales", "Profit"], barmode="group",
                 title="Sales & Profit by Region")
    return fig


def plotly_scatter_discount_profit(df: pd.DataFrame) -> go.Figure:
    sample = df.sample(min(3000, len(df)), random_state=1)
    fig = px.scatter(sample, x="Discount", y="Profit", color="Category",
                      title="Discount vs Profit", opacity=0.6, trendline=None)
    return fig


def plotly_customer_scatter(customer_df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(customer_df, x="Frequency", y="Monetary", size="Total_Profit",
                      color="Customer Value Tier", hover_name="Customer Name",
                      title="Customer Segmentation: Frequency vs Monetary Value")
    return fig
