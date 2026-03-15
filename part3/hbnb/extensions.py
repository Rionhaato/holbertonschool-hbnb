"""Application extensions."""

from __future__ import annotations

try:
    from flask_bcrypt import Bcrypt
except ModuleNotFoundError:
    Bcrypt = None


bcrypt = Bcrypt() if Bcrypt is not None else None


def init_extensions(app) -> None:
    """Initialize optional Flask extensions."""
    if bcrypt is not None:
        bcrypt.init_app(app)

