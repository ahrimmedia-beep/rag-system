def precision_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    top = retrieved_ids[:k]
    if not top:
        return 0.0
    return sum(1 for i in top if i in relevant_ids) / len(top)


def recall_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    if not relevant_ids:
        return 0.0
    top = retrieved_ids[:k]
    return sum(1 for i in top if i in relevant_ids) / len(relevant_ids)


def hit_rate(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    return 1.0 if any(i in relevant_ids for i in retrieved_ids[:k]) else 0.0


def mrr(retrieved_ids: list[str], relevant_ids: set[str]) -> float:
    for rank, i in enumerate(retrieved_ids, start=1):
        if i in relevant_ids:
            return 1.0 / rank
    return 0.0
