from datetime import date
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rdq.evaluation import evaluate_results
from src.rdq.generator import WorldConfig
from src.rdq.pipeline import PipelineConfig, run_pipeline


@st.cache_data(show_spinner=False)
def _cached_pipeline(
    seed: int,
    stores: int,
    products: int,
    history_days: int,
    future_days: int,
    start_date: date,
    forecast_bias: float,
    forecast_variance: float,
    seasonal_drift: float,
    minimum_stock: int,
):
    return run_pipeline(PipelineConfig(
        world=WorldConfig(
            seed=seed,
            stores=stores,
            products=products,
            history_days=history_days,
            future_days=future_days,
            start_date=start_date,
        ),
        forecast_bias=forecast_bias,
        forecast_variance=forecast_variance,
        seasonal_drift=seasonal_drift,
        minimum_stock=minimum_stock,
    ))


def main() -> None:
    st.set_page_config(page_title="Retail Decision Quality", layout="wide")
    st.title("Synthetic Retail Decision Quality")
    st.caption("Seeded synthetic data only. Future true demand is used for evaluation, never forecasting.")

    with st.sidebar:
        st.header("Synthetic run configuration")
        seed = st.number_input("Random seed", min_value=0, value=42, step=1)
        stores = st.number_input("Stores", min_value=1, max_value=50, value=10, step=1)
        products = st.number_input("Products", min_value=1, max_value=500, value=200, step=1)
        history_days = st.number_input("History days", min_value=28, max_value=730, value=365, step=1)
        future_days = st.number_input("Evaluation horizon (days)", min_value=1, max_value=90, value=28, step=1)
        forecast_bias = st.slider("Forecast bias injection", min_value=-1.0, max_value=2.0, value=0.0, step=0.1)
        forecast_variance = st.slider("Forecast noise variance", min_value=0.0, max_value=1.0, value=0.01, step=0.01)
        seasonal_drift = st.slider("Seasonal drift", min_value=0.0, max_value=1.0, value=0.1, step=0.05)
        minimum_stock = st.number_input("Minimum stock rule", min_value=0, value=1, step=1)

    result = _cached_pipeline(
        int(seed),
        int(stores),
        int(products),
        int(history_days),
        int(future_days),
        date(2024, 1, 1),
        float(forecast_bias),
        float(forecast_variance),
        float(seasonal_drift),
        int(minimum_stock),
    )

    outcomes = result.outcomes
    store_options = sorted(outcomes["store_id"].unique().tolist())
    category_options = sorted(outcomes["category"].unique().tolist())
    first_date = outcomes["date"].min().date()
    last_date = outcomes["date"].max().date()
    selected_stores = st.multiselect("Stores", store_options, default=store_options)
    selected_categories = st.multiselect("Categories", category_options, default=category_options)
    selected_dates = st.date_input(
        "Evaluation dates",
        value=(first_date, last_date),
        min_value=first_date,
        max_value=last_date,
    )
    if isinstance(selected_dates, tuple):
        start_date = selected_dates[0] if selected_dates and selected_dates[0] is not None else first_date
        if len(selected_dates) == 2 and selected_dates[1] is not None:
            end_date = selected_dates[1]
        else:
            end_date = last_date
    else:
        start_date = end_date = selected_dates

    mask = (
        outcomes["store_id"].isin(selected_stores)
        & outcomes["category"].isin(selected_categories)
        & outcomes["date"].dt.date.between(start_date, end_date)
    )
    filtered = outcomes.loc[mask].copy()
    if filtered.empty:
        st.warning("No outcomes match these filters.")
        return

    evaluation = evaluate_results(filtered)
    overall = evaluation.metrics.loc[evaluation.metrics["level"] == "overall"].iloc[0]
    metric_columns = st.columns(4)
    metric_columns[0].metric("WAPE", "N/A" if pd.isna(overall["wape"]) else f"{overall['wape']:.1%}")
    metric_columns[1].metric("MAPE", "N/A" if pd.isna(overall["mape"]) else f"{overall['mape']:.1%}")
    metric_columns[2].metric("Bias", "N/A" if pd.isna(overall["bias"]) else f"{overall['bias']:+.1%}")
    metric_columns[3].metric("Lost sales", f"{int(filtered['lost_sales'].sum()):,}")

    left, right = st.columns(2)
    with left:
        st.subheader("Deviation causes")
        cause_chart = evaluation.cause_summary.set_index("deviation_cause")["lost_sales"]
        st.bar_chart(cause_chart)
        st.dataframe(evaluation.cause_summary, width="stretch", hide_index=True)
    with right:
        st.subheader("Forecast versus actual demand")
        daily = filtered.groupby("date")[["qty_forecast", "qty_true"]].sum()
        daily.columns = ["Forecast", "Actual demand"]
        st.line_chart(daily)
        st.metric("Stock-out rows", f"{int(filtered['stock_out'].sum()):,}")
        st.metric("Overstock units", f"{int(filtered['overstock'].sum()):,}")

    st.subheader("Segment metrics")
    segments = evaluation.metrics[
        evaluation.metrics["level"].isin(["store", "product_category", "season"])
    ]
    st.dataframe(segments, width="stretch", hide_index=True)
    st.subheader("Simulation records")
    st.dataframe(filtered.head(1000), width="stretch", hide_index=True)
    st.caption(f"Showing up to 1,000 of {len(filtered):,} filtered store-product-day records.")


if __name__ == "__main__":
    main()
