"""
data_cleaning.py
-----------------
End-to-end cleaning pipeline for the raw Superstore sales export.

Responsibilities:
    1. Remove exact duplicate records
    2. Handle missing values with sensible, column-appropriate strategies
    3. Normalize data types (dates, numerics, categorical text)
    4. Engineer new features used throughout the EDA / forecasting notebooks

Run directly:
    python src/data_cleaning.py
"""

import numpy as np
import pandas as pd

from src.utils import RAW_DATA_PATH, PROCESSED_DATA_PATH, ensure_dir, get_logger

logger = get_logger(__name__)


def load_raw_data(path=RAW_DATA_PATH) -> pd.DataFrame:
    """Load the raw Superstore CSV export."""
    logger.info(f"Loading raw data from {path}")
    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df):,} rows and {df.shape[1]} columns")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop fully duplicated rows (ignoring the Row ID index column)."""
    before = len(df)
    dedup_cols = [c for c in df.columns if c != "Row ID"]
    df = df.drop_duplicates(subset=dedup_cols, keep="first").reset_index(drop=True)
    removed = before - len(df)
    logger.info(f"Removed {removed:,} duplicate rows ({removed / before:.2%})")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Impute or drop missing values using column-appropriate strategies."""
    missing_before = df.isna().sum().sum()

    # Customer Name: unknown label rather than dropping the whole record
    if "Customer Name" in df:
        df["Customer Name"] = df["Customer Name"].fillna("Unknown Customer")

    # Postal Code: fill with the mode postal code for that City/State pair,
    # falling back to the overall mode if no match exists.
    if "Postal Code" in df:
        mode_by_state = df.groupby("State")["Postal Code"].transform(
            lambda s: s.mode().iloc[0] if not s.mode().empty else np.nan
        )
        df["Postal Code"] = df["Postal Code"].fillna(mode_by_state)
        df["Postal Code"] = df["Postal Code"].fillna(df["Postal Code"].mode().iloc[0])

    # Sales: reconstruct from Quantity * average unit price for that Sub-Category
    if "Sales" in df:
        df["_unit_price"] = df["Sales"] / df["Quantity"].replace(0, np.nan)
        avg_unit_price = df.groupby("Sub-Category")["_unit_price"].transform("mean")
        reconstructed = (avg_unit_price * df["Quantity"]).round(2)
        df["Sales"] = df["Sales"].fillna(reconstructed)
        df.drop(columns=["_unit_price"], inplace=True)

    # Discount: assume no discount when missing (conservative default)
    if "Discount" in df:
        df["Discount"] = df["Discount"].fillna(0.0)

    # Any remaining numeric NaNs: median impute; remaining categorical NaNs: mode impute
    for col in df.columns:
        if df[col].isna().any():
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mode().iloc[0])

    missing_after = df.isna().sum().sum()
    logger.info(f"Missing values: {missing_before:,} -> {missing_after:,}")
    return df


def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize dtypes: dates to datetime, categoricals stripped/cased, numerics coerced."""
    for date_col in ["Order Date", "Ship Date"]:
        if date_col in df:
            df[date_col] = pd.to_datetime(df[date_col], format="mixed", errors="coerce")

    # Trim whitespace and normalize casing on key categorical columns
    text_cols = ["Ship Mode", "Segment", "Country", "City", "State", "Region",
                 "Category", "Sub-Category", "Product Name", "Customer Name"]
    for col in text_cols:
        if col in df:
            df[col] = df[col].astype(str).str.strip()

    # Region/Category had injected inconsistent casing -> title-case normalize
    for col in ["Region", "Category", "Sub-Category", "Segment", "Ship Mode"]:
        if col in df:
            df[col] = df[col].str.title()

    numeric_cols = ["Sales", "Profit", "Discount", "Quantity", "Postal Code"]
    for col in numeric_cols:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Postal Code"] = df["Postal Code"].astype("Int64")
    df["Quantity"] = df["Quantity"].astype(int)

    logger.info("Data types normalized (dates, numerics, categorical text)")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create derived columns used throughout EDA, storytelling, and forecasting."""
    df["Order Year"] = df["Order Date"].dt.year
    df["Order Month"] = df["Order Date"].dt.month
    df["Order Month Name"] = df["Order Date"].dt.strftime("%b")
    df["Order Quarter"] = df["Order Date"].dt.quarter
    df["Order YearMonth"] = df["Order Date"].dt.to_period("M").astype(str)
    df["Order Weekday"] = df["Order Date"].dt.day_name()

    df["Shipping Days"] = (df["Ship Date"] - df["Order Date"]).dt.days.clip(lower=0)

    df["Profit Margin"] = np.where(df["Sales"] != 0, df["Profit"] / df["Sales"], 0)
    df["Unit Price"] = np.where(df["Quantity"] != 0, df["Sales"] / df["Quantity"], 0)
    df["Is Loss Making"] = df["Profit"] < 0

    # Discount bucket for storytelling around margin erosion
    bins = [-0.01, 0.0, 0.2, 0.4, 1.0]
    labels = ["No Discount", "Low (0-20%)", "Medium (20-40%)", "High (40%+)"]
    df["Discount Band"] = pd.cut(df["Discount"], bins=bins, labels=labels)

    # Simple customer value tiering (used in segmentation notebook)
    customer_sales = df.groupby("Customer ID")["Sales"].transform("sum")
    df["Customer Value Tier"] = pd.qcut(
        customer_sales, q=[0, 0.5, 0.8, 1.0], labels=["Low Value", "Mid Value", "High Value"]
    )

    logger.info(f"Engineered {13} new feature columns")
    return df


def validate(df: pd.DataFrame) -> None:
    """Lightweight sanity checks; raises if something is clearly wrong."""
    assert df["Order Date"].notna().all(), "Null Order Date values remain after cleaning"
    assert df["Sales"].notna().all(), "Null Sales values remain after cleaning"
    assert (df["Quantity"] > 0).all(), "Non-positive quantities found"
    logger.info("Validation checks passed")


def run_pipeline(raw_path=RAW_DATA_PATH, processed_path=PROCESSED_DATA_PATH) -> pd.DataFrame:
    """Execute the full cleaning + feature engineering pipeline and persist the result."""
    df = load_raw_data(raw_path)
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = convert_data_types(df)
    df = engineer_features(df)
    validate(df)

    ensure_dir(processed_path.parent)
    df.to_csv(processed_path, index=False)
    logger.info(f"Saved cleaned dataset -> {processed_path} ({len(df):,} rows)")
    return df


if __name__ == "__main__":
    run_pipeline()
