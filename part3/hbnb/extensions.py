"""Application extensions."""

from __future__ import annotations

try:
    from flask_bcrypt import Bcrypt
except ModuleNotFoundError:
    Bcrypt = None

try:
    from flask_jwt_extended import JWTManager
except ModuleNotFoundError:
    JWTManager = None

try:
    from flask_sqlalchemy import SQLAlchemy
except ModuleNotFoundError:
    SQLAlchemy = None


bcrypt = Bcrypt() if Bcrypt is not None else None
jwt = JWTManager() if JWTManager is not None else None
db = SQLAlchemy() if SQLAlchemy is not None else None


def init_extensions(app) -> None:
    """Initialize optional Flask extensions."""
    if bcrypt is not None:
        bcrypt.init_app(app)
    if jwt is not None:
        jwt.init_app(app)
    if db is not None:
        db.init_app(app)
