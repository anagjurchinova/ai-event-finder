"""
user_route.py

Flask-RESTX namespace defining all user-related API endpoints
for the Event Finder application.

Endpoints include:

- User creation, retrieval, update, and deletion.
- Fetch users by ID, email, or name.
- Check existence of users by ID or name.

Key features:
- Uses dependency injection via the application's container.
- JWT-protected endpoints for authenticated access.
- Marshmallow schemas for request validation and response serialization.
- Logging decorator applied to automatically log calls.
"""

from dependency_injector.wiring import inject, Provide
from flask import request, abort
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields

from app.container import Container
from app.models.user import User
from app.schemas.user_schema import CreateUserSchema, UpdateUserSchema, UserSchema
from app.services.user_service import UserService
from app.util.logging_util import log_calls

user_svc_provider = Provide[Container.user_service]

# ----------------------------
# Namespace and Schema Setup
# ----------------------------
user_ns = Namespace("users", description="User based operations")

# Marshmallow schemas for validation and serialization
create_user_schema = CreateUserSchema()
update_user_schema = UpdateUserSchema()
user_schema = UserSchema()
users_schema = UserSchema(many=True)

user_create_input = user_ns.model('user_create_input', {
    'name': fields.String(required=True),
    'surname': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True),
})

user_update_input = user_ns.model('user_update_input', {
    'name': fields.String(required=False),
    'surname': fields.String(required=False),
    'password': fields.String(required=False),
})


# ----------------------------
# Routes
# ----------------------------

@log_calls("app.routes")
@user_ns.route("")
class UserBaseResource(Resource):
    """Operations on the collection of users: GET all, POST new user."""

    @inject
    @jwt_required()
    def get(self,
            user_service: UserService = user_svc_provider):
        """Get all users"""
        users = user_service.get_all()
        return users_schema.dump(users), 200

    @user_ns.expect(user_create_input)
    @inject
    def post(self,
             user_service: UserService = user_svc_provider):
        """Create a new user."""
        json_data = request.get_json()
        data = create_user_schema.load(json_data)

        user = User(**data)
        saved_user = user_service.save(user)
        return user_schema.dump(saved_user), 201


@log_calls("app.routes")
@user_ns.route('/id/<int:user_id>')
class UserByIdResource(Resource):
    """Operations on a user identified by user ID."""

    @inject
    @jwt_required()
    def get(self,
            user_id: int,
            user_service: UserService = user_svc_provider):
        """Retrieve a user by ID."""
        user = user_service.get_by_id(user_id)
        return user_schema.dump(user), 200

    @inject
    @jwt_required()
    def delete(self,
               user_id: int,
               user_service: UserService = user_svc_provider):
        """Delete a user by ID"""
        user_service.delete_by_id(user_id)
        return '', 204


@log_calls("app.routes")
@user_ns.route('/email/<string:email>')
class UserByEmailResource(Resource):
    """Operations on a user identified by email."""

    @inject
    @jwt_required()
    def get(self,
            email: str,
            user_service: UserService = user_svc_provider):
        """Retrieve a user by email."""
        user = user_service.get_by_email(email)
        return user_schema.dump(user), 200

    @user_ns.expect(user_update_input)
    @inject
    @jwt_required()
    def put(self,
            email: str,
            user_service: UserService = user_svc_provider):
        """Update a user identified by email."""
        json_data = request.get_json(silent=True) or {}
        data = update_user_schema.load(json_data, partial=True)

        if not data:
            abort(400, description="No valid update fields provided")

        updated_user = user_service.update(email, data)
        return user_schema.dump(updated_user), 200


@log_calls("app.routes")
@user_ns.route('/name/<string:name>')
class UsersByNameResource(Resource):
    """Retrieve users by their name."""

    @inject
    @jwt_required()
    def get(self,
            name: str,
            user_service: UserService = user_svc_provider):
        """Get a user by name"""
        user = user_service.get_by_name(name)
        return user_schema.dump(user), 200


# ----------------------------
# Existence Checks
# ----------------------------

@log_calls("app.routes")
@user_ns.route('/exists/id/<int:user_id>')
class ExistsByIdResource(Resource):
    """Check whether a user exists by ID."""

    @inject
    @jwt_required()
    def get(self,
            user_id: int,
            user_service: UserService = user_svc_provider):
        """Check the existence of a user by ID"""
        exists = user_service.exists_by_id(user_id)
        return {'exists': exists}, 200


@log_calls("app.routes")
@user_ns.route('/exists/name/<string:name>')
class ExistsByNameResource(Resource):
    """Check whether users exist by name."""

    @inject
    @jwt_required()
    def get(self,
            name: str,
            user_service: UserService = user_svc_provider):
        exists = user_service.exists_by_name(name)
        return {'exists': exists}, 200
