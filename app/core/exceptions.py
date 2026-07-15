class RAGError(Exception):
    """Base domain error."""


class KnowledgeBaseUnavailable(RAGError):
    """Raised when the vector store cannot be reached."""
