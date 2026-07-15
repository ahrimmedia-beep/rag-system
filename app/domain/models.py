from dataclasses import dataclass, field


@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float


@dataclass
class Source:
    source: str
    section: str | None
    score: float


@dataclass
class Answer:
    answer: str
    sources: list[Source]


@dataclass
class Message:
    role: str  # "user" | "assistant" | "tool"
    content: str


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, object]


@dataclass
class LLMResult:
    content: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
