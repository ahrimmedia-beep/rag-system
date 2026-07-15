from app.domain.models import Chunk, LLMResult, RetrievedChunk
from app.services.generation import GenerationService
from tests.fakes import FakeLLM


def _rc(text: str, **md: object) -> RetrievedChunk:
    return RetrievedChunk(chunk=Chunk(id="1", text=text, metadata=md), score=0.9)


def test_generation_uses_context_and_returns_sources():
    llm = FakeLLM([LLMResult(content="Do X (Withdrawing USDT, TRC20 network).", tool_calls=[])])
    svc = GenerationService(llm)
    ans = svc.generate(
        "how?",
        [_rc("X is done so", source="Withdrawing USDT", section="TRC20 network")],
    )
    assert "Do X" in ans.answer
    assert ans.sources[0].section == "TRC20 network"
    # the retrieved text must be injected into the user message
    assert "X is done so" in llm.calls[0]["messages"][-1].content


def test_generation_empty_context_returns_fallback_without_llm():
    llm = FakeLLM([])  # must NOT be called
    svc = GenerationService(llm)
    ans = svc.generate("how?", [])
    assert ans.sources == []
    assert "couldn't find this" in ans.answer.lower()
    assert llm.calls == []
