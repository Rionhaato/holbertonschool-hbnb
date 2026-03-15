"""SQLAlchemy-backed repository implementation."""

from __future__ import annotations

from typing import Any

from .repository import Repository


class SQLAlchemyRepository(Repository):
    """Repository implementation backed by Flask-SQLAlchemy."""

    def __init__(self, db, model_map: dict[str, type] | None = None):
        if db is None:
            raise RuntimeError("Flask-SQLAlchemy is required for SQLAlchemyRepository")
        self.db = db
        self.model_map = dict(model_map or {})

    def register_model(self, model_name: str, model_cls: type) -> None:
        """Register a mapped SQLAlchemy model for a domain name."""
        self.model_map[model_name] = model_cls

    def _resolve_model(self, model_name: str) -> type:
        model_cls = self.model_map.get(model_name)
        if model_cls is None:
            raise KeyError(f"No SQLAlchemy model registered for {model_name}")
        return model_cls

    def add(self, obj: Any) -> Any:
        self.db.session.add(obj)
        self.db.session.commit()
        return obj

    def get(self, model_name: str, obj_id: str) -> Any | None:
        model_cls = self._resolve_model(model_name)
        return self.db.session.get(model_cls, obj_id)

    def get_all(self, model_name: str | None = None) -> list[Any]:
        if model_name is None:
            results: list[Any] = []
            for registered_name in self.model_map:
                results.extend(self.get_all(registered_name))
            return results

        model_cls = self._resolve_model(model_name)
        return self.db.session.query(model_cls).all()

    def update(self, obj: Any) -> Any:
        merged = self.db.session.merge(obj)
        self.db.session.commit()
        return merged

    def delete(self, model_name: str, obj_id: str) -> bool:
        obj = self.get(model_name, obj_id)
        if obj is None:
            return False
        self.db.session.delete(obj)
        self.db.session.commit()
        return True

    def get_by_attribute(self, model_name: str, **filters: Any) -> list[Any]:
        model_cls = self._resolve_model(model_name)
        return self.db.session.query(model_cls).filter_by(**filters).all()
