from dependency_injector.wiring import inject, Provide
from flask import request
from flask_jwt_extended import create_access_token
from flask_restx import Namespace, Resource, fields

from app.container import Container
from app.error_handler.exceptions import UserNotFoundException
from app.services.user_service import UserService
from app.util.logging_util import log_calls

# Namespace for authentication operations
auth_ns = Namespace("auth", description="Authentication")

# API model for login request payload
login_model = auth_ns.model("Login", {
    "email": fields.String(required=True),
    "password": fields.String(required=True)
})

@log_calls("app.routes")
@auth_ns.route("/login")
class Login(Resource):
    """Handles user authentication and JWT token generation."""
    @inject
    @auth_ns.expect(login_model)
    def post(self,
             user_service: UserService = Provide[Container.user_service]):
        """
                Authenticate a user and return a JWT access token.

                **Request Body**:
                - `email`: User's registered email (string, required)
                - `password`: User's password (string, required)

                **Responses**:
                - `200 OK`: Returns a JWT access token.
                - `400 Bad Request`: Missing required fields.
                - `401 Unauthorized`: Invalid email or password.
        """
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {"message": "Email and password are required."}, 400

        try:
            user = user_service.get_by_email(email)
        except UserNotFoundException:
            user = None

        if not user or not user.verify_password(password):
            return {"message": "Invalid credentials"}, 401

        access_token = create_access_token(identity=str(user.id))
        return {"access_token": access_token}