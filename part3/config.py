"""Configuration classes for HBnB Part 3."""

import os


class Config:
    """Base application configuration."""

    DEBUG = False
    TESTING = False
    RESTX_MASK_SWAGGER = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
