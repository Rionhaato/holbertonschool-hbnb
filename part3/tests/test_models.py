"""Unit tests for business models."""

import pathlib
import sys
import unittest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "hbnb"))

try:
    import flask_bcrypt  # noqa: F401

    BCRYPT_AVAILABLE = True
except ModuleNotFoundError:
    BCRYPT_AVAILABLE = False

from models import Amenity, Place, Review, User


class TestUserModel(unittest.TestCase):
    """User model validation tests."""

    @unittest.skipUnless(BCRYPT_AVAILABLE, "Flask-Bcrypt is not installed")
    def test_user_email_validation(self):
        with self.assertRaises(ValueError):
            User(first_name="A", last_name="B", email="bad-email", password="x")

    @unittest.skipUnless(BCRYPT_AVAILABLE, "Flask-Bcrypt is not installed")
    def test_user_name_length_validation(self):
        with self.assertRaises(ValueError):
            User(first_name="A" * 51, last_name="B", email="a@b.com", password="x")

    @unittest.skipUnless(BCRYPT_AVAILABLE, "Flask-Bcrypt is not installed")
    def test_user_password_is_hashed(self):
        user = User(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="secret123",
        )
        self.assertNotEqual(user.password, "secret123")
        self.assertTrue(user.password.startswith("$2"))
        self.assertTrue(user.check_password("secret123"))
        self.assertFalse(user.check_password("wrong-password"))


class TestPlaceModel(unittest.TestCase):
    """Place model validation tests."""

    def test_place_invalid_coordinates(self):
        with self.assertRaises(ValueError):
            Place(
                title="Home",
                description="desc",
                price=10,
                latitude=100,
                longitude=0,
                owner_id="owner-id",
            )

    def test_place_add_amenity(self):
        place = Place(
            title="Home",
            description="desc",
            price=10,
            latitude=30,
            longitude=30,
            owner_id="owner-id",
        )
        place.add_amenity("amenity-1")
        self.assertEqual(place.amenity_ids, ["amenity-1"])


class TestReviewAmenityModel(unittest.TestCase):
    """Review and amenity model tests."""

    def test_review_rating_validation(self):
        with self.assertRaises(ValueError):
            Review(text="Good", rating=6, user_id="u1", place_id="p1")

    def test_amenity_name_required(self):
        with self.assertRaises(ValueError):
            Amenity(name="  ")


if __name__ == "__main__":
    unittest.main()
