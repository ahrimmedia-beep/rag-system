import json
from types import SimpleNamespace

from app.adapters.embeddings_openai import OpenAIEmbeddings
from app.adapters.llm_openai import OpenAILLM
from app.domain.models import Message


class _FakeOpenAIClient:
    def __init__(self) -> None:
        self.embeddings = SimpleNamespace(create=self._embeddings_create)
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._chat_create))
        self.last_kwargs: dict = {}

    def _embeddings_create(self, model: str, input: list[str]):
        return SimpleNamespace(data=[SimpleNamespace(embedding=[float(len(t))]) for t in input])

    def _chat_create(self, **kwargs):
        self.last_kwargs = kwargs
        fn = SimpleNamespace(name="search_knowledge_base", arguments=json.dumps({"query": "q"}))
        tc = SimpleNamespace(id="t1", function=fn)
        msg = SimpleNamespace(content=None, tool_calls=[tc])
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)])


def test_embeddings_adapter_maps_response():
    emb = OpenAIEmbeddings("http://x", "k", "m", client=_FakeOpenAIClient())
    assert emb.embed_query("abcd") == [4.0]


def test_llm_adapter_parses_tool_calls():
    client = _FakeOpenAIClient()
    llm = OpenAILLM("http://x", "k", "m", client=client)
    result = llm.chat("sys", [Message("user", "hi")], tools=[{"type": "function"}])
    assert result.content is None
    assert result.tool_calls[0].name == "search_knowledge_base"
    assert result.tool_calls[0].arguments == {"query": "q"}
    assert client.last_kwargs["messages"][0]["role"] == "system"
