"""
extensions.py

Initialize all Flask extensions used across the application.

This file allows extensions to be imported and used consistently
throughout the app without creating multiple instances.

Extensions included:
- SQLAlchemy (db)
- JWTManager (jwt)
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# ------------------------
# Database
# ------------------------
db = SQLAlchemy()
"""SQLAlchemy database instance. Attach to Flask app via `db.init_app(app)`."""

# ------------------------
# Authentication / JWT
# ------------------------
jwt = JWTManager()
"""JWTManager instance. Attach to Flask app via `jwt.init_app(app)`."""
