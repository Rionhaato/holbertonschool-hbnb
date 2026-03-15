"""HBnB Facade implementation."""

from __future__ import annotations

from typing import Any

from ..models import Amenity, Place, Review, User
from ..persistence import Repository


class HBnBFacade:
    """Facade that exposes business operations used by the API layer."""

    def __init__(self, repository: Repository):
        self.repository = repository

    def _create(self, model_cls: type, data: dict[str, Any]):
        obj = model_cls(**data)
        return self.repository.add(obj)

    def _get(self, model_cls: type, obj_id: str):
        return self.repository.get(model_cls.__name__, obj_id)

    def _get_all(self, model_cls: type):
        return self.repository.get_all(model_cls.__name__)

    def _update(self, model_cls: type, obj_id: str, data: dict[str, Any]):
        obj = self._get(model_cls, obj_id)
        if obj is None:
            return None

        obj.update(data)
        return self.repository.update(obj)

    def _delete(self, model_cls: type, obj_id: str) -> bool:
        return self.repository.delete(model_cls.__name__, obj_id)

    def create_user(self, data: dict[str, Any]) -> User:
        email = data.get("email", "").strip().lower()
        if not email:
            raise ValueError("email is required")

        existing = self.repository.get_by_attribute("User", email=email)
        if existing:
            raise ValueError("email already exists")

        data = dict(data)
        data["email"] = email
        return self._create(User, data)

    def get_user(self, user_id: str) -> User | None:
        return self._get(User, user_id)

    def get_users(self) -> list[User]:
        return self._get_all(User)

    def get_user_by_email(self, email: str) -> User | None:
        normalized_email = email.strip().lower()
        matches = self.repository.get_by_attribute("User", email=normalized_email)
        return matches[0] if matches else None

    def authenticate_user(self, email: str, password: str) -> User | None:
        user = self.get_user_by_email(email)
        if user is None:
            return None
        if not user.check_password(password):
            return None
        return user

    def update_user(self, user_id: str, data: dict[str, Any]) -> User | None:
        if "email" in data:
            new_email = data["email"].strip().lower()
            duplicates = self.repository.get_by_attribute("User", email=new_email)
            if any(user.id != user_id for user in duplicates):
                raise ValueError("email already exists")
            data = dict(data)
            data["email"] = new_email
        return self._update(User, user_id, data)

    def delete_user(self, user_id: str) -> bool:
        return self._delete(User, user_id)

    def create_amenity(self, data: dict[str, Any]) -> Amenity:
        name = data.get("name", "").strip()
        if not name:
            raise ValueError("name is required")
        data = dict(data)
        data["name"] = name
        return self._create(Amenity, data)

    def get_amenity(self, amenity_id: str) -> Amenity | None:
        return self._get(Amenity, amenity_id)

    def get_amenities(self) -> list[Amenity]:
        return self._get_all(Amenity)

    def update_amenity(self, amenity_id: str, data: dict[str, Any]) -> Amenity | None:
        return self._update(Amenity, amenity_id, data)

    def delete_amenity(self, amenity_id: str) -> bool:
        return self._delete(Amenity, amenity_id)

    def create_place(self, data: dict[str, Any]) -> Place:
        owner_id = data.get("owner_id")
        if not owner_id or self.get_user(owner_id) is None:
            raise ValueError("owner_id must reference an existing user")

        amenity_ids = data.get("amenity_ids", [])
        for amenity_id in amenity_ids:
            if self.get_amenity(amenity_id) is None:
                raise ValueError(f"amenity_id not found: {amenity_id}")

        return self._create(Place, data)

    def get_place(self, place_id: str) -> Place | None:
        return self._get(Place, place_id)

    def get_places(self) -> list[Place]:
        return self._get_all(Place)

    def update_place(self, place_id: str, data: dict[str, Any]) -> Place | None:
        if "owner_id" in data and self.get_user(data["owner_id"]) is None:
            raise ValueError("owner_id must reference an existing user")

        if "amenity_ids" in data:
            for amenity_id in data["amenity_ids"]:
                if self.get_amenity(amenity_id) is None:
                    raise ValueError(f"amenity_id not found: {amenity_id}")

        return self._update(Place, place_id, data)

    def delete_place(self, place_id: str) -> bool:
        return self._delete(Place, place_id)

    def create_review(self, data: dict[str, Any]) -> Review:
        if self.get_user(data.get("user_id", "")) is None:
            raise ValueError("user_id must reference an existing user")
        if self.get_place(data.get("place_id", "")) is None:
            raise ValueError("place_id must reference an existing place")
        return self._create(Review, data)

    def get_review(self, review_id: str) -> Review | None:
        return self._get(Review, review_id)

    def get_reviews(self) -> list[Review]:
        return self._get_all(Review)

    def get_reviews_by_place(self, place_id: str) -> list[Review]:
        return self.repository.get_by_attribute("Review", place_id=place_id)

    def update_review(self, review_id: str, data: dict[str, Any]) -> Review | None:
        return self._update(Review, review_id, data)

    def delete_review(self, review_id: str) -> bool:
        return self._delete(Review, review_id)
