# Small labeled fixture set. Each document has an id + text; each query lists the
# document ids considered relevant. Kept tiny and deterministic for reproducible eval.
DOCUMENTS: list[dict[str, str]] = [
    {
        "id": "vpn",
        "text": "To connect to the course VPN, install the client and use the lesson-3 token.",
    },
    {
        "id": "ide",
        "text": "Set up the IDE in lesson 2: install the extension pack and open the workspace.",
    },
    {
        "id": "deadline",
        "text": "Homework for module 1 is due at the end of week two; submit via the portal.",
    },
]

QUERIES: list[dict[str, object]] = [
    {"question": "how do I connect to the vpn?", "relevant": {"vpn"}},
    {"question": "where do I set up my editor?", "relevant": {"ide"}},
    {"question": "when is the first homework due?", "relevant": {"deadline"}},
]
