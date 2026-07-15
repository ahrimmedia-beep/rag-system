from statistics import mean

from app.adapters.in_memory import DeterministicEmbeddings, InMemoryVectorStore
from app.services.ingestion import IngestionService
from app.services.retrieval import RetrievalService
from eval.dataset import DOCUMENTS, QUERIES
from eval.metrics import hit_rate, mrr, precision_at_k, recall_at_k

K = 2
EMBEDDINGS_DIM = 3


def main() -> None:
    store = InMemoryVectorStore()
    embeddings = DeterministicEmbeddings()
    ingestion = IngestionService(
        embeddings, store, embeddings_dim=EMBEDDINGS_DIM, chunk_size=1000, chunk_overlap=0
    )
    for doc in DOCUMENTS:
        ingestion.ingest(doc["text"], {"source": doc["id"], "doc_id": doc["id"]})

    retrieval = RetrievalService(embeddings, store, top_k=K)
    p, r, h, m = [], [], [], []
    for q in QUERIES:
        hits = retrieval.retrieve(str(q["question"]))
        ids = [str(hit.chunk.metadata.get("doc_id")) for hit in hits]
        relevant = set(q["relevant"])  # type: ignore[call-overload]
        p.append(precision_at_k(ids, relevant, K))
        r.append(recall_at_k(ids, relevant, K))
        h.append(hit_rate(ids, relevant, K))
        m.append(mrr(ids, relevant))

    print(f"Queries: {len(QUERIES)}  (k={K})")
    print(f"precision@{K}: {mean(p):.3f}")
    print(f"recall@{K}:    {mean(r):.3f}")
    print(f"hit-rate@{K}:  {mean(h):.3f}")
    print(f"MRR:          {mean(m):.3f}")


if __name__ == "__main__":
    main()
