# RAG System

Provider-agnostic **agentic RAG** service: answers strictly from an ingested
knowledge base with inline source citations. FastAPI + LangChain + Qdrant,
clean hexagonal architecture.

## Architecture

Ports & adapters (hexagonal). Business logic (`app/services`) depends only on
interfaces in `app/domain`; concrete integrations live in `app/adapters` and are
wired by FastAPI dependency injection. Swapping the LLM provider (OpenAI →
DeepSeek → self-hosted Llama/Mistral via an OpenAI-compatible endpoint) or the
vector store touches exactly one adapter.

```
app/
  api/         FastAPI routes, schemas, DI
  domain/      ports (Protocols) + models
  adapters/    OpenAI-compatible LLM & embeddings, Qdrant
  services/    ingestion, retrieval, generation, memory, rag_agent
  prompts/     grounding system prompt
eval/          retrieval-quality metrics (precision@k, recall@k, hit-rate, MRR)
tests/         pytest with fakes — no network, no keys
```

## Run

```bash
cp .env.example .env      # set LLM_API_KEY (OpenAI-compatible)
docker compose up --build # app on :8000, qdrant on :6333
```

Ingest and ask:

```bash
curl -X POST localhost:8000/ingest -H 'content-type: application/json' \
  -d '{"text":"To withdraw USDT on TRC20 the fee is 1 USDT.","source":"Withdrawing USDT","section":"TRC20 network"}'

curl -X POST localhost:8000/ask -H 'content-type: application/json' \
  -d '{"session_id":"s1","question":"how do I withdraw usdt?"}'
```

## Develop

```bash
make install   # editable install with dev deps
make test      # pytest (no network/keys)
make lint      # ruff
make typecheck # mypy (strict)
make eval      # retrieval-quality metrics on the fixture set
```

## Design decisions

- **Agentic retrieval:** retrieval is exposed to the model as a `search_knowledge_base`
  tool, so the agent decides when to query the knowledge base vs. answer directly.
- **Grounding:** the system prompt forbids answering outside retrieved context,
  requires inline citations, and defines an explicit "insufficient context" fallback.
- **Provider abstraction:** `LLMProvider` / `EmbeddingsProvider` Protocols with an
  OpenAI-compatible adapter — no vendor lock-in.
- **Measurable retrieval:** the `eval/` harness scores retrieval on a labeled set,
  so chunking/top-k are tuned against metrics, not eyeballed.
