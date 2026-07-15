import threading

from app.services.memory import MemoryService


def test_memory_is_per_session():
    m = MemoryService(window=20)
    m.append("a", "q1", "a1")
    m.append("b", "q2", "a2")
    assert len(m.get("a")) == 2
    assert m.get("a")[0].content == "q1"
    assert m.get("b")[0].content == "q2"


def test_memory_trims_to_window():
    m = MemoryService(window=4)
    for i in range(5):
        m.append("s", f"q{i}", f"a{i}")
    history = m.get("s")
    assert len(history) == 4
    assert history[0].content == "q3"  # oldest kept


def test_memory_append_is_thread_safe():
    m = MemoryService(window=1000)
    threads = [threading.Thread(target=m.append, args=("s", f"q{i}", f"a{i}")) for i in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # 50 concurrent appends * 2 messages each, none lost or corrupted by a race
    assert len(m.get("s")) == 100
