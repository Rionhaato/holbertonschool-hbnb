"""Amenity entity."""

from __future__ import annotations

from .base_model import BaseModel

try:
    from ..extensions import db
except ImportError:
    from extensions import db

if db is not None:
    SQLAlchemyModel = db.Model
else:
    class SQLAlchemyModel:
        """Fallback base when Flask-SQLAlchemy is unavailable."""

        pass


class Amenity(BaseModel, SQLAlchemyModel):
    """Represents a place amenity."""

    __tablename__ = "amenities"

    if db is not None:
        _name = db.Column("name", db.String(50), nullable=False, unique=True)
        places = db.relationship(
            "Place",
            secondary="place_amenity",
            back_populates="amenities",
            lazy=True,
        )

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
