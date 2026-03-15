"""Application factory for HBnB Part 3."""

from flask import Flask

from .api import init_api
from .extensions import init_extensions
from .services import HBnBFacade
from .persistence import InMemoryRepository
from config import Config


def create_app(config_class: type[Config] = Config) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    init_extensions(app)

    repository = InMemoryRepository()
    facade = HBnBFacade(repository)
    app.config["FACADE"] = facade

    init_api(app)
    return app
