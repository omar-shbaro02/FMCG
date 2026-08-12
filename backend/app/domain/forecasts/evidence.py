from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from statistics import mean

from app.adapters.forecast.schemas import (
    BaselineComparison,
    DecaySignal,
    ForecastDirection,
    ForecastResponse,
    RetentionStatus,
    UncertaintyLevel,
)


@dataclass(frozen=True)
class CommercialSeriesPoint:
    week_start_date: date
    sell_out_units: float
    sell_in_units: float | None = None


@dataclass(frozen=True)
class DerivedForecastEvidence:
    forecast_direction: ForecastDirection
    baseline_comparison: BaselineComparison
    post_promo_retention_status: RetentionStatus
    decay_signal: DecaySignal
    uncertainty_level: UncertaintyLevel
    sell_in_sell_out_divergence: str
    evidence_values: dict[str, float | str | None]
    data_quality_notes: list[str]


def derive_evidence(
    forecast: ForecastResponse,
    baseline_values: list[float],
    actuals: list[CommercialSeriesPoint],
) -> DerivedForecastEvidence:
    predicted = [point.point_forecast for point in forecast.forecasted_values]
    if (
        not predicted
        or len(baseline_values) != len(predicted)
        or any(value < 0 for value in baseline_values)
    ):
        return DerivedForecastEvidence(
            ForecastDirection.UNCERTAIN,
            BaselineComparison.INSUFFICIENT,
            RetentionStatus.INSUFFICIENT,
            DecaySignal.UNCERTAIN,
            UncertaintyLevel.INSUFFICIENT,
            "INSUFFICIENT",
            {"reason": "baseline horizon is missing, negative, or misaligned"},
            [*forecast.data_quality_notes, "Baseline evidence is insufficient or misaligned."],
        )
    forecast_mean = mean(predicted)
    baseline_mean = mean(baseline_values)
    ratio = forecast_mean / baseline_mean if baseline_mean > 0 else None
    comparison = _comparison(ratio)
    retention = _retention(ratio)
    direction = _direction(predicted)
    decay, decay_percent = _decay(predicted)
    uncertainty, interval_width_ratio = _uncertainty(forecast)
    divergence, divergence_ratio = _divergence(actuals)
    notes = list(forecast.data_quality_notes)
    if divergence == "INSUFFICIENT":
        notes.append("Sell-in versus sell-out divergence could not be calculated.")
    return DerivedForecastEvidence(
        forecast_direction=direction,
        baseline_comparison=comparison,
        post_promo_retention_status=retention,
        decay_signal=decay,
        uncertainty_level=uncertainty,
        sell_in_sell_out_divergence=divergence,
        evidence_values={
            "forecast_mean": forecast_mean,
            "baseline_mean": baseline_mean,
            "forecast_to_baseline_ratio": ratio,
            "forecast_first": predicted[0],
            "forecast_last": predicted[-1],
            "decay_percent": decay_percent,
            "mean_interval_width_ratio": interval_width_ratio,
            "sell_in_to_sell_out_ratio": divergence_ratio,
        },
        data_quality_notes=notes,
    )


def _comparison(ratio: float | None) -> BaselineComparison:
    if ratio is None:
        return BaselineComparison.INSUFFICIENT
    if ratio > 1.05:
        return BaselineComparison.ABOVE_BASELINE
    if ratio < 0.95:
        return BaselineComparison.BELOW_BASELINE
    return BaselineComparison.AT_BASELINE


def _retention(ratio: float | None) -> RetentionStatus:
    if ratio is None:
        return RetentionStatus.INSUFFICIENT
    if ratio >= 1.10:
        return RetentionStatus.SUSTAINED
    if ratio >= 1.00:
        return RetentionStatus.PARTIAL
    if ratio >= 0.85:
        return RetentionStatus.WEAK
    return RetentionStatus.COLLAPSED


def _direction(values: list[float]) -> ForecastDirection:
    first = values[0]
    change = (values[-1] - first) / first if first else 0
    if change > 0.20:
        return ForecastDirection.STRONGLY_INCREASING
    if change > 0.05:
        return ForecastDirection.INCREASING
    if change < -0.20:
        return ForecastDirection.STRONGLY_DECLINING
    if change < -0.05:
        return ForecastDirection.DECLINING
    return ForecastDirection.STABLE


def _decay(values: list[float]) -> tuple[DecaySignal, float]:
    first = values[0]
    decay = max(0, (first - values[-1]) / first) if first else 0
    if decay <= 0.05:
        signal = DecaySignal.NONE
    elif decay <= 0.15:
        signal = DecaySignal.MILD
    elif decay <= 0.30:
        signal = DecaySignal.MODERATE
    else:
        signal = DecaySignal.STRONG
    return signal, decay


def _uncertainty(forecast: ForecastResponse) -> tuple[UncertaintyLevel, float]:
    ratios = [
        (point.upper_bound - point.lower_bound) / point.point_forecast
        for point in forecast.forecasted_values
        if point.point_forecast > 0
    ]
    if not ratios or not forecast.confidence_interval.available:
        return UncertaintyLevel.INSUFFICIENT, 0
    width = mean(ratios)
    if width <= 0.20:
        return UncertaintyLevel.LOW, width
    if width <= 0.50:
        return UncertaintyLevel.MEDIUM, width
    return UncertaintyLevel.HIGH, width


def _divergence(actuals: list[CommercialSeriesPoint]) -> tuple[str, float | None]:
    paired = [point for point in actuals if point.sell_in_units is not None]
    sell_out = sum(point.sell_out_units for point in paired)
    if not paired or sell_out <= 0:
        return "INSUFFICIENT", None
    sell_in = sum(point.sell_in_units or 0 for point in paired)
    ratio = sell_in / sell_out
    if ratio >= 1.25:
        return "MATERIAL_SELL_IN_EXCESS", ratio
    if ratio <= 0.80:
        return "MATERIAL_SELL_OUT_EXCESS", ratio
    return "ALIGNED", ratio
