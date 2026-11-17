from dataclasses import dataclass, field

import pandas as pd

from .evaluation import EvaluationResult, evaluate_results
from .forecaster import EmulatorConfig, ErrorInjectionEmulator
from .generator import WorldConfig, generate_world
from .simulator import SimulationConfig, simulate_replenishment


@dataclass(frozen=True)
class PipelineConfig:
    world: WorldConfig = field(default_factory=WorldConfig)
    forecast_bias: float = 0.0
    forecast_variance: float = 0.01
    seasonal_drift: float = 0.1
    minimum_stock: int = 1

    def __post_init__(self) -> None:
        EmulatorConfig(
            seed=self.world.seed,
            bias=self.forecast_bias,
            variance=self.forecast_variance,
            seasonal_drift=self.seasonal_drift,
        )
        SimulationConfig(minimum_stock=self.minimum_stock)


@dataclass(frozen=True)
class PipelineResult:
    world: dict[str, pd.DataFrame]
    forecasts: pd.DataFrame
    outcomes: pd.DataFrame
    evaluation: EvaluationResult


def run_pipeline(config: PipelineConfig | None = None) -> PipelineResult:
    settings = config or PipelineConfig()
    world = generate_world(settings.world)
    forecaster = ErrorInjectionEmulator(EmulatorConfig(
        seed=settings.world.seed,
        bias=settings.forecast_bias,
        variance=settings.forecast_variance,
        seasonal_drift=settings.seasonal_drift,
    ))
    forecaster.fit(world["sales_history"])
    forecasts = forecaster.predict(settings.world.future_days)
    outcomes = simulate_replenishment(
        forecasts,
        world["true_demand"],
        world["products"],
        world["warehouse"],
        SimulationConfig(minimum_stock=settings.minimum_stock),
    )
    evaluation = evaluate_results(outcomes)
    return PipelineResult(
        world=world,
        forecasts=forecasts,
        outcomes=outcomes,
        evaluation=evaluation,
    )
