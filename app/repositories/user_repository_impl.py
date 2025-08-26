from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.util.logging_util import log_calls


@log_calls("app.repositories")
class UserRepositoryImpl(UserRepository):
    """
    Concrete implementation of the UserRepository interface using SQLAlchemy ORM.

    Responsibilities:
    - Provides CRUD operations for the User model.
    - Supports existence checks by ID or name.
    - Designed for use with request-scoped SQLAlchemy sessions.
    - Does not commit or rollback transactions; assumes the caller manages session lifecycle.
    """

    def get_by_id(self, user_id: int, session: Session) -> Optional[User]:
        """
        Retrieve a user by their primary key.

        Args:
            user_id (int): The unique identifier of the user.
            session (Session): SQLAlchemy session to use.

        Returns:
            Optional[User]: The User instance if found, otherwise None.
        """
        return session.query(User).get(user_id)

    def get_by_email(self, email: str, session: Session) -> Optional[User]:
        """
        Retrieve a user by email.

        Args:
            email (str): The user's email address.
            session (Session): SQLAlchemy session to use.

        Returns:
            Optional[User]: The User instance if found, otherwise None.
        """
        return session.query(User).filter_by(email=email).first()

    def get_by_name(self, name: str, session: Session) -> Optional[User]:
        """
        Retrieve a user by name.

        Args:
            name (str): The user's name.
            session (Session): SQLAlchemy session to use.

        Returns:
            Optional[User]: The User instance if found, otherwise None.
        """
        return session.query(User).filter_by(name=name).first()

    def get_all(self, session:Session) -> list[type[User]]:
        """
        Retrieve all users in the database.

        Args:
            session (Session): SQLAlchemy session to use.

        Returns:
            list[User]: A list of all User instances.
        """
        return session.query(User).all()

    def save(self, user: User, session: Session) -> User:
        """
        Persist a new user or update an existing one.

        Args:
            user (User): The User instance to save.
            session (Session): SQLAlchemy session to use.

        Returns:
            User: The saved User instance.
        """
        session.add(user)
        return user

    def delete_by_id(self, user_id: int, session: Session) -> None:
        """
        Delete a user by their ID.

        Args:
            user_id (int): The unique identifier of the user.
            session (Session): SQLAlchemy session to use.

        Notes:
            - Logs the deletion process.
            - Flushes the session to persist deletion immediately.
            - Does not handle transaction commit; caller is responsible.
        """
        user = session.get(User, user_id)
        print(f"[repository] deleting user {user_id}, found={bool(user)}")
        session.delete(user)
        session.flush()
        print(f"[repository] flushed delete for user {user_id}")

    def exists_by_id(self, user_id: int, session: Session) -> bool:
        """
        Check if a user exists by ID.

        Args:
            user_id (int): The primary key to check.
            session (Session): SQLAlchemy session to use.

        Returns:
            bool: True if a user with this ID exists, False otherwise.
        """
        user = session.query(User).get(user_id)
        return bool(user)

    def exists_by_name(self, name: str, session: Session) -> bool:
        """
        Check if a user exists by name.

        Args:
            name (str): The name to check.
            session (Session): SQLAlchemy session to use.

        Returns:
            bool: True if a user with this name exists, False otherwise.
        """
        return session.query(User).filter_by(name=name).first() is not None

