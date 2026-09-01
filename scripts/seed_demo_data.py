#!/usr/bin/env python3
"""Generate deterministic synthetic FMCG scenarios; never use client data."""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

COLUMNS = (
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
START = date(2025, 1, 6)
PROMO_WEEKS = frozenset({12, 13})


@dataclass(frozen=True)
class Scenario:
    seed: int
    expected_primary_class: str | None
    expected_priority: str
    evidence_confidence: str
    truth: str
    builder: Callable[[random.Random], list[dict[str, Any]]]


def noisy(rng: random.Random, value: float, spread: float = 2.0) -> float:
    return round(max(0, value + rng.uniform(-spread, spread)), 3)


def record(
    week: int,
    sell_out: float,
    *,
    sell_in: float | None = None,
    sku: str = "SKU-1",
    promo: bool | None = None,
    discount: float = 0,
    net_per_unit: float = 10,
    gross_per_unit: float = 12,
    margin_per_unit: float = 3,
    stock: float = 200,
    returns: float = 0,
) -> dict[str, Any]:
    return {
        "week_start_date": (START + timedelta(weeks=week)).isoformat(),
        "sku_id": sku,
        "brand": "Synthetic Brand",
        "category": "Synthetic Beverages",
        "channel": "MODERN_TRADE",
        "region": "NORTH",
        "sell_out_units": round(sell_out, 3),
        "sell_in_units": round(sell_in if sell_in is not None else sell_out * 1.02, 3),
        "promo_flag": promo if promo is not None else week in PROMO_WEEKS,
        "discount_depth": discount,
        "net_sales_value": round(sell_out * net_per_unit, 4),
        "gross_sales_value": round(sell_out * gross_per_unit, 4),
        "gross_margin": round(sell_out * margin_per_unit, 4),
        "stock_on_hand": round(stock, 3),
        "out_of_stock_flag": False,
        "returns_units": returns,
    }


def standard_series(
    rng: random.Random,
    movement: Callable[[int], float],
    **overrides: Any,
) -> list[dict[str, Any]]:
    return [record(week, noisy(rng, movement(week)), **overrides) for week in range(26)]


def healthy(rng: random.Random) -> list[dict[str, Any]]:
    def movement(week: int) -> float:
        if week in PROMO_WEEKS:
            return 155
        return 119 if week > 13 else 100

    return standard_series(rng, movement, discount=0.15)


def temporary(rng: random.Random) -> list[dict[str, Any]]:
    return standard_series(
        rng,
        lambda week: 165 if week in PROMO_WEEKS else (101 if week > 13 else 100),
        discount=0.20,
    )


def pull_forward(rng: random.Random) -> list[dict[str, Any]]:
    def movement(week: int) -> float:
        if week in PROMO_WEEKS:
            return 180
        if 14 <= week <= 18:
            return 70
        return 96 if week > 18 else 100

    return standard_series(rng, movement, discount=0.25)


def loading(rng: random.Random) -> list[dict[str, Any]]:
    rows = []
    for week in range(26):
        sell_out = noisy(rng, 125 if week in PROMO_WEEKS else (88 if week > 13 else 100))
        sell_in = noisy(rng, 195 if week in PROMO_WEEKS else (145 if week > 13 else 102))
        stock = 200 + max(0, week - 11) * 18
        rows.append(record(week, sell_out, sell_in=sell_in, discount=0.18, stock=stock))
    return rows


def discount_dependency(rng: random.Random) -> list[dict[str, Any]]:
    rows = []
    for week in range(26):
        promoted = week in {5, 6, 12, 13, 19, 20}
        sell_out = noisy(rng, 170 if promoted else 76)
        rows.append(record(week, sell_out, promo=promoted, discount=0.35 if promoted else 0))
    return rows


def cannibalization(rng: random.Random) -> list[dict[str, Any]]:
    rows = []
    for week in range(26):
        promo = week in PROMO_WEEKS
        rows.append(record(week, noisy(rng, 175 if promo else 100), sku="SKU-PROMOTED"))
        rows.append(
            record(
                week,
                noisy(rng, 42 if promo else 90),
                sku="SKU-ADJACENT",
                promo=promo,
                discount=0,
            )
        )
    return rows


def margin_quality(rng: random.Random) -> list[dict[str, Any]]:
    rows = []
    for week in range(26):
        promo = week in PROMO_WEEKS
        units = noisy(rng, 165 if promo else 100)
        rows.append(
            record(
                week,
                units,
                discount=0.30 if promo else 0,
                net_per_unit=6.5 if promo else 10,
                margin_per_unit=0.8 if promo else 3,
            )
        )
    return rows


def insufficient(rng: random.Random) -> list[dict[str, Any]]:
    return [record(week, noisy(rng, 100), promo=False) for week in range(6)]


SCENARIOS: dict[str, Scenario] = {
    "healthy_growth": Scenario(
        1101,
        "HEALTHY_GROWTH_CANDIDATE",
        "HEALTHY_CANDIDATE",
        "STRONG",
        "Promotion uplift retains a material post-promotion baseline improvement.",
        healthy,
    ),
    "temporary_uplift": Scenario(
        1102,
        "TEMPORARY_UPLIFT",
        "INVESTIGATION_RECOMMENDED",
        "STRONG",
        "Promotion uplift returns promptly to the pre-promotion baseline.",
        temporary,
    ),
    "pull_forward": Scenario(
        1103,
        "PULL_FORWARD_RISK",
        "INVESTIGATION_RECOMMENDED",
        "STRONG",
        "Large promotion uplift is followed by several materially below-baseline weeks.",
        pull_forward,
    ),
    "loading_risk": Scenario(
        1104,
        "LOADING_RISK",
        "P1_COMMERCIAL_REVIEW",
        "STRONG",
        "Sell-in materially exceeds sell-out while channel stock accumulates.",
        loading,
    ),
    "discount_dependency": Scenario(
        1105,
        "DISCOUNT_DEPENDENCY_RISK",
        "INVESTIGATION_RECOMMENDED",
        "STRONG",
        "Movement recovers only during repeated high-discount promotion windows.",
        discount_dependency,
    ),
    "cannibalization": Scenario(
        1106,
        "CANNIBALIZATION_RISK",
        "INVESTIGATION_RECOMMENDED",
        "STRONG",
        "Promoted SKU uplift coincides with a material adjacent-SKU decline.",
        cannibalization,
    ),
    "margin_quality_risk": Scenario(
        1107,
        "MARGIN_VALUE_QUALITY_RISK",
        "P1_COMMERCIAL_REVIEW",
        "STRONG",
        "Promotion volume grows while unit net value and gross margin compress sharply.",
        margin_quality,
    ),
    "insufficient_evidence": Scenario(
        1108,
        None,
        "INVESTIGATION_RECOMMENDED",
        "INSUFFICIENT",
        "Only six non-promotion weeks exist; no confident classification is permitted.",
        insufficient,
    ),
}


def generate(output_root: Path) -> None:
    for name, scenario in SCENARIOS.items():
        destination = output_root / name
        destination.mkdir(parents=True, exist_ok=True)
        rows = scenario.builder(random.Random(scenario.seed))
        with (destination / "weekly_sales.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        truth = {
            "scenario": name,
            "synthetic": True,
            "seed": scenario.seed,
            "expected_primary_class": scenario.expected_primary_class,
            "expected_priority": scenario.expected_priority,
            "evidence_confidence": scenario.evidence_confidence,
            "truth": scenario.truth,
            "row_count": len(rows),
            "series_grain": "sku_id + channel + region",
            "time_grain": "weekly",
        }
        (destination / "truth.json").write_text(
            json.dumps(truth, indent=2) + "\n", encoding="utf-8"
        )


def generate_portfolio(output_path: Path) -> None:
    """Create one upload-ready file spanning every synthetic scenario."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    portfolio_rows: list[dict[str, Any]] = []
    for name, scenario in SCENARIOS.items():
        rows = scenario.builder(random.Random(scenario.seed))
        for row in rows:
            item = dict(row)
            original_sku = str(item["sku_id"])
            suffix = ""
            if name == "cannibalization":
                suffix = "-PROMOTED" if original_sku == "SKU-PROMOTED" else "-ADJACENT"
            item["sku_id"] = f"DEMO-{name.replace('_', '-').upper()}{suffix}"
            item["brand"] = f"Synthetic {name.replace('_', ' ').title()}"
            portfolio_rows.append(item)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(portfolio_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).parents[1] / "fixtures")
    parser.add_argument(
        "--portfolio-output",
        type=Path,
        default=Path(__file__).parents[1]
        / "frontend"
        / "public"
        / "demo-data"
        / "fmcg-demo-portfolio.csv",
    )
    args = parser.parse_args()
    generate(args.output)
    generate_portfolio(args.portfolio_output)


if __name__ == "__main__":
    main()
