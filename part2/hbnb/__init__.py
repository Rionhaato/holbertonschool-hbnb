"""Application factory for HBnB Part 2."""

from flask import Flask

from .api import init_api
from .services import HBnBFacade
from .persistence import InMemoryRepository


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config["RESTX_MASK_SWAGGER"] = False

    repository = InMemoryRepository()
    facade = HBnBFacade(repository)
    app.config["FACADE"] = facade

    init_api(app)
    return app
