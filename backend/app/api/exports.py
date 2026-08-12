import json
import textwrap
import uuid
from datetime import UTC, datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.auth import REVIEWER_ROLES, AuthenticatedUser, UserRole
from app.domain.executive_outputs import FINAL_REVIEW_STATEMENT
from app.models.entities import AuditEvent, DiagnosticCase, ExecutiveOutput, ReviewStatus
from app.security import require_roles

router = APIRouter(tags=["exports"])
EXPORT_ROLES = (
    UserRole.ADMIN,
    UserRole.COMMERCIAL_DIRECTOR,
    UserRole.READ_ONLY_EXECUTIVE,
    *REVIEWER_ROLES,
)


def _latest(session: Session, case_id: uuid.UUID) -> tuple[DiagnosticCase, ExecutiveOutput]:
    case = session.get(DiagnosticCase, case_id)
    output = session.scalar(
        select(ExecutiveOutput)
        .where(ExecutiveOutput.diagnostic_case_id == case_id)
        .order_by(ExecutiveOutput.generated_at.desc())
    )
    if case is None or output is None:
        raise HTTPException(status_code=404, detail="Executive output not found")
    return case, output


def _review_label(status: ReviewStatus) -> str:
    return (
        "HUMAN REVIEW COMPLETED"
        if status in {ReviewStatus.VALIDATED, ReviewStatus.VALIDATED_WITH_CHANGES}
        else "DRAFT — HUMAN REVIEW PENDING"
    )


def _markdown(case: DiagnosticCase, output: ExecutiveOutput) -> str:
    original = output.output_markdown
    original = original.replace(
        "DRAFT — HUMAN REVIEW PENDING", _review_label(output.human_review_status)
    )
    return f"Case ID: `{case.id}`\n\n{original}"


def _simple_pdf(lines: list[str]) -> bytes:
    escaped = [line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") for line in lines]
    commands = ["BT", "/F1 10 Tf", "48 760 Td", "13 TL"]
    for index, line in enumerate(escaped[:52]):
        if index:
            commands.append("T*")
        commands.append(f"({line[:105]}) Tj")
    commands.append("ET")
    stream = "\n".join(commands).encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    )
    return bytes(pdf)


@router.post("/api/diagnostic-cases/{case_id}/export")
def export_case(
    case_id: uuid.UUID,
    actor: Annotated[AuthenticatedUser, Depends(require_roles(*EXPORT_ROLES))],
    session: Annotated[Session, Depends(get_db)],
    format: Annotated[Literal["json", "markdown", "pdf"], Query()] = "json",
) -> Response:
    case, output = _latest(session, case_id)
    label = _review_label(output.human_review_status)
    filename = f"fmcg-diagnostic-{case.id}.{('md' if format == 'markdown' else format)}"
    if format == "json":
        body = json.dumps(
            {
                "product": "VAI Forecast-Augmented Growth Quality Diagnostic",
                "case_id": str(case.id),
                "generated_at": output.generated_at.isoformat(),
                "review_label": label,
                "review_status": output.human_review_status.value,
                "output_version": output.output_version,
                "output": output.output_json,
            },
            indent=2,
            default=str,
        ).encode()
        media_type = "application/json"
    elif format == "markdown":
        body = _markdown(case, output).encode()
        media_type = "text/markdown; charset=utf-8"
    else:
        data = output.output_json
        text = [
            "VAI Forecast-Augmented Growth Quality Diagnostic",
            label,
            f"Case identifier: {case.id}",
            f"Generated: {datetime.now(UTC).isoformat()}",
            "",
            "GROWTH SIGNAL SUMMARY",
            str(data.get("growth_signal_summary", "")),
            "",
            "RISK / PRIORITY / OWNER / CONFIDENCE",
            str(data.get("risk_classification", {})),
            f"Priority: {data.get('priority')}",
            f"Owner: {data.get('recommended_human_owner')}",
            f"Confidence: {data.get('evidence_confidence')}",
            "",
            "INVESTIGATION AND SIMULATIONS",
            *textwrap.wrap(str(data.get("investigation_plan", [])), 100),
            *textwrap.wrap(str(data.get("decision_simulation", [])), 100),
            "",
            FINAL_REVIEW_STATEMENT,
        ]
        body = _simple_pdf(text)
        media_type = "application/pdf"
    session.add(
        AuditEvent(
            actor_id=uuid.UUID(actor.id),
            event_type="EXECUTIVE_OUTPUT_EXPORTED",
            entity_type="executive_output",
            entity_id=output.id,
            before_json=None,
            after_json={"format": format, "review_status": output.human_review_status.value},
            correlation_id=str(uuid.uuid4()),
        )
    )
    session.commit()
    return Response(
        body,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
