"""
auth_exception_handlers.py

JWT-specific authentication error handlers for the Event Finder application.

- Registers callbacks for missing, invalid, and expired JWT tokens.
- Intended to be called early in the app factory, before catch-all error handlers.
"""

from flask import jsonify

from app.extensions import jwt


def register_auth_error_handlers(app):
    """
    Initialize JWTManager and register JWT-specific error handlers.

    Must be called early in the Flask app factory, before registering
    global error handlers, so that auth errors are captured correctly.

    Args:
        app (Flask): The Flask application instance.
    """
    jwt.init_app(app)

    # ------------------------
    # JWT Error Handlers
    # ------------------------
    @jwt.unauthorized_loader
    def missing_token_callback(reason):
        """
                Handler for requests missing an Authorization header or token.

                Args:
                    reason (str): Explanation from JWTManager.

                Returns:
                    Flask response: JSON error message with HTTP 401 status.
                """
        return jsonify({
            "error": {
                "code": "JWT_MISSING",
                "message": reason
            }
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        """
                Handler for invalid or malformed JWT tokens (bad signature, corrupted, etc.)

                Args:
                    reason (str): Explanation from JWTManager.

                Returns:
                    Flask response: JSON error message with HTTP 422 status.
                """
        return jsonify({
            "error": {
                "code": "JWT_INVALID",
                "message": reason
            }
        }), 422

    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_payload):
        """
                Handler for expired JWT tokens.

                Args:
                    _jwt_header (dict): JWT header (unused here).
                    _jwt_payload (dict): JWT payload (unused here).

                Returns:
                    Flask response: JSON error message with HTTP 401 status.
                """
        return jsonify({
            "error": {
                "code": "JWT_EXPIRED",
                "message": "Token has expired"
            }
        }), 401
