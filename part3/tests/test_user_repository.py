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
    from hbnb.persistence import UserRepository

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

    def test_user_repository_is_sqlalchemy_backed(self):
        self.assertIsInstance(self.repo, UserRepository)

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
