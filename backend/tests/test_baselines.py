from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.domain.baselines import BaselineInput, BaselineMethod, calculate_baseline
from app.domain.baselines.calculator import BaselineCalculationError

START = date(2025, 1, 6)


def observations(values: list[int]) -> list[BaselineInput]:
    return [
        BaselineInput(START + timedelta(weeks=index), Decimal(value))
        for index, value in enumerate(values)
    ]


def horizon(start_week: int, count: int = 4) -> list[date]:
    return [START + timedelta(weeks=start_week + index) for index in range(count)]


def test_recent_average_is_explicit_and_excludes_distortions() -> None:
    history = observations([90, 100, 110, 120])
    history[1] = BaselineInput(history[1].week_start_date, Decimal(100), promo_flag=True)
    history[2] = BaselineInput(history[2].week_start_date, Decimal(110), out_of_stock_flag=True)

    result = calculate_baseline(
        history,
        promotion_start=START + timedelta(weeks=5),
        horizon_weeks=horizon(6),
        method=BaselineMethod.RECENT_PRE_PROMO_AVERAGE,
    )

    assert {item["value"] for item in result.output_values} == {"105"}
    assert len(result.excluded_weeks) == 2
    assert result.out_of_stock_effects
    assert result.promotion_contamination_notes
    assert result.data_quality_score == Decimal("0.5000")


def test_median_and_fallback_resist_or_document_assumptions() -> None:
    history = observations([95, 100, 105, 500])
    median_result = calculate_baseline(
        history,
        promotion_start=START + timedelta(weeks=5),
        horizon_weeks=horizon(6),
        method=BaselineMethod.MEDIAN_PRE_PROMO,
    )
    fallback_result = calculate_baseline(
        history,
        promotion_start=START + timedelta(weeks=5),
        horizon_weeks=horizon(6),
        method=BaselineMethod.CONTROLLED_FALLBACK,
    )

    assert median_result.output_values[0]["value"] == "102.5"
    assert fallback_result.output_values[0]["value"] == "200"
    assert fallback_result.assumptions


def test_seasonal_requires_matching_prior_year_weeks() -> None:
    with pytest.raises(BaselineCalculationError):
        calculate_baseline(
            observations([100, 101]),
            promotion_start=START + timedelta(weeks=3),
            horizon_weeks=horizon(4),
            method=BaselineMethod.SEASONAL_COMPARISON,
        )


def test_model_baseline_is_validated_and_replaceable() -> None:
    result = calculate_baseline(
        observations([100, 101]),
        promotion_start=START + timedelta(weeks=3),
        horizon_weeks=horizon(4),
        method=BaselineMethod.MODEL_GENERATED,
        model_values=[Decimal("101")] * 4,
    )
    assert len(result.output_values) == 4
    with pytest.raises(BaselineCalculationError):
        calculate_baseline(
            observations([100]),
            promotion_start=START + timedelta(weeks=2),
            horizon_weeks=horizon(3),
            method=BaselineMethod.MODEL_GENERATED,
            model_values=[Decimal("NaN")] * 4,
        )
