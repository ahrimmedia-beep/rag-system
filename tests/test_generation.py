from app.domain.models import Chunk, LLMResult, RetrievedChunk
from app.services.generation import GenerationService
from tests.fakes import FakeLLM


def _rc(text: str, **md: object) -> RetrievedChunk:
    return RetrievedChunk(chunk=Chunk(id="1", text=text, metadata=md), score=0.9)


def test_generation_uses_context_and_returns_sources():
    llm = FakeLLM([LLMResult(content="Do X (Lesson 1, 01:00).", tool_calls=[])])
    svc = GenerationService(llm)
    ans = svc.generate(
        "how?", [_rc("X is done so", source="l1.txt", lesson="Lesson 1", timecode="01:00")]
    )
    assert "Do X" in ans.answer
    assert ans.sources[0].lesson == "Lesson 1"
    # the retrieved text must be injected into the user message
    assert "X is done so" in llm.calls[0]["messages"][-1].content


def test_generation_empty_context_returns_fallback_without_llm():
    llm = FakeLLM([])  # must NOT be called
    svc = GenerationService(llm)
    ans = svc.generate("how?", [])
    assert ans.sources == []
    assert "no answer" in ans.answer.lower()
    assert llm.calls == []
