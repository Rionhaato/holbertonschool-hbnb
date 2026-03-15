"""Users API namespace."""

from __future__ import annotations

from flask import current_app, request
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request
from flask_restx import Namespace, Resource, fields

from ..authz import is_admin


api = Namespace("users", description="User operations")

user_input_model = api.model(
    "UserInput",
    {
        "first_name": fields.String(required=True, description="User first name"),
        "last_name": fields.String(required=True, description="User last name"),
        "email": fields.String(required=True, description="User email"),
        "password": fields.String(required=True, description="User password"),
    },
)

user_update_model = api.model(
    "UserUpdate",
    {
        "first_name": fields.String(description="User first name"),
        "last_name": fields.String(description="User last name"),
        "email": fields.String(description="User email"),
        "password": fields.String(description="User password"),
        "is_admin": fields.Boolean(description="Admin flag"),
    },
)

user_response_model = api.model(
    "UserResponse",
    {
        "id": fields.String(description="User UUID"),
        "created_at": fields.String(description="Creation timestamp"),
        "updated_at": fields.String(description="Last update timestamp"),
        "first_name": fields.String(description="User first name"),
        "last_name": fields.String(description="User last name"),
        "email": fields.String(description="User email"),
        "is_admin": fields.Boolean(description="Admin flag"),
    },
)


def _facade():
    return current_app.config["FACADE"]


def _serialize_user(user) -> dict:
    payload = user.to_dict()
    payload.pop("password", None)
    return payload


def _validate_required_fields(data: dict, required_fields: list[str]) -> str | None:
    for field in required_fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            return field
    return None


@api.route("/")
class UsersResource(Resource):
    """Users collection endpoints."""

    @api.marshal_list_with(user_response_model, code=200)
    def get(self):
        """Retrieve all users."""
        users = _facade().get_users()
        return [_serialize_user(user) for user in users], 200

    @api.expect(user_input_model, validate=True)
    @api.marshal_with(user_response_model, code=201)
    def post(self):
        """Create a new user."""
        data = request.get_json(silent=True)
        if not data:
            api.abort(400, "Invalid JSON payload")

        missing_field = _validate_required_fields(
            data, ["first_name", "last_name", "email", "password"]
        )
        if missing_field:
            api.abort(400, f"{missing_field} is required")

        existing_users = _facade().get_users()
        if existing_users:
            verify_jwt_in_request(optional=True)
            if not is_admin():
                api.abort(403, "Only administrators can create new users")

        try:
            user = _facade().create_user(data)
        except (TypeError, ValueError) as exc:
            api.abort(400, str(exc))

        return _serialize_user(user), 201


@api.route("/<string:user_id>")
class UserResource(Resource):
    """Single user endpoints."""

    @api.marshal_with(user_response_model, code=200)
    def get(self, user_id: str):
        """Retrieve one user by id."""
        user = _facade().get_user(user_id)
        if user is None:
            api.abort(404, "User not found")
        return _serialize_user(user), 200

    @api.expect(user_update_model, validate=True)
    @api.marshal_with(user_response_model, code=200)
    @jwt_required()
    def put(self, user_id: str):
        """Update one user by id."""
        data = request.get_json(silent=True)
        if not data:
            api.abort(400, "Invalid JSON payload")

        user = _facade().get_user(user_id)
        if user is None:
            api.abort(404, "User not found")

        admin = is_admin()
        if not admin and get_jwt_identity() != user_id:
            api.abort(403, "You can only modify your own user details")

        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)
        if not admin:
            data.pop("email", None)
            data.pop("password", None)
            data.pop("is_admin", None)

        try:
            updated = _facade().update_user(user_id, data)
        except (TypeError, ValueError) as exc:
            api.abort(400, str(exc))

        return _serialize_user(updated), 200
