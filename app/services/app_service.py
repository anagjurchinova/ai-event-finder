from abc import ABC, abstractmethod
from typing import List

from app.models.user import User


class AppService(ABC):
    """
   Concrete implementation of AppService managing event participation.
   Handles adding/removing participants to events and listing participants.
   Validates existence of users and events, and ensures no duplicate participation.
   """

    @abstractmethod
    def add_participant_to_event(self, event_title: str, user_email: str) -> None:
        """
       Add a user to an event's participant list.

       Raises:
           EventNotFoundException: If the specified event does not exist.
           UserNotFoundException: If the specified user does not exist.
           DuplicateParticipantException: If the user is already participating in the event.
       """
        pass

    @abstractmethod
    def remove_participant_from_event(self, event_title: str, user_email: str) -> None:
        """
        Remove a user from an event's participant list.

        Raises:
            EventNotFoundException: If the specified event does not exist.
            UserNotFoundException: If the specified user does not exist.
        """
        pass

    @abstractmethod
    def list_participants(self, event_title: str) -> List[User]:
        """
        Retrieve a list of all participants for a given event.

        Raises:
            EventNotFoundException: If the specified event does not exist.
        Returns:
            List[User]: The users participating in the event.
        """
        pass
