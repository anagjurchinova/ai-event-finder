from abc import ABC, abstractmethod
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository(ABC):
    """
    Abstract base class defining the contract for User repository operations.

    Implementations are responsible for:
    - Fetching users by ID, email, or name
    - Persisting and deleting users
    - Checking existence of users
    - Returning lists of users

    All methods operate within the context of a SQLAlchemy session.
    """

    @abstractmethod
    def get_by_id(self, user_id: int, session: Session) -> Optional[User]:
        """
        Retrieve a user by their unique database ID.

        Args:
            user_id (int): The primary key of the user.
            session (Session): SQLAlchemy session to use for the query.

        Returns:
            Optional[User]: The User instance if found, else None.
        """
        pass

    @abstractmethod
    def get_by_email(self, email: str, session: Session) -> Optional[User]:
        """
        Retrieve a user by email.

        Args:
            email (str): The user's email address.
            session (Session): SQLAlchemy session to use.

        Returns:
            Optional[User]: The User instance if found, else None.
        """
        pass

    @abstractmethod
    def get_by_name(self, name: str, session: Session) -> Optional[User]:
        """
        Retrieve a user by name.

        Args:
            name (str): The user's name.
            session (Session): SQLAlchemy session to use.

        Returns:
            Optional[User]: The User instance if found, else None.
        """
        pass

    @abstractmethod
    def get_all(self, session: Session) -> list[type[User]]:
        """
        Retrieve all users.

        Args:
            session (Session): SQLAlchemy session to use.

        Returns:
            List[User]: A list of all User instances.
        """
        pass

    @abstractmethod
    def save(self, user: User, session: Session) -> User:
        """
        Persist a new user or update an existing one.

        Args:
            user (User): The User instance to save.
            session (Session): SQLAlchemy session to use.

        Returns:
            User: The saved User instance, including DB-generated fields.
        """
        pass

    @abstractmethod
    def delete_by_id(self, user_id: int, session: Session) -> None:
        """
        Delete a user by ID.

        Args:
            user_id (int): Primary key of the user to delete.
            session (Session): SQLAlchemy session to use.

        Raises:
            UserNotFound: If the user does not exist.
            AppException: On database-level deletion failure.
        """
        pass

    @abstractmethod
    def exists_by_id(self, user_id: int, session: Session) -> bool:
        """
        Check if a user exists by ID.

        Args:
            user_id (int): Primary key to check.
            session (Session): SQLAlchemy session to use.

        Returns:
            bool: True if a user exists with the given ID, else False.
        """
        pass

    @abstractmethod
    def exists_by_name(self, name: str, session: Session) -> bool:
        """
        Check if a user exists by name.

        Args:
            name (str): User's name to check.
            session (Session): SQLAlchemy session to use.

        Returns:
            bool: True if a user exists with the given name, else False.
        """
        pass
