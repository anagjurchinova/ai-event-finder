"""
Utility for generating JWT tokens in test scenarios.
"""

from flask_jwt_extended import create_access_token

def generate_test_token(app, user_id: int) -> str:
    """
    Generate a JWT access token for a specific user ID in a test environment.

    This function wraps the token creation in the Flask app context, ensuring
    the JWT configuration is available during token generation.

    Args:
        app: Flask application instance.
        user_id (int): The ID of the user for whom the token is created.

    Returns:
        str: A JWT access token representing the given user.
    """
    with app.app_context():
        return create_access_token(identity=str(user_id))