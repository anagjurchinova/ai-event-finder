from __future__ import annotations

from typing import List, Dict, Any, cast, Optional

from openai import AsyncOpenAI
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from app.configuration.config import Config
from app.repositories.chat_history_repository import ChatHistoryRepository, Message
from app.repositories.event_repository import EventRepository
from app.services.embedding.embedding_service import EmbeddingService
from app.services.model.model_service import ModelService
from app.util.format_event_util import format_event
from app.util.model_util import COUNT_EXTRACT_SYS_PROMPT


class ModelServiceImpl(ModelService):
    """
    Concrete implementation of the `ModelService` abstraction.

    Responsibilities:
    - Embedding user prompts and performing retrieval (RAG) from event data.
    - Constructing context from retrieved events and recent conversation history.
    - Calling an LLM (via OpenAI API or local model) with the enriched prompt.
    - Persisting chat history across turns (optional, if `ChatHistoryRepository` is provided).

    This service enables a conversational interface where the model:
    1. Retrieves relevant events based on semantic similarity.
    2. Incorporates conversation history into the context.
    3. Responds naturally while grounding answers in retrieved knowledge.
    """

    def __init__(
            self,
            event_repository: EventRepository,
            embedding_service: EmbeddingService,
            client: AsyncOpenAI,  # DI-provided OpenAI client
            model: str | None = None,
            sys_prompt: Optional[str] = None,
            history_repo: Optional[ChatHistoryRepository] = None,
    ):
        """
        Initialize the service.

        Args:
            event_repository (EventRepository):
                Provides access to events to search via vector embeddings.
            embedding_service (EmbeddingService):
                Generates embeddings from input text.
            client (AsyncOpenAI):
                Asynchronous OpenAI (or local) client for LLM calls.
            model (str | None, optional):
                Override for the model to use. Defaults to configured model.
            sys_prompt (str | None, optional):
                Optional system prompt to steer model behavior.
            history_repo (ChatHistoryRepository | None, optional):
                Optional storage for chat history (per session).
        """
        super().__init__(event_repository, embedding_service, sys_prompt=sys_prompt)
        self.client = client
        self.model = model or (Config.DMR_LLM_MODEL if Config.PROVIDER == "local" else Config.OPENAI_MODEL)
        self.history_repo = history_repo

    # ---------------------------
    # Public API
    # ---------------------------

    async def query_prompt(self, user_prompt: str, session_key: str) -> str:
        """
        Process a user query through the full RAG workflow.

        Steps:
            1. Embed the user prompt.
            2. Estimate number of relevant events to retrieve (K).
            3. Retrieve top-K events from the repository.
            4. Gather recent chat history (≤ Config.MAX_HISTORY_IN_CONTEXT).
            5. Construct messages (system + user) with context and query.
            6. Call the LLM and return its answer.
            7. Persist conversation turns if history tracking is enabled.

        Args:
            user_prompt (str):
                The raw query from the user.
            session_key (str):
                Identifier for maintaining per-session history.

        Returns:
            str: The assistant’s final response.
        """

        embed_vector = await self.embedding_service.create_embedding(user_prompt)

        k = await self.extract_requested_event_count(user_prompt)
        events = self.event_repository.search_by_embedding(embed_vector, k)
        rag_docs = "\n".join([format_event(e) for e in events])

        history_block = ""
        count = 0
        if session_key and self.history_repo:
            prior: List[Message] = self.history_repo.get(session_key)
            recent = prior[-Config.MAX_HISTORY_IN_CONTEXT:] if prior else []
            count = len(recent)
            if recent:
                lines = [
                    f"{m['role']}: {m['content']}".strip()
                    for m in recent
                    if m.get("role") and m.get("content")
                ]
                history_block = "\n".join(lines)

        parts: List[str] = []
        if rag_docs.strip():
            parts.append(f"DOCUMENTS:\n{rag_docs}")
        if history_block:
            parts.append(f"RECENT MESSAGES (last {count}):\n{history_block}")
            # print(f"RECENT MESSAGES (last {count}):\n{history_block}")
            print(history_block)
        combined_context = "\n\n".join(parts) if parts else "No context available."

        messages: List[ChatCompletionMessageParam] = self.build_messages(
            self.sys_prompt, combined_context, user_prompt
        )
        cfg_opts: Dict[str, Any] = dict(getattr(Config, "OPENAI_GEN_OPTS", {}) or {})
        cfg_opts.pop("stream", None)  # ensure non-streaming here

        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **cfg_opts,
        )
        answer = (resp.choices[0].message.content if resp.choices and resp.choices[0].message else "") or ""
        answer = answer.strip()

        if session_key and self.history_repo:
            self.history_repo.append(session_key, "user", user_prompt)
            self.history_repo.append(session_key, "assistant", answer)

        return answer

    def build_messages(
            self,
            sys_prompt: Optional[str],
            context: str,
            user_prompt: str,
    ) -> List[ChatCompletionMessageParam]:
        """
        Construct a valid OpenAI ChatCompletion message sequence.

        Args:
            sys_prompt (str | None):
                The base system-level instructions.
            context (str):
                The contextual grounding (retrieved events + history).
            user_prompt (str):
                The original user input.

        Returns:
            List[ChatCompletionMessageParam]:
                Messages formatted for the OpenAI API.
        """

        sys_text = (sys_prompt or "").strip()
        ctx_text = (context or "no events retrieved").strip()

        system_msg: ChatCompletionSystemMessageParam = {
            "role": "system",
            "content": f"{sys_text}\n\n{ctx_text}".strip(),
        }
        user_msg: ChatCompletionUserMessageParam = {
            "role": "user",
            "content": user_prompt,
        }

        return cast(List[ChatCompletionMessageParam], [system_msg, user_msg])

    async def extract_requested_event_count(self, user_prompt: str) -> int:
        """
        Estimate how many events the user wants retrieved.

        Uses a lightweight LLM call with a specialized system prompt (`COUNT_EXTRACT_SYS_PROMPT`)
        to parse an integer from the user request.

        Args:
            user_prompt (str):
                The natural language query (e.g., "Show me the top 5 events").

        Returns:
            int: The number of events requested by the user (defaults to 0 if parsing fails).
        """

        cfg_opts: Dict[str, Any] = dict(getattr(Config, "OPENAI_EXTRACT_K_OPTS", {}) or {})
        cfg_opts.pop("stream", None)  # remove streaming if present

        system_msg: ChatCompletionSystemMessageParam = {
            "role": "system",
            "content": f"{COUNT_EXTRACT_SYS_PROMPT}\n\n".strip(),
        }
        user_msg: ChatCompletionUserMessageParam = {
            "role": "user",
            "content": user_prompt,
        }
        messages = [system_msg, user_msg]

        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **cfg_opts,
        )

        content = (resp.choices[0].message.content
                   if resp.choices and resp.choices[0].message else "0")

        return int(content.strip())
