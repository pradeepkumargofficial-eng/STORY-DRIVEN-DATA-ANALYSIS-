"""
forecasting.py
---------------
Lightweight sales forecasting utilities. Uses a statsmodels Holt-Winters
Exponential Smoothing model (robust with limited history and no extra
system dependencies) with a linear-regression fallback if statsmodels
is unavailable. Designed to forecast monthly total sales N months ahead.
"""

import numpy as np
import pandas as pd

from src.utils import get_logger

logger = get_logger(__name__)


def _prepare_monthly_series(df: pd.DataFrame) -> pd.Series:
    monthly = df.groupby(pd.Grouper(key="Order Date", freq="MS"))["Sales"].sum()
    monthly = monthly.asfreq("MS").fillna(0)
    return monthly


def forecast_sales(df: pd.DataFrame, periods: int = 6) -> pd.DataFrame:
    """
    Forecast total monthly sales `periods` months into the future.

    Returns a DataFrame with columns: ds (month), sales (actual, NaN for future),
    forecast (fitted + predicted), and is_forecast (bool).
    """
    monthly = _prepare_monthly_series(df)

    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        model = ExponentialSmoothing(
            monthly, trend="add", seasonal="add", seasonal_periods=12,
            initialization_method="estimated",
        ).fit(optimized=True)
        fitted = model.fittedvalues
        future = model.forecast(periods)
        method = "Holt-Winters Exponential Smoothing"
    except Exception as exc:  # pragma: no cover - fallback path
        logger.warning(f"Falling back to linear trend forecast: {exc}")
        x = np.arange(len(monthly))
        coeffs = np.polyfit(x, monthly.values, deg=1)
        fitted = pd.Series(np.polyval(coeffs, x), index=monthly.index)
        future_x = np.arange(len(monthly), len(monthly) + periods)
        future_index = pd.date_range(
            monthly.index[-1] + pd.offsets.MonthBegin(1), periods=periods, freq="MS"
        )
        future = pd.Series(np.polyval(coeffs, future_x), index=future_index)
        method = "Linear Trend (fallback)"

    logger.info(f"Forecast generated using: {method}")

    history_df = pd.DataFrame({
        "ds": monthly.index,
        "sales": monthly.values,
        "forecast": fitted.reindex(monthly.index).values,
        "is_forecast": False,
    })
    future_df = pd.DataFrame({
        "ds": future.index,
        "sales": np.nan,
        "forecast": future.values,
        "is_forecast": True,
    })

    result = pd.concat([history_df, future_df], ignore_index=True)
    result["forecast"] = result["forecast"].clip(lower=0)
    return result


def forecast_accuracy(result_df: pd.DataFrame) -> dict:
    """Compute simple in-sample accuracy metrics (MAE, MAPE) on the fitted history."""
    hist = result_df[~result_df["is_forecast"]].dropna(subset=["sales", "forecast"])
    errors = hist["sales"] - hist["forecast"]
    mae = errors.abs().mean()
    mape = (errors.abs() / hist["sales"].replace(0, np.nan)).mean() * 100
    return {"MAE": round(mae, 2), "MAPE_%": round(mape, 2)}
