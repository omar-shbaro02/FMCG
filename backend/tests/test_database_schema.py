from sqlalchemy import Numeric, UniqueConstraint

from app.database import Base
from app.models import entities  # noqa: F401


def test_all_required_core_tables_are_registered() -> None:
    required = {
        "users",
        "datasets",
        "dataset_validation_issues",
        "weekly_fmcg_sales",
        "diagnostic_cases",
        "baseline_calculations",
        "forecast_runs",
        "forecast_evidence",
        "growth_quality_assessments",
        "investigation_plans",
        "decision_simulations",
        "executive_outputs",
        "human_reviews",
        "feedback_events",
        "audit_events",
    }
    assert required == set(Base.metadata.tables)


def test_weekly_series_grain_is_unique() -> None:
    table = Base.metadata.tables["weekly_fmcg_sales"]
    unique_columns = {
        tuple(column.name for column in constraint.columns)
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert ("week_start_date", "sku_id", "channel", "region") in unique_columns


def test_financial_values_use_fixed_precision() -> None:
    table = Base.metadata.tables["weekly_fmcg_sales"]
    for column_name in ("discount_depth", "net_sales_value", "gross_sales_value", "gross_margin"):
        assert isinstance(table.columns[column_name].type, Numeric)
        assert table.columns[column_name].type.asdecimal is True
