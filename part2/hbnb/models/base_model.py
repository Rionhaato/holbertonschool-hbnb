"""Base model for all business entities."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4


class BaseModel:
    """Base domain object with id and timestamps."""

    def __init__(self, **kwargs):
        self.id = self._validate_uuid(kwargs.get("id", str(uuid4())))
        self.created_at = self._coerce_datetime(kwargs.get("created_at", self._utcnow()))
        self.updated_at = self._coerce_datetime(kwargs.get("updated_at", self._utcnow()))

    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _validate_uuid(value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("id must be a string")
        try:
            UUID(value)
        except ValueError as exc:
            raise ValueError("id must be a valid UUID string") from exc
        return value

    @staticmethod
    def _coerce_datetime(value: datetime | str) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        raise TypeError("datetime value must be a datetime or ISO datetime string")

    def touch(self) -> None:
        self.updated_at = self._utcnow()

    def update(self, data: dict) -> None:
        """Apply updates while preserving immutable base fields."""
        immutable = {"id", "created_at", "updated_at"}
        for key, value in data.items():
            if key in immutable:
                continue
            if hasattr(self, key):
                setattr(self, key, value)
        self.touch()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
