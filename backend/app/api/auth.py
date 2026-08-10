from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import Settings, get_settings
from app.domain.auth import REVIEWER_ROLES, AuthenticatedUser, UserRole
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.security import AuthService, get_auth_service, get_current_user, require_roles

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    user = service.authenticate(request.email, request.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(
        access_token=service.issue_token(user),
        expires_in_seconds=settings.access_token_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
def me(user: Annotated[AuthenticatedUser, Depends(get_current_user)]) -> UserResponse:
    return UserResponse(**user.__dict__)


@router.get("/admin-access-check", response_model=UserResponse)
def admin_access_check(
    user: Annotated[AuthenticatedUser, Depends(require_roles(UserRole.ADMIN))],
) -> UserResponse:
    return UserResponse(**user.__dict__)


@router.get("/reviewer-access-check", response_model=UserResponse)
def reviewer_access_check(
    user: Annotated[
        AuthenticatedUser,
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.COMMERCIAL_DIRECTOR,
                *REVIEWER_ROLES,
            )
        ),
    ],
) -> UserResponse:
    return UserResponse(**user.__dict__)
