import uuid
from collections.abc import Iterator
from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select

from app.database import SessionLocal
from app.domain.cases import InvalidCaseTransitionError, assess_readiness, transition_case
from app.main import app
from app.models.entities import (
    AuditEvent,
    CaseStatus,
    Dataset,
    DatasetStatus,
    DiagnosticCase,
    User,
    WeeklyFmcgSale,
)


@pytest.fixture
def ready_dataset() -> Iterator[uuid.UUID]:
    dataset_id = uuid.uuid4()
    series_id = "SKU-READY|MODERN_TRADE|NORTH"
    with SessionLocal() as session:
        admin = session.get(User, uuid.UUID("00000000-0000-0000-0000-000000000001"))
        assert admin is not None
        session.add(
            Dataset(
                id=dataset_id,
                name="Case readiness fixture",
                original_filename=f"{dataset_id}.csv",
                storage_path=f"/tmp/{dataset_id}.csv",
                uploaded_by=admin.id,
                upload_status=DatasetStatus.VALID,
                schema_version="1.0",
                row_count=12,
                date_min=date(2026, 1, 5),
                date_max=date(2026, 3, 23),
                validation_summary_json={"forecast_eligible_series": [series_id]},
            )
        )
        for week in range(12):
            session.add(
                WeeklyFmcgSale(
                    week_start_date=date(2026, 1, 5) + timedelta(weeks=week),
                    sku_id="SKU-READY",
                    brand="Synthetic Brand",
                    category="Synthetic Beverages",
                    channel="MODERN_TRADE",
                    region="NORTH",
                    sell_out_units=Decimal("100"),
                    sell_in_units=Decimal("102"),
                    promo_flag=week in {5, 6},
                    discount_depth=Decimal("0.20") if week in {5, 6} else Decimal("0"),
                    net_sales_value=Decimal("1000"),
                    gross_sales_value=Decimal("1200"),
                    gross_margin=Decimal("300"),
                    stock_on_hand=Decimal("200"),
                    out_of_stock_flag=False,
                    returns_units=Decimal("0"),
                    source_dataset_id=dataset_id,
                )
            )
        session.commit()
    yield dataset_id
    with SessionLocal() as session:
        case_ids = list(
            session.scalars(
                select(DiagnosticCase.id).where(DiagnosticCase.dataset_id == dataset_id)
            )
        )
        if case_ids:
            session.execute(delete(AuditEvent).where(AuditEvent.entity_id.in_(case_ids)))
        session.execute(delete(DiagnosticCase).where(DiagnosticCase.dataset_id == dataset_id))
        session.execute(
            delete(WeeklyFmcgSale).where(WeeklyFmcgSale.source_dataset_id == dataset_id)
        )
        session.execute(delete(Dataset).where(Dataset.id == dataset_id))
        session.commit()


