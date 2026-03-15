"""Authentication API namespace."""

from __future__ import annotations

from flask import current_app, request
from flask_jwt_extended import create_access_token
from flask_restx import Namespace, Resource, fields


api = Namespace("auth", description="Authentication operations")

login_input_model = api.model(
    "LoginInput",
    {
        "email": fields.String(required=True, description="User email"),
        "password": fields.String(required=True, description="User password"),
    },
)

token_response_model = api.model(
    "TokenResponse",
    {
        "access_token": fields.String(description="JWT access token"),
        "user_id": fields.String(description="Authenticated user id"),
        "email": fields.String(description="Authenticated user email"),
        "is_admin": fields.Boolean(description="Admin claim"),
    },
)


def _facade():
    return current_app.config["FACADE"]


@api.route("/login")
class LoginResource(Resource):
    """Authentication endpoints."""

    @api.expect(login_input_model, validate=True)
    @api.marshal_with(token_response_model, code=200)
    def post(self):
        """Authenticate a user and issue a JWT access token."""
        data = request.get_json(silent=True)
        if not data:
            api.abort(400, "Invalid JSON payload")

        email = data.get("email", "")
        password = data.get("password", "")
        if not isinstance(email, str) or not email.strip():
            api.abort(400, "email is required")
        if not isinstance(password, str) or not password.strip():
            api.abort(400, "password is required")

        user = _facade().authenticate_user(email, password)
        if user is None:
            api.abort(401, "Invalid email or password")

        access_token = create_access_token(
            identity=user.id,
            additional_claims={"is_admin": user.is_admin, "email": user.email},
        )
        return {
            "access_token": access_token,
            "user_id": user.id,
            "email": user.email,
            "is_admin": user.is_admin,
        }, 200
