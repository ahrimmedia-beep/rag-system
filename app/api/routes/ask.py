from fastapi import APIRouter, Depends

from app.api.dependencies import get_rag_agent_service
from app.api.schemas import AskRequest, AskResponse, SourceModel
from app.services.rag_agent import RagAgentService

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask(
    body: AskRequest,
    service: RagAgentService = Depends(get_rag_agent_service),
) -> AskResponse:
    answer = service.answer(body.session_id, body.question)
    return AskResponse(
        answer=answer.answer,
        sources=[
            SourceModel(source=s.source, lesson=s.lesson, timecode=s.timecode, score=s.score)
            for s in answer.sources
        ],
    )
