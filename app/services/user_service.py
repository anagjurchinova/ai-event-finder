from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from app.models.user import User


class UserService(ABC):
    """
    Abstract base class defining the interface for user-related operations.

    All methods must be implemented by any concrete UserService class.
    Provides CRUD operations, existence checks, and retrieval by
    various identifiers.
    """

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieve a user by their unique ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            Optional[User]: The user object if found, otherwise None.
        """
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.

        Args:
            email (str): The user's email address.

        Returns:
            Optional[User]: The user object if found, otherwise None.
        """
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[User]:
        """
        Retrieve a user by their name.

        Args:
            name (str): The user's name.

        Returns:
            Optional[User]: The user object if found, otherwise None.
        """
        pass

    @abstractmethod
    def get_all(self) -> List[User]:
        """
        Retrieve all users in the system.

        Returns:
            List[User]: A list of all users.
        """
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        """
        Create a new user or update an existing user.

        Args:
            user (User): The user instance to save.

        Returns:
            User: The saved user instance with any updates applied.
        """
        pass

    @abstractmethod
    def update(self, email: str, data: Dict[str, Any]) -> User:
        """
        Update an existing user's attributes.

        Args:
            email (str): Email of the user to update.
            data (Dict[str, Any]): A dictionary of fields to update.

        Returns:
            User: The updated user instance.
        """
        pass

    @abstractmethod
    def delete_by_id(self, user_id: int) -> None:
        """
        Delete a user by their ID.

        Args:
            user_id (int): The ID of the user to delete.

        Raises:
            Exception: If the user is not found.
        """
        pass

    @abstractmethod
    def exists_by_id(self, user_id: int) -> bool:
        """
        Check if a user exists by their ID.

        Args:
            user_id (int): The ID to check.

        Returns:
            bool: True if user exists, False otherwise.
        """
        pass

    @abstractmethod
    def exists_by_name(self, name: str) -> bool:
        """
        Check if a user exists by their name.

        Args:
            name (str): The name to check.

        Returns:
            bool: True if a user with this name exists, False otherwise.
        """
        pass
