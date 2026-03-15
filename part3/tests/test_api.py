"""Endpoint tests for HBnB API v1."""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

try:
    from config import Config
    from hbnb import create_app

    FLASK_AVAILABLE = True
except ModuleNotFoundError:
    FLASK_AVAILABLE = False


class TestConfig(Config):
    """Test-specific configuration."""

    TESTING = True
    JWT_SECRET_KEY = "test-secret-key"


@unittest.skipUnless(FLASK_AVAILABLE, "Flask dependencies are not installed")
class TestAPI(unittest.TestCase):
    """Black-box style API tests using Flask test client."""

    def setUp(self):
        app = create_app(TestConfig)
        self.client = app.test_client()

    def _auth_headers(self, email="john@example.com", password="secret"):
        self.client.post(
            "/api/v1/users/",
            json={
                "first_name": "Auth",
                "last_name": "User",
                "email": email,
                "password": password,
            },
        )
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        self.assertEqual(response.status_code, 200)
        token = response.get_json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def _create_user(self, email="john@example.com"):
        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "email": email,
            "password": "secret",
        }
        res = self.client.post("/api/v1/users/", json=payload)
        self.assertEqual(res.status_code, 201)
        return res.get_json()

    def _create_amenity(self, name="WiFi"):
        headers = self._auth_headers()
        res = self.client.post("/api/v1/amenities/", json={"name": name}, headers=headers)
        self.assertEqual(res.status_code, 201)
        return res.get_json()

    def _create_place(self, owner_id, amenity_ids=None):
        if amenity_ids is None:
            amenity_ids = []
        payload = {
            "title": "Cozy Loft",
            "description": "Center",
            "price": 100,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "owner_id": owner_id,
            "amenity_ids": amenity_ids,
        }
        headers = self._auth_headers(email="owner@example.com")
        res = self.client.post("/api/v1/places/", json=payload, headers=headers)
        self.assertEqual(res.status_code, 201)
        return res.get_json()

    def _create_review(self, user_id, place_id, text="Great stay", rating=5):
        payload = {
            "text": text,
            "rating": rating,
            "user_id": user_id,
            "place_id": place_id,
        }
        headers = self._auth_headers(email="author@example.com")
        res = self.client.post("/api/v1/reviews/", json=payload, headers=headers)
        self.assertEqual(res.status_code, 201)
        return res.get_json()

    def test_login_returns_access_token(self):
        user = self._create_user()
        res = self.client.post(
            "/api/v1/auth/login",
            json={"email": user["email"], "password": "secret"},
        )
        self.assertEqual(res.status_code, 200)
        payload = res.get_json()
        self.assertIn("access_token", payload)
        self.assertEqual(payload["user_id"], user["id"])
        self.assertEqual(payload["email"], user["email"])
        self.assertFalse(payload["is_admin"])

    def test_protected_endpoints_require_jwt(self):
        user = self._create_user("secure@example.com")
        unauthorized_place = self.client.post(
            "/api/v1/places/",
            json={
                "title": "Secure Loft",
                "description": "Center",
                "price": 100,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "owner_id": user["id"],
                "amenity_ids": [],
            },
        )
        self.assertEqual(unauthorized_place.status_code, 401)

    def test_status_endpoint(self):
        res = self.client.get("/api/v1/status")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "OK")

    def test_users_crud_without_delete(self):
        created = self._create_user()
        self.assertNotIn("password", created)

        list_res = self.client.get("/api/v1/users/")
        self.assertEqual(list_res.status_code, 200)
        self.assertEqual(len(list_res.get_json()), 1)
        self.assertNotIn("password", list_res.get_json()[0])

        user_id = created["id"]
        get_res = self.client.get(f"/api/v1/users/{user_id}")
        self.assertEqual(get_res.status_code, 200)
        self.assertNotIn("password", get_res.get_json())

        headers = self._auth_headers()
        put_res = self.client.put(
            f"/api/v1/users/{user_id}", json={"first_name": "Jane"}, headers=headers
        )
        self.assertEqual(put_res.status_code, 200)
        self.assertEqual(put_res.get_json()["first_name"], "Jane")
        self.assertNotIn("password", put_res.get_json())

    def test_amenities_endpoints(self):
        created = self._create_amenity("Pool")
        amenity_id = created["id"]

        list_res = self.client.get("/api/v1/amenities/")
        self.assertEqual(list_res.status_code, 200)
        self.assertEqual(len(list_res.get_json()), 1)

        get_res = self.client.get(f"/api/v1/amenities/{amenity_id}")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.get_json()["name"], "Pool")

        headers = self._auth_headers()
        put_res = self.client.put(
            f"/api/v1/amenities/{amenity_id}",
            json={"name": "AC"},
            headers=headers,
        )
        self.assertEqual(put_res.status_code, 200)
        self.assertEqual(put_res.get_json()["name"], "AC")

    def test_places_endpoints_and_composed_response(self):
        user = self._create_user("owner@example.com")
        amenity = self._create_amenity("Kitchen")
        place = self._create_place(user["id"], [amenity["id"]])

        self.assertEqual(place["owner"]["id"], user["id"])
        self.assertEqual(place["amenities"][0]["id"], amenity["id"])
        self.assertEqual(place["reviews"], [])

        place_id = place["id"]
        headers = self._auth_headers(email="owner@example.com")
        put_res = self.client.put(
            f"/api/v1/places/{place_id}",
            json={"price": 120},
            headers=headers,
        )
        self.assertEqual(put_res.status_code, 200)
        self.assertEqual(put_res.get_json()["price"], 120.0)

    def test_reviews_crud_with_delete(self):
        user = self._create_user("author@example.com")
        place = self._create_place(user["id"])
        review = self._create_review(user["id"], place["id"])
        review_id = review["id"]

        get_res = self.client.get(f"/api/v1/reviews/{review_id}")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.get_json()["author"]["id"], user["id"])

        place_reviews = self.client.get(f"/api/v1/places/{place['id']}/reviews")
        self.assertEqual(place_reviews.status_code, 200)
        self.assertEqual(len(place_reviews.get_json()), 1)

        place_res = self.client.get(f"/api/v1/places/{place['id']}")
        self.assertEqual(place_res.status_code, 200)
        self.assertEqual(len(place_res.get_json()["reviews"]), 1)

        headers = self._auth_headers(email="author@example.com")
        put_res = self.client.put(
            f"/api/v1/reviews/{review_id}",
            json={"text": "Updated"},
            headers=headers,
        )
        self.assertEqual(put_res.status_code, 200)
        self.assertEqual(put_res.get_json()["text"], "Updated")

        del_res = self.client.delete(f"/api/v1/reviews/{review_id}", headers=headers)
        self.assertEqual(del_res.status_code, 200)

        get_deleted = self.client.get(f"/api/v1/reviews/{review_id}")
        self.assertEqual(get_deleted.status_code, 404)

    def test_validation_errors(self):
        bad_user = self.client.post(
            "/api/v1/users/",
            json={
                "first_name": "A",
                "last_name": "B",
                "email": "invalid-email",
                "password": "x",
            },
        )
        self.assertEqual(bad_user.status_code, 400)

        owner = self._create_user("place-owner@example.com")
        bad_place = self.client.post(
            "/api/v1/places/",
            json={
                "title": "Invalid",
                "description": "desc",
                "price": 10,
                "latitude": 500,
                "longitude": 0,
                "owner_id": owner["id"],
                "amenity_ids": [],
            },
            headers=self._auth_headers(email="place-owner@example.com"),
        )
        self.assertEqual(bad_place.status_code, 400)

        place = self._create_place(owner["id"])
        bad_review = self.client.post(
            "/api/v1/reviews/",
            json={"text": "x", "rating": 9, "user_id": owner["id"], "place_id": place["id"]},
            headers=self._auth_headers(email="place-owner@example.com"),
        )
        self.assertEqual(bad_review.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
