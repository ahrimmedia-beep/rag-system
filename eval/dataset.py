# Small labeled fixture set. Each document has an id + text; each query lists the
# document ids considered relevant. Kept tiny and deterministic for reproducible eval.
DOCUMENTS: list[dict[str, str]] = [
    {
        "id": "usdt",
        "text": (
            "To withdraw USDT on the TRC20 network the fee is 1 USDT and it is processed "
            "within 5 minutes; the ERC20 network costs more because of Ethereum gas."
        ),
    },
    {
        "id": "kyc",
        "text": (
            "Without identity verification the daily withdrawal limit is 2 BTC; completing "
            "KYC (passport and a selfie) raises the daily limit to 100 BTC."
        ),
    },
    {
        "id": "fees",
        "text": (
            "Spot trading fees are 0.1% for makers and 0.1% for takers; holding the exchange "
            "native token lowers the taker fee to 0.075%."
        ),
    },
]

QUERIES: list[dict[str, object]] = [
    {"question": "how do I withdraw usdt cheaply?", "relevant": {"usdt"}},
    {"question": "what is the withdrawal limit without verification?", "relevant": {"kyc"}},
    {"question": "what is the maker fee?", "relevant": {"fees"}},
]
