from app.domain.llm import LLMProvider
from app.domain.models import Answer, Message, RetrievedChunk, Source
from app.prompts.support import FALLBACK, SYSTEM_PROMPT


class GenerationService:
    def __init__(
        self,
        llm: LLMProvider,
        system_prompt: str = SYSTEM_PROMPT,
        fallback: str = FALLBACK,
    ) -> None:
        self._llm = llm
        self._system_prompt = system_prompt
        self._fallback = fallback

    def generate(
        self,
        question: str,
        retrieved: list[RetrievedChunk],
        history: list[Message] | None = None,
    ) -> Answer:
        if not retrieved:
            return Answer(answer=self._fallback, sources=[])
        context = self._format_context(retrieved)
        messages = list(history or [])
        messages.append(
            Message(role="user", content=f"Question: {question}\n\nCONTEXT:\n{context}")
        )
        result = self._llm.chat(self._system_prompt, messages)
        return Answer(answer=result.content or self._fallback, sources=self._sources(retrieved))

    @staticmethod
    def _format_context(retrieved: list[RetrievedChunk]) -> str:
        blocks = []
        for r in retrieved:
            md = r.chunk.metadata
            label = str(md.get("section") or md.get("source") or "source")
            header = f"[{label}]"
            blocks.append(f"{header}\n{r.chunk.text}")
        return "\n\n".join(blocks)

    @staticmethod
    def _sources(retrieved: list[RetrievedChunk]) -> list[Source]:
        return [
            Source(
                source=str(r.chunk.metadata.get("source", "unknown")),
                section=(
                    str(r.chunk.metadata["section"]) if "section" in r.chunk.metadata else None
                ),
                score=r.score,
            )
            for r in retrieved
        ]
