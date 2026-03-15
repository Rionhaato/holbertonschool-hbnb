"""Application factory for HBnB Part 3."""

from flask import Flask

from .api import init_api
from .extensions import db, init_extensions
from .models import Amenity, Place, Review, User
from .services import HBnBFacade
from .persistence import InMemoryRepository, SQLAlchemyRepository, UserRepository
from config import Config


def _build_repository(app: Flask):
    """Create the configured persistence adapter."""
    repository_type = app.config.get("REPOSITORY_TYPE", "sqlalchemy")
    if repository_type == "sqlalchemy":
        model_map = app.config.get("SQLALCHEMY_MODEL_MAP", {})
        return SQLAlchemyRepository(db, model_map=model_map)
    return InMemoryRepository()


def _build_user_repository(app: Flask):
    """Create the configured user persistence adapter."""
    repository_type = app.config.get("REPOSITORY_TYPE", "sqlalchemy")
    if repository_type == "sqlalchemy":
        return UserRepository(db)
    return None


def create_app(config_class: type[Config] = Config) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    init_extensions(app)

    app.config.setdefault(
        "SQLALCHEMY_MODEL_MAP",
        {
            "User": User,
            "Place": Place,
            "Review": Review,
            "Amenity": Amenity,
        },
    )

    repository = _build_repository(app)
    user_repository = _build_user_repository(app)
    if user_repository is not None and db is not None:
        with app.app_context():
            db.create_all()
    facade = HBnBFacade(repository, user_repository=user_repository)
    app.config["FACADE"] = facade

    init_api(app)
    return app
