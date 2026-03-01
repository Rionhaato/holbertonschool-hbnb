"""Persistence adapters."""

from .in_memory_repository import InMemoryRepository
from .repository import Repository

__all__ = ["Repository", "InMemoryRepository"]
