from typing import Protocol

from app.domain.models import LLMResult, Message


class LLMProvider(Protocol):
    def chat(
        self,
        system: str,
        messages: list[Message],
        tools: list[dict[str, object]] | None = None,
    ) -> LLMResult: ...
