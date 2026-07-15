from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    text: str = Field(min_length=1)
    source: str
    section: str | None = None


class IngestResponse(BaseModel):
    ingested_chunks: int
    source: str


class AskRequest(BaseModel):
    session_id: str = Field(min_length=1)
    question: str = Field(min_length=1)


class SourceModel(BaseModel):
    source: str
    section: str | None = None
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceModel]