def login(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "development-admin-only"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def case_payload(dataset_id: uuid.UUID) -> dict[str, object]:
    return {
        "title": "Ready promotion diagnostic",
        "dataset_id": str(dataset_id),
        "sku_id": "SKU-READY",
        "channel": "MODERN_TRADE",
        "region": "NORTH",
        "promotion_start_week": "2026-02-09",
        "promotion_end_week": "2026-02-16",
        "forecast_horizon_weeks": 6,
        "management_concern_note": "Verify growth quality before repeat.",
    }


def test_case_crud_readiness_and_submit_flow(ready_dataset: uuid.UUID) -> None:
    with TestClient(app) as client:
        headers = login(client)
        created = client.post(
            "/api/diagnostic-cases", json=case_payload(ready_dataset), headers=headers
        )
        assert created.status_code == 201
        case_id = created.json()["id"]
        assert created.json()["status"] == "DRAFT"

        patched = client.patch(
            f"/api/diagnostic-cases/{case_id}",
            json={"title": "Updated diagnostic"},
            headers=headers,
        )
        readiness = client.get(f"/api/diagnostic-cases/{case_id}/readiness", headers=headers)
        submitted = client.post(f"/api/diagnostic-cases/{case_id}/submit", headers=headers)
        baseline = client.post(
            f"/api/diagnostic-cases/{case_id}/baseline-calculations",
            json={"method": "RECENT_PRE_PROMO_AVERAGE", "recent_weeks": 4},
            headers=headers,
        )
        forecast_run = client.post(
            f"/api/diagnostic-cases/{case_id}/forecast-runs",
            headers={**headers, "Idempotency-Key": "forecast-test-1"},
        )
        forecast_retry = client.post(
            f"/api/diagnostic-cases/{case_id}/forecast-runs",
            headers={**headers, "Idempotency-Key": "forecast-test-1"},
        )
        forecast_evidence = client.get(
            f"/api/diagnostic-cases/{case_id}/forecast-evidence",
            headers=headers,
        )
        decision_intelligence = client.post(
            f"/api/diagnostic-cases/{case_id}/decision-intelligence",
            headers={**headers, "Idempotency-Key": "decision-test-1"},
        )
        decision_retry = client.post(
            f"/api/diagnostic-cases/{case_id}/decision-intelligence",
            headers={**headers, "Idempotency-Key": "decision-test-1"},
        )
        latest_output = client.get(
            f"/api/diagnostic-cases/{case_id}/decision-intelligence/latest",
            headers=headers,
        )
        original_markdown = latest_output.json()["output_markdown"]
        review = client.post(
            f"/api/diagnostic-cases/{case_id}/reviews",
            headers=headers,
            json={
                "review_status": "VALIDATED_WITH_CHANGES",
                "validated_risk_class": "TEMPORARY_UPLIFT",
                "reviewer_comments": "Aligned actuals support the corrected class.",
                "requested_evidence": [],
                "final_decision_note": "Human validation completed; no action was executed.",
            },
        )
        reviews = client.get(f"/api/diagnostic-cases/{case_id}/reviews", headers=headers)
        feedback = client.post(
            f"/api/diagnostic-cases/{case_id}/feedback",
            headers=headers,
            json={
                "feedback_type": "POST_REVIEW_OUTCOME",
                "observed_outcome": {"window": "4 weeks"},
                "classification_correct": False,
                "simulation_useful": True,
                "notes": "Correction stored separately from the draft.",
            },
        )
        exports = {
            export_format: client.post(
                f"/api/diagnostic-cases/{case_id}/export?format={export_format}",
                headers=headers,
            )
            for export_format in ("json", "markdown", "pdf")
        }
        reviewed_output = client.get(
            f"/api/diagnostic-cases/{case_id}/decision-intelligence/latest",
            headers=headers,
        )
        admin_health = client.get("/api/admin/health", headers=headers)
        admin_config = client.get("/api/admin/configuration-metadata", headers=headers)
        audit_page = client.get("/api/admin/audit-events", headers=headers)
        listed = client.get("/api/diagnostic-cases?page=1&page_size=10", headers=headers)

    assert patched.status_code == 200
    assert readiness.json() == {
        "ready": True,
        "reasons": [],
        "series_observation_count": 12,
        "status": "DRAFT",
    }
    assert submitted.status_code == 200
    assert submitted.json()["status"] == "READY_FOR_FORECAST"
    assert baseline.status_code == 201
    assert baseline.json()["baseline_method"] == "RECENT_PRE_PROMO_AVERAGE"
    assert len(baseline.json()["baseline_values_json"]["output_values"]) == 6
    assert forecast_run.status_code == 201
    assert forecast_run.json()["run_status"] == "COMPLETED"
    assert forecast_run.json()["adapter_name"] == "mock"
    assert forecast_retry.json()["id"] == forecast_run.json()["id"]
    assert forecast_evidence.status_code == 200
    assert forecast_evidence.json()["forecast_horizon"] == 6
    assert decision_intelligence.status_code == 201
    assert decision_intelligence.json()["human_review_status"] == "PENDING"
    assert decision_retry.json()["id"] == decision_intelligence.json()["id"]
    assert len(decision_intelligence.json()["output_json"]["decision_simulation"]) == 7
    assert latest_output.status_code == 200
    assert latest_output.json()["id"] == decision_intelligence.json()["id"]
    assert review.status_code == 201
    assert review.json()["review_status"] == "VALIDATED_WITH_CHANGES"
    assert reviews.status_code == 200 and len(reviews.json()) == 1
    assert feedback.status_code == 201
    assert feedback.json()["classification_correct"] is False
    assert exports["json"].json()["review_label"] == "HUMAN REVIEW COMPLETED"
    assert "HUMAN REVIEW COMPLETED" in exports["markdown"].text
    assert exports["pdf"].content.startswith(b"%PDF-1.4")
    assert reviewed_output.json()["output_markdown"] == original_markdown
    assert reviewed_output.json()["human_review_status"] == "VALIDATED_WITH_CHANGES"
    assert admin_health.json()["database"] == "reachable"
    assert admin_config.json()["secrets_included"] is False
    assert audit_page.status_code == 200 and audit_page.json()["total"] > 0
    assert listed.status_code == 200
    assert any(item["id"] == case_id for item in listed.json()["items"])
    with SessionLocal() as session:
        assert (
            session.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.entity_id == uuid.UUID(case_id))
            )
            == 3
        )


def test_invalid_scope_cannot_be_submitted(ready_dataset: uuid.UUID) -> None:
    payload = case_payload(ready_dataset)
    payload["sku_id"] = "SKU-MISSING"
    with TestClient(app) as client:
        headers = login(client)
        created = client.post("/api/diagnostic-cases", json=payload, headers=headers)
        response = client.post(
            f"/api/diagnostic-cases/{created.json()['id']}/submit", headers=headers
        )

    assert response.status_code == 422
    assert "selected series is not forecast-eligible" in response.json()["detail"]["reasons"]


def test_horizon_and_promotion_window_are_enforced(ready_dataset: uuid.UUID) -> None:
    payload = case_payload(ready_dataset)
    payload["forecast_horizon_weeks"] = 9
    with TestClient(app) as client:
        response = client.post("/api/diagnostic-cases", json=payload, headers=login(client))
    assert response.status_code == 422


def test_illegal_status_transition_is_rejected(ready_dataset: uuid.UUID) -> None:
    with SessionLocal() as session:
        admin = session.get(User, uuid.UUID("00000000-0000-0000-0000-000000000001"))
        assert admin
        case = DiagnosticCase(
            title="Transition test",
            dataset_id=ready_dataset,
            sku_id="SKU-READY",
            channel="MODERN_TRADE",
            region="NORTH",
            promotion_start_week=date(2026, 2, 9),
            promotion_end_week=date(2026, 2, 16),
            forecast_horizon_weeks=6,
            status=CaseStatus.DRAFT,
            created_by=admin.id,
        )
        session.add(case)
        session.flush()
        assert assess_readiness(session, case).ready
        with pytest.raises(InvalidCaseTransitionError):
            transition_case(case, CaseStatus.FORECASTING)
