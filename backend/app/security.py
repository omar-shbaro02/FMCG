from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.domain.auth import AuthenticatedUser, UserRole
from app.repositories.users import SqlUserRepository, UserCredentialRecord, UserRepository

password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer(auto_error=False)


class AuthService:
    def __init__(self, repository: UserRepository, settings: Settings) -> None:
        self.repository = repository
        self.settings = settings

    def authenticate(self, email: str, password: str) -> AuthenticatedUser | None:
        record = self.repository.get_by_email(email)
        if (
            record is None
            or not record.is_active
            or not password_hash.verify(password, record.password_hash)
        ):
            return None
        return self._to_user(record)

    def issue_token(self, user: AuthenticatedUser) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": user.id,
            "email": user.email,
            "role": user.role.value,
            "iat": now,
            "exp": now + timedelta(minutes=self.settings.access_token_minutes),
        }
        return jwt.encode(payload, self.settings.secret_key, algorithm="HS256")

    def resolve_token(self, token: str) -> AuthenticatedUser | None:
        try:
            payload = jwt.decode(token, self.settings.secret_key, algorithms=["HS256"])
            user_id = str(payload["sub"])
        except (InvalidTokenError, KeyError):
            return None
        record = self.repository.get_by_id(user_id)
        if record is None or not record.is_active:
            return None
        return self._to_user(record)

    @staticmethod
    def _to_user(record: UserCredentialRecord) -> AuthenticatedUser:
        return AuthenticatedUser(
            id=record.id,
            email=record.email,
            display_name=record.display_name,
            role=record.role,
            is_active=record.is_active,
        )


def get_auth_service(
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[Session, Depends(get_db)],
) -> AuthService:
    return AuthService(SqlUserRepository(session), settings)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthenticatedUser:
    user = service.resolve_token(credentials.credentials) if credentials else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid authentication is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_roles(*roles: UserRole) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    allowed = frozenset(roles)

    def dependency(
        user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    ) -> AuthenticatedUser:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role is not permitted",
            )
        return user

    return dependency
