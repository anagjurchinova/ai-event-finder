"""
Transaction Utility for SQLAlchemy with Flask.

Provides decorators for automatic transaction management, conflict retries,
and propagation-aware session handling. Designed for Flask-SQLAlchemy
2.0+ and scoped sessions.

Key features:
- `transactional`: Ensures that a function runs within a transaction.
    - Begins/commits/rolls back only if no active transaction exists.
    - Joins existing transaction if already active.
    - Converts SQLAlchemy `StaleDataError` into a `ConcurrencyException`.
- `retry_conflicts`: Retries a function that raises `ConcurrencyException`
  with exponential backoff.
"""

from contextlib import nullcontext
from functools import wraps
from time import sleep

from sqlalchemy.orm.exc import StaleDataError

from app.error_handler.exceptions import ConcurrencyException
from app.extensions import db


def _current_session():
    """
    Return the actual request-scoped SQLAlchemy Session.

    Handles Flask-SQLAlchemy's scoped_session proxy.

    Returns:
        sqlalchemy.orm.Session: The current session for the request.
    """
    s = db.session
    return s() if callable(s) else s  # unwrap if it's a scoped_session


def retry_conflicts(max_retries: int = 3, backoff_sec: float = 0.1):
    """
       Decorator to retry functions that fail due to concurrency conflicts.

       Retries functions raising `ConcurrencyException` with optional exponential backoff.

       Args:
           max_retries (int): Maximum number of retry attempts (default 3).
           backoff_sec (float): Base backoff time in seconds between retries (default 0.1).

       Usage:
           @retry_conflicts(max_retries=5, backoff_sec=0.2)
           def update_entity(...):
               ...
       """

    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return fn(*args, **kwargs)
                except ConcurrencyException:
                    _current_session().rollback()
                    if attempt == max_retries:
                        raise
                    sleep(backoff_sec * attempt)

        return wrapped

    return decorator


def transactional(fn):
    """
    Decorator to ensure transactional execution of a function.

    Behavior:
    - Begins a new transaction if none exists (outermost).
    - Joins an existing transaction if already active (nested-safe).
    - Commits on success, rolls back on exception.
    - Converts SQLAlchemy `StaleDataError` into `ConcurrencyException`.

    Args:
        fn (Callable): Function to wrap. The session is injected as a keyword argument
                       `session` for transactional operations.

    Returns:
        Callable: Wrapped function with automatic transaction handling.

    Example:
        @transactional
        def create_user(name: str, session: Session):
            user = User(name=name)
            session.add(user)
            return user
    """

    @wraps(fn)
    def wrapped(*args, **kwargs):
        session = _current_session()
        outermost = (session.get_transaction() is None)  # 2.0 API
        method_name = fn.__name__
        print(f"[transactional] method={method_name}, outermost={outermost}, in_txn={session.in_transaction()}")

        ctx = session.begin() if outermost else nullcontext()
        try:
            with ctx:
                result = fn(*args, session=session, **kwargs)
                if outermost:
                    print(f"[transactional] method={method_name} committing outermost transaction")
                return result

        except StaleDataError as e:
            if outermost:
                session.rollback()
                raise ConcurrencyException(
                    f"Resource was updated by another transaction in method {method_name}.") from e
            raise

        except Exception:
            if outermost:
                session.rollback()
            raise

    return wrapped
