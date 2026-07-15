from app.config import Settings


def test_settings_have_expected_defaults():
    s = Settings(_env_file=None)
    assert s.chunk_size == 900
    assert s.chunk_overlap == 50
    assert s.top_k == 5
    assert s.memory_window == 20
    assert s.llm_base_url == "https://api.openai.com/v1"
    assert s.embeddings_dim == 1536
    assert s.score_threshold == 0.0
