"""
utils.py
--------
Shared helper functions used across the data cleaning, EDA, visualization,
and forecasting modules: path handling, logging setup, and small reusable
utilities so the rest of the codebase stays DRY.
"""

import logging
import os
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Project paths (resolved relative to this file so scripts work regardless
# of the current working directory they are invoked from).
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "superstore.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "cleaned_data.csv"
IMAGES_DIR = PROJECT_ROOT / "images"
REPORTS_DIR = PROJECT_ROOT / "reports"


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger that prints timestamped, leveled messages."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def ensure_dir(path: os.PathLike) -> None:
    """Create a directory (and parents) if it doesn't already exist."""
    Path(path).mkdir(parents=True, exist_ok=True)


def load_csv(path: os.PathLike, parse_dates=None) -> pd.DataFrame:
    """Load a CSV file into a DataFrame with a friendly error if missing."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Expected data file not found at '{path}'. "
            "Run src/data_cleaning.py (or main.py) first."
        )
    return pd.read_csv(path, parse_dates=parse_dates)


def currency(value: float) -> str:
    """Format a number as a US currency string, e.g. 1234.5 -> '$1,234.50'."""
    return f"${value:,.2f}"


def pct(value: float, decimals: int = 1) -> str:
    """Format a fraction as a percentage string, e.g. 0.1234 -> '12.3%'."""
    return f"{value * 100:.{decimals}f}%"


def kpi_summary(df: pd.DataFrame) -> dict:
    """Compute the headline KPIs used throughout notebooks, reports, and the dashboard."""
    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    total_orders = df["Order ID"].nunique()
    total_customers = df["Customer ID"].nunique()
    profit_margin = total_profit / total_sales if total_sales else 0
    avg_order_value = total_sales / total_orders if total_orders else 0

    return {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "profit_margin": profit_margin,
        "avg_order_value": avg_order_value,
    }
