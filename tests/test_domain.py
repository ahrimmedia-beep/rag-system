from app.domain.models import Answer, Chunk, LLMResult, Message, RetrievedChunk, Source, ToolCall


def test_models_construct():
    c = Chunk(id="1", text="hello", metadata={"source": "l1"})
    rc = RetrievedChunk(chunk=c, score=0.9)
    src = Source(source="l1", section="Withdrawing USDT", score=0.9)
    ans = Answer(answer="hi", sources=[src])
    msg = Message(role="user", content="q")
    tc = ToolCall(id="t1", name="search", arguments={"query": "x"})
    res = LLMResult(content=None, tool_calls=[tc])
    assert rc.score == 0.9 and ans.sources[0].section == "Withdrawing USDT"
    assert msg.role == "user" and res.tool_calls[0].name == "search"
