import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.api.auth import router as auth_router
from app.api.baselines import router as baselines_router
from app.api.datasets import router as datasets_router
from app.api.decision_intelligence import router as decision_intelligence_router
from app.api.diagnostic_cases import router as diagnostic_cases_router
from app.api.forecast_runs import router as forecast_runs_router
from app.config import get_settings
from app.database import SessionLocal
from app.domain.auth import UserRole
from app.models.entities import User
from app.security import password_hash

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    with SessionLocal() as session:
        existing = session.scalar(select(User).where(User.email == settings.bootstrap_admin_email))
        if existing is None:
            session.add(
                User(
                    id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                    email=settings.bootstrap_admin_email.casefold(),
                    display_name="Development Administrator",
                    role=UserRole.ADMIN,
                    password_hash=password_hash.hash(settings.bootstrap_admin_password),
                )
            )
            session.commit()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Human-reviewed, forecast-augmented FMCG growth-quality diagnostics.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Correlation-ID"],
)

app.include_router(auth_router)
app.include_router(baselines_router)
app.include_router(datasets_router)
app.include_router(decision_intelligence_router)
app.include_router(diagnostic_cases_router)
app.include_router(forecast_runs_router)


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "fmcg-growth-quality-diagnostic-api",
        "timestamp": datetime.now(UTC).isoformat(),
    }
