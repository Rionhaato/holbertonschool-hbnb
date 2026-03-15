"""User entity."""

from __future__ import annotations

import re

from .base_model import BaseModel

try:
    from ..extensions import bcrypt
except ImportError:
    from extensions import bcrypt


class User(BaseModel):
    """Represents an application user."""

    EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.first_name = kwargs.get("first_name", "")
        self.last_name = kwargs.get("last_name", "")
        self.email = kwargs.get("email", "")
        self.password = kwargs.get("password", "")
        self.is_admin = kwargs.get("is_admin", False)

    @staticmethod
    def _clean_name(value: str, field: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field} must be a string")
        cleaned = value.strip()
        if len(cleaned) > 50:
            raise ValueError(f"{field} must be 50 characters or less")
        return cleaned

    @staticmethod
    def _ensure_bcrypt() -> None:
        if bcrypt is None:
            raise RuntimeError("Flask-Bcrypt is required to hash passwords")

    @staticmethod
    def _looks_hashed(value: str) -> bool:
        return value.startswith("$2a$") or value.startswith("$2b$") or value.startswith("$2y$")

    @property
    def first_name(self) -> str:
        return self._first_name

    @first_name.setter
    def first_name(self, value: str) -> None:
        self._first_name = self._clean_name(value, "first_name")

    @property
    def last_name(self) -> str:
        return self._last_name

    @last_name.setter
    def last_name(self, value: str) -> None:
        self._last_name = self._clean_name(value, "last_name")

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("email must be a string")
        cleaned = value.strip().lower()
        if not cleaned:
            raise ValueError("email is required")
        if not self.EMAIL_PATTERN.match(cleaned):
            raise ValueError("email format is invalid")
        self._email = cleaned

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("password must be a string")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("password is required")

        if self._looks_hashed(cleaned):
            self._password = cleaned
            return

        self._ensure_bcrypt()
        self._password = bcrypt.generate_password_hash(cleaned).decode("utf-8")

    @property
    def is_admin(self) -> bool:
        return self._is_admin

    @is_admin.setter
    def is_admin(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("is_admin must be a boolean")
        self._is_admin = value

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update(
            {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "email": self.email,
                "is_admin": self.is_admin,
            }
        )
        return data

    def check_password(self, plain_password: str) -> bool:
        """Verify a plaintext password against the stored hash."""
        if not isinstance(plain_password, str):
            raise TypeError("password must be a string")
        self._ensure_bcrypt()
        return bcrypt.check_password_hash(self.password, plain_password)
