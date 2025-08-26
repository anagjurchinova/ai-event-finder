from abc import ABC, abstractmethod

class EmbeddingService(ABC):
    """
    Abstract base class for asynchronous generation of vector embeddings from text.

    Implementations should:
    - Accept a plain string (e.g., prompt, event description).
    - Return a normalized numerical embedding as a list of floats.
    - Raise a suitable exception if embedding generation fails or input is invalid.

    This abstraction allows embedding providers (local or cloud-based) to be
    swapped without changing the application logic.
    """

    @abstractmethod
    async def create_embedding(self, text: str) -> list[float]:
        """
        Generate a normalized embedding vector from input text asynchronously.

        Args:
            text (str): Non-empty string to embed (e.g., prompt, formatted event).

        Returns:
            list[float]: Normalized embedding vector of fixed dimension.

        Raises:
            Exception (or provider-specific subclass):
                If the input is invalid, embedding generation fails,
                or the returned vector is malformed.
        """
        pass
