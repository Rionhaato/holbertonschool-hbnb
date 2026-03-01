"""Amenity entity."""

from .base_model import BaseModel


class Amenity(BaseModel):
    """Represents a place amenity."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get("name", "")

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("name must be a string")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("name is required")
        if len(cleaned) > 50:
            raise ValueError("name must be 50 characters or less")
        self._name = cleaned

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"name": self.name})
        return data
