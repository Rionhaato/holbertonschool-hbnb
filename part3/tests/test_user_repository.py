"""Tests for the SQLAlchemy-backed user repository."""

from __future__ import annotations

import pathlib
import sys
import unittest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from config import Config
    from hbnb import create_app
    from hbnb.persistence import SQLAlchemyRepository, UserRepository

    SQLA_AVAILABLE = True
except ModuleNotFoundError:
    SQLA_AVAILABLE = False


class RepositoryTestConfig(Config):
    """Config for repository integration tests."""

    TESTING = True
    REPOSITORY_TYPE = "sqlalchemy"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret-key"


@unittest.skipUnless(SQLA_AVAILABLE, "Flask-SQLAlchemy dependencies are not installed")
class TestUserRepository(unittest.TestCase):
    """Verify CRUD behavior for the SQLAlchemy user repository."""

    def setUp(self):
        self.app = create_app(RepositoryTestConfig)
        self.repo = self.app.config["FACADE"].user_repository
        self.generic_repo = self.app.config["FACADE"].repository

    def test_user_repository_is_sqlalchemy_backed(self):
        self.assertIsInstance(self.repo, UserRepository)
        self.assertIsInstance(self.generic_repo, SQLAlchemyRepository)

    def test_user_persists_and_can_be_queried_by_email(self):
        with self.app.app_context():
            user = self.app.config["FACADE"].create_user(
                {
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "email": "jane@example.com",
                    "password": "secret",
                }
            )
            fetched = self.repo.get_by_email("jane@example.com")
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched.id, user.id)
            self.assertTrue(fetched.check_password("secret"))

    def test_place_review_and_amenity_persist_with_sqlalchemy(self):
        with self.app.app_context():
            owner = self.app.config["FACADE"].create_user(
                {
                    "first_name": "Owner",
                    "last_name": "User",
                    "email": "owner@example.com",
                    "password": "secret",
                }
            )
            amenity = self.app.config["FACADE"].create_amenity({"name": "WiFi"})
            place = self.app.config["FACADE"].create_place(
                {
                    "title": "Loft",
                    "description": "Central",
                    "price": 120,
                    "latitude": 40.0,
                    "longitude": -73.0,
                    "owner_id": owner.id,
                    "amenity_ids": [amenity.id],
                }
            )
            review = self.app.config["FACADE"].create_review(
                {
                    "text": "Great stay",
                    "rating": 5,
                    "user_id": owner.id,
                    "place_id": place.id,
                }
            )

            fetched_place = self.generic_repo.get("Place", place.id)
            fetched_review = self.generic_repo.get("Review", review.id)
            fetched_amenity = self.generic_repo.get("Amenity", amenity.id)

            self.assertIsNotNone(fetched_place)
            self.assertEqual(fetched_place.title, "Loft")
            self.assertEqual(fetched_place.amenity_ids, [amenity.id])
            self.assertIsNotNone(fetched_review)
            self.assertEqual(fetched_review.text, "Great stay")
            self.assertIsNotNone(fetched_amenity)
            self.assertEqual(fetched_amenity.name, "WiFi")
