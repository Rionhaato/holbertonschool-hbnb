"""Application factory for HBnB Part 3."""

from flask import Flask

from .api import init_api
from .extensions import db, init_extensions
from .services import HBnBFacade
from .persistence import InMemoryRepository, SQLAlchemyRepository
from config import Config


def _build_repository(app: Flask):
    """Create the configured persistence adapter."""
    repository_type = app.config.get("REPOSITORY_TYPE", "in_memory")
    if repository_type == "sqlalchemy":
        model_map = app.config.get("SQLALCHEMY_MODEL_MAP", {})
        return SQLAlchemyRepository(db, model_map=model_map)
    return InMemoryRepository()


def create_app(config_class: type[Config] = Config) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    init_extensions(app)

    repository = _build_repository(app)
    facade = HBnBFacade(repository)
    app.config["FACADE"] = facade

    init_api(app)
    return app
