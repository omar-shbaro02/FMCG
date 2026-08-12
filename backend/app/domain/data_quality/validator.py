from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Literal

import pandas as pd

REQUIRED_COLUMNS = (
    "week_start_date",
    "sku_id",
    "brand",
    "category",
    "channel",
    "region",
    "sell_out_units",
    "sell_in_units",
    "promo_flag",
    "discount_depth",
    "net_sales_value",
    "gross_sales_value",
    "gross_margin",
    "stock_on_hand",
    "out_of_stock_flag",
    "returns_units",
)
SERIES_COLUMNS = ("sku_id", "channel", "region")
GRAIN_COLUMNS = ("week_start_date", *SERIES_COLUMNS)
NUMERIC_COLUMNS = (
    "sell_out_units",
    "sell_in_units",
    "discount_depth",
    "net_sales_value",
    "gross_sales_value",
    "gross_margin",
    "stock_on_hand",
    "returns_units",
)
NON_NEGATIVE_COLUMNS = (
    "sell_out_units",
    "sell_in_units",
    "discount_depth",
    "net_sales_value",
    "gross_sales_value",
    "stock_on_hand",
    "returns_units",
)
BOOLEAN_COLUMNS = ("promo_flag", "out_of_stock_flag")
TRUE_VALUES = {"true", "1", "yes", "y"}
FALSE_VALUES = {"false", "0", "no", "n"}


@dataclass(frozen=True)
class ValidationIssue:
    severity: Literal["CRITICAL", "WARNING", "INFO"]
    issue_code: str
    issue_message: str
    field_name: str | None = None
    row_reference: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return {
            "severity": self.severity,
            "field_name": self.field_name,
            "row_reference": self.row_reference,
            "issue_code": self.issue_code,
            "issue_message": self.issue_message,
        }


@dataclass(frozen=True)
class SeriesEligibility:
    series_id: str
    observation_count: int
    eligible: bool
    reasons: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "series_id": self.series_id,
            "observation_count": self.observation_count,
            "eligible": self.eligible,
            "reasons": self.reasons,
        }


