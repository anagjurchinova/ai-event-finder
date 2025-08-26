from datetime import datetime
from typing import List

from app.error_handler.exceptions import (
    EventNotFoundException,
    EventSaveException,
    EventDeleteException,
    EventAlreadyExistsException
)
from app.extensions import db
from app.models.event import Event
from app.repositories.event_repository import EventRepository
from app.repositories.user_repository import UserRepository
from app.services.embedding.embedding_service import EmbeddingService
from app.services.event_service import EventService
from app.util.format_event_util import format_event
from app.util.logging_util import log_calls
from app.util.transaction_util import transactional, retry_conflicts
from app.util.validation_util import validate_user, validate_event


@log_calls("app.services")
class EventServiceImpl(EventService):
    """
    Concrete implementation of EventService using EventRepository and UserRepository.

    Adds:
        - Transaction management via @transactional
        - Retry on conflicts via @retry_conflicts
        - Validation for users and events
        - Asynchronous embedding creation for event content
        - Exception handling for common failure scenarios
    """

    def __init__(self, event_repository: EventRepository, user_repository: UserRepository,
                 embedding_service: EmbeddingService):
        """
        Initialize EventServiceImpl with required repositories and services.

        Args:
            event_repository: Repository for event persistence.
            user_repository: Repository to access user information.
            embedding_service: Service to generate embeddings for events.
        """
        self.embedding_service = embedding_service
        self.event_repository = event_repository
        self.user_repository = user_repository

    @transactional
    def get_by_title(self, title: str, session=None) -> Event:
        """Retrieve a single event by title, raises EventNotFoundException if not found."""
        event = self.event_repository.get_by_title(title, session)
        validate_event(event, f"No event with title '{title}'")
        return event

    @transactional
    def get_by_location(self, location: str, session=None) -> List[Event]:
        """Retrieve all events for a given location."""
        return self.event_repository.get_by_location(location, session)

    @transactional
    def get_by_category(self, category: str, session=None) -> List[Event]:
        """Retrieve all events for a given category."""
        return self.event_repository.get_by_category(category, session)

    @transactional
    def get_by_organizer(self, email: str, session=None) -> List[Event]:
        """Retrieve all events organized by a given user's email."""
        organizer = self.user_repository.get_by_email(email, session)
        validate_user(organizer, f"No user found with email {email}")
        return self.event_repository.get_by_organizer_id(organizer.id, session)

    @transactional
    def get_by_date(self, date: datetime, session=None) -> List[Event]:
        """Retrieve all events scheduled on a specific date."""
        return self.event_repository.get_by_date(date, session)

    @transactional
    def get_all(self, session=None) -> List[Event]:
        """Retrieve all events."""
        return self.event_repository.get_all(session)

    @retry_conflicts(max_retries=3, backoff_sec=0.1)
    @transactional
    def delete_by_title(self, title: str, session=None) -> None:
        """
        Delete an event by title.

        Raises:
            EventNotFoundException: If the event does not exist.
            EventDeleteException: If deletion fails.
        """
        event = self.event_repository.get_by_title(title, session)
        if not event:
            raise EventNotFoundException(f"Event with title '{title}' not found.")
        try:
            self.event_repository.delete_by_title(title, session)
        except Exception as e:
            raise EventDeleteException(original_exception=e)

    async def create(self, data: dict) -> Event:
        """
        Create a new event asynchronously with embedding generation.

        Steps:
            1. Check for duplicate title.
            2. Resolve organizer email to User object.
            3. Build Event object excluding 'organizer_email'.
            4. Generate embedding asynchronously (external call to embedding service).
            5. Persist the event.

        Raises:
            EventAlreadyExistsException: If an event with the same title exists.
            EventSaveException: If saving the event fails.
            EventNotFoundException: If organizer email is invalid.
        """

        if self.event_repository.get_by_title(data['title'], db.session):
            # end the read txn and bail
            db.session.rollback()
            raise EventAlreadyExistsException(data['title'])

        email = data.get('organizer_email')
        organizer = self.user_repository.get_by_email(email, db.session)
        validate_user(organizer, f"No user found with email {email}")

        payload = {k: v for k, v in data.items() if k != 'organizer_email'}
        event = Event(**payload, organizer_id=organizer.id)

        formatted = format_event(event)
        db.session.rollback()

        event.embedding = await self.embedding_service.create_embedding(formatted)

        try:
            saved = self._persist(event, recheck_title=True, title_for_recheck=data['title'])
            return saved
        except EventAlreadyExistsException:
            raise
        except Exception as e:
            raise EventSaveException(original_exception=e)

    # noinspection PyUnreachableCode
    async def update(self, title: str, patch: dict) -> Event:
        """
        Update an existing event by title.

        Steps:
            1. Fetch existing event (read-only transaction).
            2. Apply patch fields to a temporary Event object.
            3. Generate new embedding asynchronously (external call to embedding service).
            4. Persist updated event transactionally.

        Raises:
            EventNotFoundException: If the event does not exist.
            EventSaveException: If saving fails.
        """

        existing_event = self.event_repository.get_by_title(title, db.session)
        if not existing_event:
            raise EventNotFoundException(f"Event with title '{title}' not found.")

        temp_data = {col: getattr(existing_event, col) for col in existing_event.__table__.columns.keys()}
        temp_data.update(patch)
        temp_event = Event(**temp_data)

        db.session.rollback()

        temp_event.embedding = await self.embedding_service.create_embedding(format_event(temp_event))

        # noinspection PyUnreachableCode
        @transactional
        def _write_update(session=None):
            # re-fetch to attach to current transactional session
            event_to_update = self.event_repository.get_by_title(title, session)
            if not event_to_update:
                raise EventNotFoundException(f"Event with title '{title}' no longer exists.")

            for key, value in patch.items():
                setattr(event_to_update, key, value)

            event_to_update.embedding = temp_event.embedding

            session.flush()
            return event_to_update

        return _write_update()

    @retry_conflicts(max_retries=3, backoff_sec=0.1)
    @transactional
    def _persist(self, event: Event, *, session=None, recheck_title: bool = False,
                 title_for_recheck: str | None = None) -> Event:
        """
        Persist an event to the database, optionally checking for title conflicts.

        Args:
            event: Event object to persist.
            recheck_title: If True, re-check for conflicting title (used in create).
            title_for_recheck: Title to check for conflicts.

        Raises:
            EventAlreadyExistsException: If a conflicting title is found.
        """

        if recheck_title and title_for_recheck:
            with session.no_autoflush:
                found = self.event_repository.get_by_title(title_for_recheck, session)

                if found and getattr(found, "id", None) != getattr(event, "id", None):
                    raise EventAlreadyExistsException(title_for_recheck)

        return self.event_repository.save(event, session)
