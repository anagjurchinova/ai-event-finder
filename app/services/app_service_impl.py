from typing import List

from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.error_handler.exceptions import UserNotInEventException, UserAlreadyInEventException, EventSaveException
from app.extensions import db
from app.models.event import Event
from app.models.user import User
from app.repositories.event_repository import EventRepository
from app.repositories.user_repository import UserRepository
from app.services.app_service import AppService
from app.util.event_util import return_not_found_by_title_message
from app.util.logging_util import log_calls
from app.util.transaction_util import transactional, retry_conflicts
from app.util.user_util import return_not_found_by_email_message
from app.util.validation_util import validate_user, validate_event


@log_calls("app.services")
class AppServiceImpl(AppService):
    """
    Concrete implementation of AppService that orchestrates user–event interactions.

    Delegates persistence to UserRepository and EventRepository.
    Handles validation, transaction management, retries on conflicts, and custom exceptions.
    """

    def __init__(self, user_repo: UserRepository, event_repo: EventRepository):
        """
        Initialize AppServiceImpl with repositories.

        user_repo: Used to lookup users by email.
        event_repo: Used to lookup and persist events by title.
        """
        self.user_repo = user_repo
        self.event_repo = event_repo

    @retry_conflicts(max_retries=3, backoff_sec=0.1)
    @transactional
    def add_participant_to_event(self, event_title: str, user_email: str, session=None) -> None:
        """
        Add a user (by email) to a specific event (by title).

        Performs validation and ensures the user is not already in the event.
        Retries up to 3 times on version conflicts.
        Converts duplicate-invite database errors into UserAlreadyInEventException.

        Raises:
            UserAlreadyInEventException: If the user is already a participant.
            EventSaveException: If saving to the database fails for other reasons.
        """

        event = self._get_event_and_validate(event_title, session)
        user = self._get_user_and_validate(user_email, session)

        if user in event.guests:
            raise UserAlreadyInEventException(user_email=user_email,
                                              event_title=event_title)

        try:
            event.guests.append(user)
            self.event_repo.save(event, session)
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                raise UserAlreadyInEventException(user_email=user_email,
                                                  event_title=event_title)
            raise EventSaveException(original_exception=e)

    @retry_conflicts(max_retries=3, backoff_sec=0.1)
    @transactional
    def remove_participant_from_event(self, event_title: str, user_email: str, session=None) -> None:
        """
        Remove a user (by email) from a specific event (by title).

        Validates that both user and event exist, and that the user is a participant.

        Raises:
            UserNotInEventException: If the user is not currently participating.
        """
        event = self._get_event_and_validate(event_title=event_title, session=session)
        user = self._get_user_and_validate(user_email=user_email, session=session)

        if user not in event.guests:
            raise UserNotInEventException(user_email=user_email, event_title=event_title)
        event.guests.remove(user)
        self.event_repo.save(event, session)

    def list_participants(self, event_title: str) -> List[User]:
        """
         Retrieve all participants of a specific event.

         Raises:
             EventNotFoundException: If the event does not exist.
         """
        event = self._get_event_and_validate(event_title=event_title, session=db.session)
        return list(event.guests)

    # ----------- PRIVATE HELPERS ------------- #
    def _get_event_and_validate(self, event_title: str, session: Session) -> Event:
        """
        Fetch an event by title and validate its existence.

        Raises:
            EventNotFoundException: If the event does not exist.
        """

        event = self.event_repo.get_by_title(event_title, session)
        validate_event(event, return_not_found_by_title_message(event_title))
        return event

    def _get_user_and_validate(self, user_email: str, session: Session) -> User:
        """
       Fetch a user by email and validate its existence.

       Raises:
           UserNotFoundException: If the user does not exist.
       """
        user = self.user_repo.get_by_email(user_email, session)
        validate_user(user, return_not_found_by_email_message(user_email))
        return user
