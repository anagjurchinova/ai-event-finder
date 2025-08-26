"""
global_error_handler.py

Centralized error handling for Event Finder Flask application.

- Registers handlers for:
  - Marshmallow validation errors
  - Common HTTP errors (400, 413, 415, etc.)
  - Domain-specific exceptions (User, Event, Embedding, Concurrency, ModelWarmup)
  - Fallback for all unhandled exceptions, logging detailed traceback

- Intended to be registered after JWT/auth error handlers in the app factory.
"""

import logging
import traceback

from flask import jsonify, request
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException, UnsupportedMediaType, BadRequest, RequestEntityTooLarge

from app.error_handler.exceptions import (
    UserNotFoundException,
    DuplicateEmailException,
    UserSaveException,
    UserDeleteException,
    EventNotFoundException,
    EventAlreadyExistsException,
    EventSaveException,
    EventDeleteException,
    UserNotInEventException,
    UserAlreadyInEventException,
    ConcurrencyException,
    EmbeddingServiceException,
    ModelWarmupException
)


def register_error_handlers(app):
    """
    Register all global error handlers for the Flask app.

    Handlers include:
        - Marshmallow validation errors (422)
        - HTTP/bad request errors (400, 413, 415)
        - Domain-specific exceptions (404, 409, 500)
        - Embedding and model warmup exceptions
        - Generic fallback for unhandled exceptions (500)

    Args:
        app (Flask): The Flask application instance.
    """
    logger = logging.getLogger(__name__)

    # -------------------------
    # Validation & HTTP errors
    # -------------------------

    @app.errorhandler(ValidationError)
    def handle_marshmallow_validation(err: ValidationError):
        # err.messages is a dict of field -> list[str]
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "Invalid request payload.",
                                  "fields": err.messages, }}), 422

    @app.errorhandler(BadRequest)
    def handle_bad_request(err: BadRequest):
        # e.g. malformed JSON -> “Failed to decode JSON object …”
        return jsonify({"error": {"code": "BAD_REQUEST", "message": err.description or "Bad request."}}), 400

    @app.errorhandler(UnsupportedMediaType)
    def handle_unsupported_media(err: UnsupportedMediaType):
        return jsonify(
            {"error": {"code": "UNSUPPORTED_MEDIA_TYPE", "message": err.description or "Unsupported media type."}}), 415

    @app.errorhandler(RequestEntityTooLarge)
    def handle_too_large(_err: RequestEntityTooLarge):
        return jsonify({"error": {"code": "REQUEST_ENTITY_TOO_LARGE", "message": "Payload too large."}}), 413

    # -------------------------
    # User-related exceptions
    # -------------------------

    @app.errorhandler(UserNotFoundException)
    def handle_user_not_found(exception):
        return jsonify({"error": {"code": "USER_NOT_FOUND", "message": str(exception)}}), 404

    @app.errorhandler(DuplicateEmailException)
    def handle_duplicate_email(exception):
        return jsonify({"error": {"code": "DUPLICATE_EMAIL", "message": str(exception)}}), 409

    @app.errorhandler(UserSaveException)
    def handle_user_save(exception):
        return jsonify({"error": {"code": "USER_SAVE_ERROR", "message": str(exception)}}), 500

    @app.errorhandler(UserDeleteException)
    def handle_user_delete(exception):
        return jsonify({"error": {"code": "USER_DELETE_ERROR", "message": str(exception)}}), 500

    # -------------------------
    # Event-related exceptions
    # -------------------------

    @app.errorhandler(EventNotFoundException)
    def handle_event_not_found(exception):
        return jsonify({"error": {"code": "EVENT_NOT_FOUND", "message": str(exception)}}), 404

    @app.errorhandler(EventAlreadyExistsException)
    def handle_event_already_exists(exception):
        return jsonify({"error": {"code": "EVENT_ALREADY_EXISTS", "message": str(exception)}}), 409

    @app.errorhandler(EventSaveException)
    def handle_event_save(exception):
        return jsonify({"error": {"code": "EVENT_SAVE_ERROR", "message": str(exception)}}), 500

    @app.errorhandler(EventDeleteException)
    def handle_event_delete(exception):
        return jsonify({"error": {"code": "EVENT_DELETE_ERROR", "message": str(exception)}}), 500

    @app.errorhandler(UserNotInEventException)
    def handle_user_not_in_event(exception):
        return jsonify({"error": {"code": "USER_NOT_IN_EVENT", "message": str(exception)}}), 404

    @app.errorhandler(UserAlreadyInEventException)
    def handle_user_already_in_event(exception):
        return jsonify({"error": {"code": "USER_ALREADY_IN_EVENT", "message": str(exception)}}), 409

    # -------------------------
    # Concurrency & Embedding exceptions
    # -------------------------

    @app.errorhandler(ConcurrencyException)
    def handle_concurrency_exception(exception):
        return jsonify({"error": {"code": "CONCURRENT_UPDATE", "message": str(exception)}}), 409

    @app.errorhandler(EmbeddingServiceException)
    def handle_embedding_service_error(exception: EmbeddingServiceException):
        return jsonify({"error": {"code": "EMBEDDING_SERVICE_ERROR", "message": str(exception), }}), getattr(exception,
                                                                                                             "status_code",
                                                                                                             500)

    @app.errorhandler(ModelWarmupException)
    def handle_model_warmup_error(_exc: ModelWarmupException):
        return {"error": "Internal server error"}, 500

    # -------------------------
    # Global fallback
    # -------------------------
    @app.errorhandler(Exception)
    def handle_all_exceptions(e):
        """
            Catch-all handler for unhandled exceptions.
            Logs full traceback and request info for debugging.
            Returns a generic 500 response, or forwards HTTPExceptions.
        """
        logger.error("=" * 60)
        logger.error(f"UNHANDLED EXCEPTION: {type(e).__name__}")
        logger.error(f"Message: {str(e)}")
        logger.error(f"Module: {type(e).__module__}")
        logger.error(f"Request: {request.method} {request.url}")
        logger.error(f"Headers: {dict(request.headers)}")

        # Print the full traceback
        logger.error("Full traceback:")
        for line in traceback.format_exc().split('\n'):
            if line.strip():
                logger.error(line)
        logger.error("=" * 60)

        # Handle HTTPExceptions
        if isinstance(e, HTTPException):
            return jsonify({
                "error": {
                    "code": e.name.upper().replace(" ", "_"),
                    "message": e.description,
                }
            }), e.code

        # Generic 500 error
        return jsonify({
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": f"Unexpected error: {type(e).__name__}"
            }
        }), 500
