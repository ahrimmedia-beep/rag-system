from app.adapters.in_memory import DeterministicEmbeddings as FakeEmbeddings
from app.adapters.in_memory import InMemoryVectorStore as FakeVectorStore
from app.domain.models import LLMResult, Message

__all__ = ["FakeEmbeddings", "FakeVectorStore", "FakeLLM"]


class FakeLLM:
    def __init__(self, responses: list[LLMResult]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def chat(
        self,
        system: str,
        messages: list[Message],
        tools: list[dict[str, object]] | None = None,
    ) -> LLMResult:
        self.calls.append({"system": system, "messages": messages, "tools": tools})
        return self._responses.pop(0)
