"""
event_route.py

Flask-RESTX namespace defining all event-related API endpoints
for the Event Finder application.

Endpoints include:

- Event creation, retrieval, update, and deletion.
- Fetch events by title, location, category, organizer, or date.

Key features:
- Uses dependency injection via the application's container.
- JWT-protected endpoints for authenticated access.
- Marshmallow schemas for request validation and response serialization.
- Logging decorator applied to automatically log calls.
"""

from datetime import datetime

from dependency_injector.wiring import inject, Provide
from flask import request, abort
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields

from app.container import Container
from app.schemas.event_schema import CreateEventSchema, EventSchema, UpdateEventSchema
from app.services.event_service import EventService
from app.util.logging_util import log_calls

event_svc_provider = Provide[Container.event_service]

# ----------------------------
# Namespace and Schema Setup
# ----------------------------
event_ns = Namespace("events", description="Event based operations")

# Instantiate Marshmallow schemas for input validation and serialization of Event object(s)
create_event_schema = CreateEventSchema()
update_event_schema = UpdateEventSchema()
event_schema = EventSchema()
events_schema = EventSchema(many=True)

# Swagger/OpenAPI request models
event_create_input = event_ns.model('event_create_input', {
    'title': fields.String(required=True),  # Event title must be provided
    'description': fields.String(required=True),  # Event description
    'datetime': fields.String(required=True),  # Date/time in specific format
    'location': fields.String(required=True),  # Location string
    'category': fields.String(required=True),  # Category string
    'organizer_email': fields.String(required=True),  # Email of user organizing this event
})

event_update_input = event_ns.model('event_update_input', {
    'description': fields.String(required=False),
    'datetime': fields.DateTime(required=False),
    'location': fields.String(required=False),
    'category': fields.String(required=False),
})


# ----------------------------
# Routes
# ----------------------------

@log_calls("app.routes")
@event_ns.route("")
class EventBaseResource(Resource):
    """Operations on the collection of events: GET all, POST new event."""

    @inject
    @jwt_required()
    def get(self,
            event_service: EventService = event_svc_provider):
        """Retrieve all events."""
        events = event_service.get_all()
        return events_schema.dump(events), 200

    @event_ns.expect(event_create_input)
    @inject
    @jwt_required()
    async def post(self,
                   event_service: EventService = event_svc_provider):
        """Create a new event"""

        data = create_event_schema.load(request.get_json())
        saved = await event_service.create(data)
        return event_schema.dump(saved), 201


@log_calls("app.routes")
@event_ns.route('/title/<string:title>')
class EventByTitleResource(Resource):
    """Operations on an event identified by title."""

    @inject
    @jwt_required()
    def get(self,
            title: str,
            event_service: EventService = event_svc_provider):
        """Retrieve an event by title."""
        event = event_service.get_by_title(title)
        return event_schema.dump(event), 200

    @inject
    @jwt_required()
    def delete(self,
               title: str,
               event_service: EventService = event_svc_provider):
        """Delete an event by title"""
        event = event_service.get_by_title(title)
        if not event:
            abort(404, description=f"Event with title {title} not found")
        event_service.delete_by_title(title)
        return '', 204  # No content on successful delete

    # noinspection PyUnreachableCode
    @event_ns.expect(event_update_input)
    @inject
    @jwt_required()
    async def put(self,
                  title: str,
                  event_service: EventService = event_svc_provider):
        """Update an event identified by title."""

        body = request.get_json() or {}
        patch = update_event_schema.load(body, partial=True)

        if not patch:
            abort(400, description="No valid update fields provided")

        updated_event = await event_service.update(title, patch)
        return event_schema.dump(updated_event), 200


@log_calls("app.routes")
@event_ns.route('/location/<string:location>')
class EventsByLocationResource(Resource):
    """Retrieve events by location."""

    @inject
    @jwt_required()
    def get(self,
            location: str,
            event_service: EventService = event_svc_provider):
        events = event_service.get_by_location(location)
        return events_schema.dump(events), 200


@log_calls("app.routes")
@event_ns.route('/category/<string:category>')
class EventsByCategoryResource(Resource):
    """Retrieve events by category."""

    @inject
    @jwt_required()
    def get(self,
            category: str,
            event_service: EventService = event_svc_provider):
        events = event_service.get_by_category(category)
        return events_schema.dump(events), 200


@log_calls("app.routes")
@event_ns.route('/organizer/<string:email>')
class EventsByOrganizerResource(Resource):
    """Retrieve events organized by a specific user."""

    @inject
    @jwt_required()
    def get(self,
            email: str,
            event_service: EventService = event_svc_provider):
        events = event_service.get_by_organizer(email)
        return events_schema.dump(events), 200


@log_calls("app.routes")
@event_ns.route('/date/<string:date_str>')
class EventsByDateResource(Resource):
    """Retrieve events by date (YYYY-MM-DD)."""

    @inject
    @jwt_required()
    def get(self,
            date_str: str,
            event_service: EventService = event_svc_provider):
        try:
            # Parse incoming date string to datetime.date
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            abort(400, description="Date must be in 'YYYY-MM-DD' format")
        events = event_service.get_by_date(date_obj)
        return events_schema.dump(events), 200
