from fastapi import APIRouter, Depends

from app.api.dependencies import get_ingestion_service
from app.api.schemas import IngestRequest, IngestResponse
from app.services.ingestion import IngestionService

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
def ingest(
    body: IngestRequest,
    service: IngestionService = Depends(get_ingestion_service),
) -> IngestResponse:
    metadata: dict[str, object] = {"source": body.source}
    if body.lesson is not None:
        metadata["lesson"] = body.lesson
    if body.timecode is not None:
        metadata["timecode"] = body.timecode
    n = service.ingest(body.text, metadata)
    return IngestResponse(ingested_chunks=n, source=body.source)
