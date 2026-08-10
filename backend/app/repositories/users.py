from dataclasses import dataclass
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.auth import UserRole
from app.models.entities import User


@dataclass(frozen=True)
class UserCredentialRecord:
    id: str
    email: str
    display_name: str
    role: UserRole
    password_hash: str
    is_active: bool = True


class UserRepository(Protocol):
    def get_by_email(self, email: str) -> UserCredentialRecord | None: ...

    def get_by_id(self, user_id: str) -> UserCredentialRecord | None: ...


class InMemoryUserRepository:
    def __init__(self, users: list[UserCredentialRecord] | None = None) -> None:
        self._by_id = {user.id: user for user in users or []}
        self._by_email = {user.email.casefold(): user for user in users or []}

    def get_by_email(self, email: str) -> UserCredentialRecord | None:
        return self._by_email.get(email.casefold())

    def get_by_id(self, user_id: str) -> UserCredentialRecord | None:
        return self._by_id.get(user_id)


class SqlUserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_email(self, email: str) -> UserCredentialRecord | None:
        user = self.session.scalar(select(User).where(User.email == email.casefold()))
        return self._record(user)

    def get_by_id(self, user_id: str) -> UserCredentialRecord | None:
        user = self.session.get(User, user_id)
        return self._record(user)

    @staticmethod
    def _record(user: User | None) -> UserCredentialRecord | None:
        if user is None:
            return None
        return UserCredentialRecord(
            id=str(user.id),
            email=user.email,
            display_name=user.display_name,
            role=user.role,
            password_hash=user.password_hash,
            is_active=user.is_active,
        )
