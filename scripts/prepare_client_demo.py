#!/usr/bin/env python3
"""Prepare and verify a deterministic, synthetic client-demo workspace."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import uuid
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
from app.database import SessionLocal
from app.models.entities import AuditEvent, Dataset, DatasetStatus, User, WeeklyFmcgSale
from sqlalchemy import select

DEMO_PREFIX = "[DEMO]"
CHANNEL = "MODERN_TRADE"
REGION = "NORTH"
PROMOTION_START = "2025-03-31"
PROMOTION_END = "2025-04-07"
FINAL_REVIEW_STATEMENT = (
    "This output supports leadership review. It does not make or execute the final "
    "commercial decision."
)
SCENARIOS = (
    ("healthy_growth", "SKU-DEMO-HEALTHY", "Retained growth candidate", True),
    ("temporary_uplift", "SKU-DEMO-TEMPORARY", "Temporary promotion uplift", False),
    ("pull_forward", "SKU-DEMO-RECOVERY", "Post-promotion recovery concern", False),
    ("loading_risk", "SKU-DEMO-LOADING", "Channel loading risk", False),
)


class DemoError(RuntimeError):
    """A client-demo preparation or verification failure."""


def api_request(
    client: httpx.Client,
    method: str,
    path: str,
    *,
    token: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    headers = dict(kwargs.pop("headers", {}))
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = client.request(method, path, headers=headers, **kwargs)
    if not response.is_success:
        raise DemoError(f"{method} {path} failed ({response.status_code}): {response.text}")
    payload = response.json()
    if not isinstance(payload, dict):
        raise DemoError(f"{method} {path} returned an unexpected response")
    return payload


def login(client: httpx.Client) -> str:
    response = api_request(
        client,
        "POST",
        "/api/auth/login",
        json={
            "email": os.getenv("BOOTSTRAP_ADMIN_EMAIL", "admin@example.com"),
            "password": os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "development-admin-only"),
        },
    )
    token = response.get("access_token")
    if not isinstance(token, str):
        raise DemoError("Login response did not include an access token")
    return token


def existing_demo_cases(client: httpx.Client, token: str) -> list[dict[str, Any]]:
    payload = api_request(
        client, "GET", "/api/diagnostic-cases?page=1&page_size=100", token=token
    )
    items = payload.get("items", [])
    return [item for item in items if str(item.get("title", "")).startswith(DEMO_PREFIX)]


def seed_dataset(fixtures: Path) -> uuid.UUID:
    with SessionLocal() as session:
        admin_email = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "admin@example.com").casefold()
        admin = session.scalar(select(User).where(User.email == admin_email))
        if admin is None:
            raise DemoError("Bootstrap administrator is unavailable")

        dataset = Dataset(
            name=f"{DEMO_PREFIX} Synthetic promotion portfolio",
            original_filename="synthetic-client-demo-portfolio.csv",
            storage_path=f"demo://{uuid.uuid4()}",
            uploaded_by=admin.id,
            upload_status=DatasetStatus.VALID,
            schema_version="1.0",
            row_count=0,
            date_min=None,
            date_max=None,
            validation_summary_json={},
        )
        session.add(dataset)
        session.flush()

        all_dates: list[date] = []
        eligible_series: list[str] = []
        row_count = 0
        for scenario, demo_sku, _, _ in SCENARIOS:
            source = fixtures / scenario / "weekly_sales.csv"
            if not source.is_file():
                raise DemoError(f"Missing synthetic fixture: {source}")
            with source.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            for row in rows:
                week = date.fromisoformat(row["week_start_date"])
                all_dates.append(week)
                session.add(
                    WeeklyFmcgSale(
                        week_start_date=week,
                        sku_id=demo_sku,
                        brand=row["brand"],
                        category=row["category"],
                        channel=CHANNEL,
                        region=REGION,
                        sell_out_units=Decimal(row["sell_out_units"]),
                        sell_in_units=Decimal(row["sell_in_units"]),
                        promo_flag=row["promo_flag"].casefold() == "true",
                        discount_depth=Decimal(row["discount_depth"]),
                        net_sales_value=Decimal(row["net_sales_value"]),
                        gross_sales_value=Decimal(row["gross_sales_value"]),
                        gross_margin=Decimal(row["gross_margin"]),
                        stock_on_hand=Decimal(row["stock_on_hand"]),
                        out_of_stock_flag=row["out_of_stock_flag"].casefold() == "true",
                        returns_units=Decimal(row["returns_units"]),
                        source_dataset_id=dataset.id,
                    )
                )
                row_count += 1
            eligible_series.append(f"{demo_sku}|{CHANNEL}|{REGION}")

        dataset.row_count = row_count
        dataset.date_min = min(all_dates)
        dataset.date_max = max(all_dates)
        dataset.validation_summary_json = {
            "dataset_id": str(dataset.id),
            "overall_status": DatasetStatus.VALID.value,
            "row_count": row_count,
            "valid_row_count": row_count,
            "rejected_row_count": 0,
            "date_min": dataset.date_min.isoformat(),
            "date_max": dataset.date_max.isoformat(),
            "forecast_eligible_series": eligible_series,
            "forecast_ineligible_series": [],
            "warnings": [],
            "critical_errors": [],
            "business_distortion_notes": [
                "Synthetic scenarios intentionally contain commercially meaningful distortions."
            ],
            "transformations": ["Demo SKU identifiers assigned to isolate scenario grains"],
            "declarations": {
                "currency": "USD",
                "gross_margin_representation": "amount",
                "stock_unit": "units",
                "synthetic": "true",
            },
            "missing_fields": [],
            "missing_weeks": {},
            "duplicate_series": [],
        }
        session.add(
            AuditEvent(
                actor_id=admin.id,
                event_type="CLIENT_DEMO_DATASET_PREPARED",
                entity_type="dataset",
                entity_id=dataset.id,
                before_json=None,
                after_json={"synthetic": True, "scenario_count": len(SCENARIOS)},
                correlation_id=str(uuid.uuid4()),
            )
        )
        session.commit()
        return dataset.id


def prepare(client: httpx.Client, token: str, fixtures: Path) -> list[dict[str, Any]]:
    current = existing_demo_cases(client, token)
    if current:
        print(f"Demo is already prepared with {len(current)} cases.")
        return current

    dataset_id = seed_dataset(fixtures)
    created: list[dict[str, Any]] = []
    for scenario, sku_id, title, validate_case in SCENARIOS:
        case = api_request(
            client,
            "POST",
            "/api/diagnostic-cases",
            token=token,
            json={
                "title": f"{DEMO_PREFIX} {title}",
                "dataset_id": str(dataset_id),
                "sku_id": sku_id,
                "channel": CHANNEL,
                "region": REGION,
                "promotion_start_week": PROMOTION_START,
                "promotion_end_week": PROMOTION_END,
                "forecast_horizon_weeks": 6,
                "management_concern_note": (
                    f"Synthetic evidence for the {title.casefold()} case. Determine what must "
                    "be verified before leadership treats the apparent growth as healthy."
                ),
            },
        )
        case_id = str(case["id"])
        api_request(client, "POST", f"/api/diagnostic-cases/{case_id}/submit", token=token)
        api_request(
            client,
            "POST",
            f"/api/diagnostic-cases/{case_id}/baseline-calculations",
            token=token,
            json={"method": "RECENT_PRE_PROMO_AVERAGE", "recent_weeks": 8},
        )
        api_request(
            client,
            "POST",
            f"/api/diagnostic-cases/{case_id}/forecast-runs",
            token=token,
            headers={"Idempotency-Key": f"client-demo-{scenario}-forecast-v1"},
        )
        api_request(
            client,
            "POST",
            f"/api/diagnostic-cases/{case_id}/decision-intelligence",
            token=token,
            headers={"Idempotency-Key": f"client-demo-{scenario}-decision-v1"},
        )
        if validate_case:
            api_request(
                client,
                "POST",
                f"/api/diagnostic-cases/{case_id}/reviews",
                token=token,
                json={
                    "review_status": "VALIDATED",
                    "validated_risk_class": None,
                    "reviewer_comments": (
                        "Demo validation: evidence was reviewed; this records judgment only."
                    ),
                    "requested_evidence": [],
                    "final_decision_note": "No commercial action was executed by the system.",
                },
            )
        created.append(case)
        print(f"Prepared {case['title']}")
    return created


def check(client: httpx.Client, token: str) -> None:
    health = api_request(client, "GET", "/health")
    cases = existing_demo_cases(client, token)
    if health.get("status") != "healthy":
        raise DemoError("API health check is not healthy")
    if len(cases) != len(SCENARIOS):
        raise DemoError(f"Expected {len(SCENARIOS)} demo cases, found {len(cases)}")
    statuses = {str(item["status"]) for item in cases}
    if "READY_FOR_REVIEW" not in statuses or "COMPLETED" not in statuses:
        raise DemoError(f"Demo case mix is incomplete: {sorted(statuses)}")
    for case in cases:
        case_id = str(case["id"])
        api_request(client, "GET", f"/api/diagnostic-cases/{case_id}/forecast-evidence", token=token)
        output = api_request(
            client,
            "GET",
            f"/api/diagnostic-cases/{case_id}/decision-intelligence/latest",
            token=token,
        )
        statement = str(output.get("output_json", {}).get("final_human_review_statement", ""))
        if statement != FINAL_REVIEW_STATEMENT:
            raise DemoError(f"Required final review statement changed for {case['title']}")
    print(
        json.dumps(
            {
                "status": "ready",
                "demo_cases": len(cases),
                "case_statuses": sorted(statuses),
                "forecast_adapter": os.getenv("FORECAST_ADAPTER", "mock"),
                "synthetic_data_only": True,
            },
            indent=2,
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "check"), nargs="?", default="prepare")
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--fixtures", type=Path, default=Path("/demo/fixtures"))
    args = parser.parse_args()
    try:
        with httpx.Client(base_url=args.api_url, timeout=30.0) as client:
            token = login(client)
            if args.command == "prepare":
                prepare(client, token, args.fixtures)
            check(client, token)
    except (DemoError, httpx.HTTPError, OSError, ValueError) as exc:
        print(f"Demo preparation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
