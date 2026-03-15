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
        self.app = app
        self.client = app.test_client()

    def _auth_headers(self, email="john@example.com", password="secret"):
        if self.app.config["FACADE"].get_user_by_email(email) is None:
            self.app.config["FACADE"].create_user(
                {
                    "first_name": "Auth",
                    "last_name": "User",
                    "email": email,
                    "password": password,
                }
            )
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        self.assertEqual(response.status_code, 200)
        token = response.get_json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def _admin_headers(self, email="admin@example.com", password="secret"):
        if self.app.config["FACADE"].get_user_by_email(email) is None:
            self.app.config["FACADE"].create_user(
                {
                    "first_name": "Admin",
                    "last_name": "User",
                    "email": email,
                    "password": password,
                    "is_admin": True,
                }
            )
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        self.assertEqual(response.status_code, 200)
        token = response.get_json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def _create_user(self, email="john@example.com"):
        existing = self.app.config["FACADE"].get_user_by_email(email)
        if existing is None:
            user = self.app.config["FACADE"].create_user(
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": email,
                    "password": "secret",
                }
            )
            return user.to_dict()
        return existing.to_dict()

    def _create_amenity(self, name="WiFi"):
        headers = self._admin_headers()
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
        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "password": "secret",
        }
        res = self.client.post("/api/v1/users/", json=payload)
        self.assertEqual(res.status_code, 201)
        user = res.get_json()
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

    def test_user_can_only_update_own_profile_and_not_email_or_password(self):
        user = self._create_user("self@example.com")
        other_user = self._create_user("other@example.com")

        own_headers = self._auth_headers(email="self@example.com")
        res = self.client.put(
            f"/api/v1/users/{user['id']}",
            json={
                "first_name": "Updated",
                "email": "ignored@example.com",
                "password": "new-secret",
            },
            headers=own_headers,
        )
        self.assertEqual(res.status_code, 200)
        payload = res.get_json()
        self.assertEqual(payload["first_name"], "Updated")
        self.assertEqual(payload["email"], "self@example.com")
        self.assertNotIn("password", payload)

        forbidden = self.client.put(
            f"/api/v1/users/{other_user['id']}",
            json={"first_name": "Hack"},
            headers=own_headers,
        )
        self.assertEqual(forbidden.status_code, 403)

    def test_admin_can_create_and_update_any_user(self):
        seed_user = self._create_user("seed@example.com")
        admin_headers = self._admin_headers()

        create_res = self.client.post(
            "/api/v1/users/",
            json={
                "first_name": "Managed",
                "last_name": "User",
                "email": "managed@example.com",
                "password": "secret",
            },
            headers=admin_headers,
        )
        self.assertEqual(create_res.status_code, 201)
        managed_user = create_res.get_json()

        update_res = self.client.put(
            f"/api/v1/users/{seed_user['id']}",
            json={
                "first_name": "AdminUpdated",
                "email": "admin-updated@example.com",
                "password": "new-secret",
                "is_admin": True,
            },
            headers=admin_headers,
        )
        self.assertEqual(update_res.status_code, 200)
        update_payload = update_res.get_json()
        self.assertEqual(update_payload["first_name"], "AdminUpdated")
        self.assertEqual(update_payload["email"], "admin-updated@example.com")
        self.assertTrue(update_payload["is_admin"])
        self.assertEqual(managed_user["email"], "managed@example.com")

    def test_non_admin_cannot_create_users_after_bootstrap(self):
        self._create_user("bootstrap@example.com")
        res = self.client.post(
            "/api/v1/users/",
            json={
                "first_name": "Blocked",
                "last_name": "User",
                "email": "blocked@example.com",
                "password": "secret",
            },
            headers=self._auth_headers(email="bootstrap@example.com"),
        )
        self.assertEqual(res.status_code, 403)

    def test_amenities_are_admin_only(self):
        self._create_user("member@example.com")
        forbidden_create = self.client.post(
            "/api/v1/amenities/",
            json={"name": "Gym"},
            headers=self._auth_headers(email="member@example.com"),
        )
        self.assertEqual(forbidden_create.status_code, 403)

        allowed_create = self.client.post(
            "/api/v1/amenities/",
            json={"name": "Gym"},
            headers=self._admin_headers(),
        )
        self.assertEqual(allowed_create.status_code, 201)
        amenity_id = allowed_create.get_json()["id"]

        allowed_update = self.client.put(
            f"/api/v1/amenities/{amenity_id}",
            json={"name": "Sauna"},
            headers=self._admin_headers(),
        )
        self.assertEqual(allowed_update.status_code, 200)
        self.assertEqual(allowed_update.get_json()["name"], "Sauna")

    def test_place_owner_controls_place_mutations(self):
        owner = self._create_user("owner2@example.com")
        other_user = self._create_user("intruder@example.com")

        place = self.client.post(
            "/api/v1/places/",
            json={
                "title": "Owner Place",
                "description": "Center",
                "price": 100,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "owner_id": owner["id"],
                "amenity_ids": [],
            },
            headers=self._auth_headers(email="owner2@example.com"),
        )
        self.assertEqual(place.status_code, 201)
        place_id = place.get_json()["id"]

        forbidden_create = self.client.post(
            "/api/v1/places/",
            json={
                "title": "Bad Place",
                "description": "Center",
                "price": 100,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "owner_id": owner["id"],
                "amenity_ids": [],
            },
            headers=self._auth_headers(email="intruder@example.com"),
        )
        self.assertEqual(forbidden_create.status_code, 403)

        forbidden_update = self.client.put(
            f"/api/v1/places/{place_id}",
            json={"price": 200},
            headers=self._auth_headers(email="intruder@example.com"),
        )
        self.assertEqual(forbidden_update.status_code, 403)

        owner_update = self.client.put(
            f"/api/v1/places/{place_id}",
            json={"price": 150, "owner_id": other_user["id"]},
            headers=self._auth_headers(email="owner2@example.com"),
        )
        self.assertEqual(owner_update.status_code, 200)
        updated_payload = owner_update.get_json()
        self.assertEqual(updated_payload["price"], 150.0)
        self.assertEqual(updated_payload["owner_id"], owner["id"])

    def test_admin_can_bypass_place_ownership_rules(self):
        owner = self._create_user("realowner@example.com")
        admin_headers = self._admin_headers()

        create_res = self.client.post(
            "/api/v1/places/",
            json={
                "title": "Admin Managed",
                "description": "Center",
                "price": 100,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "owner_id": owner["id"],
                "amenity_ids": [],
            },
            headers=admin_headers,
        )
        self.assertEqual(create_res.status_code, 201)
        place_id = create_res.get_json()["id"]

        update_res = self.client.put(
            f"/api/v1/places/{place_id}",
            json={"price": 175},
            headers=admin_headers,
        )
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.get_json()["price"], 175.0)

    def test_review_rules_enforce_author_and_uniqueness(self):
        owner = self._create_user("host@example.com")
        reviewer = self._create_user("guest@example.com")
        other_user = self._create_user("otherguest@example.com")

        place_res = self.client.post(
            "/api/v1/places/",
            json={
                "title": "Beach House",
                "description": "Ocean",
                "price": 300,
                "latitude": 12.34,
                "longitude": 56.78,
                "owner_id": owner["id"],
                "amenity_ids": [],
            },
            headers=self._auth_headers(email="host@example.com"),
        )
        self.assertEqual(place_res.status_code, 201)
        place_id = place_res.get_json()["id"]

        own_review = self.client.post(
            "/api/v1/reviews/",
            json={"text": "Mine", "rating": 5, "user_id": owner["id"], "place_id": place_id},
            headers=self._auth_headers(email="host@example.com"),
        )
        self.assertEqual(own_review.status_code, 403)

        review_res = self.client.post(
            "/api/v1/reviews/",
            json={"text": "Great", "rating": 5, "user_id": reviewer["id"], "place_id": place_id},
            headers=self._auth_headers(email="guest@example.com"),
        )
        self.assertEqual(review_res.status_code, 201)
        review_id = review_res.get_json()["id"]

        duplicate = self.client.post(
            "/api/v1/reviews/",
            json={"text": "Again", "rating": 4, "user_id": reviewer["id"], "place_id": place_id},
            headers=self._auth_headers(email="guest@example.com"),
        )
        self.assertEqual(duplicate.status_code, 400)

        forbidden_update = self.client.put(
            f"/api/v1/reviews/{review_id}",
            json={"text": "Hijack"},
            headers=self._auth_headers(email="otherguest@example.com"),
        )
        self.assertEqual(forbidden_update.status_code, 403)

        allowed_update = self.client.put(
            f"/api/v1/reviews/{review_id}",
            json={"text": "Updated review"},
            headers=self._auth_headers(email="guest@example.com"),
        )
        self.assertEqual(allowed_update.status_code, 200)

        forbidden_delete = self.client.delete(
            f"/api/v1/reviews/{review_id}",
            headers=self._auth_headers(email="otherguest@example.com"),
        )
        self.assertEqual(forbidden_delete.status_code, 403)

    def test_admin_can_bypass_review_ownership_rules(self):
        owner = self._create_user("adminhost@example.com")
        reviewer = self._create_user("adminguest@example.com")
        admin_headers = self._admin_headers(email="superadmin@example.com")

        place_res = self.client.post(
            "/api/v1/places/",
            json={
                "title": "Admin Review Target",
                "description": "Ocean",
                "price": 300,
                "latitude": 12.34,
                "longitude": 56.78,
                "owner_id": owner["id"],
                "amenity_ids": [],
            },
            headers=self._auth_headers(email="adminhost@example.com"),
        )
        self.assertEqual(place_res.status_code, 201)
        place_id = place_res.get_json()["id"]

        review_res = self.client.post(
            "/api/v1/reviews/",
            json={"text": "Admin authored", "rating": 5, "user_id": reviewer["id"], "place_id": place_id},
            headers=admin_headers,
        )
        self.assertEqual(review_res.status_code, 201)
        review_id = review_res.get_json()["id"]

        update_res = self.client.put(
            f"/api/v1/reviews/{review_id}",
            json={"text": "Admin updated"},
            headers=admin_headers,
        )
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.get_json()["text"], "Admin updated")

        delete_res = self.client.delete(
            f"/api/v1/reviews/{review_id}",
            headers=admin_headers,
        )
        self.assertEqual(delete_res.status_code, 200)

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

        headers = self._admin_headers()
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
