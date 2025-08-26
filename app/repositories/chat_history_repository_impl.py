import threading
from typing import List, Dict

from .chat_history_repository import ChatHistoryRepository, Message


class MemoryChatHistoryRepository(ChatHistoryRepository):
    """
    In-memory implementation of ChatHistoryRepository.

    Stores chat messages per session/key with a maximum number of messages.
    Thread-safe using a lock, suitable for multithreaded environments.
    """

    def __init__(self, max_messages: int = 50):
        """
        Initialize the in-memory store.

        Args:
            max_messages (int): Maximum number of messages to retain per key.
                                Older messages are discarded when limit is exceeded.
        """
        self._store: Dict[str, List[Message]] = {}
        self._lock = threading.Lock()
        self._max = max_messages

    def get(self, key: str) -> List[Message]:
        """
       Retrieve the chat history for a given session key.

       Args:
           key (str): Session or conversation identifier.

       Returns:
           List[Message]: List of messages in chronological order.
                          Returns an empty list if no messages exist.
        """
        with self._lock:
            return list(self._store.get(key, []))

    def set(self, key: str, messages: List[Message]) -> None:
        """
        Replace the chat history for a given key, respecting the max message limit.

        Args:
            key (str): Session or conversation identifier.
            messages (List[Message]): List of messages to store.
        """
        with self._lock:
            self._store[key] = list(messages)[-self._max:]

    def append(self, key: str, role: str, content: str) -> None:
        """
        Add a single message to the chat history for the given key.

        If the total messages exceed `max_messages`, older messages are removed.

        Args:
            key (str): Session or conversation identifier.
            role (str): Role of the message sender ("user", "assistant", or "system").
            content (str): Message content to append.
        """
        with self._lock:
            hist = self._store.setdefault(key, [])
            hist.append({"role": role, "content": content})
            if len(hist) > self._max:
                self._store[key] = hist[-self._max:]
