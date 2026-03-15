"""Persistence adapters."""

from .in_memory_repository import InMemoryRepository
from .repository import Repository
from .sqlalchemy_repository import SQLAlchemyRepository

__all__ = ["Repository", "InMemoryRepository", "SQLAlchemyRepository"]
