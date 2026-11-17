import argparse
import hashlib
from datetime import date

import pandas as pd

from .generator import WorldConfig
from .pipeline import PipelineConfig, run_pipeline


def checksum(frame: pd.DataFrame) -> str:
    digest = hashlib.sha256()
    digest.update(repr(tuple(frame.columns)).encode("utf-8"))
    digest.update(repr(tuple(str(dtype) for dtype in frame.dtypes)).encode("utf-8"))
    digest.update(pd.util.hash_pandas_object(frame, index=True).to_numpy().tobytes())
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a fictional synthetic retail world.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--stores", type=int, default=10)
    parser.add_argument("--products", type=int, default=200)
    parser.add_argument("--history-days", type=int, default=365)
    parser.add_argument("--future-days", type=int, default=28)
    parser.add_argument("--start-date", type=date.fromisoformat, default=date(2024, 1, 1))
    parser.add_argument("--forecast-bias", type=float, default=0.0)
    parser.add_argument("--forecast-variance", type=float, default=0.01)
    parser.add_argument("--seasonal-drift", type=float, default=0.1)
    parser.add_argument("--minimum-stock", type=int, default=1)
    args = parser.parse_args()
    try:
        world_config = WorldConfig(**{
            name: getattr(args, name)
            for name in ("seed", "stores", "products", "history_days", "future_days", "start_date")
        })
        result = run_pipeline(PipelineConfig(
            world=world_config,
            forecast_bias=args.forecast_bias,
            forecast_variance=args.forecast_variance,
            seasonal_drift=args.seasonal_drift,
            minimum_stock=args.minimum_stock,
        ))
        world = result.world
        forecasts = result.forecasts
        outcomes = result.outcomes
        evaluation = result.evaluation
    except (TypeError, ValueError) as error:
        parser.error(str(error))

    print(f"Synthetic retail world | seed={world_config.seed}")
    for name, frame in world.items():
        withheld = " (evaluation-only; samples withheld)" if name == "true_demand" else ""
        print(f"\n{name}: {len(frame):,} rows | SHA-256 {checksum(frame)}{withheld}")
        if name != "true_demand":
            print(frame.head(3).to_string(index=False))

    print(f"\nforecasts: {len(forecasts):,} rows | SHA-256 {checksum(forecasts)}")
    print(f"emulator: bias={args.forecast_bias}, variance={args.forecast_variance}, seasonal_drift={args.seasonal_drift}")
    print(forecasts.head(3).to_string(index=False))
    print(f"\nsimulation: {len(outcomes):,} rows | SHA-256 {checksum(outcomes)}")
    print(
        f"stock-out rows: {int(outcomes['stock_out'].sum()):,} | "
        f"lost sales: {int(outcomes['lost_sales'].sum()):,} | "
        f"minimum stock: {args.minimum_stock}"
    )
    print(outcomes.head(3).to_string(index=False))
    metric_summary = evaluation.metrics[
        evaluation.metrics["level"].isin(["overall", "store", "product_category", "season"])
    ]
    print("\nWAPE / MAPE / bias by overall, store, category, and season")
    print(metric_summary.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("\nDeviation causes")
    print(evaluation.cause_summary.to_string(index=False, float_format=lambda value: f"{value:.4f}"))


if __name__ == "__main__":
    main()
