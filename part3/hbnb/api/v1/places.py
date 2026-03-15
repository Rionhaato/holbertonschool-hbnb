"""Places API namespace."""

from __future__ import annotations

from flask import current_app, request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields


api = Namespace("places", description="Place operations")

place_input_model = api.model(
    "PlaceInput",
    {
        "title": fields.String(required=True, description="Place title"),
        "description": fields.String(required=False, description="Place description"),
        "price": fields.Float(required=True, description="Nightly price"),
        "latitude": fields.Float(required=True, description="Latitude"),
        "longitude": fields.Float(required=True, description="Longitude"),
        "owner_id": fields.String(required=True, description="Owner user id"),
        "amenity_ids": fields.List(
            fields.String, required=False, description="Amenity ids"
        ),
    },
)

place_update_model = api.model(
    "PlaceUpdate",
    {
        "title": fields.String(description="Place title"),
        "description": fields.String(description="Place description"),
        "price": fields.Float(description="Nightly price"),
        "latitude": fields.Float(description="Latitude"),
        "longitude": fields.Float(description="Longitude"),
        "owner_id": fields.String(description="Owner user id"),
        "amenity_ids": fields.List(fields.String, description="Amenity ids"),
    },
)

place_owner_model = api.model(
    "PlaceOwner",
    {
        "id": fields.String(description="Owner id"),
        "first_name": fields.String(description="Owner first name"),
        "last_name": fields.String(description="Owner last name"),
        "email": fields.String(description="Owner email"),
    },
)

place_amenity_model = api.model(
    "PlaceAmenity",
    {
        "id": fields.String(description="Amenity id"),
        "name": fields.String(description="Amenity name"),
    },
)

place_review_model = api.model(
    "PlaceReview",
    {
        "id": fields.String(description="Review id"),
        "text": fields.String(description="Review text"),
        "rating": fields.Integer(description="Rating (0-5)"),
        "user_id": fields.String(description="Author user id"),
        "place_id": fields.String(description="Place id"),
    },
)

place_response_model = api.model(
    "PlaceResponse",
    {
        "id": fields.String(description="Place UUID"),
        "created_at": fields.String(description="Creation timestamp"),
        "updated_at": fields.String(description="Last update timestamp"),
        "title": fields.String(description="Place title"),
        "description": fields.String(description="Place description"),
        "price": fields.Float(description="Nightly price"),
        "latitude": fields.Float(description="Latitude"),
        "longitude": fields.Float(description="Longitude"),
        "owner_id": fields.String(description="Owner user id"),
        "amenity_ids": fields.List(fields.String, description="Amenity ids"),
        "owner": fields.Nested(place_owner_model, description="Owner details"),
        "amenities": fields.List(
            fields.Nested(place_amenity_model), description="Amenity details"
        ),
        "reviews": fields.List(
            fields.Nested(place_review_model), description="Reviews for this place"
        ),
    },
)


def _facade():
    return current_app.config["FACADE"]


def _serialize_place(place) -> dict:
    facade = _facade()
    payload = place.to_dict()

    owner = facade.get_user(place.owner_id)
    if owner is not None:
        payload["owner"] = {
            "id": owner.id,
            "first_name": owner.first_name,
            "last_name": owner.last_name,
            "email": owner.email,
        }
    else:
        payload["owner"] = None

    amenities = []
    for amenity_id in place.amenity_ids:
        amenity = facade.get_amenity(amenity_id)
        if amenity is not None:
            amenities.append({"id": amenity.id, "name": amenity.name})
    payload["amenities"] = amenities

    reviews = facade.get_reviews_by_place(place.id)
    payload["reviews"] = [
        {
            "id": review.id,
            "text": review.text,
            "rating": review.rating,
            "user_id": review.user_id,
            "place_id": review.place_id,
        }
        for review in reviews
    ]
    return payload


def _missing_required_field(data: dict, required_fields: list[str]) -> str | None:
    for field in required_fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            return field
    return None


@api.route("/")
class PlacesResource(Resource):
    """Places collection endpoints."""

    @api.marshal_list_with(place_response_model, code=200)
    def get(self):
        """Retrieve all places."""
        places = _facade().get_places()
        return [_serialize_place(place) for place in places], 200

    @api.expect(place_input_model, validate=True)
    @api.marshal_with(place_response_model, code=201)
    @jwt_required()
    def post(self):
        """Create a place."""
        data = request.get_json(silent=True)
        if not data:
            api.abort(400, "Invalid JSON payload")

        missing = _missing_required_field(
            data, ["title", "price", "latitude", "longitude", "owner_id"]
        )
        if missing:
            api.abort(400, f"{missing} is required")

        data.setdefault("description", "")
        data.setdefault("amenity_ids", [])

        try:
            place = _facade().create_place(data)
        except (TypeError, ValueError) as exc:
            api.abort(400, str(exc))

        return _serialize_place(place), 201


@api.route("/<string:place_id>")
class PlaceResource(Resource):
    """Single place endpoints."""

    @api.marshal_with(place_response_model, code=200)
    def get(self, place_id: str):
        """Retrieve one place by id."""
        place = _facade().get_place(place_id)
        if place is None:
            api.abort(404, "Place not found")
        return _serialize_place(place), 200

    @api.expect(place_update_model, validate=True)
    @api.marshal_with(place_response_model, code=200)
    @jwt_required()
    def put(self, place_id: str):
        """Update one place by id."""
        data = request.get_json(silent=True)
        if not data:
            api.abort(400, "Invalid JSON payload")

        place = _facade().get_place(place_id)
        if place is None:
            api.abort(404, "Place not found")

        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)

        try:
            updated = _facade().update_place(place_id, data)
        except (TypeError, ValueError) as exc:
            api.abort(400, str(exc))

        return _serialize_place(updated), 200


@api.route("/<string:place_id>/reviews")
class PlaceReviewsResource(Resource):
    """Reviews collection for a specific place."""

    @api.marshal_list_with(place_review_model, code=200)
    def get(self, place_id: str):
        """Retrieve all reviews for one place."""
        place = _facade().get_place(place_id)
        if place is None:
            api.abort(404, "Place not found")

        reviews = _facade().get_reviews_by_place(place_id)
        return [review.to_dict() for review in reviews], 200
