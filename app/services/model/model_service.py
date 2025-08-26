from abc import ABC, abstractmethod
from typing import List, Optional

from openai.types.chat import ChatCompletionMessageParam

from app.repositories.event_repository import EventRepository
from app.services.embedding.embedding_service import EmbeddingService
from app.util.model_util import DEFAULT_SYS_PROMPT


class ModelService(ABC):
    """
    Abstract base class for chat-based event retrieval and reasoning.

    This service defines the contract for:
    - Converting user queries into embeddings via `EmbeddingService`
    - Using vector search (via `EventRepository`) to retrieve relevant events
    - Building messages (system + user context) to query an LLM
    - Returning either a conversational answer or a structured value (e.g., count)

    Concrete implementations (e.g., `ModelServiceImpl`) are responsible for
    integrating with a specific LLM provider and handling the full query lifecycle.
    """

    def __init__(
            self,
            event_repository: EventRepository,
            embedding_service: EmbeddingService,
            sys_prompt: str | None = None
    ):
        """
        Initialize a ModelService with its dependencies.

        Args:
            event_repository: Repository interface for event storage and vector search.
            embedding_service: Service for generating embeddings from text.
            sys_prompt: Optional system prompt to guide the LLM.
                        Defaults to `DEFAULT_SYS_PROMPT` if not provided.
        """
        self.event_repository = event_repository
        self.embedding_service = embedding_service
        self.sys_prompt = sys_prompt or DEFAULT_SYS_PROMPT

    @abstractmethod
    async def query_prompt(self, user_prompt: str, session_key: str) -> str:
        """
        Handle a free-form user query against the event database.

        The standard flow is:
        1. Embed the user prompt with `embedding_service`.
        2. Perform vector similarity search via `event_repository.search_by_embedding`.
        3. Format retrieved events into context.
        4. Build a system + user message sequence.
        5. Query the underlying LLM asynchronously.
        6. Return the assistant’s text response.

        Args:
            user_prompt: The raw input query from the user.
            session_key: A key for tracking conversational state (LLM-dependent).

        Returns:
            str: Assistant response, informed by retrieved events.
        """

    @abstractmethod
    def build_messages(
            self,
            sys_prompt: Optional[str],
            context: str,
            user_prompt: str,
    ) -> List[ChatCompletionMessageParam]:
        """
        Construct a valid OpenAI ChatCompletion message sequence.

        Implementations are responsible for:
          - Combining the system prompt with contextual information
            (e.g., retrieved events, prior history).
          - Including the user’s raw prompt as the final message.
          - Returning a sequence of role-based messages that conform to
            the OpenAI `ChatCompletionMessageParam` schema.

        Args:
            sys_prompt (str | None):
                The base system-level instructions to steer the assistant.
                May be None, in which case the implementation should
                handle defaults.
            context (str):
                Contextual grounding (retrieved events, history, or fallback).
            user_prompt (str):
                The original user input.

        Returns:
            List[ChatCompletionMessageParam]:
                Messages formatted for the OpenAI API, e.g.:
                [
                    {"role": "system", "content": "..."},
                    {"role": "user", "content": "..."}
                ]
        """
        pass

    @abstractmethod
    async def extract_requested_event_count(self, user_prompt: str) -> int:
        """
        Extract the number of events requested from a user query.

        The extraction should be handled via an LLM call with a specialized
        system prompt that coerces the model to return a plain integer.

        Expected behavior:
        - Prefer explicit positive integers in the prompt.
        - Handle ranges/comparisons sensibly (e.g., "up to 7" → 7).
        - Ignore unrelated numerals (dates, times, etc.).
        - Clamp to a minimum of 1 if the result is non-positive.
        - If ambiguous, fall back to the configured default.

        Args:
            user_prompt: The user’s query, e.g. "Show me 5 events this weekend".

        Returns:
            int: The normalized requested event count.
        """
