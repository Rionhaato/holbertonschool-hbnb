"""Reviews API namespace."""

from __future__ import annotations

from flask import current_app, request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields


api = Namespace("reviews", description="Review operations")

review_input_model = api.model(
    "ReviewInput",
    {
        "text": fields.String(required=True, description="Review text"),
        "rating": fields.Integer(required=False, description="Rating (0-5)"),
        "user_id": fields.String(required=True, description="Author user id"),
        "place_id": fields.String(required=True, description="Place id"),
    },
)

review_update_model = api.model(
    "ReviewUpdate",
    {
        "text": fields.String(description="Review text"),
        "rating": fields.Integer(description="Rating (0-5)"),
    },
)

review_author_model = api.model(
    "ReviewAuthor",
    {
        "id": fields.String(description="Author id"),
        "first_name": fields.String(description="Author first name"),
        "last_name": fields.String(description="Author last name"),
        "email": fields.String(description="Author email"),
    },
)

review_place_model = api.model(
    "ReviewPlace",
    {
        "id": fields.String(description="Place id"),
        "title": fields.String(description="Place title"),
    },
)

review_response_model = api.model(
    "ReviewResponse",
    {
        "id": fields.String(description="Review UUID"),
        "created_at": fields.String(description="Creation timestamp"),
        "updated_at": fields.String(description="Last update timestamp"),
        "text": fields.String(description="Review text"),
        "rating": fields.Integer(description="Rating (0-5)"),
        "user_id": fields.String(description="Author user id"),
        "place_id": fields.String(description="Place id"),
        "author": fields.Nested(review_author_model, description="Author details"),
        "place": fields.Nested(review_place_model, description="Place details"),
    },
)


def _facade():
    return current_app.config["FACADE"]


def _serialize_review(review) -> dict:
    facade = _facade()
    payload = review.to_dict()

    user = facade.get_user(review.user_id)
    if user is not None:
        payload["author"] = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }
    else:
        payload["author"] = None

    place = facade.get_place(review.place_id)
    if place is not None:
        payload["place"] = {
            "id": place.id,
            "title": place.title,
        }
    else:
        payload["place"] = None

    return payload


def _missing_required_field(data: dict, required_fields: list[str]) -> str | None:
    for field in required_fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            return field
    return None


@api.route("/")
class ReviewsResource(Resource):
    """Reviews collection endpoints."""

    @api.marshal_list_with(review_response_model, code=200)
    def get(self):
        """Retrieve all reviews."""
        reviews = _facade().get_reviews()
        return [_serialize_review(review) for review in reviews], 200

    @api.expect(review_input_model, validate=True)
    @api.marshal_with(review_response_model, code=201)
    @jwt_required()
    def post(self):
        """Create a review."""
        data = request.get_json(silent=True)
        if not data:
            api.abort(400, "Invalid JSON payload")

        missing = _missing_required_field(data, ["text", "user_id", "place_id"])
        if missing:
            api.abort(400, f"{missing} is required")

        data.setdefault("rating", 0)

        try:
            review = _facade().create_review(data)
        except (TypeError, ValueError) as exc:
            api.abort(400, str(exc))

        return _serialize_review(review), 201


@api.route("/<string:review_id>")
class ReviewResource(Resource):
    """Single review endpoints."""

    @api.marshal_with(review_response_model, code=200)
    def get(self, review_id: str):
        """Retrieve one review by id."""
        review = _facade().get_review(review_id)
        if review is None:
            api.abort(404, "Review not found")
        return _serialize_review(review), 200

    @api.expect(review_update_model, validate=True)
    @api.marshal_with(review_response_model, code=200)
    @jwt_required()
    def put(self, review_id: str):
        """Update one review by id."""
        data = request.get_json(silent=True)
        if not data:
            api.abort(400, "Invalid JSON payload")

        review = _facade().get_review(review_id)
        if review is None:
            api.abort(404, "Review not found")

        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)
        data.pop("user_id", None)
        data.pop("place_id", None)

        try:
            updated = _facade().update_review(review_id, data)
        except (TypeError, ValueError) as exc:
            api.abort(400, str(exc))

        return _serialize_review(updated), 200

    @jwt_required()
    def delete(self, review_id: str):
        """Delete one review by id."""
        review = _facade().get_review(review_id)
        if review is None:
            api.abort(404, "Review not found")

        _facade().delete_review(review_id)
        return {"message": "Review deleted"}, 200
