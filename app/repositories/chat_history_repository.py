from typing import List, Dict, Protocol

# A single chat message, with role and content
Message = Dict[str, str]  # {"role": "user" | "assistant" | "system", "content": "..."}

class ChatHistoryRepository(Protocol):
    """
    Interface for storing and retrieving chat history per session or key.

    Implementations can store messages in memory, database, or any persistent store.
    """

    def get(self, key: str) -> List[Message]:
        """
        Retrieve the list of messages for a given session key.

        Args:
            key (str): Session or conversation identifier.

        Returns:
            List[Message]: List of chat messages in chronological order.
        """
        ...

    def set(self, key: str, messages: List[Message]) -> None:
        """
        Overwrite the chat history for a given key.

        Args:
            key (str): Session or conversation identifier.
            messages (List[Message]): List of messages to store.
        """
        ...

    def append(self, key: str, role: str, content: str) -> None:
        """
        Add a single message to the chat history of the given key.

        Args:
            key (str): Session or conversation identifier.
            role (str): Role of the message sender ("user", "assistant", or "system").
            content (str): Message content.
        """
        ...
