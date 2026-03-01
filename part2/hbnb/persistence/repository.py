"""Abstract repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Repository(ABC):
    """Defines persistence operations expected by the facade."""

    @abstractmethod
    def add(self, obj: Any) -> Any:
        """Store and return an object."""

    @abstractmethod
    def get(self, model_name: str, obj_id: str) -> Any | None:
        """Get one object by model and id."""

    @abstractmethod
    def get_all(self, model_name: str | None = None) -> list[Any]:
        """Get all objects, optionally filtered by model."""

    @abstractmethod
    def update(self, obj: Any) -> Any:
        """Update an existing object."""

    @abstractmethod
    def delete(self, model_name: str, obj_id: str) -> bool:
        """Delete one object by model and id."""

    @abstractmethod
    def get_by_attribute(self, model_name: str, **filters: Any) -> list[Any]:
        """Return model objects matching exact attribute filters."""
