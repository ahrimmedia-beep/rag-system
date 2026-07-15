from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import ask, health, ingest
from app.core.exceptions import RAGError
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="RAG System", version="0.1.0")
    app.include_router(health.router)
    app.include_router(ingest.router)
    app.include_router(ask.router)

    @app.exception_handler(RAGError)
    def _handle_rag_error(request: Request, exc: RAGError) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": "knowledge base unavailable"})

    return app


app = create_app()
