from fastapi import APIRouter, Depends, Response

from app.api.dependencies import get_vector_store
from app.domain.vector_store import VectorStore

router = APIRouter()


@router.get("/health")
def health(response: Response, store: VectorStore = Depends(get_vector_store)) -> dict[str, object]:
    qdrant_ok = store.health_check()
    if not qdrant_ok:
        response.status_code = 503
    return {"status": "ok", "qdrant": qdrant_ok}
