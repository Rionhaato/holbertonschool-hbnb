"""Authorization helpers for JWT-protected endpoints."""

from __future__ import annotations

from flask_jwt_extended import get_jwt


def is_admin() -> bool:
    """Return whether the current JWT belongs to an admin user."""
    return bool(get_jwt().get("is_admin", False))
