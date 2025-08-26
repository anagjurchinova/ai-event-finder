from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from app.models.event import Event


class EventService(ABC):
    """
    Abstract base class defining the contract for event-related operations.
    Implementations handle persistence, validation, and error management.
    """

    @abstractmethod
    def get_by_title(self, title: str) -> Event:
        """Retrieve a single event by its title."""
        pass

    @abstractmethod
    def get_by_location(self, location: str) -> List[Event]:
        """Retrieve all events matching a given location."""
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> List[Event]:
        """Retrieve all events matching a given category."""
        pass

    @abstractmethod
    def get_by_organizer(self, email: str) -> List[Event]:
        """Retrieve all events organized by a user identified by email."""
        pass

    @abstractmethod
    def get_by_date(self, date: datetime) -> List[Event]:
        """Retrieve all events scheduled on a specific date."""
        pass

    @abstractmethod
    def get_all(self) -> List[Event]:
        """Retrieve a complete list of all events."""
        pass

    @abstractmethod
    def create(self, data: dict) -> Event:
        """
        Create a new event from validated input data.

        Args:
            data: A dictionary containing event details.

        Returns:
            The newly created Event object.
        """
        pass

    @abstractmethod
    def update(self, title: str, patch: dict) -> Event:
        """
        Update an existing event.

        Args:
            title: The title of the event to update.
            patch: A dictionary of fields to update.

        Returns:
            The updated Event object.
        """
        pass

    @abstractmethod
    def delete_by_title(self, title: str) -> None:
        """
        Delete an event by its title.

        Args:
            title: The title of the event to delete.

        Raises:
            EventNotFoundException: If no event with the given title exists.
        """
        pass