@dataclass
class ValidationReport:
    row_count: int
    valid_row_count: int = 0
    rejected_row_count: int = 0
    date_min: date | None = None
    date_max: date | None = None
    missing_fields: list[str] = field(default_factory=list)
    missing_weeks: dict[str, list[str]] = field(default_factory=dict)
    duplicate_series: list[str] = field(default_factory=list)
    series_eligibility: list[SeriesEligibility] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)
    business_distortion_notes: list[str] = field(default_factory=list)
    transformations: list[str] = field(default_factory=list)
    declarations: dict[str, str] = field(default_factory=dict)

    @property
    def has_critical_errors(self) -> bool:
        return any(issue.severity == "CRITICAL" for issue in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(issue.severity == "WARNING" for issue in self.issues)

    def as_dict(self) -> dict[str, Any]:
        return {
            "row_count": self.row_count,
            "valid_row_count": self.valid_row_count,
            "rejected_row_count": self.rejected_row_count,
            "date_min": self.date_min.isoformat() if self.date_min else None,
            "date_max": self.date_max.isoformat() if self.date_max else None,
            "missing_fields": self.missing_fields,
            "missing_weeks": self.missing_weeks,
            "duplicate_series": self.duplicate_series,
            "forecast_eligible_series": [
                item.series_id for item in self.series_eligibility if item.eligible
            ],
            "forecast_ineligible_series": [
                item.as_dict() for item in self.series_eligibility if not item.eligible
            ],
            "warnings": [item.as_dict() for item in self.issues if item.severity == "WARNING"],
            "critical_errors": [
                item.as_dict() for item in self.issues if item.severity == "CRITICAL"
            ],
            "business_distortion_notes": self.business_distortion_notes,
            "transformations": self.transformations,
            "declarations": self.declarations,
        }


class DatasetValidator:
    def __init__(self, minimum_history_weeks: int = 12) -> None:
        self.minimum_history_weeks = minimum_history_weeks

    def validate(
        self,
        path: Path,
        *,
        currency: str,
        gross_margin_representation: Literal["amount", "percentage"],
        stock_unit: Literal["units", "cases"],
    ) -> ValidationReport:
        declarations = {
            "currency": currency.upper(),
            "gross_margin_representation": gross_margin_representation,
            "stock_unit": stock_unit,
        }
        try:
            frame = self._read(path)
        except (OSError, UnicodeError, ValueError, pd.errors.ParserError) as exc:
            return ValidationReport(
                row_count=0,
                declarations=declarations,
                issues=[
                    ValidationIssue(
                        "CRITICAL",
                        "DATASET_READ_ERROR",
                        f"Dataset could not be read safely: {type(exc).__name__}",
                    )
                ],
            )
        frame.columns = [str(column).strip() for column in frame.columns]
        report = ValidationReport(
            row_count=len(frame),
            declarations=declarations,
        )
        if not re.fullmatch(r"[A-Za-z]{3}", currency):
            report.issues.append(
                ValidationIssue("CRITICAL", "INVALID_CURRENCY", "Currency must be a 3-letter code")
            )
        report.missing_fields = [column for column in REQUIRED_COLUMNS if column not in frame]
        for column in report.missing_fields:
            report.issues.append(
                ValidationIssue(
                    "CRITICAL",
                    "MISSING_REQUIRED_COLUMN",
                    f"Required column is missing: {column}",
                    column,
                )
            )
        if report.missing_fields:
            report.rejected_row_count = len(frame)
            return report

        invalid_rows: set[int] = set()
        parsed_dates: dict[int, date] = {}
        parsed_numbers: dict[tuple[int, str], Decimal] = {}
        parsed_booleans: dict[tuple[int, str], bool] = {}

        for index, row in frame.iterrows():
            row_number = int(index) + 2
            row_ref = str(row_number)
            for column in REQUIRED_COLUMNS:
                if self._is_missing(row[column]):
                    severity: Literal["CRITICAL", "WARNING", "INFO"] = (
                        "CRITICAL" if column in (*GRAIN_COLUMNS, "sell_out_units") else "WARNING"
                    )
                    report.issues.append(
                        ValidationIssue(
                            severity,
                            "MISSING_VALUE",
                            f"{column} is missing",
                            column,
                            row_ref,
                        )
                    )
                    if severity == "CRITICAL":
                        invalid_rows.add(int(index))
            try:
                parsed_dates[int(index)] = self._parse_date(row["week_start_date"])
            except ValueError:
                invalid_rows.add(int(index))
                report.issues.append(
                    ValidationIssue(
                        "CRITICAL",
                        "INVALID_DATE",
                        "week_start_date must be a valid date",
                        "week_start_date",
                        row_ref,
                    )
                )
            for column in NUMERIC_COLUMNS:
                if self._is_missing(row[column]):
                    continue
                try:
                    value = Decimal(str(row[column]).strip())
                    if not value.is_finite():
                        raise InvalidOperation
                    parsed_numbers[(int(index), column)] = value
                    if column in NON_NEGATIVE_COLUMNS and value < 0:
                        invalid_rows.add(int(index))
                        report.issues.append(
                            ValidationIssue(
                                "CRITICAL",
                                "NEGATIVE_VALUE",
                                f"{column} cannot be negative",
                                column,
                                row_ref,
                            )
                        )
                except (InvalidOperation, ValueError):
                    invalid_rows.add(int(index))
                    report.issues.append(
                        ValidationIssue(
                            "CRITICAL",
                            "INVALID_NUMBER",
                            f"{column} must be a finite number",
                            column,
                            row_ref,
                        )
                    )
            for column in BOOLEAN_COLUMNS:
                if self._is_missing(row[column]):
                    continue
                normalized = str(row[column]).strip().casefold()
                if normalized in TRUE_VALUES | FALSE_VALUES:
                    parsed_booleans[(int(index), column)] = normalized in TRUE_VALUES
                else:
                    invalid_rows.add(int(index))
                    report.issues.append(
                        ValidationIssue(
                            "CRITICAL",
                            "INVALID_BOOLEAN",
                            f"{column} must use a recognized boolean value",
                            column,
                            row_ref,
                        )
                    )

        self._validate_discount_scale(parsed_numbers, report, invalid_rows)
        self._validate_margin(parsed_numbers, gross_margin_representation, report, invalid_rows)
        self._validate_grain(frame, parsed_dates, report, invalid_rows)
        valid_indices = [int(index) for index in frame.index if int(index) not in invalid_rows]
        report.rejected_row_count = len(invalid_rows)
        report.valid_row_count = len(frame) - len(invalid_rows)
        valid_dates = [parsed_dates[index] for index in valid_indices if index in parsed_dates]
        if valid_dates:
            report.date_min, report.date_max = min(valid_dates), max(valid_dates)
        self._validate_series(frame, valid_indices, parsed_dates, parsed_booleans, report)
        self._add_distortion_notes(parsed_numbers, parsed_booleans, valid_indices, report)
        if valid_dates and valid_dates != sorted(valid_dates):
            report.transformations.append("Rows sorted chronologically for analysis snapshot")
        report.transformations.extend(
            [
                "Text column names trimmed",
                "Boolean values normalized to true/false",
                "Dates normalized to ISO-8601",
            ]
        )
        return report

    @staticmethod
    def _read(path: Path) -> pd.DataFrame:
        if path.suffix.casefold() == ".csv":
            return pd.read_csv(path, dtype=object, keep_default_na=True)
        return pd.read_excel(path, dtype=object)

    @staticmethod
    def _is_missing(value: Any) -> bool:
        return bool(pd.isna(value)) or (isinstance(value, str) and not value.strip())

    @staticmethod
    def _parse_date(value: Any) -> date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        parsed = datetime.strptime(str(value).strip(), "%Y-%m-%d")
        return parsed.date()

    def _validate_discount_scale(
        self,
        values: dict[tuple[int, str], Decimal],
        report: ValidationReport,
        invalid_rows: set[int],
    ) -> None:
        discounts = [
            (row, value) for (row, column), value in values.items() if column == "discount_depth"
        ]
        fractions = [(row, value) for row, value in discounts if Decimal("0") < value <= 1]
        percentages = [(row, value) for row, value in discounts if value > 1]
        for row, value in discounts:
            if value > 100:
                invalid_rows.add(row)
                report.issues.append(
                    ValidationIssue(
                        "CRITICAL",
                        "DISCOUNT_OUT_OF_RANGE",
                        "discount_depth cannot exceed 100%",
                        "discount_depth",
                        str(row + 2),
                    )
                )
        if fractions and percentages:
            report.issues.append(
                ValidationIssue(
                    "CRITICAL",
                    "MIXED_DISCOUNT_SCALE",
                    "discount_depth mixes fractional and percentage scales",
                    "discount_depth",
                )
            )
            invalid_rows.update(row for row, _ in discounts)
        elif percentages:
            report.transformations.append("discount_depth normalized from percentage to fraction")

    @staticmethod
    def _validate_margin(
        values: dict[tuple[int, str], Decimal],
        representation: str,
        report: ValidationReport,
        invalid_rows: set[int],
    ) -> None:
        if representation != "percentage":
            return
        for (row, column), value in values.items():
            if column == "gross_margin" and not Decimal("-100") <= value <= Decimal("100"):
                invalid_rows.add(row)
                report.issues.append(
                    ValidationIssue(
                        "CRITICAL",
                        "MARGIN_OUT_OF_RANGE",
                        "Percentage gross_margin must be between -100 and 100",
                        "gross_margin",
                        str(row + 2),
                    )
                )

    @staticmethod
    def _validate_grain(
        frame: pd.DataFrame,
        dates: dict[int, date],
        report: ValidationReport,
        invalid_rows: set[int],
    ) -> None:
        seen: dict[tuple[Any, ...], int] = {}
        for index, row in frame.iterrows():
            row_index = int(index)
            if row_index not in dates:
                continue
            key = (dates[row_index], *(str(row[column]).strip() for column in SERIES_COLUMNS))
            if key in seen:
                first = seen[key]
                invalid_rows.update((first, row_index))
                series_id = "|".join(str(value) for value in key)
                report.duplicate_series.append(series_id)
                report.issues.append(
                    ValidationIssue(
                        "CRITICAL",
                        "DUPLICATE_GRAIN",
                        f"Duplicate weekly series grain; first row {first + 2}",
                        None,
                        str(row_index + 2),
                    )
                )
            else:
                seen[key] = row_index

    def _validate_series(
        self,
        frame: pd.DataFrame,
        valid_indices: list[int],
        dates: dict[int, date],
        booleans: dict[tuple[int, str], bool],
        report: ValidationReport,
    ) -> None:
        groups: dict[str, list[int]] = {}
        for index in valid_indices:
            row = frame.loc[index]
            series_id = "|".join(str(row[column]).strip() for column in SERIES_COLUMNS)
            groups.setdefault(series_id, []).append(index)
        for series_id, indices in groups.items():
            series_dates = sorted(dates[index] for index in indices if index in dates)
            missing: list[str] = []
            if series_dates:
                expected = series_dates[0]
                present = set(series_dates)
                while expected <= series_dates[-1]:
                    if expected not in present:
                        missing.append(expected.isoformat())
                    expected += timedelta(days=7)
            if missing:
                report.missing_weeks[series_id] = missing
                report.issues.append(
                    ValidationIssue(
                        "WARNING",
                        "MISSING_WEEKS",
                        f"Series {series_id} has {len(missing)} missing week(s)",
                    )
                )
            reasons: list[str] = []
            if len(indices) < self.minimum_history_weeks:
                reasons.append(f"fewer than {self.minimum_history_weeks} historical weeks")
            if not any(booleans.get((index, "promo_flag"), False) for index in indices):
                reasons.append("no identifiable promotion window")
            if missing:
                reasons.append("history contains missing weeks")
            report.series_eligibility.append(
                SeriesEligibility(series_id, len(indices), not reasons, reasons)
            )
            if reasons:
                report.issues.append(
                    ValidationIssue(
                        "WARNING",
                        "FORECAST_INELIGIBLE",
                        f"Series {series_id}: {'; '.join(reasons)}",
                    )
                )

    @staticmethod
    def _add_distortion_notes(
        numbers: dict[tuple[int, str], Decimal],
        booleans: dict[tuple[int, str], bool],
        valid_indices: list[int],
        report: ValidationReport,
    ) -> None:
        if any(booleans.get((index, "out_of_stock_flag"), False) for index in valid_indices):
            report.business_distortion_notes.append(
                "Out-of-stock periods may suppress observed consumer demand."
            )
        if any(numbers.get((index, "returns_units"), Decimal(0)) > 0 for index in valid_indices):
            report.business_distortion_notes.append(
                "Returns are present and may distort sell-out interpretation."
            )
        if any(
            numbers.get((index, "sell_in_units"), Decimal(0))
            > numbers.get((index, "sell_out_units"), Decimal(0)) * Decimal("1.25")
            for index in valid_indices
        ):
            report.business_distortion_notes.append(
                "Material sell-in versus sell-out divergence remains available "
                "for loading-risk review."
            )
