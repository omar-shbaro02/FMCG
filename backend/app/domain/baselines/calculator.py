from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum
from statistics import median


class BaselineMethod(StrEnum):
    RECENT_PRE_PROMO_AVERAGE = "RECENT_PRE_PROMO_AVERAGE"
    MEDIAN_PRE_PROMO = "MEDIAN_PRE_PROMO"
    SEASONAL_COMPARISON = "SEASONAL_COMPARISON"
    MODEL_GENERATED = "MODEL_GENERATED"
    CONTROLLED_FALLBACK = "CONTROLLED_FALLBACK"


@dataclass(frozen=True)
class BaselineInput:
    week_start_date: date
    value: Decimal
    promo_flag: bool = False
    out_of_stock_flag: bool = False


@dataclass(frozen=True)
class BaselineResult:
    method: BaselineMethod
    period_start: date
    period_end: date
    input_values: list[dict[str, str]]
    output_values: list[dict[str, str]]
    assumptions: list[str]
    excluded_weeks: list[dict[str, str]]
    out_of_stock_effects: list[str]
    promotion_contamination_notes: list[str]
    data_quality_score: Decimal

    def persistence_payload(self) -> dict[str, object]:
        return {
            "baseline_values_json": {
                "input_values": self.input_values,
                "output_values": self.output_values,
            },
            "assumptions_json": {"items": self.assumptions},
            "quality_notes_json": {
                "excluded_weeks": self.excluded_weeks,
                "out_of_stock_effects": self.out_of_stock_effects,
                "promotion_contamination_notes": self.promotion_contamination_notes,
                "data_quality_score": str(self.data_quality_score),
            },
        }


class BaselineCalculationError(ValueError):
    pass


def calculate_baseline(
    history: list[BaselineInput],
    *,
    promotion_start: date,
    horizon_weeks: list[date],
    method: BaselineMethod,
    recent_weeks: int = 8,
    model_values: list[Decimal] | None = None,
) -> BaselineResult:
    if not history or not horizon_weeks:
        raise BaselineCalculationError("History and output horizon are required")
    ordered = sorted(history, key=lambda item: item.week_start_date)
    pre_promotion = [item for item in ordered if item.week_start_date < promotion_start]
    excluded: list[dict[str, str]] = []
    usable: list[BaselineInput] = []
    for item in pre_promotion:
        reasons = []
        if item.promo_flag:
            reasons.append("promotion_contamination")
        if item.out_of_stock_flag:
            reasons.append("out_of_stock")
        if reasons:
            excluded.append({"week": item.week_start_date.isoformat(), "reason": ",".join(reasons)})
        else:
            usable.append(item)
    if not usable and method != BaselineMethod.MODEL_GENERATED:
        raise BaselineCalculationError("No uncontaminated pre-promotion observations remain")

    selected: list[BaselineInput]
    assumptions: list[str]
    if method == BaselineMethod.RECENT_PRE_PROMO_AVERAGE:
        selected = usable[-recent_weeks:]
        level = sum((item.value for item in selected), Decimal(0)) / len(selected)
        values = [level] * len(horizon_weeks)
        assumptions = [
            f"Recent {len(selected)} uncontaminated pre-promotion weeks represent expected movement"
        ]
    elif method == BaselineMethod.MEDIAN_PRE_PROMO:
        selected = usable
        level = Decimal(str(median(item.value for item in selected)))
        values = [level] * len(horizon_weeks)
        assumptions = ["Median limits sensitivity to unusual pre-promotion movement"]
    elif method == BaselineMethod.SEASONAL_COMPARISON:
        selected = usable
        lookup = {item.week_start_date: item.value for item in usable}
        seasonal = [lookup.get(week.replace(year=week.year - 1)) for week in horizon_weeks]
        if any(value is None for value in seasonal):
            raise BaselineCalculationError("Seasonal comparison requires matching prior-year weeks")
        values = [value for value in seasonal if value is not None]
        assumptions = ["Prior-year matching weeks are commercially comparable"]
    elif method == BaselineMethod.MODEL_GENERATED:
        selected = usable
        if model_values is None or len(model_values) != len(horizon_weeks):
            raise BaselineCalculationError(
                "Model-generated baseline requires one value per horizon week"
            )
        if any(not value.is_finite() or value < 0 for value in model_values):
            raise BaselineCalculationError(
                "Model-generated baseline values must be finite and non-negative"
            )
        values = model_values
        assumptions = [
            "External baseline model output was supplied through the controlled interface"
        ]
    else:
        selected = usable
        level = sum((item.value for item in usable), Decimal(0)) / len(usable)
        values = [level] * len(horizon_weeks)
        assumptions = ["Controlled fallback uses all uncontaminated pre-promotion history"]

    quality = Decimal(len(selected)) / Decimal(max(len(pre_promotion), 1))
    return BaselineResult(
        method=method,
        period_start=min(item.week_start_date for item in selected or pre_promotion),
        period_end=max(item.week_start_date for item in selected or pre_promotion),
        input_values=[
            {"week": item.week_start_date.isoformat(), "value": str(item.value)}
            for item in selected
        ],
        output_values=[
            {"week": week.isoformat(), "value": str(value)}
            for week, value in zip(horizon_weeks, values, strict=True)
        ],
        assumptions=assumptions,
        excluded_weeks=excluded,
        out_of_stock_effects=[
            "Out-of-stock weeks were excluded and may understate observed demand."
        ]
        if any("out_of_stock" in item["reason"] for item in excluded)
        else [],
        promotion_contamination_notes=["Promotion-contaminated pre-period weeks were excluded."]
        if any("promotion_contamination" in item["reason"] for item in excluded)
        else [],
        data_quality_score=quality.quantize(Decimal("0.0001")),
    )
