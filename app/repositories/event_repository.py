from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Sequence

from sqlalchemy.orm import Session

from app.models.event import Event


class EventRepository(ABC):
    """
    Abstract base class defining the interface for an Event repository.

    This repository manages Event entities and provides methods for:
        - Retrieval (by ID, title, organizer, date, location, category, or embedding similarity)
        - Deletion
        - Saving or updating
        - Existence checks

    Implementations should handle database sessions and maintain transactional integrity
    for all operations.
    """

    # ------------------------
    # Retrieval Methods
    # ------------------------

    @abstractmethod
    def get_all(self, session: Session) -> List[Event]:
        """
        Retrieve all events in the repository.

        Args:
            session (Session): SQLAlchemy session to use for the query.

        Returns:
            List[Event]: List of all Event instances.
        """
        pass

    @abstractmethod
    def get_by_id(self, event_id: int, session: Session) -> Optional[Event]:
        """
        Retrieve a single event by its unique ID.

        Args:
            event_id (int): The primary key of the event.
            session (Session): SQLAlchemy session to use.

        Returns:
            Optional[Event]: The matching Event, or None if not found.
        """
        pass

    @abstractmethod
    def get_by_title(self, title: str, session: Session) -> Optional[Event]:
        """
        Retrieve all events with the specified title.

        Args:
            title (str): The title to match.
            session (Session): SQLAlchemy session to use.

        Returns:
            List[Event]: List of events with the given title.
        """
        pass

    @abstractmethod
    def get_by_organizer_id(self, organizer_id: int, session: Session) -> List[Event]:
        """
        Retrieve all events organized by a specific user.

        Args:
            organizer_id (int): The ID of the organizer.
            session (Session): SQLAlchemy session to use.

        Returns:
            List[Event]: List of events organized by the user.
        """
        pass

    @abstractmethod
    def get_by_date(self, date: datetime, session: Session) -> List[Event]:
        """
        Retrieve all events scheduled on a specific date.

        Args:
            date (datetime): The date to filter by.
            session (Session): SQLAlchemy session to use.

        Returns:
            List[Event]: List of events held on the given date.
        """
        pass

    @abstractmethod
    def get_by_location(self, location: str, session: Session) -> List[Event]:
        """
        Retrieve all events held at a specific location.

        Args:
            location (str): Location to filter by.
            session (Session): SQLAlchemy session to use.

        Returns:
            List[Event]: List of events at the given location.
        """
        pass

    @abstractmethod
    def get_by_category(self, category: str, session: Session) -> List[Event]:
        """
        Retrieve all events within a specific category.

        Args:
            category (str): Category to filter by.
            session (Session): SQLAlchemy session to use.

        Returns:
            List[Event]: List of events in the category.
        """
        pass

    @abstractmethod
    def search_by_embedding(self, query_vector: Sequence[float], k: int, probes: Optional[int]) -> List[Event]:
        """
        Retrieve the top-K events whose embeddings are most similar to the given vector.

        Args:
            query_vector (Sequence[float]): The query embedding vector.
            k (int): Number of top results to return.
            probes (Optional[int]): Optional parameter to control search precision (implementation-specific).

        Returns:
            List[Event]: Top-K events ordered by similarity (most similar first).
        """
        pass

    # ------------------------
    # Deletion Methods
    # ------------------------

    @abstractmethod
    def delete_by_id(self, event_id: int, session: Session) -> None:
        """
        Delete an event by its ID.

        Args:
            event_id (int): The ID of the event to delete.
            session (Session): SQLAlchemy session to use.
        """
        pass

    @abstractmethod
    def delete_by_title(self, title: str, session: Session) -> None:
        """
        Delete all events with a given title.

        Args:
            title (str): The title of events to delete.
            session (Session): SQLAlchemy session to use.

        Note:
            This assumes multiple events can share the same title.
        """
        pass

    # ------------------------
    # Save Method
    # ------------------------

    @abstractmethod
    def save(self, event: Event, session: Session) -> Event:
        """
        Save a new event or update an existing one.

        Args:
            event (Event): Event instance to save or update.
            session (Session): SQLAlchemy session to use.

        Returns:
            Event: The saved or updated Event instance with generated fields populated.
        """
        pass

    # ------------------------
    # Existence Checks
    # ------------------------

    @abstractmethod
    def exists_by_id(self, event_id: int, session: Session) -> bool:
        """
        Check if an event exists with the given ID.

        Args:
            event_id (int): The ID to check.
            session (Session): SQLAlchemy session to use.

        Returns:
            bool: True if the event exists, False otherwise.
        """
        pass

    @abstractmethod
    def exists_by_title(self, title: str, session: Session) -> bool:
        """
        Check if any events exist with the given title.

        Args:
            title (str): Title to check.
            session (Session): SQLAlchemy session to use.

        Returns:
            bool: True if one or more events exist with the title, False otherwise.
        """
        pass

    @abstractmethod
    def exists_by_location(self, location: str, session: Session) -> bool:
        """
        Check if any events exist at a given location.

        Args:
            location (str): Location to check.
            session (Session): SQLAlchemy session to use.

        Returns:
            bool: True if one or more events exist at the location, False otherwise.
        """
        pass

    @abstractmethod
    def exists_by_category(self, category: str, session: Session) -> bool:
        """
        Check if any events exist within a specific category.

        Args:
            category (str): Category to check.
            session (Session): SQLAlchemy session to use.

        Returns:
            bool: True if one or more events exist in the category, False otherwise.
        """
        pass

    @abstractmethod
    def exists_by_date(self, date: datetime, session: Session) -> bool:
        """
        Check if any events are scheduled on a specific date.

        Args:
            date (datetime): Date to check.
            session (Session): SQLAlchemy session to use.

        Returns:
            bool: True if one or more events exist on the date, False otherwise.
        """
        pass
