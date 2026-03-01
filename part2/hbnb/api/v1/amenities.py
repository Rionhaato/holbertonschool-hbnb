"""Amenities API namespace."""

from __future__ import annotations

from flask import current_app, request
from flask_restx import Namespace, Resource, fields


api = Namespace("amenities", description="Amenity operations")

amenity_input_model = api.model(
    "AmenityInput",
    {
        "name": fields.String(required=True, description="Amenity name"),
    },
)

amenity_update_model = api.model(
    "AmenityUpdate",
    {
        "name": fields.String(description="Amenity name"),
    },
)

amenity_response_model = api.model(
    "AmenityResponse",
    {
        "id": fields.String(description="Amenity UUID"),
        "created_at": fields.String(description="Creation timestamp"),
        "updated_at": fields.String(description="Last update timestamp"),
        "name": fields.String(description="Amenity name"),
    },
)


def _facade():
    return current_app.config["FACADE"]


@api.route("/")
class AmenitiesResource(Resource):
    """Amenities collection endpoints."""

    @api.marshal_list_with(amenity_response_model, code=200)
    def get(self):
        """Retrieve all amenities."""
        amenities = _facade().get_amenities()
        return [amenity.to_dict() for amenity in amenities], 200

    @api.expect(amenity_input_model, validate=True)
    @api.marshal_with(amenity_response_model, code=201)
    def post(self):
        """Create an amenity."""
        data = request.get_json(silent=True)
        if not data:
            api.abort(400, "Invalid JSON payload")

        name = data.get("name")
        if name is None or (isinstance(name, str) and not name.strip()):
            api.abort(400, "name is required")

        try:
            amenity = _facade().create_amenity(data)
        except (TypeError, ValueError) as exc:
            api.abort(400, str(exc))

        return amenity.to_dict(), 201


@api.route("/<string:amenity_id>")
class AmenityResource(Resource):
    """Single amenity endpoints."""

    @api.marshal_with(amenity_response_model, code=200)
    def get(self, amenity_id: str):
        """Retrieve one amenity by id."""
        amenity = _facade().get_amenity(amenity_id)
        if amenity is None:
            api.abort(404, "Amenity not found")
        return amenity.to_dict(), 200

    @api.expect(amenity_update_model, validate=True)
    @api.marshal_with(amenity_response_model, code=200)
    def put(self, amenity_id: str):
        """Update one amenity by id."""
        data = request.get_json(silent=True)
        if not data:
            api.abort(400, "Invalid JSON payload")

        amenity = _facade().get_amenity(amenity_id)
        if amenity is None:
            api.abort(404, "Amenity not found")

        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)

        try:
            updated = _facade().update_amenity(amenity_id, data)
        except (TypeError, ValueError) as exc:
            api.abort(400, str(exc))

        return updated.to_dict(), 200
