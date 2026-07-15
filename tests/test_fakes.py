from app.domain.models import Chunk, LLMResult
from tests.fakes import FakeEmbeddings, FakeLLM, FakeVectorStore


def test_fake_vector_store_ranks_by_similarity():
    store = FakeVectorStore()
    emb = FakeEmbeddings()
    chunks = [Chunk(id="1", text="aaa", metadata={}), Chunk(id="2", text="eee", metadata={})]
    store.upsert(chunks, emb.embed_documents([c.text for c in chunks]))
    hits = store.search(emb.embed_query("aaa"), top_k=1)
    assert hits[0].chunk.id == "1"


def test_fake_llm_pops_scripted_responses():
    llm = FakeLLM([LLMResult(content="hi", tool_calls=[])])
    out = llm.chat("sys", [])
    assert out.content == "hi" and len(llm.calls) == 1


def test_fake_vector_store_health_check_is_always_true():
    assert FakeVectorStore().health_check() is True
