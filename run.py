"""
ASGI Adapter for Flask Application

This module wraps the existing Flask WSGI app as an ASGI app, enabling
it to run with ASGI servers (e.g., Uvicorn, Hypercorn) while maintaining
the same Flask application logic.

Usage:
    $ uvicorn app.asgi:app --reload

Variables:
- flask_app: The Flask application instance created via `create_app()`.
- app: The ASGI-compatible application, wrapping `flask_app`.
"""

from asgiref.wsgi import WsgiToAsgi

from app import create_app

# Create the standard Flask app
flask_app = create_app()

# Wrap it as an ASGI app
app = WsgiToAsgi(flask_app)
