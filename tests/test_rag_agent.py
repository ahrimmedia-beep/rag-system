from app.domain.models import Chunk, LLMResult, ToolCall
from app.services.generation import GenerationService
from app.services.memory import MemoryService
from app.services.rag_agent import RagAgentService
from app.services.retrieval import RetrievalService
from tests.fakes import FakeEmbeddings, FakeLLM, FakeVectorStore


def _store_with(*chunks: Chunk) -> FakeVectorStore:
    store = FakeVectorStore()
    emb = FakeEmbeddings()
    store.upsert(list(chunks), emb.embed_documents([c.text for c in chunks]))
    return store


def test_agent_calls_tool_then_answers_grounded():
    store = _store_with(Chunk(id="1", text="aaaa answer here", metadata={"lesson": "L1"}))
    retrieval = RetrievalService(FakeEmbeddings(), store, top_k=1)
    # call 1 (agent): decides to search -> tool call; call 2 (generation): final answer
    llm = FakeLLM(
        [
            LLMResult(
                content=None,
                tool_calls=[
                    ToolCall(id="t1", name="search_knowledge_base", arguments={"query": "aaaa"})
                ],
            ),
            LLMResult(content="Grounded answer (L1).", tool_calls=[]),
        ]
    )
    generation = GenerationService(llm)
    memory = MemoryService(window=20)
    agent = RagAgentService(llm, retrieval, generation, memory)
    ans = agent.answer("s1", "how?")
    assert ans.answer == "Grounded answer (L1)."
    assert ans.sources and ans.sources[0].lesson == "L1"
    assert len(memory.get("s1")) == 2


def test_agent_answers_directly_when_no_tool_call():
    store = _store_with(Chunk(id="1", text="x", metadata={}))
    retrieval = RetrievalService(FakeEmbeddings(), store)
    llm = FakeLLM([LLMResult(content="Hello!", tool_calls=[])])
    agent = RagAgentService(llm, retrieval, GenerationService(FakeLLM([])), MemoryService())
    ans = agent.answer("s1", "hi")
    assert ans.answer == "Hello!" and ans.sources == []
