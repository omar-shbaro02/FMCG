from pathlib import Path

import pandas as pd

from app.domain.data_quality import DatasetValidator

REQUIRED_HEADER = (
    "week_start_date,sku_id,brand,category,channel,region,sell_out_units,"
    "sell_in_units,promo_flag,discount_depth,net_sales_value,gross_sales_value,"
    "gross_margin,stock_on_hand,out_of_stock_flag,returns_units\n"
)


def write_csv(path: Path, rows: list[str]) -> Path:
    path.write_text(REQUIRED_HEADER + "\n".join(rows) + "\n", encoding="utf-8")
    return path


def row(
    week: str,
    *,
    sell_out: str = "100",
    sell_in: str = "105",
    promo: str = "false",
    discount: str = "0",
    stock: str = "250",
    out_of_stock: str = "false",
    returns: str = "0",
) -> str:
    return (
        f"{week},SKU-1,Brand A,Beverages,Modern Trade,North,{sell_out},{sell_in},"
        f"{promo},{discount},1000,1200,300,{stock},{out_of_stock},{returns}"
    )


def validate(path: Path, minimum: int = 4):
    return DatasetValidator(minimum).validate(
        path,
        currency="USD",
        gross_margin_representation="amount",
        stock_unit="units",
    )


def test_valid_complete_promotional_series_is_forecast_eligible(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "valid.csv",
        [
            row("2026-01-05"),
            row("2026-01-12"),
            row("2026-01-19", promo="true", discount="20"),
            row("2026-01-26"),
        ],
    )
    report = validate(source)

    assert not report.has_critical_errors
    assert report.valid_row_count == 4
    assert report.rejected_row_count == 0
    assert report.series_eligibility[0].eligible
    assert "discount_depth normalized from percentage to fraction" in report.transformations


def test_missing_columns_block_every_row_without_silent_deletion(tmp_path: Path) -> None:
    source = tmp_path / "missing.csv"
    source.write_text("week_start_date,sku_id\n2026-01-05,SKU-1\n", encoding="utf-8")

    report = validate(source)

    assert report.has_critical_errors
    assert "sell_out_units" in report.missing_fields
    assert report.row_count == report.rejected_row_count == 1


def test_invalid_values_duplicates_and_mixed_discount_scale_are_critical(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "invalid.csv",
        [
            row("2026-01-05", sell_out="-1", discount="0.2"),
            row("2026-01-05", discount="20", out_of_stock="maybe"),
        ],
    )

    report = validate(source)
    codes = {issue.issue_code for issue in report.issues if issue.severity == "CRITICAL"}

    assert {"NEGATIVE_VALUE", "INVALID_BOOLEAN", "DUPLICATE_GRAIN", "MIXED_DISCOUNT_SCALE"} <= codes
    assert report.rejected_row_count == 2


def test_missing_weeks_sparse_history_and_distortions_remain_visible(tmp_path: Path) -> None:
    source = write_csv(
        tmp_path / "warnings.csv",
        [
            row("2026-01-05", sell_out="50", sell_in="100", out_of_stock="true", returns="3"),
            row("2026-01-19", promo="true"),
        ],
    )

    report = validate(source, minimum=4)

    assert report.missing_weeks["SKU-1|Modern Trade|North"] == ["2026-01-12"]
    assert not report.series_eligibility[0].eligible
    assert len(report.business_distortion_notes) == 3


def test_xlsx_uses_the_same_validation_contract(tmp_path: Path) -> None:
    source = tmp_path / "valid.xlsx"
    data = pd.read_csv(
        write_csv(
            tmp_path / "source.csv",
            [row("2026-01-05"), row("2026-01-12", promo="true")],
        )
    )
    data.to_excel(source, index=False)

    report = validate(source, minimum=2)

    assert report.valid_row_count == 2
    assert not report.has_critical_errors
