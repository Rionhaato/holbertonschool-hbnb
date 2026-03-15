"""HBnB Facade implementation."""

from __future__ import annotations

from typing import Any

from ..models import Amenity, Place, Review, User
from ..persistence import Repository


class HBnBFacade:
    """Facade that exposes business operations used by the API layer."""

    def __init__(self, repository: Repository, user_repository: Repository | None = None):
        self.repository = repository
        self.user_repository = user_repository or repository

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

    @staticmethod
    def _assign_place_amenities(place: Place, amenities: list[Amenity]) -> None:
        """Attach amenity relationships when the Place model supports them."""
        if hasattr(place, "amenities"):
            place.amenities = list(amenities)
            if hasattr(place, "_amenity_ids_cache"):
                place._amenity_ids_cache = [amenity.id for amenity in amenities]

    def create_user(self, data: dict[str, Any]) -> User:
        email = data.get("email", "").strip().lower()
        if not email:
            raise ValueError("email is required")

        existing = self.get_user_by_email(email)
        if existing is not None:
            raise ValueError("email already exists")

        data = dict(data)
        data["email"] = email
        user = User(**data)
        return self.user_repository.add(user)

    def get_user(self, user_id: str) -> User | None:
        return self.user_repository.get(User.__name__, user_id)

    def get_users(self) -> list[User]:
        return self.user_repository.get_all(User.__name__)

    def get_user_by_email(self, email: str) -> User | None:
        normalized_email = email.strip().lower()
        if hasattr(self.user_repository, "get_by_email"):
            return self.user_repository.get_by_email(normalized_email)
        matches = self.user_repository.get_by_attribute("User", email=normalized_email)
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
            email_filter = "_email" if hasattr(self.user_repository, "get_by_email") else "email"
            duplicates = self.user_repository.get_by_attribute("User", **{email_filter: new_email})
            if any(user.id != user_id for user in duplicates):
                raise ValueError("email already exists")
            data = dict(data)
            data["email"] = new_email

        user = self.get_user(user_id)
        if user is None:
            return None

        user.update(data)
        return self.user_repository.update(user)

    def delete_user(self, user_id: str) -> bool:
        return self.user_repository.delete(User.__name__, user_id)

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
        amenities = []
        for amenity_id in amenity_ids:
            amenity = self.get_amenity(amenity_id)
            if amenity is None:
                raise ValueError(f"amenity_id not found: {amenity_id}")
            amenities.append(amenity)

        place = Place(**data)
        self._assign_place_amenities(place, amenities)
        return self.repository.add(place)

    def get_place(self, place_id: str) -> Place | None:
        return self._get(Place, place_id)

    def get_places(self) -> list[Place]:
        return self._get_all(Place)

    def update_place(self, place_id: str, data: dict[str, Any]) -> Place | None:
        if "owner_id" in data and self.get_user(data["owner_id"]) is None:
            raise ValueError("owner_id must reference an existing user")

        if "amenity_ids" in data:
            amenities = []
            for amenity_id in data["amenity_ids"]:
                amenity = self.get_amenity(amenity_id)
                if amenity is None:
                    raise ValueError(f"amenity_id not found: {amenity_id}")
                amenities.append(amenity)
        else:
            amenities = None

        place = self.get_place(place_id)
        if place is None:
            return None

        place.update(data)
        if amenities is not None:
            self._assign_place_amenities(place, amenities)
        return self.repository.update(place)

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

    def get_review_by_user_and_place(self, user_id: str, place_id: str) -> Review | None:
        matches = self.repository.get_by_attribute(
            "Review",
            user_id=user_id,
            place_id=place_id,
        )
        return matches[0] if matches else None

    def update_review(self, review_id: str, data: dict[str, Any]) -> Review | None:
        return self._update(Review, review_id, data)

    def delete_review(self, review_id: str) -> bool:
        return self._delete(Review, review_id)
