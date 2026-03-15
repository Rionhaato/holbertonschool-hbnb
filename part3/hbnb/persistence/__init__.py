"""Persistence adapters."""

from .in_memory_repository import InMemoryRepository
from .repository import Repository
from .sqlalchemy_repository import SQLAlchemyRepository
from .user_repository import UserRepository

__all__ = ["Repository", "InMemoryRepository", "SQLAlchemyRepository", "UserRepository"]
