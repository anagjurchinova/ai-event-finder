"""
__init__.py

Application factory and Flask app setup.

This file defines the `create_app` factory that initializes:
- Flask application instance
- CORS configuration
- Database (SQLAlchemy) and migrations
- JWT authentication
- Dependency Injection container
- API namespaces and Swagger UI
- Logging and error handlers
- Optional warmup of local ML models
"""

import asyncio
import os
import secrets
from datetime import timedelta
from importlib import resources

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_migrate import upgrade as flask_migrate_upgrade
from flask_restx import Api

from app.cli import seed_cli
from app.configuration.config import Config
from app.configuration.logging_config import configure_logging
from app.container import Container
from app.error_handler.auth_exception_handlers import register_auth_error_handlers
from app.error_handler.global_error_handler import register_error_handlers
from app.extensions import db, jwt
from app.models.user import User  # keep imports so autogenerate sees models
from app.routes.app_route import app_ns
from app.routes.event_route import event_ns
from app.routes.login_route import auth_ns
from app.routes.user_route import user_ns
from app.services import user_service
from app.services import user_service_impl
from app.util.model_util import warmup_local_models
import logging

# ------------------------
# Migrations setup
# ------------------------
PROJECT_ROOT = resources.files("app").parent
MIGRATIONS_DIR = (PROJECT_ROOT / "migrations").as_posix()

migrate = Migrate(directory=MIGRATIONS_DIR)


# ------------------------
# API Setup
# ------------------------
def create_api(app: Flask) -> None:
    """Initialize API namespaces and Swagger documentation."""

    authorizations = {
        "BearerAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Paste your JWT token here. Format: Bearer <token>"
        }
    }

    api = Api(
        app,
        title="Event Finder API",
        version="1.0",
        description="REST API",
        doc="/swagger/",  # optional: where Swagger UI lives
        authorizations=authorizations
    )
    # Register API namespaces
    api.add_namespace(user_ns, path="/users")
    api.add_namespace(event_ns, path="/events")
    api.add_namespace(auth_ns, path="/auth")
    api.add_namespace(app_ns, path="/app")


# ------------------------
# Application Factory
# ------------------------
def create_app(test_config: dict | None = None) -> Flask:
    """
       Application factory function.

       Args:
           test_config (dict | None): Optional config overrides for testing.

       Returns:
           Flask: Configured Flask application instance.
       """
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    # General config
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", secrets.token_hex(32))
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(64))
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

    # ------------------------
    # CORS Configuration
    # ------------------------
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        allow_headers="*",
        expose_headers="*",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        supports_credentials=False,  # must be False when origins="*"
        max_age=86400,  # cache preflight 24h
    )

    # ------------------------
    # Extensions
    # ------------------------
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    app.cli.add_command(seed_cli)

    # ------------------------
    # Auto DB migration
    # ------------------------
    with app.app_context():
        flask_migrate_upgrade()
        env_type = "Test" if test_config and test_config.get("TESTING") else "Production"
        logging.info(f"{env_type} database upgraded successfully.")

    # ------------------------
    # Dependency Injection
    # ------------------------
    container = Container()
    container.init_resources()
    container.wire(modules=[
        "app.routes.user_route",
        "app.routes.app_route",
        "app.routes.event_route",
        "app.routes.login_route",
    ])
    app.di = container

    # ------------------------
    # API Namespaces
    # ------------------------
    create_api(app)

    # ------------------------
    # Logging & Error Handlers
    # ------------------------
    register_auth_error_handlers(app)
    configure_logging()
    register_error_handlers(app)

    # ------------------------
    # Warmup local models if provider is local
    # ------------------------
    if Config.PROVIDER == "local":
        loop = asyncio.get_event_loop()
        loop.create_task(warmup_local_models(container))

    # ------------------------
    # Teardown
    # ------------------------
    @app.teardown_appcontext
    def shutdown_session(exc=None):
        """CRITICAL: Remove scoped DB session to return connection to the pool."""
        db.session.remove()

    return app
