from eval.metrics import hit_rate, mrr, precision_at_k, recall_at_k

RETRIEVED = ["a", "b", "c", "d"]
RELEVANT = {"b", "d", "z"}


def test_precision_at_k():
    assert precision_at_k(RETRIEVED, RELEVANT, k=2) == 0.5  # {b} of {a,b}


def test_recall_at_k():
    assert recall_at_k(RETRIEVED, RELEVANT, k=4) == 2 / 3  # {b,d} of {b,d,z}


def test_hit_rate():
    assert hit_rate(RETRIEVED, RELEVANT, k=2) == 1.0
    assert hit_rate(["a", "c"], RELEVANT, k=2) == 0.0


def test_mrr_uses_first_relevant_rank():
    assert mrr(RETRIEVED, RELEVANT) == 0.5  # first relevant "b" at rank 2
    assert mrr(["a", "c"], RELEVANT) == 0.0
