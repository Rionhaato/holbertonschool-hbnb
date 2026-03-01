"""In-memory repository implementation for Part 2."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .repository import Repository


class InMemoryRepository(Repository):
    """Stores objects by model name and object id."""

    def __init__(self):
        self._storage: dict[str, dict[str, Any]] = defaultdict(dict)

    @staticmethod
    def _model_name(obj_or_name: Any) -> str:
        if isinstance(obj_or_name, str):
            return obj_or_name
        return obj_or_name.__class__.__name__

    def add(self, obj: Any) -> Any:
        model_name = self._model_name(obj)
        self._storage[model_name][obj.id] = obj
        return obj

    def get(self, model_name: str, obj_id: str) -> Any | None:
        return self._storage.get(model_name, {}).get(obj_id)

    def get_all(self, model_name: str | None = None) -> list[Any]:
        if model_name is not None:
            return list(self._storage.get(model_name, {}).values())

        all_objects = []
        for objects_by_id in self._storage.values():
            all_objects.extend(objects_by_id.values())
        return all_objects

    def update(self, obj: Any) -> Any:
        model_name = self._model_name(obj)
        if obj.id not in self._storage.get(model_name, {}):
            raise KeyError(f"{model_name} with id {obj.id} does not exist")
        self._storage[model_name][obj.id] = obj
        return obj

    def delete(self, model_name: str, obj_id: str) -> bool:
        model_bucket = self._storage.get(model_name, {})
        if obj_id not in model_bucket:
            return False
        del model_bucket[obj_id]
        return True

    def get_by_attribute(self, model_name: str, **filters: Any) -> list[Any]:
        result = []
        for obj in self._storage.get(model_name, {}).values():
            if all(getattr(obj, key, None) == value for key, value in filters.items()):
                result.append(obj)
        return result
