"""Place entity."""

from __future__ import annotations

from .base_model import BaseModel

try:
    from ..extensions import db
except ImportError:
    from extensions import db

try:
    from sqlalchemy.ext.mutable import MutableList
except ModuleNotFoundError:
    MutableList = None

if db is not None:
    SQLAlchemyModel = db.Model
else:
    class SQLAlchemyModel:
        """Fallback base when Flask-SQLAlchemy is unavailable."""

        pass


class Place(BaseModel, SQLAlchemyModel):
    """Represents a place listed in HBnB."""

    __tablename__ = "places"

    if db is not None:
        _title = db.Column("title", db.String(100), nullable=False)
        _description = db.Column("description", db.Text, nullable=False, default="")
        _price = db.Column("price", db.Float, nullable=False, default=0.0)
        _latitude = db.Column("latitude", db.Float, nullable=False, default=0.0)
        _longitude = db.Column("longitude", db.Float, nullable=False, default=0.0)
        _owner_id = db.Column("owner_id", db.String(36), nullable=False, index=True)
        if MutableList is not None:
            _amenity_ids = db.Column(
                "amenity_ids",
                MutableList.as_mutable(db.JSON),
                nullable=False,
                default=list,
            )
        else:
            _amenity_ids = db.Column("amenity_ids", db.JSON, nullable=False, default=list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = kwargs.get("title", "")
        self.description = kwargs.get("description", "")
        self.price = kwargs.get("price", 0.0)
        self.latitude = kwargs.get("latitude", 0.0)
        self.longitude = kwargs.get("longitude", 0.0)
        self.owner_id = kwargs.get("owner_id")
        self.amenity_ids = kwargs.get("amenity_ids", [])

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("title must be a string")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("title is required")
        if len(cleaned) > 100:
            raise ValueError("title must be 100 characters or less")
        self._title = cleaned

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("description must be a string")
        self._description = value.strip()

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float | int) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("price must be numeric")
        price = float(value)
        if price < 0:
            raise ValueError("price must be greater than or equal to 0")
        self._price = price

    @property
    def latitude(self) -> float:
        return self._latitude

    @latitude.setter
    def latitude(self, value: float | int) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("latitude must be numeric")
        latitude = float(value)
        if latitude < -90 or latitude > 90:
            raise ValueError("latitude must be between -90 and 90")
        self._latitude = latitude

    @property
    def longitude(self) -> float:
        return self._longitude

    @longitude.setter
    def longitude(self, value: float | int) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("longitude must be numeric")
        longitude = float(value)
        if longitude < -180 or longitude > 180:
            raise ValueError("longitude must be between -180 and 180")
        self._longitude = longitude

    @property
    def owner_id(self) -> str:
        return self._owner_id

    @owner_id.setter
    def owner_id(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("owner_id must be a string")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("owner_id is required")
        self._owner_id = cleaned

    @property
    def amenity_ids(self) -> list[str]:
        return list(self._amenity_ids)

    @amenity_ids.setter
    def amenity_ids(self, value: list[str]) -> None:
        if not isinstance(value, list):
            raise TypeError("amenity_ids must be a list")
        normalized = []
        for amenity_id in value:
            if not isinstance(amenity_id, str):
                raise TypeError("amenity_ids must only contain strings")
            cleaned = amenity_id.strip()
            if not cleaned:
                raise ValueError("amenity_ids cannot contain empty values")
            if cleaned not in normalized:
                normalized.append(cleaned)
        self._amenity_ids = normalized

    def add_amenity(self, amenity_id: str) -> None:
        """Attach an amenity id to the place."""
        if not isinstance(amenity_id, str):
            raise TypeError("amenity_id must be a string")
        cleaned = amenity_id.strip()
        if not cleaned:
            raise ValueError("amenity_id cannot be empty")
        if cleaned not in self._amenity_ids:
            self._amenity_ids.append(cleaned)
            self.touch()

    def remove_amenity(self, amenity_id: str) -> bool:
        """Detach an amenity id from the place."""
        if amenity_id in self._amenity_ids:
            self._amenity_ids.remove(amenity_id)
            self.touch()
            return True
        return False

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update(
            {
                "title": self.title,
                "description": self.description,
                "price": self.price,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "owner_id": self.owner_id,
                "amenity_ids": self.amenity_ids,
            }
        )
        return data
