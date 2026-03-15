"""User-specific SQLAlchemy repository."""

from __future__ import annotations

from ..models import User
from .sqlalchemy_repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    """Repository for SQLAlchemy-backed user persistence."""

    def __init__(self, db):
        super().__init__(db, model_map={"User": User})

    def get_by_email(self, email: str) -> User | None:
        matches = self.get_by_attribute("User", _email=email)
        return matches[0] if matches else None
