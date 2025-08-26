"""
exceptions.py

Custom exceptions used across the Event Finder application.

Organized by domain:

- User-related exceptions
- Event-related exceptions
- Embedding and model-related exceptions
- Concurrency / internal error exceptions
"""


# ------------------------
# User-related exceptions
# ------------------------


class UserNotFoundException(Exception):
    """
    Raised when no user exists for the given identifier.
    Must provide exactly one identifier (user_id, name, or email).

    Example:
        raise UserNotFoundException("User with id=5 not found")
    """

    def __init__(self, message: str):
        super().__init__(message)


class DuplicateEmailException(Exception):
    """
    Raised when attempting to create or update a user with an email
    that is already taken.
    """

    def __init__(self, email: str):
        self.email = email
        message = f"User with email {email} already exists."
        super().__init__(message)


class UserSaveException(Exception):
    """
    Raised when persisting a user to the database fails.
    Attributes:
        original_exception (Exception|None): The underlying exception.
    """

    def __init__(self, original_exception: Exception = None):
        self.original_exception = original_exception
        # generic message only
        message = "Unable to save user due to an internal error."
        super().__init__(message)


class UserDeleteException(Exception):
    """
    Raised when deleting a user from the database fails (aside from not found).
    Attributes:
        user_id (int|None): ID of the user we tried to delete.
        original_exception (Exception|None): The underlying exception.
    """

    def __init__(self, user_id: int = None, original_exception: Exception = None):
        self.user_id = user_id
        self.original_exception = original_exception
        # generic message only
        message = f"Unable to delete user{f' with id={user_id}' if user_id is not None else ''}."
        super().__init__(message)


# ------------------------
# Event-related exceptions
# ------------------------

class EventNotFoundException(Exception):
    """Raised when no event exists for the given identifier."""

    def __init__(self, message):
        super().__init__(message)


class EventDeleteException(Exception):
    """
    Raised when deleting an event from the database fails (aside from not found).
    Attributes:
        event_id (int|None): ID of the event we tried to delete.
        original_exception (Exception|None): The underlying exception.
    """

    def __init__(self, event_id: int = None, original_exception: Exception = None):
        self.event_id = event_id
        self.original_exception = original_exception

        message = f"Unable to delete event{f' with id={event_id}' if event_id is not None else ''}."
        super().__init__(message)


class EventAlreadyExistsException(Exception):
    """Raised when attempting to create an event that already exists."""

    def __init__(self, event_name: str, original_exception: Exception = None):
        self.original_exception = original_exception

        message = f"Event with name {event_name} already exists."
        super().__init__(message)


class UserAlreadyInEventException(Exception):
    """Raised when a user is already in an event."""

    def __init__(self, event_title: str, user_email: str):
        self.event_title = event_title
        self.user_email = user_email
        message = f"User with email {user_email} already exists in event with title {event_title}."
        super().__init__(message)


class UserNotInEventException(Exception):
    """Raised when a user is not part of an event they are expected to be in."""

    def __init__(self, event_title: str, user_email: str):
        self.event_title = event_title
        self.user_email = user_email
        message = f"User with email {user_email} doesn't exist in event with title {event_title}."
        super().__init__(message)


class InvalidDateFormatException(Exception):
    """Raised when a date string cannot be parsed to the expected format."""

    def __init__(self, date_string: str, date_format: str, original_exception: Exception = None):
        self.original_exception = original_exception

        message = f"Invalid date format {date_string}. Expected format: {date_format}."
        super().__init__(message)


class EventSaveException(Exception):
    """Raised when persisting an event fails due to an internal error."""

    def __init__(self, original_exception: Exception):
        super().__init__("Unable to save event due to an internal error.")
        self.original_exception = original_exception


# ------------------------
# Embedding / Model exceptions
# ------------------------


class EmbeddingServiceException(Exception):
    """
    Raised for any embedding-related failure (bad input, provider error, shape mismatch, etc.).

    Attributes:
        status_code (int): HTTP-like code (4xx vs 5xx).
        original_exception (Exception|None): The underlying exception.
    """

    def __init__(self, message: str, status_code: int = 500, original_exception: Exception | None = None):
        self.status_code = int(status_code)
        self.original_exception = original_exception
        super().__init__(message)


class ModelWarmupException(Exception):
    """Raised when a model warm-up at app start fails."""

    def __init__(self, message: str):
        super().__init__(message)


# ------------------------
# Internal / Concurrency exceptions
# ------------------------


class ConcurrencyException(Exception):
    """
    Raised when a database update fails due to concurrent modifications.

    This typically occurs in optimistic locking scenarios, where
    a record has been modified by another transaction after it
    was last read, preventing an update to stale data.
    """

    def __init__(self, message: str):
        super().__init__(message)
