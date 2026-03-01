"""API bootstrap module."""

from flask import Flask
from flask_restx import Api

from .v1 import amenities_ns, places_ns, reviews_ns, status_ns, users_ns


def init_api(app: Flask) -> None:
    """Initialize Flask-RESTx API."""
    api = Api(
        app,
        version="1.0",
        title="HBnB API",
        description="HBnB Evolution API - Part 2",
        doc="/api/v1/",
    )
    api.add_namespace(status_ns, path="/api/v1/status")
    api.add_namespace(users_ns, path="/api/v1/users")
    api.add_namespace(places_ns, path="/api/v1/places")
    api.add_namespace(reviews_ns, path="/api/v1/reviews")
    api.add_namespace(amenities_ns, path="/api/v1/amenities")
