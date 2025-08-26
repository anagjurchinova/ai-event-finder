import numpy as np
from numpy.linalg import norm
from openai import AsyncOpenAI

from app.configuration.config import Config
from app.error_handler.exceptions import EmbeddingServiceException
from app.util.logging_util import log_calls
from .embedding_service import EmbeddingService


@log_calls("app.services")
class EmbeddingServiceImpl(EmbeddingService):
    """
    Concrete implementation of EmbeddingService using OpenAI (or local) models.

    Generates async embeddings with unified dimensions and normalizes vectors.
    Suitable for ASGI environments and fully non-blocking.

    Attributes:
        client (AsyncOpenAI): The async OpenAI client used to generate embeddings.
        model (str): The embedding model name. Defaults to a local or OpenAI model
            based on configuration.
    """

    def __init__(self, client: AsyncOpenAI, model: str | None = None):
        """
        Initialize the embedding service with a client and optional model.

        Args:
            client (AsyncOpenAI): Async client for OpenAI embeddings.
            model (str | None): Optional specific model to use. Defaults to
                Config.DMR_EMBEDDING_MODEL for local or Config.OPENAI_EMBEDDING_MODEL for cloud.
        """
        self.client = client
        self.model = model or (
            Config.DMR_EMBEDDING_MODEL if Config.PROVIDER == "local"
            else Config.OPENAI_EMBEDDING_MODEL
        )

    async def create_embedding(self, text: str) -> list[float]:
        """
        Generate a normalized embedding vector for the given text.

        Args:
            text (str): Input text to embed. Must be a non-empty string.

        Returns:
            list[float]: Normalized embedding vector of dimension Config.UNIFIED_VECTOR_DIM.

        Raises:
            EmbeddingServiceException: If the input is invalid, OpenAI request fails,
                the returned embedding is malformed, or normalization fails.
        """

        if not isinstance(text, str) or not text.strip():
            raise EmbeddingServiceException("Input text must be a non-empty string.")

        try:
            resp = await self.client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=Config.UNIFIED_VECTOR_DIM,
                encoding_format="float"
            )

        except Exception as e:
            raise EmbeddingServiceException(
                "OpenAI embedding request failed.", original_exception=e
            )


        try:
            emb = resp.data[0].embedding
        except Exception as e:
            raise EmbeddingServiceException(
                "OpenAI returned an unexpected embedding payload.", original_exception=e
            )

        if len(emb) != Config.UNIFIED_VECTOR_DIM:
            raise EmbeddingServiceException(
                f"Expected {Config.UNIFIED_VECTOR_DIM}-dim embedding, got {len(emb)}"
            )
        vec = np.array(emb, dtype=np.float32)
        norm_val = norm(vec)
        print(norm_val)
        if norm_val == 0:
            raise EmbeddingServiceException("Embedding vector has zero norm, cannot normalize.")
        normalized = vec / norm_val

        norm_val = norm(normalized)
        print(norm_val)

        return normalized.tolist()
